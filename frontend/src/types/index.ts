// 資料夾類型
export interface Folder {
  id: string
  name: string
  emoji: string
  color?: string
  order: number
  is_expanded: boolean
  notebook_count: number
  notebooks?: Notebook[]
  created_at: string
  updated_at: string
}

// 筆記本類型
export interface Notebook {
  id: string
  name: string
  description?: string
  folder_id?: string
  order: number
  created_at: string
  updated_at: string
  source_count: number
  note_count: number
  sources?: Source[]
}

// 來源類型 - 擴充支援音檔
export type SourceType = 'pdf' | 'text' | 'web' | 'youtube' | 'gdocs' | 'audio'

export interface Source {
  id: string
  notebook_id: string
  type: SourceType
  name: string
  url?: string
  file_path?: string
  content?: string
  content_length: number
  metadata?: Record<string, unknown>
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  created_at: string
  updated_at: string
}

// 對話訊息類型
export interface ChatMessage {
  id: string
  notebook_id: string
  role: 'user' | 'assistant'
  content: string
  source_refs?: SourceReference[]
  used_source_ids?: string[]
  created_at: string
}

export interface SourceReference {
  source_id: string
  source_name: string
  chunk_text: string
  similarity: number
}

// 筆記類型
export interface Note {
  id: string
  notebook_id: string
  title?: string
  content: string
  from_message_id?: string
  created_at: string
  updated_at: string
}

// 工作室輸出類型 - 擴充 Podcast
export type StudioOutputType =
  | 'summary'
  | 'mindmap'
  | 'flashcards'
  | 'quiz'
  | 'report'
  | 'datatable'
  | 'presentation'
  | 'infographic'
  | 'podcast'

export interface StudioOutput {
  id: string
  notebook_id: string
  type: StudioOutputType
  title?: string
  data: unknown
  source_ids?: string[]
  created_at: string
}

// 心智圖數據
export interface MindmapData {
  central: string
  branches: MindmapBranch[]
}

export interface MindmapBranch {
  name: string
  children: MindmapBranch[]
}

// 學習卡數據
export interface FlashcardsData {
  cards: Flashcard[]
}

export interface Flashcard {
  front: string
  back: string
}

// 測驗數據
export interface QuizData {
  questions: QuizQuestion[]
}

export interface QuizQuestion {
  type: 'multiple_choice' | 'true_false'
  question: string
  options?: string[]
  correct: string | boolean
  explanation: string
}

// Podcast 數據
export interface PodcastData {
  title: string
  description?: string
  script?: PodcastScript
  has_audio?: boolean
  audio_base64?: string
}

export interface PodcastScript {
  title: string
  description?: string
  segments: PodcastSegment[]
}

export interface PodcastSegment {
  speaker: string
  text: string
  emotion?: string
}

export interface PodcastSpeaker {
  name: string
  role: string
  personality?: string
}

export interface PodcastVoice {
  id: string
  name: string
  gender: string
  description: string
}

export interface PodcastStyle {
  id: string
  name: string
  description: string
}

// 搜尋相關
export interface SearchResult {
  source_id: string
  source_name: string
  source_type?: string
  snippet: string
  score: number
  search_type: 'fulltext' | 'vector' | 'hybrid'
  fulltext_score?: number
  vector_score?: number
  hybrid_score?: number
}

export interface SearchResponse {
  query: string
  type: 'fulltext' | 'vector' | 'hybrid'
  results: SearchResult[]
}

// API 回應類型
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// AI 提供商類型
export type AIProvider = 'gemini' | 'openai' | 'anthropic' | 'ollama' | 'groq' | 'deepseek'

export interface AIProviderInfo {
  id: AIProvider
  name: string
  available: boolean
  supports_embedding: boolean
  supports_image: boolean
  models: string[]
}

// 設定類型 - 擴充多提供商
export interface Settings {
  ai_provider: AIProvider
  gemini_model: string
  openai_model: string
  has_gemini_key: boolean
  has_openai_key: boolean
  has_anthropic_key: boolean
  has_groq_key: boolean
  has_deepseek_key: boolean
  provider_ready: boolean
  current_provider?: AIProvider
  current_config?: {
    provider: AIProvider
    is_ready: boolean
    has_embedding: boolean
    has_image: boolean
  }
}

export interface ProvidersResponse {
  current_provider: AIProvider
  providers: AIProviderInfo[]
}

// TTS 相關
export interface TTSRequest {
  text: string
  voice?: string
  provider?: string
}

export interface TTSResponse {
  audio_base64: string
  format: string
}
