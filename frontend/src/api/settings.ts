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
    description: 'settings:providers.gemini.description',
    icon: '🔷',
    color: '#4285F4',
    features: ['settings:providers.gemini.features.textGeneration', 'settings:providers.gemini.features.embedding', 'settings:providers.gemini.features.imageGeneration'],
  },
  openai: {
    id: 'openai',
    name: 'OpenAI',
    description: 'settings:providers.openai.description',
    icon: '🟢',
    color: '#10A37F',
    features: ['settings:providers.openai.features.textGeneration', 'settings:providers.openai.features.embedding', 'settings:providers.openai.features.imageGeneration', 'settings:providers.openai.features.ttsStt'],
  },
  anthropic: {
    id: 'anthropic',
    name: 'Anthropic Claude',
    description: 'settings:providers.anthropic.description',
    icon: '🟠',
    color: '#D97706',
    features: ['settings:providers.anthropic.features.textGeneration', 'settings:providers.anthropic.features.longContext'],
  },
  ollama: {
    id: 'ollama',
    name: 'Ollama (本地)',
    description: 'settings:providers.ollama.description',
    icon: '🦙',
    color: '#6B7280',
    features: ['settings:providers.ollama.features.textGeneration', 'settings:providers.ollama.features.embedding', 'settings:providers.ollama.features.offline'],
  },
  groq: {
    id: 'groq',
    name: 'Groq (高速)',
    description: 'settings:providers.groq.description',
    icon: '⚡',
    color: '#F59E0B',
    features: ['settings:providers.groq.features.textGeneration', 'settings:providers.groq.features.fastInference', 'settings:providers.groq.features.stt'],
  },
  deepseek: {
    id: 'deepseek',
    name: 'DeepSeek (推理)',
    description: 'settings:providers.deepseek.description',
    icon: '🧠',
    color: '#8B5CF6',
    features: ['settings:providers.deepseek.features.textGeneration', 'settings:providers.deepseek.features.reasoning', 'settings:providers.deepseek.features.chainOfThought'],
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
