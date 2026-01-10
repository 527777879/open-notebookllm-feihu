import apiClient from './client'
import type { ChatMessage, ApiResponse } from '@/types'

// 取得對話歷史
export const getMessages = (notebookId: string) =>
  apiClient.get<ApiResponse<ChatMessage[]>>(`/api/notebooks/${notebookId}/chats`)

// 發送訊息（非串流）
export const sendMessage = (
  notebookId: string,
  message: string,
  sourceIds?: string[]
) =>
  apiClient.post<ApiResponse<ChatMessage>>(`/api/notebooks/${notebookId}/chats`, {
    message,
    source_ids: sourceIds,
  })

// 串流發送訊息
export const streamMessage = async (
  notebookId: string,
  message: string,
  sourceIds: string[] | undefined,
  onChunk: (chunk: string) => void,
  onSources: (refs: unknown[]) => void,
  onDone: (messageId: string) => void,
  onError: (error: string) => void
) => {
  try {
    const response = await fetch(`/api/notebooks/${notebookId}/chats/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, source_ids: sourceIds }),
    })

    if (!response.ok) {
      throw new Error('串流請求失敗')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('無法讀取串流')
    }

    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'chunk') {
              onChunk(data.content)
            } else if (data.type === 'sources') {
              onSources(data.references)
            } else if (data.type === 'done') {
              onDone(data.message_id)
            } else if (data.type === 'error') {
              onError(data.message)
            }
          } catch {
            // 忽略解析錯誤
          }
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error.message : '未知錯誤')
  }
}

// 取得建議問題
export const getSuggestedQuestions = (notebookId: string) =>
  apiClient.get<ApiResponse<string[]>>(`/api/notebooks/${notebookId}/suggested-questions`)

// 刪除訊息
export const deleteMessage = (notebookId: string, messageId: string) =>
  apiClient.delete<ApiResponse<void>>(`/api/notebooks/${notebookId}/chats/${messageId}`)

// 清空對話
export const clearMessages = (notebookId: string) =>
  apiClient.delete<ApiResponse<void>>(`/api/notebooks/${notebookId}/chats/clear`)
