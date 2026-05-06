import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Mic,
  Video,
  Network,
  FileText,
  CreditCard,
  HelpCircle,
  BarChart3,
  Presentation,
  Table,
  Loader2,
  Play,
  Pause,
  Download,
  Radio,
  Volume2,
  Gauge,
  CheckCircle2,
  Lightbulb,
  GitBranch,
  Box,
} from 'lucide-react'
import { useSourceStore } from '@/store'
import * as studioApi from '@/api/studio'
import type {
  StudioOutputType,
  PodcastScript,
  PodcastSegment,
  PodcastSpeaker,
  PodcastVoice,
  DifficultyLevel,
  InfographicData,
  DiagramData,
  Flashcard,
  QuizQuestion,
} from '@/types'
import Button from '@/components/common/Button'
import Modal from '@/components/common/Modal'
import MindmapRenderer from './MindmapRenderer'
import ChartRenderer from './ChartRenderer'
import DiagramRenderer from './DiagramRenderer'

interface StudioPanelProps {
  notebookId: string
}

const getDefaultSpeakers = (t: any): PodcastSpeaker[] => [
  { name: t('podcast.defaultHost.name'), role: 'host', personality: t('podcast.defaultHost.personality') },
  { name: t('podcast.defaultGuest.name'), role: 'guest', personality: t('podcast.defaultGuest.personality') },
]

