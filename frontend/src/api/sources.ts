import apiClient from './client'
import type { Source, ApiResponse, SearchResponse } from '@/types'

// ==================== 來源管理 ====================

// 取得筆記本的所有來源
export const getSources = (notebookId: string) =>
  apiClient.get<ApiResponse<Source[]>>(`/api/notebooks/${notebookId}/sources`)

// 上傳文件來源（支援文件和音檔）
export interface UploadOptions {
  sttProvider?: 'openai' | 'groq' | 'local'
  language?: string
}

export const uploadSource = (notebookId: string, file: File, options?: UploadOptions) => {
  const formData = new FormData()
  formData.append('file', file)

  if (options?.sttProvider) {
    formData.append('stt_provider', options.sttProvider)
  }
  if (options?.language) {
    formData.append('language', options.language)
  }

  return apiClient.post<ApiResponse<Source>>(
    `/api/notebooks/${notebookId}/sources/upload`,
    formData
  )
}

// 新增網址來源
export const addUrlSource = (notebookId: string, url: string) =>
  apiClient.post<ApiResponse<Source>>(`/api/notebooks/${notebookId}/sources/url`, { url })

// 新增 YouTube 來源
export const addYoutubeSource = (notebookId: string, url: string) =>
  apiClient.post<ApiResponse<Source>>(`/api/notebooks/${notebookId}/sources/youtube`, { url })

// 新增純文字來源
export const addTextSource = (notebookId: string, name: string, content: string) =>
  apiClient.post<ApiResponse<Source>>(`/api/notebooks/${notebookId}/sources/text`, { name, content })

// 取得單一來源
export const getSource = (sourceId: string) =>
  apiClient.get<ApiResponse<Source>>(`/api/sources/${sourceId}`)

// 刪除來源
export const deleteSource = (sourceId: string) =>
  apiClient.delete<ApiResponse<void>>(`/api/sources/${sourceId}`)

// ==================== 搜尋功能 ====================

export type SearchType = 'hybrid' | 'fulltext' | 'vector'

export interface SearchOptions {
  query: string
  type?: SearchType
  topK?: number
  sourceIds?: string[]
}

// 搜尋筆記本內的來源
export const searchSources = (notebookId: string, options: SearchOptions) =>
  apiClient.post<ApiResponse<SearchResponse>>(`/api/notebooks/${notebookId}/search`, {
    query: options.query,
    type: options.type || 'hybrid',
    top_k: options.topK || 10,
    source_ids: options.sourceIds,
  })

// 重建全文搜尋索引
export const reindexSources = (notebookId?: string) =>
  apiClient.post<ApiResponse<{ message: string }>>(`/api/sources/reindex`, {
    notebook_id: notebookId,
  })

// ==================== 工具函數 ====================

// 檢查是否為音檔
export const isAudioFile = (filename: string): boolean => {
  const audioExtensions = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac']
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  return audioExtensions.includes(ext)
}

// 取得來源類型圖示
export const getSourceTypeIcon = (type: string): string => {
  const icons: Record<string, string> = {
    pdf: '📄',
    text: '📝',
    web: '🌐',
    youtube: '▶️',
    gdocs: '📑',
    audio: '🎵',
  }
  return icons[type] || '📁'
}

// 取得來源類型標籤
export const getSourceTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    pdf: 'PDF',
    text: '文字',
    web: '網頁',
    youtube: 'YouTube',
    gdocs: '文件',
    audio: '音檔',
  }
  return labels[type] || type
}
