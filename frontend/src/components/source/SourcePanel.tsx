import { useState, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Plus,
  Search,
  FileText,
  Globe,
  Youtube,
  File,
  Trash2,
  Upload,
  Link,
  CheckSquare,
  Square,
  Music,
  Mic,
  RefreshCw,
} from 'lucide-react'
import { useSourceStore } from '@/store'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Modal from '@/components/common/Modal'
import type { SourceType } from '@/types'
import { isAudioFile } from '@/api/sources'

interface SourcePanelProps {
  notebookId: string
}

const sourceTypeIcons: Record<SourceType, typeof FileText> = {
  pdf: FileText,
  text: File,
  web: Globe,
  youtube: Youtube,
  gdocs: FileText,
  audio: Music,
}

export default function SourcePanel({ notebookId }: SourcePanelProps) {
  const { t } = useTranslation(['source', 'common'])

  const sourceTypeLabels: Record<SourceType | 'all', string> = {
    all: t('typeLabels.all'),
    pdf: t('typeLabels.pdf'),
    text: t('typeLabels.text'),
    web: t('typeLabels.web'),
    youtube: t('typeLabels.youtube'),
    gdocs: t('typeLabels.gdocs'),
    audio: t('typeLabels.audio'),
  }

  const sttProviders = [
    { id: 'openai' as const, name: 'OpenAI Whisper', description: t('sttProviders.openai.description') },
    { id: 'groq' as const, name: 'Groq Whisper', description: t('sttProviders.groq.description') },
    { id: 'local' as const, name: '本地 Whisper', description: t('sttProviders.local.description') },
  ]
  const fileInputRef = useRef<HTMLInputElement>(null)
  const audioInputRef = useRef<HTMLInputElement>(null)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [addType, setAddType] = useState<'file' | 'audio' | 'url' | 'youtube' | 'text'>('file')
  const [urlInput, setUrlInput] = useState('')
  const [textName, setTextName] = useState('')
  const [textContent, setTextContent] = useState('')
  const [selectedSttProvider, setSelectedSttProvider] = useState<'openai' | 'groq' | 'local'>('openai')
  const [sttLanguage, setSttLanguage] = useState('zh')

  const {
    selectedIds,
    filterType,
    searchQuery,
    isUploading,
    getFilteredSources,
    setFilter,
    setSearchQuery,
    toggleSelection,
    selectAll,
    clearSelection,
    uploadFile,
    addUrl,
    addYoutube,
    addText,
    deleteSource,
    reembedSource,
  } = useSourceStore()

  const [reembeddingId, setReembeddingId] = useState<string | null>(null)

  const filteredSources = getFilteredSources()
  const allSelected = filteredSources.length > 0 && selectedIds.length === filteredSources.length

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // 檢查是否為音檔
      if (isAudioFile(file.name)) {
        await uploadFile(notebookId, file, {
          sttProvider: selectedSttProvider,
          language: sttLanguage,
        })
      } else {
        await uploadFile(notebookId, file)
      }
      e.target.value = ''
      setIsAddModalOpen(false)
    }
  }

  const handleAudioChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      await uploadFile(notebookId, file, {
        sttProvider: selectedSttProvider,
        language: sttLanguage,
      })
      e.target.value = ''
      setIsAddModalOpen(false)
    }
  }

  const handleAddUrl = async () => {
    if (!urlInput.trim()) return

    if (addType === 'youtube') {
      await addYoutube(notebookId, urlInput)
    } else {
      await addUrl(notebookId, urlInput)
    }

    setUrlInput('')
    setIsAddModalOpen(false)
  }

  const handleAddText = async () => {
    if (!textContent.trim()) return

    await addText(notebookId, textName || t('unnamedText'), textContent)
    setTextName('')
    setTextContent('')
    setIsAddModalOpen(false)
  }

  const handleDelete = async (sourceId: string) => {
    if (window.confirm(t('deleteConfirm'))) {
      await deleteSource(sourceId)
    }
  }

  const handleReembed = async (sourceId: string) => {
    setReembeddingId(sourceId)
    await reembedSource(sourceId)
    setReembeddingId(null)
  }

  // 可重新嵌入的文件類型
  const isReembedableType = (type: SourceType) => ['pdf', 'text'].includes(type)

  return (
    <div className="h-full flex flex-col">
      {/* 標題區 */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-900">{t('title')}</h2>
          <Button
            size="sm"
            onClick={() => setIsAddModalOpen(true)}
          >
            <Plus className="w-4 h-4 mr-1" />
            {t('addSource')}
          </Button>
        </div>

        {/* 搜尋 */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={t('searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* 類型篩選 */}
      <div className="px-4 py-2 border-b border-gray-200 flex flex-wrap gap-1.5">
        {(Object.keys(sourceTypeLabels) as (SourceType | 'all')[]).map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
              filterType === type
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {sourceTypeLabels[type]}
          </button>
        ))}
      </div>

      {/* 全選 */}
      <div className="px-4 py-2 border-b border-gray-200">
        <button
          onClick={() => (allSelected ? clearSelection() : selectAll())}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          {allSelected ? (
            <CheckSquare className="w-4 h-4 text-primary-600" />
          ) : (
            <Square className="w-4 h-4" />
          )}
          {t('selectAll')}
        </button>
      </div>

      {/* 來源列表 */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredSources.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-sm">
            <p>{t('noSources')}</p>
            <p className="mt-1">{t('noSourcesDesc')}</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredSources.map((source) => {
              const Icon = sourceTypeIcons[source.type] || File
              const isSelected = selectedIds.includes(source.id)

              return (
                <div
                  key={source.id}
                  className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                    isSelected ? 'bg-primary-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => toggleSelection(source.id)}
                >
                  <div
                    className={`w-4 h-4 rounded border flex items-center justify-center ${
                      isSelected
                        ? 'bg-primary-600 border-primary-600'
                        : 'border-gray-300'
                    }`}
                  >
                    {isSelected && <Check className="w-3 h-3 text-white" />}
                  </div>

                  <Icon className="w-4 h-4 text-gray-400 flex-shrink-0" />

                  <span className="flex-1 text-sm text-gray-700 truncate">
                    {source.name}
                  </span>

                  {source.type === 'audio' && (
                    <span className="text-xs px-1.5 py-0.5 bg-purple-100 text-purple-600 rounded">
                      🎵
                    </span>
                  )}

                  {isReembedableType(source.type) && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleReembed(source.id)
                      }}
                      disabled={reembeddingId === source.id}
                      className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-blue-50 transition-all"
                      title={t('reembed')}
                    >
                      <RefreshCw className={`w-3.5 h-3.5 text-blue-500 ${reembeddingId === source.id ? 'animate-spin' : ''}`} />
                    </button>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(source.id)
                    }}
                    className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-50 transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-500" />
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* 新增來源 Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title={t('addSourceModal')}
      >
        <div className="space-y-4">
          {/* 類型選擇 */}
          <div className="flex gap-2 flex-wrap">
            {[
              { type: 'file' as const, icon: Upload, label: t('addTypes.file') },
              { type: 'audio' as const, icon: Mic, label: t('addTypes.audio') },
              { type: 'url' as const, icon: Link, label: t('addTypes.url') },
              { type: 'youtube' as const, icon: Youtube, label: 'YouTube' },
              { type: 'text' as const, icon: FileText, label: t('addTypes.text') },
            ].map(({ type, icon: Icon, label }) => (
              <button
                key={type}
                onClick={() => setAddType(type)}
                className={`flex-1 min-w-[80px] flex flex-col items-center gap-2 p-3 rounded-lg border transition-colors ${
                  addType === type
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon className={`w-5 h-5 ${addType === type ? 'text-primary-600' : 'text-gray-400'}`} />
                <span className="text-xs">{label}</span>
              </button>
            ))}
          </div>

          {/* 內容區 */}
          {addType === 'file' && (
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md,.docx,.doc,.xlsx,.xls,.csv"
                onChange={handleFileChange}
                className="hidden"
              />
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 transition-colors"
              >
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">{t('fileUpload')}</p>
                <p className="text-xs text-gray-400 mt-1">{t('fileSupport')}</p>
              </div>
            </div>
          )}

          {addType === 'audio' && (
            <div className="space-y-4">
              <input
                ref={audioInputRef}
                type="file"
                accept=".mp3,.mp4,.mpeg,.mpga,.m4a,.wav,.webm,.ogg,.flac"
                onChange={handleAudioChange}
                className="hidden"
              />
              <div
                onClick={() => audioInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 transition-colors"
              >
                <Mic className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">{t('audioUpload')}</p>
                <p className="text-xs text-gray-400 mt-1">{t('audioSupport')}</p>
              </div>

              {/* STT 提供商選擇 */}
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  {t('sttService')}
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {sttProviders.map((provider) => (
                    <label
                      key={provider.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedSttProvider === provider.id
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="sttProvider"
                        value={provider.id}
                        checked={selectedSttProvider === provider.id}
                        onChange={(e) => setSelectedSttProvider(e.target.value as typeof selectedSttProvider)}
                        className="w-4 h-4 text-primary-600"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{provider.name}</p>
                        <p className="text-xs text-gray-500">{provider.description}</p>
                      </div>
                    </label>
                  ))}
                </div>

                {/* 語言選擇 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('language')}
                  </label>
                  <select
                    value={sttLanguage}
                    onChange={(e) => setSttLanguage(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                  >
                    <option value="zh">中文</option>
                    <option value="en">English</option>
                    <option value="ja">日本語</option>
                    <option value="ko">한국어</option>
                    <option value="auto">{t('autoDetect')}</option>
                  </select>
                </div>
              </div>

              {isUploading && (
                <div className="bg-blue-50 p-3 rounded-lg text-sm text-blue-700 flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  {t('transcribing')}
                </div>
              )}
            </div>
          )}

          {(addType === 'url' || addType === 'youtube') && (
            <div className="space-y-3">
              <Input
                placeholder={addType === 'youtube' ? 'https://youtube.com/watch?v=...' : 'https://example.com/article'}
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
              />
              <div className="flex justify-end">
                <Button
                  onClick={handleAddUrl}
                  loading={isUploading}
                  disabled={!urlInput.trim()}
                >
                  {t('common:add')}
                </Button>
              </div>
            </div>
          )}

          {addType === 'text' && (
            <div className="space-y-3">
              <Input
                placeholder={t('titlePlaceholder')}
                value={textName}
                onChange={(e) => setTextName(e.target.value)}
              />
              <textarea
                placeholder={t('textPlaceholder')}
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                className="w-full h-40 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              />
              <div className="flex justify-end">
                <Button
                  onClick={handleAddText}
                  loading={isUploading}
                  disabled={!textContent.trim()}
                >
                  {t('common:add')}
                </Button>
              </div>
            </div>
          )}
        </div>
      </Modal>
    </div>
  )
}

// Check icon for checkbox
function Check({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
      <polyline points="20,6 9,17 4,12" />
    </svg>
  )
}
