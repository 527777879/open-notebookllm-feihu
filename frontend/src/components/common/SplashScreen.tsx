import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

interface SplashScreenProps {
  duration?: number
  onComplete: () => void
}

export default function SplashScreen({ duration = 3000, onComplete }: SplashScreenProps) {
  const [fadeOut, setFadeOut] = useState(false)
  const { t } = useTranslation()

  useEffect(() => {
    // 開始淡出動畫
    const fadeTimer = setTimeout(() => {
      setFadeOut(true)
    }, duration - 500) // 提前 500ms 開始淡出

    // 完成後切換到主頁面
    const completeTimer = setTimeout(() => {
      onComplete()
    }, duration)

    return () => {
      clearTimeout(fadeTimer)
      clearTimeout(completeTimer)
    }
  }, [duration, onComplete])

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 transition-opacity duration-500 ${
        fadeOut ? 'opacity-0' : 'opacity-100'
      }`}
    >
      <div className="flex flex-col items-center">
        {/* Logo 圖片 */}
        <div className={`transform transition-all duration-1000 ${fadeOut ? 'scale-95 opacity-0' : 'scale-100 opacity-100'}`}>
          <img
            src="/logo.jpg"
            alt={t('common:splashAlt')}
            className="w-auto max-w-[80vw] max-h-[60vh] rounded-2xl shadow-2xl animate-fade-in"
          />
        </div>

        {/* 載入指示器 */}
        <div className={`mt-8 flex items-center gap-2 transition-opacity duration-500 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-gray-500 text-sm ml-2">{t('common:loading')}</span>
        </div>
      </div>
    </div>
  )
}
