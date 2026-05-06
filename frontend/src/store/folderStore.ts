import { create } from 'zustand'
import type { Folder, Notebook } from '@/types'
import * as foldersApi from '@/api/folders'
import i18n from '@/i18n'

interface FolderState {
  folders: Folder[]
  uncategorizedNotebooks: Notebook[]
  isLoading: boolean
  error: string | null

  // Actions
  fetchFoldersWithNotebooks: () => Promise<void>
  createFolder: (name: string, emoji?: string) => Promise<Folder | null>
  updateFolder: (folderId: string, data: { name?: string; emoji?: string; is_expanded?: boolean }) => Promise<void>
  deleteFolder: (folderId: string) => Promise<void>
  toggleFolderExpand: (folderId: string) => void
  moveNotebookToFolder: (notebookId: string, folderId: string | null) => Promise<void>
  reorderFolders: (folderIds: string[]) => Promise<void>
}

export const useFolderStore = create<FolderState>((set, get) => ({
  folders: [],
  uncategorizedNotebooks: [],
  isLoading: false,
  error: null,

  fetchFoldersWithNotebooks: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await foldersApi.getFoldersWithNotebooks()
      if (response.data.success && response.data.data) {
        set({
          folders: response.data.data.folders,
          uncategorizedNotebooks: response.data.data.uncategorized,
          isLoading: false
        })
      }
    } catch (error) {
      set({ error: i18n.t('common:error.loadFolders'), isLoading: false })
      console.error(`${i18n.t('common:error.loadFolders')}:`, error)
    }
  },

  createFolder: async (name, emoji = '📁') => {
    try {
      const response = await foldersApi.createFolder({ name, emoji })
      if (response.data.success && response.data.data) {
        const newFolder = response.data.data
        set((state) => ({
          folders: [...state.folders, newFolder]
        }))
        return newFolder
      }
      return null
    } catch (error) {
      console.error(`${i18n.t('common:error.createFolder')}:`, error)
      return null
    }
  },

  updateFolder: async (folderId, data) => {
    try {
      const response = await foldersApi.updateFolder(folderId, data)
      if (response.data.success && response.data.data) {
        set((state) => ({
          folders: state.folders.map((f) =>
            f.id === folderId ? { ...f, ...response.data.data } : f
          )
        }))
      }
    } catch (error) {
      console.error(`${i18n.t('common:error.updateFolder')}:`, error)
    }
  },

  deleteFolder: async (folderId) => {
    try {
      const response = await foldersApi.deleteFolder(folderId)
      if (response.data.success) {
        // 刪除後重新載入
        get().fetchFoldersWithNotebooks()
      }
    } catch (error) {
      console.error(`${i18n.t('common:error.deleteFolder')}:`, error)
    }
  },

  toggleFolderExpand: (folderId) => {
    const folder = get().folders.find((f) => f.id === folderId)
    if (folder) {
      get().updateFolder(folderId, { is_expanded: !folder.is_expanded })
    }
  },

  moveNotebookToFolder: async (notebookId, folderId) => {
    try {
      if (folderId) {
        await foldersApi.addNotebookToFolder(folderId, notebookId)
      } else {
        // 找到筆記本當前的資料夾
        const currentFolder = get().folders.find((f) =>
          f.notebooks?.some((nb) => nb.id === notebookId)
        )
        if (currentFolder) {
          await foldersApi.removeNotebookFromFolder(currentFolder.id, notebookId)
        }
      }
      // 重新載入
      get().fetchFoldersWithNotebooks()
    } catch (error) {
      console.error(`${i18n.t('common:error.moveNotebook')}:`, error)
    }
  },

  reorderFolders: async (folderIds) => {
    try {
      await foldersApi.reorderFolders(folderIds)
      set((state) => ({
        folders: folderIds
          .map((id) => state.folders.find((f) => f.id === id))
          .filter((f): f is Folder => f !== undefined)
      }))
    } catch (error) {
      console.error(`${i18n.t('common:error.reorderFailed')}:`, error)
    }
  }
}))
