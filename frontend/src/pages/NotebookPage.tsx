import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Header from '@/components/layout/Header'
import ThreeColumnLayout from '@/components/layout/ThreeColumnLayout'
import SourcePanel from '@/components/source/SourcePanel'
import ChatPanel from '@/components/chat/ChatPanel'
import StudioPanel from '@/components/studio/StudioPanel'
import Loading from '@/components/common/Loading'
import { useNotebookStore, useSourceStore, useChatStore } from '@/store'

export default function NotebookPage() {
  const { id } = useParams<{ id: string }>()
  const { t } = useTranslation('notebook')

  const { currentNotebook, isLoading, fetchNotebook } = useNotebookStore()
  const { fetchSources } = useSourceStore()
  const { fetchMessages, fetchSuggestedQuestions } = useChatStore()

  useEffect(() => {
    if (id) {
      fetchNotebook(id)
      fetchSources(id)
      fetchMessages(id)
      fetchSuggestedQuestions(id)
    }
  }, [id, fetchNotebook, fetchSources, fetchMessages, fetchSuggestedQuestions])

  if (isLoading || !currentNotebook) {
    return (
      <div className="h-screen flex flex-col">
        <Header showBack />
        <Loading fullscreen message={t('loadingNotebook')} />
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      <Header title={currentNotebook.name} showBack />

      <div className="flex-1 overflow-hidden">
        <ThreeColumnLayout
          leftPanel={<SourcePanel notebookId={currentNotebook.id} />}
          centerPanel={<ChatPanel notebookId={currentNotebook.id} />}
          rightPanel={<StudioPanel notebookId={currentNotebook.id} />}
        />
      </div>
    </div>
  )
}