export default function StudioPanel({ notebookId }: StudioPanelProps) {
  const { t } = useTranslation(['studio', 'common'])

  const studioItems = [
    { type: 'summary' as const, icon: Mic, label: t('items.audioSummary'), color: 'bg-purple-100 text-purple-600' },
    { type: 'summary' as const, icon: Video, label: t('items.videoSummary'), color: 'bg-blue-100 text-blue-600' },
    { type: 'mindmap' as const, icon: Network, label: t('items.mindmap'), color: 'bg-green-100 text-green-600' },
    { type: 'flowchart' as const, icon: GitBranch, label: t('items.flowchart'), color: 'bg-teal-100 text-teal-600' },
    { type: 'diagram' as const, icon: Box, label: t('items.diagram'), color: 'bg-violet-100 text-violet-600' },
    { type: 'report' as const, icon: FileText, label: t('items.report'), color: 'bg-orange-100 text-orange-600' },
    { type: 'flashcards' as const, icon: CreditCard, label: t('items.flashcards'), color: 'bg-pink-100 text-pink-600' },
    { type: 'quiz' as const, icon: HelpCircle, label: t('items.quiz'), color: 'bg-cyan-100 text-cyan-600' },
    { type: 'infographic' as const, icon: BarChart3, label: t('items.infographic'), color: 'bg-yellow-100 text-yellow-600' },
    { type: 'presentation' as const, icon: Presentation, label: t('items.presentation'), color: 'bg-indigo-100 text-indigo-600' },
    { type: 'datatable' as const, icon: Table, label: t('items.datatable'), color: 'bg-gray-100 text-gray-600' },
    { type: 'podcast' as const, icon: Radio, label: t('items.podcast'), color: 'bg-red-100 text-red-600' },
  ]

  const podcastStyles = [
    { id: 'conversational', name: t('podcast.styles.conversational.name'), description: t('podcast.styles.conversational.description') },
    { id: 'educational', name: t('podcast.styles.educational.name'), description: t('podcast.styles.educational.description') },
    { id: 'debate', name: t('podcast.styles.debate.name'), description: t('podcast.styles.debate.description') },
    { id: 'interview', name: t('podcast.styles.interview.name'), description: t('podcast.styles.interview.description') },
  ]

  const difficultyOptions: { id: DifficultyLevel; name: string; description: string; color: string }[] = [
    { id: 'easy', name: t('difficulty.options.easy.name'), description: t('difficulty.options.easy.description'), color: 'bg-green-100 text-green-700 border-green-300' },
    { id: 'medium', name: t('difficulty.options.medium.name'), description: t('difficulty.options.medium.description'), color: 'bg-yellow-100 text-yellow-700 border-yellow-300' },
    { id: 'hard', name: t('difficulty.options.hard.name'), description: t('difficulty.options.hard.description'), color: 'bg-red-100 text-red-700 border-red-300' },
    { id: 'mixed', name: t('difficulty.options.mixed.name'), description: t('difficulty.options.mixed.description'), color: 'bg-blue-100 text-blue-700 border-blue-300' },
  ]
  const [generatingType, setGeneratingType] = useState<StudioOutputType | null>(null)
  const [result, setResult] = useState<{ type: string; data: unknown } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isResultModalOpen, setIsResultModalOpen] = useState(false)
  const { selectedIds } = useSourceStore()

  // Podcast 相關狀態
  const [isPodcastModalOpen, setIsPodcastModalOpen] = useState(false)
  const [podcastStyle, setPodcastStyle] = useState('conversational')
  const [podcastDuration, setPodcastDuration] = useState(10)
  const [podcastSpeakers, setPodcastSpeakers] = useState<PodcastSpeaker[]>(getDefaultSpeakers(t))
  const [withAudio, setWithAudio] = useState(false)
  const [availableVoices, setAvailableVoices] = useState<PodcastVoice[]>([])
  const [speakerVoices, setSpeakerVoices] = useState<Record<string, string>>({})

  // 學習卡/測驗難度選擇相關狀態
  const [isDifficultyModalOpen, setIsDifficultyModalOpen] = useState(false)
  const [pendingType, setPendingType] = useState<'flashcards' | 'quiz' | null>(null)
  const [selectedDifficulty, setSelectedDifficulty] = useState<DifficultyLevel>('mixed')
  const [selectedCount, setSelectedCount] = useState(10)

  // 音訊播放狀態
  const [audioBase64, setAudioBase64] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // 匯出結果
  const handleExport = () => {
    if (!result) {
      alert(t('noResultExport'))
      return
    }

    const content = JSON.stringify(result.data, null, 2)
    const blob = new Blob([content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${t('exportPrefix')}${result.type}_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // 載入可用語音
  useEffect(() => {
    const loadVoices = async () => {
      try {
        const response = await studioApi.getPodcastVoices(notebookId)
        if (response.data.success && response.data.data) {
          setAvailableVoices(response.data.data.voices)
        }
      } catch (error) {
        console.error(t('loadVoicesFailed'), error)
      }
    }
    loadVoices()
  }, [notebookId])

  const handleGenerate = async (type: StudioOutputType) => {
    if (type === 'podcast') {
      setIsPodcastModalOpen(true)
      return
    }

    // 學習卡和測驗需要選擇難度
    if (type === 'flashcards' || type === 'quiz') {
      setPendingType(type)
      setIsDifficultyModalOpen(true)
      return
    }

    await executeGenerate(type)
  }

  const executeGenerate = async (type: StudioOutputType, options?: studioApi.StudioOutputOptions) => {
    setGeneratingType(type)
    setResult(null)
    setError(null)

    try {
      const response = await studioApi.generateStudioOutput(
        notebookId,
        type,
        selectedIds.length > 0 ? selectedIds : undefined,
        options
      )

      if (response.data.success && response.data.data) {
        setResult({
          type,
          data: response.data.data.data,
        })
        setIsResultModalOpen(true)
      } else {
        setError(response.data.error || t('generateFailed'))
      }
    } catch (err: unknown) {
      console.error(t('generateFailedLog'), err)
      const errorMessage = err instanceof Error ? err.message : t('generateFailedNetwork')
      setError(errorMessage)
    } finally {
      setGeneratingType(null)
    }
  }

  const handleGenerateWithDifficulty = async () => {
    if (!pendingType) return
    setIsDifficultyModalOpen(false)

    await executeGenerate(pendingType, {
      count: selectedCount,
      difficulty: selectedDifficulty,
    })

    setPendingType(null)
  }

  const handleGeneratePodcast = async () => {
    setIsPodcastModalOpen(false)
    setGeneratingType('podcast')
    setResult(null)
    setError(null)
    setAudioBase64(null)

    try {
      const response = await studioApi.generatePodcast(notebookId, {
        sourceIds: selectedIds.length > 0 ? selectedIds : undefined,
        speakers: podcastSpeakers,
        durationMinutes: podcastDuration,
        style: podcastStyle,
        withAudio,
        speakerVoices: withAudio ? speakerVoices : undefined,
      })

      if (response.data.success && response.data.data) {
        setResult({
          type: 'podcast',
          data: response.data.data.data,
        })
        if (response.data.data.audio_base64) {
          setAudioBase64(response.data.data.audio_base64)
        }
        setIsResultModalOpen(true)
      } else {
        setError(response.data.error || t('podcast.generateFailed'))
      }
    } catch (err: unknown) {
      console.error(t('podcast.generateFailedLog'), err)
      const errorMessage = err instanceof Error ? err.message : t('podcast.generateFailedNetwork')
      setError(errorMessage)
    } finally {
      setGeneratingType(null)
    }
  }

  const handlePlayPause = () => {
    if (!audioBase64) return

    if (!audioRef.current) {
      audioRef.current = new Audio(`data:audio/mp3;base64,${audioBase64}`)
      audioRef.current.onended = () => setIsPlaying(false)
    }

    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleDownloadAudio = () => {
    if (!audioBase64) return
    studioApi.downloadBase64Audio(audioBase64, 'podcast.mp3')
  }

  const addSpeaker = () => {
    if (podcastSpeakers.length >= 4) return
    setPodcastSpeakers([
      ...podcastSpeakers,
      { name: `${t('podcast.speakerPrefix')}${podcastSpeakers.length + 1}`, role: 'guest', personality: '' },
    ])
  }

  const removeSpeaker = (index: number) => {
    if (podcastSpeakers.length <= 1) return
    setPodcastSpeakers(podcastSpeakers.filter((_, i) => i !== index))
  }

  const updateSpeaker = (index: number, field: keyof PodcastSpeaker, value: string) => {
    const updated = [...podcastSpeakers]
    updated[index] = { ...updated[index], [field]: value }
    setPodcastSpeakers(updated)
  }

  return (
    <div className="h-full flex flex-col">
      {/* 標題區 */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="font-semibold text-gray-900">{t('title')}</h2>
        <button
          onClick={handleExport}
          disabled={!result}
          className={`text-sm ${result ? 'text-primary-600 hover:text-primary-700' : 'text-gray-400 cursor-not-allowed'}`}
        >
          {t('export')}
        </button>
      </div>

      {/* 工具網格 */}
      <div className="p-4 grid grid-cols-2 gap-3">
        {studioItems.map((item, index) => {
          const Icon = item.icon
          const isGenerating = generatingType === item.type

          return (
            <button
              key={index}
              onClick={() => handleGenerate(item.type)}
              disabled={isGenerating}
              className="flex flex-col items-center gap-2 p-4 rounded-xl border border-gray-200 hover:border-primary-500 hover:shadow-md transition-all disabled:opacity-50"
            >
              <div className={`w-10 h-10 rounded-lg ${item.color} flex items-center justify-center`}>
                {isGenerating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Icon className="w-5 h-5" />
                )}
              </div>
              <span className="text-xs text-gray-700">{item.label}</span>
            </button>
          )
        })}
      </div>

      {/* 錯誤顯示區 */}
      {error && (
        <div className="mx-4 mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <span className="text-red-500 font-bold">!</span>
            <div className="flex-1">
              <p className="text-sm text-red-700 font-medium">{t('generateFailedTitle')}</p>
              <p className="text-xs text-red-600 mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-600"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* 結果顯示按鈕（有結果時顯示） */}
      {result && (
        <div className="mx-4 mt-2">
          <button
            onClick={() => setIsResultModalOpen(true)}
            className="w-full p-3 bg-primary-50 border border-primary-200 rounded-lg text-primary-700 hover:bg-primary-100 transition-colors flex items-center justify-center gap-2"
          >
            <FileText className="w-4 h-4" />
            {t('viewResult')}
          </button>
        </div>
      )}

      {/* 提示區 */}
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          {t('tip')}
          <br />
          {t('tipSecond')}
        </p>

        <button className="mt-3 w-full flex items-center justify-center gap-2 p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          <FileText className="w-4 h-4" />
          {t('addNote')}
        </button>
      </div>

      {/* Podcast 設定 Modal */}
      <Modal
        isOpen={isPodcastModalOpen}
        onClose={() => setIsPodcastModalOpen(false)}
        title={t('podcast.title')}
      >
        <div className="space-y-6">
          {/* 風格選擇 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('podcast.style')}
            </label>
            <div className="grid grid-cols-2 gap-2">
              {podcastStyles.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setPodcastStyle(style.id)}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    podcastStyle === style.id
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <p className="text-sm font-medium text-gray-900">{style.name}</p>
                  <p className="text-xs text-gray-500">{style.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* 時長選擇 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('podcast.duration')}
            </label>
            <div className="flex gap-2">
              {[5, 10, 15, 20].map((duration) => (
                <button
                  key={duration}
                  onClick={() => setPodcastDuration(duration)}
                  className={`flex-1 py-2 rounded-lg border transition-colors ${
                    podcastDuration === duration
                      ? 'border-primary-600 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {duration} {t('podcast.minutes')}
                </button>
              ))}
            </div>
          </div>

          {/* 講者設定 */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">
                {t('podcast.speakerSettings')}
              </label>
              {podcastSpeakers.length < 4 && (
                <button
                  onClick={addSpeaker}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  {t('podcast.addSpeaker')}
                </button>
              )}
            </div>
            <div className="space-y-3">
              {podcastSpeakers.map((speaker, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-3 space-y-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={speaker.name}
                      onChange={(e) => updateSpeaker(index, 'name', e.target.value)}
                      placeholder={t('podcast.speakerNamePlaceholder')}
                      className="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    <select
                      value={speaker.role}
                      onChange={(e) => updateSpeaker(index, 'role', e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="host">{t('podcast.speakerRoles.host')}</option>
                      <option value="guest">{t('podcast.speakerRoles.guest')}</option>
                      <option value="expert">{t('podcast.speakerRoles.expert')}</option>
                    </select>
                    {podcastSpeakers.length > 1 && (
                      <button
                        onClick={() => removeSpeaker(index)}
                        className="p-1.5 text-red-500 hover:bg-red-50 rounded"
                      >
                        ×
                      </button>
                    )}
                  </div>
                  <input
                    type="text"
                    value={speaker.personality || ''}
                    onChange={(e) => updateSpeaker(index, 'personality', e.target.value)}
                    placeholder={t('podcast.personalityPlaceholder')}
                    className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  {withAudio && availableVoices.length > 0 && (
                    <select
                      value={speakerVoices[speaker.name] || ''}
                      onChange={(e) => setSpeakerVoices({ ...speakerVoices, [speaker.name]: e.target.value })}
                      className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="">{t('podcast.selectVoice')}</option>
                      {availableVoices.map((voice) => (
                        <option key={voice.id} value={voice.id}>
                          {voice.name} ({voice.gender})
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 音訊選項 */}
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <input
              type="checkbox"
              id="withAudio"
              checked={withAudio}
              onChange={(e) => setWithAudio(e.target.checked)}
              className="w-4 h-4 text-primary-600 rounded"
            />
            <label htmlFor="withAudio" className="flex-1">
              <span className="text-sm font-medium text-gray-900">{t('podcast.generateAudio')}</span>
              <p className="text-xs text-gray-500">{t('podcast.generateAudioDesc')}</p>
            </label>
            <Volume2 className="w-5 h-5 text-gray-400" />
          </div>

          {/* 生成按鈕 */}
          <div className="flex justify-end gap-3">
            <Button
              variant="secondary"
              onClick={() => setIsPodcastModalOpen(false)}
            >
              {t('common:cancel')}
            </Button>
            <Button
              onClick={handleGeneratePodcast}
              loading={generatingType === 'podcast'}
            >
              <Radio className="w-4 h-4 mr-2" />
              {t('podcast.generatePodcast')}
            </Button>
          </div>
        </div>
      </Modal>

      {/* 難度選擇 Modal */}
      <Modal
        isOpen={isDifficultyModalOpen}
        onClose={() => {
          setIsDifficultyModalOpen(false)
          setPendingType(null)
        }}
        title={t('difficulty.title', { type: pendingType === 'flashcards' ? t('items.flashcards') : t('items.quiz') })}
      >
        <div className="space-y-6">
          {/* 數量選擇 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('difficulty.count')}
            </label>
            <div className="flex gap-2">
              {[5, 10, 15, 20].map((count) => (
                <button
                  key={count}
                  onClick={() => setSelectedCount(count)}
                  className={`flex-1 py-2 rounded-lg border transition-colors ${
                    selectedCount === count
                      ? 'border-primary-600 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {count} {pendingType === 'flashcards' ? t('difficulty.cardsUnit') : t('difficulty.questionsUnit')}
                </button>
              ))}
            </div>
          </div>

          {/* 難度選擇 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('difficulty.setting')}
            </label>
            <div className="grid grid-cols-2 gap-2">
              {difficultyOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSelectedDifficulty(option.id)}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    selectedDifficulty === option.id
                      ? `${option.color} border-2`
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <p className="text-sm font-medium">{option.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{option.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Bloom 認知層次說明 */}
          <div className="bg-blue-50 rounded-lg p-3">
            <p className="text-xs text-blue-700 font-medium mb-1 flex items-center gap-1">
              <Lightbulb className="w-3 h-3" />
              {t('difficulty.bloomLevel')}
            </p>
            <p className="text-xs text-blue-600">
              {selectedDifficulty === 'easy' && t('difficulty.bloomDescriptions.easy')}
              {selectedDifficulty === 'medium' && t('difficulty.bloomDescriptions.medium')}
              {selectedDifficulty === 'hard' && t('difficulty.bloomDescriptions.hard')}
              {selectedDifficulty === 'mixed' && t('difficulty.bloomDescriptions.mixed')}
            </p>
          </div>

          {/* 生成按鈕 */}
          <div className="flex justify-end gap-3">
            <Button
              variant="secondary"
              onClick={() => {
                setIsDifficultyModalOpen(false)
                setPendingType(null)
              }}
            >
              {t('common:cancel')}
            </Button>
            <Button
              onClick={handleGenerateWithDifficulty}
              loading={generatingType === pendingType}
            >
              <Gauge className="w-4 h-4 mr-2" />
              {t('difficulty.startGenerate')}
            </Button>
          </div>
        </div>
      </Modal>

      {/* 結果顯示 Modal */}
      <Modal
        isOpen={isResultModalOpen}
        onClose={() => setIsResultModalOpen(false)}
        title={t(`resultTitles.${result?.type || 'default'}`)}
      >
        <div className="max-h-[70vh] overflow-y-auto">
          {/* Podcast 音訊播放器 */}
          {result?.type === 'podcast' && audioBase64 && (
            <div className="mb-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={handlePlayPause}
                  className="w-12 h-12 rounded-full bg-red-600 text-white flex items-center justify-center hover:bg-red-700 transition-colors"
                >
                  {isPlaying ? (
                    <Pause className="w-5 h-5" />
                  ) : (
                    <Play className="w-5 h-5 ml-0.5" />
                  )}
                </button>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{t('podcast.audioTitle')}</p>
                  <p className="text-sm text-gray-500">{t('podcast.clickToPlay')}</p>
                </div>
                <button
                  onClick={handleDownloadAudio}
                  className="p-2 rounded-lg hover:bg-white/50 transition-colors"
                  title={t('podcast.downloadAudio')}
                >
                  <Download className="w-5 h-5 text-gray-600" />
                </button>
              </div>
            </div>
          )}

          {result && <ResultDisplay type={result.type} data={result.data} />}

          <div className="mt-4 pt-4 border-t flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsResultModalOpen(false)}>
              {t('common:close')}
            </Button>
            <Button onClick={handleExport}>
              <Download className="w-4 h-4 mr-2" />
              {t('common:export')}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

// 展平嵌套數據的輔助函數
function flattenData(data: unknown): unknown {
  if (!data || typeof data !== 'object') return data
  const obj = data as Record<string, unknown>
  // 如果數據有 data 屬性且是對象，則合併內層數據與外層其他字段
  if (obj.data && typeof obj.data === 'object') {
    const innerData = obj.data as Record<string, unknown>
    // 保留外層的其他字段（如 image, type 等）並與內層數據合併
    const result: Record<string, unknown> = { ...innerData }
    for (const key of Object.keys(obj)) {
      if (key !== 'data' && key !== 'type') {
        result[key] = obj[key]
      }
    }
    return result
  }
  return data
}

// 結果顯示組件
function ResultDisplay({ type, data: rawData }: { type: string; data: unknown }) {
  const { t } = useTranslation(['studio', 'common'])

  // 展平可能嵌套的數據
  const data = flattenData(rawData)

  if (type === 'summary' || type === 'report') {
    const content = (data as { summary?: string; content?: string }).summary ||
                    (data as { content?: string }).content || ''
    return (
      <div className="prose prose-sm max-w-none">
        <div className="whitespace-pre-wrap text-sm text-gray-700">{content}</div>
      </div>
    )
  }

  if (type === 'flashcards') {
    const flashcardsData = (data as { data?: { cards?: Flashcard[]; metadata?: unknown } }).data ||
                           (data as { cards?: Flashcard[]; metadata?: unknown })
    const cards = flashcardsData?.cards || []
    const metadata = (flashcardsData as { metadata?: { difficulty_distribution?: Record<string, number>; categories?: string[] } })?.metadata

    // 難度顏色映射
    const difficultyColors: Record<string, string> = {
      easy: 'bg-green-100 text-green-700',
      medium: 'bg-yellow-100 text-yellow-700',
      hard: 'bg-red-100 text-red-700',
    }

    return (
      <div className="space-y-4">
        {/* 元數據摘要 */}
        {metadata && (
          <div className="flex items-center gap-4 text-xs text-gray-500 pb-3 border-b">
            <span>{t('flashcardResult.cardCount', { count: cards.length })}</span>
            {metadata.difficulty_distribution && (
              <span>
                {t('flashcardResult.difficultyDistribution', {
                  easy: metadata.difficulty_distribution.easy || 0,
                  medium: metadata.difficulty_distribution.medium || 0,
                  hard: metadata.difficulty_distribution.hard || 0,
                })}
              </span>
            )}
          </div>
        )}

        {/* 學習卡列表 */}
        {cards.map((card: Flashcard, index: number) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4 space-y-2">
            {/* 標籤列 */}
            <div className="flex items-center gap-2 mb-2">
              {card.difficulty && (
                <span className={`text-xs px-2 py-0.5 rounded ${difficultyColors[card.difficulty] || 'bg-gray-100 text-gray-600'}`}>
                  {t(`flashcardResult.difficultyLabels.${card.difficulty}`, card.difficulty as string)}
                </span>
              )}
              {card.category && (
                <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                  {card.category}
                </span>
              )}
              {card.cognitive_level && (
                <span className="text-xs text-gray-400">
                  {card.cognitive_level}
                </span>
              )}
            </div>

            {/* 問題 */}
            <p className="font-medium text-gray-900">{card.front}</p>

            {/* 提示 */}
            {card.hint && (
              <p className="text-xs text-amber-600 flex items-center gap-1">
                <Lightbulb className="w-3 h-3" />
                {t('flashcardResult.hint', { hint: card.hint })}
              </p>
            )}

            {/* 答案 */}
            <div className="pt-2 border-t border-gray-200">
              <p className="text-sm text-gray-600">{card.back}</p>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (type === 'quiz') {
    const quizData = (data as { data?: { questions?: QuizQuestion[]; metadata?: unknown; quiz_title?: string } }).data ||
                     (data as { questions?: QuizQuestion[]; metadata?: unknown; quiz_title?: string })
    const questions = quizData?.questions || []
    const metadata = (quizData as { metadata?: { total_points?: number; time_limit_minutes?: number; passing_score?: number } })?.metadata
    const quizTitle = (quizData as { quiz_title?: string })?.quiz_title

    // 難度顏色映射
    const difficultyColors: Record<string, string> = {
      easy: 'bg-green-100 text-green-700',
      medium: 'bg-yellow-100 text-yellow-700',
      hard: 'bg-red-100 text-red-700',
    }

    return (
      <div className="space-y-4">
        {/* 標題和元數據 */}
        {(quizTitle || metadata) && (
          <div className="bg-cyan-50 rounded-lg p-4">
            {quizTitle && <h4 className="font-medium text-gray-900">{quizTitle}</h4>}
            {metadata && (
              <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 mt-2">
                <span>{t('quizResult.questionCount', { count: questions.length })}</span>
                {metadata.total_points && <span>{t('quizResult.totalPoints', { points: metadata.total_points })}</span>}
                {metadata.time_limit_minutes && <span>{t('quizResult.timeLimit', { minutes: metadata.time_limit_minutes })}</span>}
                {metadata.passing_score && <span>{t('quizResult.passingScore', { score: metadata.passing_score })}</span>}
              </div>
            )}
          </div>
        )}

        {/* 題目列表 */}
        {questions.map((q: QuizQuestion, index: number) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4 space-y-3">
            {/* 題目標籤 */}
            <div className="flex items-center gap-2">
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-100 text-cyan-700">
                {t(`quizResult.typeLabels.${q.type}`, q.type as string)}
              </span>
              {q.difficulty && (
                <span className={`text-xs px-2 py-0.5 rounded ${difficultyColors[q.difficulty] || 'bg-gray-100'}`}>
                  {t(`quizResult.difficultyLabels.${q.difficulty}`, q.difficulty as string)}
                </span>
              )}
              {q.points && (
                <span className="text-xs text-gray-400">{t('quizResult.points', { points: q.points })}</span>
              )}
            </div>

            {/* 題目內容 */}
            <p className="font-medium text-gray-900">
              {index + 1}. {q.question}
            </p>

            {/* 選擇題選項 */}
            {q.type === 'multiple_choice' && q.options && (
              <div className="space-y-1 ml-4">
                {q.options.map((opt: string, i: number) => {
                  const isCorrect = q.correct === String.fromCharCode(65 + i)
                  return (
                    <p key={i} className={`text-sm flex items-center gap-2 ${isCorrect ? 'text-green-700 font-medium' : 'text-gray-600'}`}>
                      {isCorrect && <CheckCircle2 className="w-4 h-4" />}
                      {String.fromCharCode(65 + i)}. {opt}
                    </p>
                  )
                })}
              </div>
            )}

            {/* 判斷題答案 */}
            {q.type === 'true_false' && (
              <p className="text-sm text-green-700 font-medium flex items-center gap-2 ml-4">
                <CheckCircle2 className="w-4 h-4" />
                {t('quizResult.answer')}{q.correct === true ? t('quizResult.correct') : t('quizResult.incorrect')}
              </p>
            )}

            {/* 填空題答案 */}
            {q.type === 'fill_blank' && (
              <p className="text-sm text-green-700 font-medium ml-4">
                {t('quizResult.answer')}{String(q.correct)}
                {q.alternatives && q.alternatives.length > 0 && (
                  <span className="text-gray-500 font-normal">{t('quizResult.alsoAccept', { alternatives: q.alternatives.join('、') })}</span>
                )}
              </p>
            )}

            {/* 配對題 */}
            {q.type === 'matching' && q.left_items && q.right_items && (
              <div className="grid grid-cols-2 gap-4 ml-4">
                <div className="space-y-1">
                  {q.left_items.map((item, i) => (
                    <p key={i} className="text-sm text-gray-600">{i + 1}. {item}</p>
                  ))}
                </div>
                <div className="space-y-1">
                  {q.right_items.map((item, i) => (
                    <p key={i} className="text-sm text-gray-600">{String.fromCharCode(65 + i)}. {item}</p>
                  ))}
                </div>
              </div>
            )}

            {/* 簡答題參考答案 */}
            {q.type === 'short_answer' && (
              <div className="ml-4 space-y-2">
                {q.sample_answer && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">{t('quizResult.referenceAnswer')}</span>{q.sample_answer}
                  </p>
                )}
                {q.key_points && q.key_points.length > 0 && (
                  <div className="text-sm text-gray-500">
                    <span className="font-medium">{t('quizResult.gradingPoints')}</span>
                    <ul className="list-disc list-inside mt-1">
                      {q.key_points.map((point, i) => (
                        <li key={i}>{point}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* 提示 */}
            {q.hint && (
              <p className="text-xs text-amber-600 flex items-center gap-1 ml-4">
                <Lightbulb className="w-3 h-3" />
                {t('quizResult.hint', { hint: q.hint })}
              </p>
            )}

            {/* 解釋 */}
            {q.explanation && (
              <div className="pt-2 border-t border-gray-200 mt-2">
                <p className="text-xs text-gray-500">
                  <span className="font-medium">{t('quizResult.explanation')}</span>{q.explanation}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  if (type === 'mindmap') {
    const mindmap = (data as { data?: Record<string, unknown> }).data || data
    if (!mindmap) return <p className="text-gray-500">{t('mindmapResult.renderFailed')}</p>

    return <MindmapRenderer data={mindmap as Parameters<typeof MindmapRenderer>[0]['data']} />
  }

  // 流程圖顯示（Draw.io）
  if (type === 'flowchart') {
    const diagramData = (data as { data?: DiagramData }).data || data as DiagramData
    if (!diagramData || !diagramData.xml) {
      return <p className="text-gray-500">{t('flowchartResult.renderFailed')}</p>
    }
    return <DiagramRenderer data={{ ...diagramData, type: 'flowchart' }} />
  }

  // 架構圖顯示（Draw.io）
  if (type === 'diagram') {
    const diagramData = (data as { data?: DiagramData }).data || data as DiagramData
    if (!diagramData || !diagramData.xml) {
      return <p className="text-gray-500">{t('diagramResult.renderFailed')}</p>
    }
    return <DiagramRenderer data={{ ...diagramData, type: 'diagram' }} />
  }

  if (type === 'podcast') {
    const podcastData = data as { script?: PodcastScript; title?: string; description?: string }
    const script = podcastData.script

    if (!script || !script.segments) {
      return (
        <div className="text-gray-500">
          <p>{podcastData.title || 'Podcast'}</p>
          {podcastData.description && (
            <p className="text-sm mt-1">{podcastData.description}</p>
          )}
        </div>
      )
    }

    return (
      <div className="space-y-4">
        {script.title && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900">{script.title}</h4>
            {script.description && (
              <p className="text-sm text-gray-600 mt-1">{script.description}</p>
            )}
          </div>
        )}
        <div className="space-y-3">
          {script.segments.map((segment: PodcastSegment, index: number) => (
            <div key={index} className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-600">
                  {segment.speaker.charAt(0)}
                </div>
              </div>
              <div className="flex-1">
                <p className="text-xs font-medium text-gray-500 mb-1">
                  {segment.speaker}
                  {segment.emotion && (
                    <span className="ml-2 text-gray-400">({segment.emotion})</span>
                  )}
                </p>
                <p className="text-sm text-gray-700">{segment.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // 簡報顯示
  if (type === 'presentation') {
    const presData = data as {
      title?: string
      slides?: Array<{
        title: string
        content: string | string[]
        image?: string
        speaker_notes?: string
      }>
    }
    const slides = presData.slides || []

    if (slides.length === 0) {
      return <p className="text-gray-500">{t('presentationResult.cannotDisplay')}</p>
    }

    return (
      <div className="space-y-4">
        {presData.title && (
          <h4 className="font-medium text-gray-900 text-center">{presData.title}</h4>
        )}
        {slides.map((slide, index) => (
          <div key={index} className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-100">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center">
                {index + 1}
              </span>
              <h5 className="font-medium text-gray-900">{slide.title}</h5>
            </div>
            {slide.image && (
              <img
                src={slide.image.startsWith('data:') ? slide.image : `data:image/png;base64,${slide.image}`}
                alt={slide.title}
                className="w-full h-32 object-cover rounded-lg mb-2"
              />
            )}
            <div className="text-sm text-gray-600">
              {Array.isArray(slide.content) ? (
                <ul className="list-disc list-inside space-y-1">
                  {slide.content.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p>{slide.content}</p>
              )}
            </div>
            {slide.speaker_notes && (
              <p className="mt-2 text-xs text-gray-400 italic">{t('presentationResult.notes', { notes: slide.speaker_notes })}</p>
            )}
          </div>
        ))}
      </div>
    )
  }

  // 資訊圖表顯示（Chart.js 版）
  if (type === 'infographic') {
    // 嘗試解析新格式（Chart.js）
    const rawInfographic = data as { data?: InfographicData; charts?: unknown[]; image?: string }
    const infographicData = rawInfographic?.data || rawInfographic

    // 檢查是否為新格式（有 charts 陣列）
    if (infographicData && 'charts' in infographicData && Array.isArray((infographicData as InfographicData).charts)) {
      return <ChartRenderer data={infographicData as InfographicData} />
    }

    // 舊格式兼容：顯示 AI 圖片或 sections
    const oldFormatData = data as {
      title?: string
      sections?: Array<{
        title: string
        content: string
        icon?: string
        stats?: Array<{ label: string; value: string }>
      }>
      image?: string
    }

    return (
      <div className="space-y-4">
        {oldFormatData.title && (
          <h4 className="font-medium text-gray-900 text-center">{oldFormatData.title}</h4>
        )}
        {oldFormatData.image && (
          <img
            src={oldFormatData.image.startsWith('data:') ? oldFormatData.image : `data:image/png;base64,${oldFormatData.image}`}
            alt={oldFormatData.title || t('chartResult.infographicAlt')}
            className="w-full rounded-lg"
          />
        )}
        {oldFormatData.sections?.map((section, index) => (
          <div key={index} className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-2">
              {section.icon && <span className="mr-2">{section.icon}</span>}
              {section.title}
            </h5>
            <p className="text-sm text-gray-600">{section.content}</p>
            {section.stats && (
              <div className="mt-2 flex flex-wrap gap-2">
                {section.stats.map((stat, i) => (
                  <div key={i} className="bg-white rounded px-2 py-1">
                    <span className="text-xs text-gray-500">{stat.label}: </span>
                    <span className="text-sm font-medium text-gray-900">{stat.value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  // 資料表顯示
  if (type === 'datatable') {
    const tableData = data as {
      title?: string
      headers?: string[]
      rows?: string[][]
    }

    if (!tableData.headers || !tableData.rows) {
      return (
        <pre className="text-xs bg-gray-50 p-4 rounded-lg overflow-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      )
    }

    return (
      <div className="space-y-2">
        {tableData.title && (
          <h4 className="font-medium text-gray-900">{tableData.title}</h4>
        )}
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
            <thead className="bg-gray-100">
              <tr>
                {tableData.headers.map((header, i) => (
                  <th key={i} className="px-3 py-2 text-left font-medium text-gray-700 border-b">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableData.rows.map((row, i) => (
                <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  {row.map((cell, j) => (
                    <td key={j} className="px-3 py-2 text-gray-600 border-b border-gray-100">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  return (
    <pre className="text-xs bg-gray-50 p-4 rounded-lg overflow-auto">
      {JSON.stringify(data, null, 2)}
    </pre>
  )
}
