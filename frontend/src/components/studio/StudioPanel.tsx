import { useState, useRef, useEffect } from 'react'
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
  ChevronRight,
  Play,
  Pause,
  Download,
  Radio,
  Users,
  Settings2,
  Volume2,
} from 'lucide-react'
import { useSourceStore } from '@/store'
import * as studioApi from '@/api/studio'
import type { StudioOutputType, PodcastScript, PodcastSegment, PodcastSpeaker, PodcastVoice, PodcastStyle } from '@/types'
import Button from '@/components/common/Button'
import Modal from '@/components/common/Modal'

interface StudioPanelProps {
  notebookId: string
}

const studioItems = [
  { type: 'summary' as const, icon: Mic, label: '語音摘要', color: 'bg-purple-100 text-purple-600' },
  { type: 'summary' as const, icon: Video, label: '影片摘要', color: 'bg-blue-100 text-blue-600' },
  { type: 'mindmap' as const, icon: Network, label: '心智圖', color: 'bg-green-100 text-green-600' },
  { type: 'report' as const, icon: FileText, label: '報告', color: 'bg-orange-100 text-orange-600' },
  { type: 'flashcards' as const, icon: CreditCard, label: '學習卡', color: 'bg-pink-100 text-pink-600' },
  { type: 'quiz' as const, icon: HelpCircle, label: '測驗', color: 'bg-cyan-100 text-cyan-600' },
  { type: 'infographic' as const, icon: BarChart3, label: '資訊圖表', color: 'bg-yellow-100 text-yellow-600' },
  { type: 'presentation' as const, icon: Presentation, label: '簡報', color: 'bg-indigo-100 text-indigo-600' },
  { type: 'datatable' as const, icon: Table, label: '資料表', color: 'bg-gray-100 text-gray-600' },
  { type: 'podcast' as const, icon: Radio, label: 'Podcast', color: 'bg-red-100 text-red-600' },
]

const podcastStyles = [
  { id: 'conversational', name: '輕鬆對談', description: '自然友善的談話風格' },
  { id: 'educational', name: '教育講解', description: '清晰易懂的教學模式' },
  { id: 'debate', name: '辯論討論', description: '多角度觀點交流' },
  { id: 'interview', name: '專訪形式', description: '訪談問答模式' },
]

const defaultSpeakers: PodcastSpeaker[] = [
  { name: '主持人', role: 'host', personality: '專業、親切' },
  { name: '來賓', role: 'guest', personality: '博學、風趣' },
]

