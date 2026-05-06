import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, Globe, CheckSquare, Square, BookmarkPlus, ArrowLeft } from 'lucide-react'
import Button from '@/components/common/Button'
import { useSourceStore } from '@/store'
import * as sourceApi from '@/api/sources'
import type { WebSearchResult } from '@/types'

interface WebSearchPanelProps {
  notebookId: string
  onBack: () => void
}

export default function WebSearchPanel({ notebookId, onBack }: WebSearchPanelProps) {
  const { t } = useTranslation('source')
  const { fetchSources } = useSourceStore()

  const [query, setQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<WebSearchResult[]>([])
  const [answer, setAnswer] = useState<string | null>(null)
  const [selectedUrls, setSelectedUrls] = useState<Set<string>>(new Set())
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saveResult, setSaveResult] = useState<{ saved: number; failed: number } | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    setIsSearching(true)
    setError(null)
    setSearchResults([])
    setAnswer(null)
    setSelectedUrls(new Set())
    setSaveResult(null)

    try {
      const response = await sourceApi.webSearch(query)
      if (response.data.success && response.data.data) {
        setSearchResults(response.data.data.results || [])
        setAnswer(response.data.data.answer || null)
      } else {
        setError(response.data.error || t('webSearch.error'))
      }
    } catch {
      setError(t('webSearch.error'))
    } finally {
      setIsSearching(false)
    }
  }

  const toggleResult = (url: string) => {
    setSelectedUrls(prev => {
      const next = new Set(prev)
      if (next.has(url)) next.delete(url)
      else next.add(url)
      return next
    })
  }

  const selectAllResults = () => {
    if (selectedUrls.size === searchResults.length) {
      setSelectedUrls(new Set())
    } else {
      setSelectedUrls(new Set(searchResults.map(r => r.url)))
    }
  }

  const handleSaveSelected = async () => {
    if (selectedUrls.size === 0) return
    setIsSaving(true)
    setSaveResult(null)

    const selected = searchResults
      .filter(r => selectedUrls.has(r.url))
      .map(r => ({ title: r.title, url: r.url, content: r.content, raw_content: r.raw_content }))

    try {
      const response = await sourceApi.saveWebSearchResults(notebookId, selected)
      if (response.data.success && response.data.data) {
        const { saved_count, failed_count } = response.data.data
        setSaveResult({ saved: saved_count, failed: failed_count })
        setSelectedUrls(new Set())
        fetchSources(notebookId)
      } else {
        setError(t('webSearch.saveError'))
      }
    } catch {
      setError(t('webSearch.saveError'))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header with back button */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-3">
          <button onClick={onBack} className="p-1 hover:bg-gray-100 rounded">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <h2 className="font-semibold text-gray-900">{t('webSearch.title')}</h2>
        </div>

        {/* Search input */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder={t('webSearch.placeholder')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <Button onClick={handleSearch} loading={isSearching} disabled={!query.trim()}>
            {t('webSearch.search')}
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mt-3 p-3 bg-red-50 text-red-700 text-sm rounded-lg">
          {error}
        </div>
      )}

      {/* Save Result */}
      {saveResult && (
        <div className="mx-4 mt-3 p-3 bg-green-50 text-green-700 text-sm rounded-lg">
          {t('webSearch.saveSuccess', { saved: saveResult.saved })}
          {saveResult.failed > 0 && ` · ${t('webSearch.saveFailed', { failed: saveResult.failed })}`}
        </div>
      )}

      {/* AI Answer */}
      {answer && (
        <div className="mx-4 mt-3 p-3 bg-blue-50 text-blue-800 text-sm rounded-lg">
          <p className="font-medium mb-1">{t('webSearch.aiAnswer')}</p>
          <p>{answer}</p>
        </div>
      )}

      {/* Results */}
      {searchResults.length > 0 && (
        <>
          {/* Select all + Save */}
          <div className="px-4 py-2 border-b border-gray-200 flex items-center justify-between">
            <button
              onClick={selectAllResults}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
            >
              {selectedUrls.size === searchResults.length ? (
                <CheckSquare className="w-4 h-4 text-primary-600" />
              ) : (
                <Square className="w-4 h-4" />
              )}
              {t('webSearch.selectAll')} ({searchResults.length})
            </button>
            <Button
              size="sm"
              onClick={handleSaveSelected}
              loading={isSaving}
              disabled={selectedUrls.size === 0}
            >
              <BookmarkPlus className="w-4 h-4 mr-1" />
              {t('webSearch.saveSelected')} {selectedUrls.size > 0 && `(${selectedUrls.size})`}
            </Button>
          </div>

          {/* Result list */}
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {searchResults.map((result, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  selectedUrls.has(result.url)
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => toggleResult(result.url)}
              >
                <div className="flex items-start gap-2">
                  <div className={`w-4 h-4 mt-0.5 rounded border flex items-center justify-center flex-shrink-0 ${
                    selectedUrls.has(result.url) ? 'bg-primary-600 border-primary-600' : 'border-gray-300'
                  }`}>
                    {selectedUrls.has(result.url) && (
                      <svg className="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <polyline points="20,6 9,17 4,12" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <Globe className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                      <h3 className="text-sm font-medium text-gray-900 truncate">{result.title}</h3>
                    </div>
                    <p className="text-xs text-primary-600 truncate mt-0.5">{result.url}</p>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{result.content}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Empty state */}
      {!isSearching && searchResults.length === 0 && !error && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center py-8 text-gray-500 text-sm">
            <Search className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p>{t('webSearch.emptyHint')}</p>
          </div>
        </div>
      )}
    </div>
  )
}
