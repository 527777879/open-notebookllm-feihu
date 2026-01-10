import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { Download, Copy, Check, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react'

interface MindmapNode {
  text?: string
  name?: string
  description?: string
  color?: string
  icon?: string
  children?: MindmapNode[]
}

interface MindmapData {
  central?: { text: string; description?: string; icon?: string } | string
  central_text?: string
  branches?: MindmapNode[]
  mermaid?: string
  metadata?: {
    title?: string
    totalNodes?: number
    maxDepth?: number
  }
}

interface MindmapRendererProps {
  data: MindmapData
}

// 初始化 Mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  mindmap: {
    padding: 20,
    useMaxWidth: true,
  },
  securityLevel: 'loose',
})

export default function MindmapRenderer({ data }: MindmapRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svgContent, setSvgContent] = useState<string>('')
  const [copied, setCopied] = useState(false)
  const [zoom, setZoom] = useState(1)
  const [renderError, setRenderError] = useState<string | null>(null)

  useEffect(() => {
    renderMindmap()
  }, [data])

  const renderMindmap = async () => {
    if (!data) return

    try {
      // 優先使用後端生成的 Mermaid 代碼
      let mermaidCode = data.mermaid

      // 如果沒有 Mermaid 代碼，從 JSON 生成
      if (!mermaidCode) {
        mermaidCode = generateMermaidCode(data)
      }

      // 渲染 Mermaid
      const { svg } = await mermaid.render('mindmap-svg', mermaidCode)
      setSvgContent(svg)
      setRenderError(null)
    } catch (error) {
      console.error('Mermaid 渲染失敗:', error)
      setRenderError('心智圖渲染失敗，顯示文字版本')
    }
  }

  const generateMermaidCode = (mindmapData: MindmapData): string => {
    const lines = ['mindmap']

    // 處理中心節點
    const central = mindmapData.central
    let centralText = ''
    if (typeof central === 'object' && central?.text) {
      centralText = central.text
    } else if (typeof central === 'string') {
      centralText = central
    } else if (mindmapData.central_text) {
      centralText = mindmapData.central_text
    } else {
      centralText = '中心主題'
    }

    lines.push(`  root((${centralText}))`)

    // 處理分支
    const branches = mindmapData.branches || []
    for (const branch of branches) {
      addMermaidNode(lines, branch, 2)
    }

    return lines.join('\n')
  }

  const addMermaidNode = (lines: string[], node: MindmapNode, indent: number) => {
    const text = node.text || node.name || ''
    if (!text) return

    const prefix = '  '.repeat(indent)
    lines.push(`${prefix}${text}`)

    const children = node.children || []
    for (const child of children) {
      addMermaidNode(lines, child, indent + 1)
    }
  }

  const handleCopyMermaid = () => {
    const mermaidCode = data.mermaid || generateMermaidCode(data)
    navigator.clipboard.writeText(mermaidCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownloadSvg = () => {
    if (!svgContent) return
    const blob = new Blob([svgContent], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mindmap-${Date.now()}.svg`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 2))
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.4))
  const handleResetZoom = () => setZoom(1)

  // 如果渲染失敗，顯示文字版本
  if (renderError) {
    return (
      <div className="space-y-4">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-700">
          {renderError}
        </div>
        <TextMindmapView data={data} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 工具列 */}
      <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            className="p-1.5 rounded hover:bg-gray-200 transition-colors"
            title="縮小"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm text-gray-600 min-w-[3rem] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1.5 rounded hover:bg-gray-200 transition-colors"
            title="放大"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1.5 rounded hover:bg-gray-200 transition-colors"
            title="重置縮放"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyMermaid}
            className="flex items-center gap-1 px-2 py-1 text-sm rounded hover:bg-gray-200 transition-colors"
            title="複製 Mermaid 代碼"
          >
            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? '已複製' : 'Mermaid'}</span>
          </button>
          <button
            onClick={handleDownloadSvg}
            className="flex items-center gap-1 px-2 py-1 text-sm rounded hover:bg-gray-200 transition-colors"
            title="下載 SVG"
          >
            <Download className="w-4 h-4" />
            <span>SVG</span>
          </button>
        </div>
      </div>

      {/* 心智圖標題 */}
      {data.metadata?.title && (
        <h4 className="text-center font-medium text-gray-900">
          {data.metadata.title}
        </h4>
      )}

      {/* Mermaid 渲染區域 */}
      <div
        ref={containerRef}
        className="bg-white border border-gray-200 rounded-lg p-4 overflow-auto min-h-[300px] flex items-center justify-center"
        style={{ maxHeight: '500px' }}
      >
        {svgContent ? (
          <div
            style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        ) : (
          <div className="text-gray-400 text-sm">載入中...</div>
        )}
      </div>

      {/* 節點統計 */}
      {data.metadata && (
        <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
          {data.metadata.totalNodes && (
            <span>共 {data.metadata.totalNodes} 個節點</span>
          )}
          {data.metadata.maxDepth && (
            <span>最大深度 {data.metadata.maxDepth} 層</span>
          )}
        </div>
      )}
    </div>
  )
}

// 文字版心智圖（備援顯示）
function TextMindmapView({ data }: { data: MindmapData }) {
  const getCentralText = () => {
    if (typeof data.central === 'object' && data.central?.text) {
      return data.central.text
    } else if (typeof data.central === 'string') {
      return data.central
    } else if (data.central_text) {
      return data.central_text
    }
    return '中心主題'
  }

  const getCentralDescription = () => {
    if (typeof data.central === 'object' && data.central?.description) {
      return data.central.description
    }
    return null
  }

  const renderNode = (node: MindmapNode, level: number = 0) => {
    const text = node.text || node.name || ''
    if (!text) return null

    return (
      <div key={text + level} className="ml-4">
        <div className="flex items-start gap-2 py-1">
          <span
            className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
            style={{ backgroundColor: node.color || '#6B7280' }}
          />
          <div>
            <span className="text-sm text-gray-700">{text}</span>
            {node.description && (
              <p className="text-xs text-gray-500">{node.description}</p>
            )}
          </div>
        </div>
        {node.children && node.children.length > 0 && (
          <div className="border-l-2 border-gray-200 ml-1">
            {node.children.map((child) => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="text-center">
        <span className="inline-block px-4 py-2 bg-primary-600 text-white rounded-lg font-medium">
          {getCentralText()}
        </span>
        {getCentralDescription() && (
          <p className="text-sm text-gray-500 mt-1">{getCentralDescription()}</p>
        )}
      </div>
      <div className="mt-4">
        {data.branches?.map((branch) => renderNode(branch, 0))}
      </div>
    </div>
  )
}
