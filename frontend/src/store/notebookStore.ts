import { create } from 'zustand'
import type { Notebook } from '@/types'
import * as notebookApi from '@/api/notebooks'
import i18n from '@/i18n'

interface NotebookState {
  notebooks: Notebook[]
  currentNotebook: Notebook | null
  isLoading: boolean
  error: string | null

  // Actions
  fetchNotebooks: () => Promise<void>
  createNotebook: (name: string, description?: string) => Promise<Notebook | null>
  fetchNotebook: (id: string) => Promise<void>
  updateNotebook: (id: string, data: { name?: string; description?: string }) => Promise<void>
  deleteNotebook: (id: string) => Promise<void>
  setCurrentNotebook: (notebook: Notebook | null) => void
  clearError: () => void
}

export const useNotebookStore = create<NotebookState>((set, _get) => ({
  notebooks: [],
  currentNotebook: null,
  isLoading: false,
  error: null,

  fetchNotebooks: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await notebookApi.getNotebooks()
      if (response.data.success && response.data.data) {
        set({ notebooks: response.data.data })
      }
    } catch (error) {
      set({ error: i18n.t('common:error.loadNotebooks') })
    } finally {
      set({ isLoading: false })
    }
  },

  createNotebook: async (name: string, description?: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await notebookApi.createNotebook({ name, description })
      if (response.data.success && response.data.data) {
        const newNotebook = response.data.data
        set((state) => ({
          notebooks: [newNotebook, ...state.notebooks],
        }))
        return newNotebook
      }
      return null
    } catch (error) {
      set({ error: i18n.t('common:error.createNotebook') })
      return null
    } finally {
      set({ isLoading: false })
    }
  },

  fetchNotebook: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await notebookApi.getNotebook(id)
      if (response.data.success && response.data.data) {
        set({ currentNotebook: response.data.data })
      }
    } catch (error) {
      set({ error: i18n.t('common:error.loadNotebook'), currentNotebook: null })
    } finally {
      set({ isLoading: false })
    }
  },

  updateNotebook: async (id: string, data: { name?: string; description?: string }) => {
    try {
      const response = await notebookApi.updateNotebook(id, data)
      if (response.data.success && response.data.data) {
        const updatedNotebook = response.data.data
        set((state) => ({
          notebooks: state.notebooks.map((nb) =>
            nb.id === id ? updatedNotebook : nb
          ),
          currentNotebook:
            state.currentNotebook?.id === id ? updatedNotebook : state.currentNotebook,
        }))
      }
    } catch (error) {
      set({ error: i18n.t('common:error.updateNotebook') })
    }
  },

  deleteNotebook: async (id: string) => {
    try {
      await notebookApi.deleteNotebook(id)
      set((state) => ({
        notebooks: state.notebooks.filter((nb) => nb.id !== id),
        currentNotebook: state.currentNotebook?.id === id ? null : state.currentNotebook,
      }))
    } catch (error) {
      set({ error: i18n.t('common:error.deleteNotebook') })
    }
  },

  setCurrentNotebook: (notebook) => {
    set({ currentNotebook: notebook })
  },

  clearError: () => {
    set({ error: null })
  },
}))
