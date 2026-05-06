import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, Check, AlertCircle, RefreshCw } from 'lucide-react'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import {
  getSettings,
  getProviders,
  updateSettings,
  testApi,
  getProviderModels,
  PROVIDER_INFO
} from '@/api/settings'
import type { Settings, AIProvider, AIProviderInfo } from '@/types'

export default function SettingsPage() {
  const { t } = useTranslation('settings')
  const navigate = useNavigate()
  const [settings, setSettings] = useState<Settings | null>(null)
  const [providers, setProviders] = useState<AIProviderInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [availableModels, setAvailableModels] = useState<string[]>([])

  const [formData, setFormData] = useState({
    provider: 'gemini' as AIProvider,
    apiKey: '',
    model: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    // 當提供商改變時，載入可用模型
    loadModels(formData.provider)
  }, [formData.provider])

  const fetchData = async () => {
    try {
      const [settingsRes, providersRes] = await Promise.all([
        getSettings(),
        getProviders()
      ])

      if (settingsRes.data.success && settingsRes.data.data) {
        setSettings(settingsRes.data.data)
        setFormData({
          provider: settingsRes.data.data.current_provider || 'gemini',
          apiKey: '',
          model: '',
        })
      }

      if (providersRes.data.success && providersRes.data.data) {
        setProviders(providersRes.data.data.providers)
      }
    } catch (error) {
      console.error(t('loadSettingsFailed'), error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadModels = async (provider: AIProvider) => {
    try {
      const response = await getProviderModels(provider)
      if (response.data.success && response.data.data) {
        setAvailableModels(response.data.data.models)
      }
    } catch (error) {
      console.error(t('loadModelsFailed'), error)
      setAvailableModels([])
    }
  }

  const handleTestApi = async () => {
    // Ollama 不需要 API Key
    if (formData.provider !== 'ollama' && !formData.apiKey) {
      setTestResult({ success: false, message: t('enterApiKey') })
      return
    }

    setIsTesting(true)
    setTestResult(null)

    try {
      const response = await testApi(formData.provider, formData.apiKey || undefined)

      if (response.data.success) {
        setTestResult({ success: true, message: response.data.data?.message || t('apiConnected') })
      } else {
        setTestResult({ success: false, message: response.data.error || t('connectionFailed') })
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : t('connectionTestFailed')
      setTestResult({ success: false, message: errorMessage })
    } finally {
      setIsTesting(false)
    }
  }

  const handleSave = async () => {
    // Ollama 不需要 API Key
    if (formData.provider !== 'ollama' && !formData.apiKey) {
      setTestResult({ success: false, message: t('enterApiKey') })
      return
    }

    setIsSaving(true)

    try {
      const response = await updateSettings({
        provider: formData.provider,
        apiKey: formData.apiKey || undefined,
        model: formData.model || undefined,
      })

      if (response.data.success) {
        setTestResult({ success: true, message: t('settingsSaved') })
        await fetchData()
      } else {
        setTestResult({ success: false, message: response.data.error || t('saveFailed') })
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : t('saveSettingsFailed')
      setTestResult({ success: false, message: errorMessage })
    } finally {
      setIsSaving(false)
    }
  }

  const getApiKeyUrl = (provider: AIProvider) => {
    const urls: Record<AIProvider, string> = {
      gemini: 'https://aistudio.google.com/app/apikey',
      openai: 'https://platform.openai.com/api-keys',
      anthropic: 'https://console.anthropic.com/settings/keys',
      ollama: 'https://ollama.ai/download',
      groq: 'https://console.groq.com/keys',
      deepseek: 'https://platform.deepseek.com/api_keys',
    }
    return urls[provider]
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-primary">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface-primary">
      <header className="h-14 border-b border-gray-200 bg-white px-4 flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <h1 className="font-semibold text-lg">{t('title')}</h1>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8">
        {/* 當前狀態 */}
        <div className="card p-4 mb-6">
          {settings?.provider_ready ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <Check className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="font-medium text-green-700">{t('serviceReady')}</p>
                <p className="text-sm text-gray-500">
                  {t('currentProvider')} {PROVIDER_INFO[settings.current_provider || 'gemini']?.name}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="font-medium text-amber-700">{t('notConfigured')}</p>
                <p className="text-sm text-gray-500">{t('notConfiguredDesc')}</p>
              </div>
            </div>
          )}
        </div>

        {/* 提供商選擇 */}
        <div className="card p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{t('selectProvider')}</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {providers.map((provider) => {
              const info = PROVIDER_INFO[provider.id]
              return (
                <button
                  key={provider.id}
                  onClick={() => setFormData({ ...formData, provider: provider.id, model: '' })}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    formData.provider === provider.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">{info?.icon}</span>
                    <span className="font-medium">{info?.name}</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-2">{info?.description ? t(info.description) : ''}</p>
                  <div className="flex flex-wrap gap-1">
                    {provider.available ? (
                      <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">
                        {t('available')}
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded">
                        {t('notConfiguredLabel')}
                      </span>
                    )}
                    {provider.supports_embedding && (
                      <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                        {t('embedding')}
                      </span>
                    )}
                    {provider.supports_image && (
                      <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded">
                        {t('image')}
                      </span>
                    )}
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* API Key 設定 */}
        <div className="card p-6 space-y-4">
          <h2 className="text-lg font-semibold">
            {t('providerSettings', { name: PROVIDER_INFO[formData.provider]?.name })}
          </h2>

          {formData.provider !== 'ollama' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('apiKey')}
              </label>
              <Input
                type="password"
                placeholder={t('apiKeyPlaceholder', { name: PROVIDER_INFO[formData.provider]?.name })}
                value={formData.apiKey}
                onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
              />
              <p className="mt-1 text-sm text-gray-500">
                <a
                  href={getApiKeyUrl(formData.provider)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  {t('getApiKey')}
                </a>
              </p>
            </div>
          ) : (
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">
                {t('ollamaNoKey')}
              </p>
              <a
                href="https://ollama.ai/download"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary-600 hover:underline"
              >
                {t('downloadOllama')}
              </a>
            </div>
          )}

          <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('model')}
              </label>
            <select
              value={formData.model}
              onChange={(e) => setFormData({ ...formData, model: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">{t('useDefaultModel')}</option>
              {availableModels.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>

          {testResult && (
            <div
              className={`flex items-center gap-2 p-3 rounded-lg ${
                testResult.success
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              {testResult.success ? (
                <Check className="w-5 h-5" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              <span>{testResult.message}</span>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="secondary"
              onClick={handleTestApi}
              loading={isTesting}
            >
              {t('testConnection')}
            </Button>
            <Button
              onClick={handleSave}
              loading={isSaving}
            >
              {t('saveSettings')}
            </Button>
          </div>
        </div>

        {/* 功能說明 */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium mb-2">{t('providerFeatures')}</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>{t('providerDescriptions.gemini')}</li>
            <li>{t('providerDescriptions.openai')}</li>
            <li>{t('providerDescriptions.anthropic')}</li>
            <li>{t('providerDescriptions.ollama')}</li>
            <li>{t('providerDescriptions.groq')}</li>
            <li>{t('providerDescriptions.deepseek')}</li>
          </ul>
        </div>
      </main>
    </div>
  )
}
