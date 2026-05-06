import { useRef, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { DrawIoEmbed, DrawIoEmbedRef, EventExport } from 'react-drawio'
import { Download, Copy, Check, Edit3, Eye, Maximize2 } from 'lucide-react'
import type { DiagramData } from '../../types'

interface DiagramRendererProps {
  data: DiagramData
  onUpdate?: (xml: string) => void
}

export default function DiagramRenderer({ data, onUpdate }: DiagramRendererProps) {
  const { t } = useTranslation(['studio', 'common'])
  const drawioRef = useRef<DrawIoEmbedRef>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [copied, setCopied] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [exportedSvg, setExportedSvg] = useState<string | null>(null)

  // 取得圖表類型標籤
  const getTypeLabel = () => {
    if (data.type === 'flowchart') return t('diagramResult.flowchart')
    const typeLabels: Record<string, string> = {
      architecture: t('diagramResult.architecture'),
      sequence: t('diagramResult.sequence'),
      class: t('diagramResult.class'),
      er: t('diagramResult.er'),
      network: t('diagramResult.network'),
      auto: t('diagramResult.auto')
    }
    return typeLabels[data.diagram_type || 'auto'] || t('diagramResult.default')
  }

  // 處理匯出事件
  const handleExport = useCallback((exportData: EventExport) => {
    if (exportData.format === 'svg') {
      setExportedSvg(exportData.data)
    }
  }, [])

  // 複製 XML
  const handleCopyXml = () => {
    if (data.xml) {
      navigator.clipboard.writeText(data.xml)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // 下載 SVG
  const handleDownloadSvg = () => {
    if (drawioRef.current) {
      drawioRef.current.exportDiagram({
        format: 'svg'
      })
    }
  }

  // 下載 PNG（保留備用）
  const _handleDownloadPng = () => {
    if (drawioRef.current) {
      drawioRef.current.exportDiagram({
        format: 'png'
      })
    }
  }
  // 避免 unused variable 警告
  void _handleDownloadPng

  // 處理 SVG 匯出後下載
  const downloadExportedSvg = useCallback(() => {
    if (exportedSvg) {
      const blob = new Blob([exportedSvg], { type: 'image/svg+xml' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${data.title || 'diagram'}-${Date.now()}.svg`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      setExportedSvg(null)
    }
  }, [exportedSvg, data.title])

  // 當匯出完成時下載
  if (exportedSvg) {
    downloadExportedSvg()
  }

  // 切換編輯模式
  const toggleEditMode = () => {
    setIsEditing(!isEditing)
  }

  // 切換全螢幕
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  // 如果沒有 XML 資料，顯示錯誤訊息
  if (!data.xml) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <p className="font-medium">{t('diagramResult.cannotDisplay')}</p>
        <p className="text-sm mt-1">{t('diagramResult.missingXml')}</p>
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${isFullscreen ? 'fixed inset-0 z-50 bg-white p-4' : ''}`}>
      {/* 工具列 */}
      <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
            {getTypeLabel()}
          </span>
          {data.title && (
            <span className="text-sm font-medium text-gray-700">{data.title}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleEditMode}
            className={`flex items-center gap-1 px-2 py-1 text-sm rounded transition-colors ${
              isEditing
                ? 'bg-blue-100 text-blue-700'
                : 'hover:bg-gray-200'
            }`}
            title={isEditing ? t('diagramResult.viewMode') : t('diagramResult.editMode')}
          >
            {isEditing ? <Eye className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
            <span>{isEditing ? t('diagramResult.view') : t('diagramResult.edit')}</span>
          </button>
          <button
            onClick={handleCopyXml}
            className="flex items-center gap-1 px-2 py-1 text-sm rounded hover:bg-gray-200 transition-colors"
            title={t('diagramResult.copyXml')}
          >
            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? t('common:copied') : 'XML'}</span>
          </button>
          <button
            onClick={handleDownloadSvg}
            className="flex items-center gap-1 px-2 py-1 text-sm rounded hover:bg-gray-200 transition-colors"
            title={t('diagramResult.downloadSvg')}
          >
            <Download className="w-4 h-4" />
            <span>SVG</span>
          </button>
          <button
            onClick={toggleFullscreen}
            className="p-1.5 rounded hover:bg-gray-200 transition-colors"
            title={isFullscreen ? t('diagramResult.exitFullscreen') : t('diagramResult.fullscreen')}
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 圖表描述 */}
      {data.description && (
        <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
          {data.description}
        </p>
      )}

      {/* Draw.io 嵌入區域 */}
      <div
        className={`border border-gray-200 rounded-lg overflow-hidden bg-white ${
          isFullscreen ? 'flex-1' : ''
        }`}
        style={{ height: isFullscreen ? 'calc(100vh - 200px)' : '500px' }}
      >
        <DrawIoEmbed
          ref={drawioRef}
          xml={data.xml}
          configuration={{
            defaultFonts: ['Noto Sans TC', 'Microsoft JhengHei', 'sans-serif'],
          }}
          urlParameters={{
            ui: 'min',
            spin: true,
            libraries: true,
            saveAndExit: false,
            noSaveBtn: !isEditing,
            noExitBtn: true,
          }}
          onExport={handleExport}
          onSave={(saveData) => {
            if (onUpdate && saveData.xml) {
              onUpdate(saveData.xml)
            }
          }}
        />
      </div>

      {/* 圖表元素資訊（如果有） */}
      {data.elements && data.elements.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-3">
          <h5 className="text-sm font-medium text-gray-700 mb-2">{t('diagramResult.elements')}</h5>
          <div className="flex flex-wrap gap-2">
            {data.elements.slice(0, 10).map((element, index) => (
              <span
                key={element.id || index}
                className={`px-2 py-1 text-xs rounded ${
                  element.type === 'node'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-green-100 text-green-700'
                }`}
              >
                {element.label || element.id}
              </span>
            ))}
            {data.elements.length > 10 && (
              <span className="px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded">
                {t('diagramResult.moreElements', { count: data.elements.length - 10 })}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
