import apiClient from './client'
import type { ApiResponse, Folder, Notebook } from '@/types'

/**
 * 取得所有資料夾
 */
export function getFolders(includeNotebooks = false) {
  return apiClient.get<ApiResponse<Folder[]>>('/api/folders', {
    params: { include_notebooks: includeNotebooks }
  })
}

/**
 * 建立資料夾
 */
export function createFolder(data: { name: string; emoji?: string; color?: string }) {
  return apiClient.post<ApiResponse<Folder>>('/api/folders', data)
}

/**
 * 取得單一資料夾
 */
export function getFolder(folderId: string, includeNotebooks = true) {
  return apiClient.get<ApiResponse<Folder>>(`/api/folders/${folderId}`, {
    params: { include_notebooks: includeNotebooks }
  })
}

/**
 * 更新資料夾
 */
export function updateFolder(
  folderId: string,
  data: { name?: string; emoji?: string; color?: string; is_expanded?: boolean }
) {
  return apiClient.put<ApiResponse<Folder>>(`/api/folders/${folderId}`, data)
}

/**
 * 刪除資料夾
 */
export function deleteFolder(folderId: string) {
  return apiClient.delete<ApiResponse<void>>(`/api/folders/${folderId}`)
}

/**
 * 將筆記本加入資料夾
 */
export function addNotebookToFolder(folderId: string, notebookId: string) {
  return apiClient.put<ApiResponse<Notebook>>(`/api/folders/${folderId}/notebooks/${notebookId}`)
}

/**
 * 將筆記本從資料夾移出
 */
export function removeNotebookFromFolder(folderId: string, notebookId: string) {
  return apiClient.delete<ApiResponse<Notebook>>(`/api/folders/${folderId}/notebooks/${notebookId}`)
}

/**
 * 重新排序資料夾
 */
export function reorderFolders(folderIds: string[]) {
  return apiClient.put<ApiResponse<void>>('/api/folders/reorder', { folder_ids: folderIds })
}

/**
 * 重新排序資料夾內的筆記本
 */
export function reorderNotebooksInFolder(folderId: string, notebookIds: string[]) {
  return apiClient.put<ApiResponse<void>>(`/api/folders/${folderId}/notebooks/reorder`, {
    notebook_ids: notebookIds
  })
}

/**
 * 取得所有資料夾及未分類筆記本
 */
export function getFoldersWithNotebooks() {
  return apiClient.get<ApiResponse<{ folders: Folder[]; uncategorized: Notebook[] }>>(
    '/api/folders/with-notebooks'
  )
}
