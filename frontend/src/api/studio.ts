import apiClient from './client'
import type {
  StudioOutput,
  StudioOutputType,
  ApiResponse,
  PodcastSpeaker,
  PodcastVoice,
  PodcastStyle,
  TTSResponse,
  DifficultyLevel,
  DiagramType
} from '@/types'

// ==================== 工作室輸出 ====================

// 取得工作室輸出列表
export const getStudioOutputs = (notebookId: string) =>
  apiClient.get<ApiResponse<StudioOutput[]>>(`/api/notebooks/${notebookId}/studio/outputs`)

// 生成摘要
export const generateSummary = (notebookId: string, sourceIds?: string[]) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/summary`, {
    source_ids: sourceIds,
  })

// 生成心智圖
export const generateMindmap = (notebookId: string, sourceIds?: string[]) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/mindmap`, {
    source_ids: sourceIds,
  })

// 生成學習卡（支援難度分級）
export const generateFlashcards = (
  notebookId: string,
  count?: number,
  sourceIds?: string[],
  difficulty?: DifficultyLevel
) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/flashcards`, {
    count: count || 10,
    source_ids: sourceIds,
    difficulty: difficulty || 'mixed',
  })

// 生成測驗（支援難度分級）
export const generateQuiz = (
  notebookId: string,
  count?: number,
  sourceIds?: string[],
  difficulty?: DifficultyLevel
) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/quiz`, {
    count: count || 10,
    source_ids: sourceIds,
    difficulty: difficulty || 'mixed',
  })

// 生成報告
export const generateReport = (notebookId: string, sourceIds?: string[]) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/report`, {
    source_ids: sourceIds,
  })

// 生成資料表
export const generateDatatable = (notebookId: string, sourceIds?: string[]) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/datatable`, {
    source_ids: sourceIds,
  })

// 生成簡報
export const generatePresentation = (
  notebookId: string,
  sourceIds?: string[],
  slideCount?: number,
  withImages?: boolean
) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/presentation`, {
    source_ids: sourceIds,
    slide_count: slideCount || 8,
    with_images: withImages ?? true,
  })

// 生成資訊圖表（Chart.js 數據視覺化）
export const generateInfographic = (
  notebookId: string,
  sourceIds?: string[],
  withAiImage?: boolean
) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/infographic`, {
    source_ids: sourceIds,
    with_ai_image: withAiImage ?? false,
  })

// 生成流程圖（Draw.io 格式）
export const generateFlowchart = (notebookId: string, sourceIds?: string[]) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/flowchart`, {
    source_ids: sourceIds,
  })

// 生成架構圖（Draw.io 格式）
export const generateDiagram = (
  notebookId: string,
  sourceIds?: string[],
  diagramType?: DiagramType
) =>
  apiClient.post<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/diagram`, {
    source_ids: sourceIds,
    diagram_type: diagramType || 'auto',
  })

// 取得單一輸出
export const getStudioOutput = (notebookId: string, outputId: string) =>
  apiClient.get<ApiResponse<StudioOutput>>(`/api/notebooks/${notebookId}/studio/outputs/${outputId}`)

// 刪除輸出
export const deleteStudioOutput = (notebookId: string, outputId: string) =>
  apiClient.delete<ApiResponse<void>>(`/api/notebooks/${notebookId}/studio/outputs/${outputId}`)

// ==================== Podcast 播客 ====================

export interface PodcastOptions {
  sourceIds?: string[]
  speakers?: PodcastSpeaker[]
  durationMinutes?: number
  style?: string
  withAudio?: boolean
  speakerVoices?: Record<string, string>
}

