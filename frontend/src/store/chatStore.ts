import { create } from 'zustand'
import type { ChatMessage, SourceReference } from '@/types'
import * as chatApi from '@/api/chat'

interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  isStreaming: boolean
  streamingContent: string
  suggestedQuestions: string[]
  currentSourceRefs: SourceReference[]
  error: string | null

  // Actions
  fetchMessages: (notebookId: string) => Promise<void>
  sendMessage: (notebookId: string, message: string, sourceIds?: string[]) => Promise<void>
  sendStreamMessage: (notebookId: string, message: string, sourceIds?: string[]) => Promise<void>
  fetchSuggestedQuestions: (notebookId: string) => Promise<void>
  deleteMessage: (notebookId: string, messageId: string) => Promise<void>
  clearMessages: (notebookId: string) => Promise<void>
  clearError: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  isStreaming: false,
  streamingContent: '',
  suggestedQuestions: [],
  currentSourceRefs: [],
  error: null,

  fetchMessages: async (notebookId: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await chatApi.getMessages(notebookId)
      if (response.data.success && response.data.data) {
        set({ messages: response.data.data })
      }
    } catch (error) {
      set({ error: '無法載入對話歷史' })
    } finally {
      set({ isLoading: false })
    }
  },

  sendMessage: async (notebookId: string, message: string, sourceIds?: string[]) => {
    set({ isLoading: true, error: null })

    // 先添加用戶訊息到 UI
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      notebook_id: notebookId,
      role: 'user',
      content: message,
      used_source_ids: sourceIds,
      created_at: new Date().toISOString(),
    }
    set((state) => ({ messages: [...state.messages, userMessage] }))

    try {
      const response = await chatApi.sendMessage(notebookId, message, sourceIds)
      if (response.data.success && response.data.data) {
        // 更新用戶訊息 ID 並添加助手回應
        set((state) => ({
          messages: [
            ...state.messages.slice(0, -1), // 移除臨時用戶訊息
            { ...userMessage, id: response.data.data!.id.replace('assistant', 'user') },
            response.data.data!,
          ],
        }))
      }
    } catch (error) {
      set({ error: '發送訊息失敗' })
      // 移除臨時訊息
      set((state) => ({ messages: state.messages.slice(0, -1) }))
    } finally {
      set({ isLoading: false })
    }
  },

  sendStreamMessage: async (notebookId: string, message: string, sourceIds?: string[]) => {
    set({ isStreaming: true, streamingContent: '', currentSourceRefs: [], error: null })

    // 先添加用戶訊息
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      notebook_id: notebookId,
      role: 'user',
      content: message,
      used_source_ids: sourceIds,
      created_at: new Date().toISOString(),
    }
    set((state) => ({ messages: [...state.messages, userMessage] }))

    await chatApi.streamMessage(
      notebookId,
      message,
      sourceIds,
      // onChunk
      (chunk: string) => {
        set((state) => ({ streamingContent: state.streamingContent + chunk }))
      },
      // onSources
      (refs: unknown[]) => {
        set({ currentSourceRefs: refs as SourceReference[] })
      },
      // onDone
      (messageId: string) => {
        const { streamingContent, currentSourceRefs } = get()
        const assistantMessage: ChatMessage = {
          id: messageId,
          notebook_id: notebookId,
          role: 'assistant',
          content: streamingContent,
          source_refs: currentSourceRefs,
          used_source_ids: sourceIds,
          created_at: new Date().toISOString(),
        }
        set((state) => ({
          messages: [...state.messages, assistantMessage],
          isStreaming: false,
          streamingContent: '',
        }))
      },
      // onError
      (error: string) => {
        set({ error, isStreaming: false, streamingContent: '' })
      }
    )
  },

  fetchSuggestedQuestions: async (notebookId: string) => {
    try {
      const response = await chatApi.getSuggestedQuestions(notebookId)
      if (response.data.success && response.data.data) {
        set({ suggestedQuestions: response.data.data })
      }
    } catch (error) {
      // 靜默失敗
    }
  },

  deleteMessage: async (notebookId: string, messageId: string) => {
    try {
      await chatApi.deleteMessage(notebookId, messageId)
      set((state) => ({
        messages: state.messages.filter((m) => m.id !== messageId),
      }))
    } catch (error) {
      set({ error: '刪除訊息失敗' })
    }
  },

  clearMessages: async (notebookId: string) => {
    try {
      await chatApi.clearMessages(notebookId)
      set({ messages: [] })
    } catch (error) {
      set({ error: '清空對話失敗' })
    }
  },

  clearError: () => {
    set({ error: null })
  },
}))
