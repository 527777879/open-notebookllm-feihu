import { create } from 'zustand'
import type { Source, SourceType } from '@/types'
import * as sourceApi from '@/api/sources'
import type { UploadOptions } from '@/api/sources'
import i18n from '@/i18n'

interface SourceState {
  sources: Source[]
  selectedIds: string[]
  filterType: SourceType | 'all'
  searchQuery: string
  isLoading: boolean
  isUploading: boolean
  error: string | null

  // Actions
  fetchSources: (notebookId: string) => Promise<void>
  uploadFile: (notebookId: string, file: File, options?: UploadOptions) => Promise<Source | null>
  addUrl: (notebookId: string, url: string) => Promise<Source | null>
  addYoutube: (notebookId: string, url: string) => Promise<Source | null>
  addText: (notebookId: string, name: string, content: string) => Promise<Source | null>
  deleteSource: (sourceId: string) => Promise<void>
  reembedSource: (sourceId: string) => Promise<void>
  toggleSelection: (sourceId: string) => void
  selectAll: () => void
  clearSelection: () => void
  setFilter: (type: SourceType | 'all') => void
  setSearchQuery: (query: string) => void
  clearError: () => void

  // Computed
  getFilteredSources: () => Source[]
  getSelectedSources: () => Source[]
}

export const useSourceStore = create<SourceState>((set, get) => ({
  sources: [],
  selectedIds: [],
  filterType: 'all',
  searchQuery: '',
  isLoading: false,
  isUploading: false,
  error: null,

  fetchSources: async (notebookId: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await sourceApi.getSources(notebookId)
      if (response.data.success && response.data.data) {
        set({ sources: response.data.data })
      }
    } catch (error) {
      set({ error: i18n.t('source:error.loadSources') })
    } finally {
      set({ isLoading: false })
    }
  },

  uploadFile: async (notebookId: string, file: File, options?: UploadOptions) => {
    set({ isUploading: true, error: null })
    try {
      const response = await sourceApi.uploadSource(notebookId, file, options)
      if (response.data.success && response.data.data) {
        const newSource = response.data.data
        set((state) => ({
          sources: [newSource, ...state.sources],
        }))
        return newSource
      }
      return null
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : i18n.t('source:error.uploadFile')
      set({ error: errorMessage })
      return null
    } finally {
      set({ isUploading: false })
    }
  },

  addUrl: async (notebookId: string, url: string) => {
    set({ isUploading: true, error: null })
    try {
      const response = await sourceApi.addUrlSource(notebookId, url)
      if (response.data.success && response.data.data) {
        const newSource = response.data.data
        set((state) => ({
          sources: [newSource, ...state.sources],
        }))
        return newSource
      }
      return null
    } catch (error) {
      set({ error: i18n.t('source:error.addUrl') })
      return null
    } finally {
      set({ isUploading: false })
    }
  },

  addYoutube: async (notebookId: string, url: string) => {
    set({ isUploading: true, error: null })
    try {
      const response = await sourceApi.addYoutubeSource(notebookId, url)
      if (response.data.success && response.data.data) {
        const newSource = response.data.data
        set((state) => ({
          sources: [newSource, ...state.sources],
        }))
        return newSource
      }
      return null
    } catch (error) {
      set({ error: i18n.t('source:error.addYoutube') })
      return null
    } finally {
      set({ isUploading: false })
    }
  },

  addText: async (notebookId: string, name: string, content: string) => {
    set({ isUploading: true, error: null })
    try {
      const response = await sourceApi.addTextSource(notebookId, name, content)
      if (response.data.success && response.data.data) {
        const newSource = response.data.data
        set((state) => ({
          sources: [newSource, ...state.sources],
        }))
        return newSource
      }
      return null
    } catch (error) {
      set({ error: i18n.t('source:error.addText') })
      return null
    } finally {
      set({ isUploading: false })
    }
  },

  deleteSource: async (sourceId: string) => {
    try {
      await sourceApi.deleteSource(sourceId)
      set((state) => ({
        sources: state.sources.filter((s) => s.id !== sourceId),
        selectedIds: state.selectedIds.filter((id) => id !== sourceId),
      }))
    } catch (error) {
      set({ error: i18n.t('source:error.deleteSource') })
    }
  },

  reembedSource: async (sourceId: string) => {
    try {
      await sourceApi.reembedSource(sourceId)
    } catch (error) {
      set({ error: i18n.t('source:error.reembedSource') })
    }
  },

  toggleSelection: (sourceId: string) => {
    set((state) => ({
      selectedIds: state.selectedIds.includes(sourceId)
        ? state.selectedIds.filter((id) => id !== sourceId)
        : [...state.selectedIds, sourceId],
    }))
  },

  selectAll: () => {
    const filteredSources = get().getFilteredSources()
    set({ selectedIds: filteredSources.map((s) => s.id) })
  },

  clearSelection: () => {
    set({ selectedIds: [] })
  },

  setFilter: (type) => {
    set({ filterType: type })
  },

  setSearchQuery: (query) => {
    set({ searchQuery: query })
  },

  clearError: () => {
    set({ error: null })
  },

  getFilteredSources: () => {
    const { sources, filterType, searchQuery } = get()

    return sources.filter((source) => {
      // 類型篩選
      if (filterType !== 'all' && source.type !== filterType) {
        return false
      }

      // 搜尋篩選
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        return (
          source.name.toLowerCase().includes(query) ||
          source.url?.toLowerCase().includes(query)
        )
      }

      return true
    })
  },

  getSelectedSources: () => {
    const { sources, selectedIds } = get()
    return sources.filter((s) => selectedIds.includes(s.id))
  },
}))
