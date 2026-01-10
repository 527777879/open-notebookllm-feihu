import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Bar, Line, Pie, Doughnut, Radar, PolarArea, Scatter } from 'react-chartjs-2'
import type { ChartConfig, InfographicData } from '@/types'
import { Lightbulb, TrendingUp, AlertCircle } from 'lucide-react'

// 註冊 Chart.js 組件
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface ChartRendererProps {
  data: InfographicData
}

// 單一圖表組件
function SingleChart({ chart }: { chart: ChartConfig }) {
  const chartConfig = chart.config

  // 根據類型渲染對應的圖表
  const renderChart = () => {
    const commonProps = {
      data: chartConfig.data as any,
      options: {
        ...chartConfig.options,
        responsive: true,
        maintainAspectRatio: false,
      } as any,
    }

    switch (chart.type) {
      case 'bar':
        return <Bar {...commonProps} />
      case 'line':
        return <Line {...commonProps} />
      case 'pie':
        return <Pie {...commonProps} />
      case 'doughnut':
        return <Doughnut {...commonProps} />
      case 'radar':
        return <Radar {...commonProps} />
      case 'polarArea':
        return <PolarArea {...commonProps} />
      case 'scatter':
        return <Scatter {...commonProps} />
      default:
        return <Bar {...commonProps} />
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
      {/* 圖表標題 */}
      <div>
        <h4 className="font-medium text-gray-900">{chart.title}</h4>
        {chart.description && (
          <p className="text-sm text-gray-500 mt-1">{chart.description}</p>
        )}
      </div>

      {/* 圖表容器 */}
      <div className="h-64 relative">
        {renderChart()}
      </div>

      {/* 洞察列表 */}
      {chart.insights && chart.insights.length > 0 && (
        <div className="pt-3 border-t border-gray-100">
          <p className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
            <Lightbulb className="w-3 h-3" />
            關鍵洞察
          </p>
          <ul className="space-y-1">
            {chart.insights.map((insight, index) => (
              <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                <span className="text-primary-500">•</span>
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// 資訊圖表渲染組件
export default function ChartRenderer({ data }: ChartRendererProps) {
  if (!data || !data.charts || data.charts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>無法顯示圖表資料</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 標題和說明 */}
      {data.title && (
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900">{data.title}</h3>
          {data.description && (
            <p className="text-sm text-gray-500 mt-1">{data.description}</p>
          )}
          {data.data_source && (
            <p className="text-xs text-gray-400 mt-1">資料來源：{data.data_source}</p>
          )}
        </div>
      )}

      {/* AI 生成圖片（如果有） */}
      {data.image && (
        <div className="rounded-lg overflow-hidden border border-gray-200">
          <img
            src={data.image.startsWith('data:') ? data.image : `data:image/png;base64,${data.image}`}
            alt={data.title || '資訊圖表'}
            className="w-full"
          />
        </div>
      )}

      {/* 圖表網格 */}
      <div className={`grid gap-4 ${data.charts.length === 1 ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-2'}`}>
        {data.charts.map((chart) => (
          <SingleChart key={chart.id} chart={chart} />
        ))}
      </div>

      {/* 總結 */}
      {data.summary && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 space-y-4">
          {/* 關鍵發現 */}
          {data.summary.key_findings && data.summary.key_findings.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                關鍵發現
              </h4>
              <ul className="space-y-2">
                {data.summary.key_findings.map((finding, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                      {index + 1}
                    </span>
                    {finding}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 建議 */}
          {data.summary.recommendations && data.summary.recommendations.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-amber-600" />
                建議行動
              </h4>
              <ul className="space-y-2">
                {data.summary.recommendations.map((rec, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 元數據 */}
      {data.metadata && (
        <div className="flex items-center justify-center gap-4 text-xs text-gray-400">
          <span>共 {data.metadata.total_charts} 個圖表</span>
          {data.metadata.chart_types && (
            <span>類型：{data.metadata.chart_types.join(', ')}</span>
          )}
          {data.metadata.data_points && (
            <span>數據點：{data.metadata.data_points}</span>
          )}
        </div>
      )}
    </div>
  )
}
