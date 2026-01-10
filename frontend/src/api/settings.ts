import apiClient from './client'
import type { Settings, ProvidersResponse, AIProvider, ApiResponse } from '@/types'

// 取得設定
export const getSettings = () =>
  apiClient.get<ApiResponse<Settings>>('/api/settings')

// 取得可用的 AI 提供商列表
export const getProviders = () =>
  apiClient.get<ApiResponse<ProvidersResponse>>('/api/settings/providers')

// 更新設定（切換 Provider）
export interface UpdateSettingsParams {
  provider: AIProvider
  apiKey?: string
  model?: string
}

export const updateSettings = (params: UpdateSettingsParams) =>
  apiClient.put<ApiResponse<{
    provider: AIProvider
    provider_ready: boolean
    config: {
      provider: AIProvider
      is_ready: boolean
      has_embedding: boolean
      has_image: boolean
    }
  }>>('/api/settings', {
    provider: params.provider,
    api_key: params.apiKey,
    model: params.model,
  })

// 測試 API 連線
export const testApi = (provider: AIProvider, apiKey?: string) =>
  apiClient.post<ApiResponse<{
    message: string
    response: string
  }>>('/api/settings/test-api', {
    provider,
    api_key: apiKey,
  })

// 重置 AI 服務
export const resetService = () =>
  apiClient.post<ApiResponse<{
    provider_ready: boolean
    current_provider: AIProvider
    config: {
      provider: AIProvider
      is_ready: boolean
      has_embedding: boolean
      has_image: boolean
    }
  }>>('/api/settings/reset')

// 取得指定提供商的可用模型列表
export const getProviderModels = (provider: AIProvider) =>
  apiClient.get<ApiResponse<{
    provider: AIProvider
    models: string[]
  }>>(`/api/settings/models/${provider}`)

// ==================== 提供商資訊 ====================

export interface ProviderDisplayInfo {
  id: AIProvider
  name: string
  description: string
  icon: string
  color: string
  features: string[]
}

// 提供商顯示資訊
export const PROVIDER_INFO: Record<AIProvider, ProviderDisplayInfo> = {
  gemini: {
    id: 'gemini',
    name: 'Google Gemini',
    description: '支援多模態、嵌入、圖片生成',
    icon: '🔷',
    color: '#4285F4',
    features: ['文字生成', '向量嵌入', '圖片生成'],
  },
  openai: {
    id: 'openai',
    name: 'OpenAI',
    description: 'GPT-4.1/5.1 + DALL-E 3',
    icon: '🟢',
    color: '#10A37F',
    features: ['文字生成', '向量嵌入', '圖片生成', 'TTS/STT'],
  },
  anthropic: {
    id: 'anthropic',
    name: 'Anthropic Claude',
    description: 'Claude Opus/Sonnet 系列',
    icon: '🟠',
    color: '#D97706',
    features: ['文字生成', '長上下文'],
  },
  ollama: {
    id: 'ollama',
    name: 'Ollama (本地)',
    description: '本地模型，免費無限使用',
    icon: '🦙',
    color: '#6B7280',
    features: ['文字生成', '向量嵌入', '離線使用'],
  },
  groq: {
    id: 'groq',
    name: 'Groq (高速)',
    description: '超高速推理，Llama 3.3 70B',
    icon: '⚡',
    color: '#F59E0B',
    features: ['文字生成', '高速推理', 'STT'],
  },
  deepseek: {
    id: 'deepseek',
    name: 'DeepSeek (推理)',
    description: '支援 DeepSeek-R1 推理模型',
    icon: '🧠',
    color: '#8B5CF6',
    features: ['文字生成', '推理模型', 'Chain-of-Thought'],
  },
}

// 取得提供商顯示資訊
export const getProviderInfo = (provider: AIProvider): ProviderDisplayInfo => {
  return PROVIDER_INFO[provider] || {
    id: provider,
    name: provider,
    description: '',
    icon: '❓',
    color: '#6B7280',
    features: [],
  }
}