export default function StudioPanel({ notebookId }: StudioPanelProps) {
  const [generatingType, setGeneratingType] = useState<StudioOutputType | null>(null)
  const [result, setResult] = useState<{ type: string; data: unknown } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isResultModalOpen, setIsResultModalOpen] = useState(false)
  const { selectedIds } = useSourceStore()

  // Podcast 相關狀態
  const [isPodcastModalOpen, setIsPodcastModalOpen] = useState(false)
  const [podcastStyle, setPodcastStyle] = useState('conversational')
  const [podcastDuration, setPodcastDuration] = useState(10)
  const [podcastSpeakers, setPodcastSpeakers] = useState<PodcastSpeaker[]>(defaultSpeakers)
  const [withAudio, setWithAudio] = useState(false)
  const [availableVoices, setAvailableVoices] = useState<PodcastVoice[]>([])
  const [speakerVoices, setSpeakerVoices] = useState<Record<string, string>>({})

  // 音訊播放狀態
  const [audioBase64, setAudioBase64] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // 匯出結果
  const handleExport = () => {
    if (!result) {
      alert('尚無結果可匯出')
      return
    }

    const content = JSON.stringify(result.data, null, 2)
    const blob = new Blob([content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `工作室_${result.type}_${new Date().toISOString().slice(0, 10)}.json`
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
        console.error('載入語音列表失敗:', error)
      }
    }
    loadVoices()
  }, [notebookId])

  const handleGenerate = async (type: StudioOutputType) => {
    if (type === 'podcast') {
      setIsPodcastModalOpen(true)
      return
    }

    setGeneratingType(type)
    setResult(null)
    setError(null)

    try {
      const response = await studioApi.generateStudioOutput(
        notebookId,
        type,
        selectedIds.length > 0 ? selectedIds : undefined
      )

      if (response.data.success && response.data.data) {
        setResult({
          type,
          data: response.data.data.data,
        })
        setIsResultModalOpen(true)
      } else {
        // API 返回 success: false
        setError(response.data.error || '生成失敗，請稍後再試')
      }
    } catch (err: unknown) {
      console.error('生成失敗:', err)
      const errorMessage = err instanceof Error ? err.message : '生成失敗，請檢查網路連線或後端服務'
      setError(errorMessage)
    } finally {
      setGeneratingType(null)
    }
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
        setError(response.data.error || 'Podcast 生成失敗')
      }
    } catch (err: unknown) {
      console.error('生成 Podcast 失敗:', err)
      const errorMessage = err instanceof Error ? err.message : 'Podcast 生成失敗，請檢查網路連線或後端服務'
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
      { name: `講者 ${podcastSpeakers.length + 1}`, role: 'guest', personality: '' },
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
        <h2 className="font-semibold text-gray-900">工作室</h2>
        <button
          onClick={handleExport}
          disabled={!result}
          className={`text-sm ${result ? 'text-primary-600 hover:text-primary-700' : 'text-gray-400 cursor-not-allowed'}`}
        >
          Export
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
              <p className="text-sm text-red-700 font-medium">生成失敗</p>
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
            查看生成結果
          </button>
        </div>
      )}

      {/* 提示區 */}
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          工作室輸出內容會儲存在這裡。
          <br />
          加入來源後，點選即可新增語音摘要、研讀指南、心智圖等內容！
        </p>

        <button className="mt-3 w-full flex items-center justify-center gap-2 p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          <FileText className="w-4 h-4" />
          新增記事
        </button>
      </div>

      {/* Podcast 設定 Modal */}
      <Modal
        isOpen={isPodcastModalOpen}
        onClose={() => setIsPodcastModalOpen(false)}
        title="生成 Podcast"
      >
        <div className="space-y-6">
          {/* 風格選擇 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              對談風格
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
              預估時長（分鐘）
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
                  {duration} 分
                </button>
              ))}
            </div>
          </div>

          {/* 講者設定 */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">
                講者設定（1-4 人）
              </label>
              {podcastSpeakers.length < 4 && (
                <button
                  onClick={addSpeaker}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  + 新增講者
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
                      placeholder="講者名稱"
                      className="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    <select
                      value={speaker.role}
                      onChange={(e) => updateSpeaker(index, 'role', e.target.value)}
                      className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="host">主持人</option>
                      <option value="guest">來賓</option>
                      <option value="expert">專家</option>
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
                    placeholder="個性描述（選填，如：專業、幽默）"
                    className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  {withAudio && availableVoices.length > 0 && (
                    <select
                      value={speakerVoices[speaker.name] || ''}
                      onChange={(e) => setSpeakerVoices({ ...speakerVoices, [speaker.name]: e.target.value })}
                      className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="">選擇語音</option>
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
              <span className="text-sm font-medium text-gray-900">生成音訊</span>
              <p className="text-xs text-gray-500">將腳本轉換為語音（需要 TTS 服務）</p>
            </label>
            <Volume2 className="w-5 h-5 text-gray-400" />
          </div>

          {/* 生成按鈕 */}
          <div className="flex justify-end gap-3">
            <Button
              variant="secondary"
              onClick={() => setIsPodcastModalOpen(false)}
            >
              取消
            </Button>
            <Button
              onClick={handleGeneratePodcast}
              loading={generatingType === 'podcast'}
            >
              <Radio className="w-4 h-4 mr-2" />
              生成 Podcast
            </Button>
          </div>
        </div>
      </Modal>

      {/* 結果顯示 Modal */}
      <Modal
        isOpen={isResultModalOpen}
        onClose={() => setIsResultModalOpen(false)}
        title={getResultTitle(result?.type || '')}
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
                  <p className="font-medium text-gray-900">Podcast 音訊</p>
                  <p className="text-sm text-gray-500">點擊播放收聽</p>
                </div>
                <button
                  onClick={handleDownloadAudio}
                  className="p-2 rounded-lg hover:bg-white/50 transition-colors"
                  title="下載音訊"
                >
                  <Download className="w-5 h-5 text-gray-600" />
                </button>
              </div>
            </div>
          )}

          {result && <ResultDisplay type={result.type} data={result.data} />}

          <div className="mt-4 pt-4 border-t flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsResultModalOpen(false)}>
              關閉
            </Button>
            <Button onClick={handleExport}>
              <Download className="w-4 h-4 mr-2" />
              匯出
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

// 獲取結果標題
function getResultTitle(type: string): string {
  const titles: Record<string, string> = {
    summary: '摘要',
    mindmap: '心智圖',
    flashcards: '學習卡',
    quiz: '測驗',
    report: '報告',
    presentation: '簡報',
    infographic: '資訊圖表',
    datatable: '資料表',
    podcast: 'Podcast',
  }
  return titles[type] || '生成結果'
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
    const cards = (data as { data?: { cards?: Array<{ front: string; back: string }> } }).data?.cards ||
                  (data as { cards?: Array<{ front: string; back: string }> }).cards || []
    return (
      <div className="space-y-3">
        {cards.map((card: { front: string; back: string }, index: number) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4">
            <p className="font-medium text-gray-900 mb-2">{card.front}</p>
            <p className="text-sm text-gray-600">{card.back}</p>
          </div>
        ))}
      </div>
    )
  }

  if (type === 'quiz') {
    const questions = (data as { data?: { questions?: Array<{ question: string; options?: string[]; correct: string | boolean }> } }).data?.questions ||
                      (data as { questions?: Array<{ question: string; options?: string[]; correct: string | boolean }> }).questions || []
    return (
      <div className="space-y-4">
        {questions.map((q: { question: string; options?: string[]; correct: string | boolean }, index: number) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4">
            <p className="font-medium text-gray-900 mb-2">
              {index + 1}. {q.question}
            </p>
            {q.options && (
              <div className="space-y-1 ml-4">
                {q.options.map((opt: string, i: number) => (
                  <p key={i} className="text-sm text-gray-600">
                    {String.fromCharCode(65 + i)}. {opt}
                  </p>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  if (type === 'mindmap') {
    const mindmap = (data as { data?: { central?: string; branches?: Array<{ name: string; children?: Array<{ name: string }> }> } }).data ||
                    (data as { central?: string; branches?: Array<{ name: string; children?: Array<{ name: string }> }> })
    if (!mindmap || !mindmap.central) return <p className="text-gray-500">無法顯示心智圖</p>

    return (
      <div className="space-y-2">
        <div className="text-center">
          <span className="inline-block px-4 py-2 bg-primary-600 text-white rounded-lg font-medium">
            {mindmap.central}
          </span>
        </div>
        <div className="ml-8 space-y-2">
          {mindmap.branches?.map((branch: { name: string; children?: Array<{ name: string }> }, index: number) => (
            <div key={index}>
              <div className="flex items-center gap-2">
                <ChevronRight className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-700">{branch.name}</span>
              </div>
              {branch.children && branch.children.length > 0 && (
                <div className="ml-6 mt-1 space-y-1">
                  {branch.children.map((child: { name: string }, i: number) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-gray-600">
                      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                      {child.name}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
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
      return <p className="text-gray-500">無法顯示簡報</p>
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
              <p className="mt-2 text-xs text-gray-400 italic">備註: {slide.speaker_notes}</p>
            )}
          </div>
        ))}
      </div>
    )
  }

  // 資訊圖表顯示
  if (type === 'infographic') {
    const infoData = data as {
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
        {infoData.title && (
          <h4 className="font-medium text-gray-900 text-center">{infoData.title}</h4>
        )}
        {infoData.image && (
          <img
            src={infoData.image.startsWith('data:') ? infoData.image : `data:image/png;base64,${infoData.image}`}
            alt={infoData.title || '資訊圖表'}
            className="w-full rounded-lg"
          />
        )}
        {infoData.sections?.map((section, index) => (
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