// 生成完整播客（腳本 + 可選音訊）
export const generatePodcast = (notebookId: string, options: PodcastOptions = {}) =>
  apiClient.post<ApiResponse<StudioOutput & { audio_base64?: string }>>(
    `/api/notebooks/${notebookId}/studio/podcast`,
    {
      source_ids: options.sourceIds,
      speakers: options.speakers,
      duration_minutes: options.durationMinutes || 10,
      style: options.style || 'conversational',
      with_audio: options.withAudio ?? false,
      speaker_voices: options.speakerVoices,
    }
  )

// 僅生成播客腳本
export const generatePodcastScript = (notebookId: string, options: Omit<PodcastOptions, 'withAudio' | 'speakerVoices'> = {}) =>
  apiClient.post<ApiResponse<{ script: unknown }>>(
    `/api/notebooks/${notebookId}/studio/podcast/script`,
    {
      source_ids: options.sourceIds,
      speakers: options.speakers,
      duration_minutes: options.durationMinutes || 10,
      style: options.style || 'conversational',
    }
  )

// 從腳本生成播客音訊
export const generatePodcastAudio = (
  notebookId: string,
  script: unknown,
  speakerVoices?: Record<string, string>
) =>
  apiClient.post<ApiResponse<{ audio_base64: string; format: string }>>(
    `/api/notebooks/${notebookId}/studio/podcast/audio`,
    {
      script,
      speaker_voices: speakerVoices,
    }
  )

// 取得可用的播客語音和風格
export const getPodcastVoices = (notebookId: string) =>
  apiClient.get<ApiResponse<{ voices: PodcastVoice[]; styles: PodcastStyle[] }>>(
    `/api/notebooks/${notebookId}/studio/podcast/voices`
  )

// ==================== TTS 文字轉語音 ====================

// 文字轉語音
export const textToSpeech = (notebookId: string, text: string, voice?: string, provider?: string) =>
  apiClient.post<ApiResponse<TTSResponse>>(
    `/api/notebooks/${notebookId}/studio/tts`,
    {
      text,
      voice: voice || 'alloy',
      provider: provider || 'openai',
    }
  )

// ==================== 工具函數 ====================

// 工作室輸出選項
export interface StudioOutputOptions {
  count?: number
  slideCount?: number
  withImages?: boolean
  difficulty?: DifficultyLevel
  withAiImage?: boolean
  diagramType?: DiagramType
}

// 根據類型調用對應的生成 API
export const generateStudioOutput = (
  notebookId: string,
  type: StudioOutputType,
  sourceIds?: string[],
  options?: StudioOutputOptions
) => {
  switch (type) {
    case 'summary':
      return generateSummary(notebookId, sourceIds)
    case 'mindmap':
      return generateMindmap(notebookId, sourceIds)
    case 'flowchart':
      return generateFlowchart(notebookId, sourceIds)
    case 'diagram':
      return generateDiagram(notebookId, sourceIds, options?.diagramType)
    case 'flashcards':
      return generateFlashcards(notebookId, options?.count, sourceIds, options?.difficulty)
    case 'quiz':
      return generateQuiz(notebookId, options?.count, sourceIds, options?.difficulty)
    case 'report':
      return generateReport(notebookId, sourceIds)
    case 'datatable':
      return generateDatatable(notebookId, sourceIds)
    case 'presentation':
      return generatePresentation(notebookId, sourceIds, options?.slideCount, options?.withImages)
    case 'infographic':
      return generateInfographic(notebookId, sourceIds, options?.withAiImage)
    case 'podcast':
      return generatePodcast(notebookId, { sourceIds })
    default:
      throw new Error(`未知的輸出類型: ${type}`)
  }
}

// 播放 Base64 音訊
export const playBase64Audio = (base64: string, format: string = 'mp3'): HTMLAudioElement => {
  const audio = new Audio(`data:audio/${format};base64,${base64}`)
  audio.play()
  return audio
}

// 下載 Base64 音訊
export const downloadBase64Audio = (base64: string, filename: string = 'audio.mp3') => {
  const link = document.createElement('a')
  link.href = `data:audio/mp3;base64,${base64}`
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
