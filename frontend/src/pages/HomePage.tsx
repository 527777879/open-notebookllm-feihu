import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Plus,
  BookOpen,
  Clock,
  Trash2,
  FolderPlus,
  ChevronRight,
  ChevronDown,
  Edit2,
  FolderOpen,
} from 'lucide-react'
import Header from '@/components/layout/Header'
import Modal from '@/components/common/Modal'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import Loading from '@/components/common/Loading'
import { useNotebookStore, useFolderStore } from '@/store'
import type { Notebook, Folder } from '@/types'

// 常用表情符號
const FOLDER_EMOJIS = ['📁', '📂', '📚', '💼', '🎯', '🚀', '💡', '🔬', '📊', '🎨', '🏠', '⭐']

export default function HomePage() {
  const navigate = useNavigate()
  const { t } = useTranslation(['home', 'common'])
  const [isCreateNotebookModalOpen, setIsCreateNotebookModalOpen] = useState(false)
  const [isCreateFolderModalOpen, setIsCreateFolderModalOpen] = useState(false)
  const [isEditFolderModalOpen, setIsEditFolderModalOpen] = useState(false)
  const [editingFolder, setEditingFolder] = useState<Folder | null>(null)
  const [newNotebookName, setNewNotebookName] = useState('')
  const [newFolderName, setNewFolderName] = useState('')
  const [newFolderEmoji, setNewFolderEmoji] = useState('📁')
  const [isCreating, setIsCreating] = useState(false)
  const [draggedNotebook, setDraggedNotebook] = useState<string | null>(null)

  const { createNotebook, deleteNotebook } = useNotebookStore()
  const {
    folders,
    uncategorizedNotebooks,
    isLoading,
    fetchFoldersWithNotebooks,
    createFolder,
    updateFolder,
    deleteFolder,
    toggleFolderExpand,
    moveNotebookToFolder,
  } = useFolderStore()

  useEffect(() => {
    fetchFoldersWithNotebooks()
  }, [fetchFoldersWithNotebooks])

  const handleCreateNotebook = async () => {
    if (!newNotebookName.trim()) return

    setIsCreating(true)
    const notebook = await createNotebook(newNotebookName.trim())
    setIsCreating(false)

    if (notebook) {
      setIsCreateNotebookModalOpen(false)
      setNewNotebookName('')
      fetchFoldersWithNotebooks()
      navigate(`/notebook/${notebook.id}`)
    }
  }

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return

    setIsCreating(true)
    await createFolder(newFolderName.trim(), newFolderEmoji)
    setIsCreating(false)
    setIsCreateFolderModalOpen(false)
    setNewFolderName('')
    setNewFolderEmoji('📁')
  }

  const handleUpdateFolder = async () => {
    if (!editingFolder || !newFolderName.trim()) return

    await updateFolder(editingFolder.id, {
      name: newFolderName.trim(),
      emoji: newFolderEmoji,
    })
    setIsEditFolderModalOpen(false)
    setEditingFolder(null)
    setNewFolderName('')
    setNewFolderEmoji('📁')
  }

  const handleDeleteNotebook = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (window.confirm(t('deleteNotebookConfirm'))) {
      await deleteNotebook(id)
      fetchFoldersWithNotebooks()
    }
  }

  const handleDeleteFolder = async (e: React.MouseEvent, folder: Folder) => {
    e.stopPropagation()
    if (window.confirm(t('deleteFolderConfirm', { name: folder.name }))) {
      await deleteFolder(folder.id)
    }
  }

  const handleEditFolder = (e: React.MouseEvent, folder: Folder) => {
    e.stopPropagation()
    setEditingFolder(folder)
    setNewFolderName(folder.name)
    setNewFolderEmoji(folder.emoji)
    setIsEditFolderModalOpen(true)
  }

  // 拖放處理
  const handleDragStart = (notebookId: string) => {
    setDraggedNotebook(notebookId)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDropOnFolder = async (e: React.DragEvent, folderId: string) => {
    e.preventDefault()
    if (draggedNotebook) {
      await moveNotebookToFolder(draggedNotebook, folderId)
      setDraggedNotebook(null)
    }
  }

  const handleDropOnUncategorized = async (e: React.DragEvent) => {
    e.preventDefault()
    if (draggedNotebook) {
      await moveNotebookToFolder(draggedNotebook, null)
      setDraggedNotebook(null)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString(t('common:dateLocale'), {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  if (isLoading && folders.length === 0 && uncategorizedNotebooks.length === 0) {
    return (
      <div className="min-h-screen bg-surface-primary">
        <Header onCreateNotebook={() => setIsCreateNotebookModalOpen(true)} />
        <Loading fullscreen message={t('common:loading')} />
      </div>
    )
  }

  const totalNotebooks = folders.reduce((sum, f) => sum + (f.notebooks?.length || 0), 0) + uncategorizedNotebooks.length

  return (
    <div className="min-h-screen bg-surface-primary">
      <Header onCreateNotebook={() => setIsCreateNotebookModalOpen(true)} />

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t('title')}</h1>
            <p className="text-gray-600 mt-1">
              {t('folderCount', { count: folders.length, total: totalNotebooks })}
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setIsCreateFolderModalOpen(true)}>
              <FolderPlus className="w-4 h-4 mr-2" />
              {t('addFolder')}
            </Button>
            <Button onClick={() => setIsCreateNotebookModalOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              {t('addNotebook')}
            </Button>
          </div>
        </div>

        {totalNotebooks === 0 && folders.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">{t('noNotebooks')}</h3>
            <p className="text-gray-600 mb-6">{t('noNotebooksDesc')}</p>
            <Button onClick={() => setIsCreateNotebookModalOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              {t('createNotebook')}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* 資料夾列表 */}
            {folders.map((folder) => (
              <FolderSection
                key={folder.id}
                folder={folder}
                onToggle={() => toggleFolderExpand(folder.id)}
                onEdit={(e) => handleEditFolder(e, folder)}
                onDelete={(e) => handleDeleteFolder(e, folder)}
                onNotebookClick={(id) => navigate(`/notebook/${id}`)}
                onNotebookDelete={handleDeleteNotebook}
                onDragStart={handleDragStart}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDropOnFolder(e, folder.id)}
                formatDate={formatDate}
              />
            ))}

            {/* 未分類筆記本 */}
            {uncategorizedNotebooks.length > 0 && (
              <div
                className="bg-white rounded-xl border border-gray-200 overflow-hidden"
                onDragOver={handleDragOver}
                onDrop={handleDropOnUncategorized}
              >
                <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                  <div className="flex items-center gap-2">
                    <FolderOpen className="w-5 h-5 text-gray-400" />
                    <span className="font-medium text-gray-700">{t('uncategorized')}</span>
                    <span className="text-sm text-gray-500">({uncategorizedNotebooks.length})</span>
                  </div>
                </div>
                <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {uncategorizedNotebooks.map((notebook) => (
                    <NotebookCard
                      key={notebook.id}
                      notebook={notebook}
                      onClick={() => navigate(`/notebook/${notebook.id}`)}
                      onDelete={handleDeleteNotebook}
                      onDragStart={() => handleDragStart(notebook.id)}
                      formatDate={formatDate}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* 建立筆記本 Modal */}
      <Modal
        isOpen={isCreateNotebookModalOpen}
        onClose={() => setIsCreateNotebookModalOpen(false)}
        title={t('createNotebookModal')}
      >
        <div className="space-y-4">
          <Input
            placeholder={t('notebookNamePlaceholder')}
            value={newNotebookName}
            onChange={(e) => setNewNotebookName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleCreateNotebook()
            }}
            autoFocus
          />
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setIsCreateNotebookModalOpen(false)}>
              {t('common:cancel')}
            </Button>
            <Button onClick={handleCreateNotebook} loading={isCreating} disabled={!newNotebookName.trim()}>
              {t('common:create')}
            </Button>
          </div>
        </div>
      </Modal>

      {/* 建立/編輯資料夾 Modal */}
      <Modal
        isOpen={isCreateFolderModalOpen || isEditFolderModalOpen}
        onClose={() => {
          setIsCreateFolderModalOpen(false)
          setIsEditFolderModalOpen(false)
          setEditingFolder(null)
          setNewFolderName('')
          setNewFolderEmoji('📁')
        }}
        title={editingFolder ? t('editFolderModal') : t('createFolderModal')}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('chooseIcon')}</label>
            <div className="flex flex-wrap gap-2">
              {FOLDER_EMOJIS.map((emoji) => (
                <button
                  key={emoji}
                  onClick={() => setNewFolderEmoji(emoji)}
                  className={`w-10 h-10 text-xl rounded-lg border-2 transition-all ${
                    newFolderEmoji === emoji
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>
          <Input
            placeholder={t('folderNamePlaceholder')}
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                editingFolder ? handleUpdateFolder() : handleCreateFolder()
              }
            }}
            autoFocus
          />
          <div className="flex justify-end gap-3">
            <Button
              variant="secondary"
              onClick={() => {
                setIsCreateFolderModalOpen(false)
                setIsEditFolderModalOpen(false)
                setEditingFolder(null)
              }}
            >
              {t('common:cancel')}
            </Button>
            <Button
              onClick={editingFolder ? handleUpdateFolder : handleCreateFolder}
              loading={isCreating}
              disabled={!newFolderName.trim()}
            >
              {editingFolder ? t('common:save') : t('common:create')}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

// 資料夾區塊組件
function FolderSection({
  folder,
  onToggle,
  onEdit,
  onDelete,
  onNotebookClick,
  onNotebookDelete,
  onDragStart,
  onDragOver,
  onDrop,
  formatDate,
}: {
  folder: Folder
  onToggle: () => void
  onEdit: (e: React.MouseEvent) => void
  onDelete: (e: React.MouseEvent) => void
  onNotebookClick: (id: string) => void
  onNotebookDelete: (e: React.MouseEvent, id: string) => void
  onDragStart: (id: string) => void
  onDragOver: (e: React.DragEvent) => void
  onDrop: (e: React.DragEvent) => void
  formatDate: (date: string) => string
}) {
  const { t } = useTranslation(['home', 'common'])
  return (
    <div
      className="bg-white rounded-xl border border-gray-200 overflow-hidden"
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      {/* 資料夾標題 */}
      <div
        className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center gap-2">
          {folder.is_expanded ? (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-400" />
          )}
          <span className="text-xl">{folder.emoji}</span>
          <span className="font-medium text-gray-700">{folder.name}</span>
          <span className="text-sm text-gray-500">({folder.notebooks?.length || 0})</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onEdit}
            className="p-1.5 rounded-lg hover:bg-gray-200 transition-colors"
            title={t('common:edit')}
          >
            <Edit2 className="w-4 h-4 text-gray-500" />
          </button>
          <button
            onClick={onDelete}
            className="p-1.5 rounded-lg hover:bg-red-50 transition-colors"
            title={t('common:delete')}
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      </div>

      {/* 資料夾內容 */}
      {folder.is_expanded && (
        <div className="p-4">
          {folder.notebooks && folder.notebooks.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {folder.notebooks.map((notebook) => (
                <NotebookCard
                  key={notebook.id}
                  notebook={notebook}
                  onClick={() => onNotebookClick(notebook.id)}
                  onDelete={onNotebookDelete}
                  onDragStart={() => onDragStart(notebook.id)}
                  formatDate={formatDate}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>{t('dragNotebookHere')}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// 筆記本卡片組件
function NotebookCard({
  notebook,
  onClick,
  onDelete,
  onDragStart,
  formatDate,
}: {
  notebook: Notebook
  onClick: () => void
  onDelete: (e: React.MouseEvent, id: string) => void
  onDragStart: () => void
  formatDate: (date: string) => string
}) {
  const { t } = useTranslation('home')
  return (
    <div
      onClick={onClick}
      draggable
      onDragStart={onDragStart}
      className="card p-4 cursor-pointer group hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-primary-600" />
        </div>
        <button
          onClick={(e) => onDelete(e, notebook.id)}
          className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-50 transition-all"
        >
          <Trash2 className="w-4 h-4 text-red-500" />
        </button>
      </div>

      <h3 className="font-semibold text-gray-900 mb-1 truncate">{notebook.name}</h3>

      <div className="flex items-center gap-4 text-sm text-gray-500">
        <span>{t('sourceCount', { count: notebook.source_count })}</span>
        <span className="flex items-center gap-1">
          <Clock className="w-3.5 h-3.5" />
          {formatDate(notebook.updated_at)}
        </span>
      </div>
    </div>
  )
}
