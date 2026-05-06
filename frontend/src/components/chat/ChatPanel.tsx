import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Send, Sparkles, Copy, ThumbsUp, ThumbsDown, Bookmark } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChatStore, useSourceStore } from '@/store'
import Button from '@/components/common/Button'
import type { ChatMessage } from '@/types'

interface ChatPanelProps {
  notebookId: string
}

export default function ChatPanel({ notebookId }: ChatPanelProps) {
  const { t } = useTranslation('chat')
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const {
    messages,
    isStreaming,
    streamingContent,
    suggestedQuestions,
    sendStreamMessage,
  } = useChatStore()

  const { selectedIds } = useSourceStore()

  // 自動滾動到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  const handleSend = async () => {
    if (!inputValue.trim() || isStreaming) return

    const message = inputValue.trim()
    setInputValue('')

    await sendStreamMessage(
      notebookId,
      message,
      selectedIds.length > 0 ? selectedIds : undefined
    )
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question)
    inputRef.current?.focus()
  }

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  // 複製全部對話
  const handleCopyAll = () => {
    const allContent = messages
      .map((m) => `${m.role === 'user' ? t('user') : t('ai')}: ${m.content}`)
      .join('\n\n')
    navigator.clipboard.writeText(allContent)
    alert(t('copiedAll'))
  }

  // 匯出對話
  const handleExport = () => {
    const allContent = messages
      .map((m) => `## ${m.role === 'user' ? t('user') : t('ai')}\n\n${m.content}`)
      .join('\n\n---\n\n')

    const blob = new Blob([allContent], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${t('exportPrefix')}${new Date().toISOString().slice(0, 10)}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="h-full flex flex-col">
      {/* 標題區 */}
      <div className="p-4 border-b border-gray-200 bg-white flex items-center justify-between">
        <h2 className="font-semibold text-gray-900">{t('title')}</h2>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={handleExport} disabled={messages.length === 0}>
            {t('export')}
          </Button>
          <Button variant="ghost" size="sm" onClick={handleCopyAll} disabled={messages.length === 0}>
            {t('copyAll')}
          </Button>
        </div>
      </div>

      {/* 訊息區 */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && !isStreaming ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {t('startUsing')}
            </h3>
            <p className="text-gray-500 text-sm max-w-sm">
              {t('startUsingDesc')}
            </p>

            {/* 建議問題 */}
            {suggestedQuestions.length > 0 && (
              <div className="mt-6 space-y-2 w-full max-w-md">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="w-full text-left px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-sm text-gray-700"
                  >
                    <Sparkles className="w-4 h-4 inline-block mr-2 text-primary-500" />
                    {question}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message: ChatMessage) => (
              <MessageBubble
                key={message.id}
                message={message}
                onCopy={() => handleCopy(message.content)}
              />
            ))}

            {/* 串流中的訊息 */}
            {isStreaming && streamingContent && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1 bg-white border border-gray-200 rounded-lg p-4">
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {streamingContent}
                    </ReactMarkdown>
                  </div>
                  <div className="mt-2 flex items-center gap-1">
                    <span className="inline-block w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
                    <span className="text-xs text-gray-400">{t('generating')}</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* 輸入區 */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t('inputPlaceholder')}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
              {selectedIds.length > 0 ? t('selectedSources', { count: selectedIds.length }) : t('allSources')}
            </span>
          </div>
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim() || isStreaming}
            className="px-4"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}

// 訊息氣泡組件
function MessageBubble({
  message,
  onCopy,
}: {
  message: ChatMessage
  onCopy: () => void
}) {
  const { t } = useTranslation('chat')
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null)
  const [isBookmarked, setIsBookmarked] = useState(false)
  const isUser = message.role === 'user'

  const handleThumbsUp = () => {
    setFeedback(feedback === 'up' ? null : 'up')
  }

  const handleThumbsDown = () => {
    setFeedback(feedback === 'down' ? null : 'down')
  }

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked)
    if (!isBookmarked) {
      // 複製到剪貼簿作為「儲存」的暫時方案
      navigator.clipboard.writeText(message.content)
      alert(t('savedToClipboard'))
    }
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-gray-200' : 'bg-primary-600'
        }`}
      >
        {isUser ? (
          <span className="text-sm font-medium text-gray-600">U</span>
        ) : (
          <Sparkles className="w-4 h-4 text-white" />
        )}
      </div>

      <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : ''}`}>
        <div
          className={`inline-block rounded-lg p-4 ${
            isUser
              ? 'bg-primary-600 text-white'
              : 'bg-white border border-gray-200'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* 來源引用 */}
        {!isUser && message.source_refs && message.source_refs.length > 0 && (
          <div className="mt-2 text-xs text-gray-500">
            {t('sourceRef')} {message.source_refs.map((ref) => ref.source_name).join(', ')}
          </div>
        )}

        {/* 操作按鈕 */}
        {!isUser && (
          <div className="mt-2 flex items-center gap-1">
            <button
              onClick={onCopy}
              className="p-1.5 rounded hover:bg-gray-100 transition-colors"
              title={t('copyTitle')}
            >
              <Copy className="w-4 h-4 text-gray-400" />
            </button>
            <button
              onClick={handleThumbsUp}
              className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${feedback === 'up' ? 'bg-green-100' : ''}`}
              title={t('thumbsUp')}
            >
              <ThumbsUp className={`w-4 h-4 ${feedback === 'up' ? 'text-green-600' : 'text-gray-400'}`} />
            </button>
            <button
              onClick={handleThumbsDown}
              className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${feedback === 'down' ? 'bg-red-100' : ''}`}
              title={t('thumbsDown')}
            >
              <ThumbsDown className={`w-4 h-4 ${feedback === 'down' ? 'text-red-600' : 'text-gray-400'}`} />
            </button>
            <button
              onClick={handleBookmark}
              className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${isBookmarked ? 'bg-yellow-100' : ''}`}
              title={t('bookmark')}
            >
              <Bookmark className={`w-4 h-4 ${isBookmarked ? 'text-yellow-600' : 'text-gray-400'}`} />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
