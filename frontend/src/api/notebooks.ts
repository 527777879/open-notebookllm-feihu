import apiClient from './client'
import type { Notebook, ApiResponse } from '@/types'

// 取得所有筆記本
export const getNotebooks = () =>
  apiClient.get<ApiResponse<Notebook[]>>('/api/notebooks')

// 建立筆記本
export const createNotebook = (data: { name: string; description?: string }) =>
  apiClient.post<ApiResponse<Notebook>>('/api/notebooks', data)

// 取得單一筆記本
export const getNotebook = (id: string) =>
  apiClient.get<ApiResponse<Notebook>>(`/api/notebooks/${id}`)

// 更新筆記本
export const updateNotebook = (id: string, data: { name?: string; description?: string }) =>
  apiClient.put<ApiResponse<Notebook>>(`/api/notebooks/${id}`, data)

// 刪除筆記本
export const deleteNotebook = (id: string) =>
  apiClient.delete<ApiResponse<void>>(`/api/notebooks/${id}`)
