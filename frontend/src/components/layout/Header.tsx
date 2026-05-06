import { Link, useNavigate } from 'react-router-dom'
import { BookOpen, Settings, Plus, ArrowLeft, Globe } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import i18n from '@/i18n'
import { useState, useRef, useEffect } from 'react'

interface HeaderProps {
  title?: string
  showBack?: boolean
  onCreateNotebook?: () => void
}

export default function Header({ title, showBack, onCreateNotebook }: HeaderProps) {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [langOpen, setLangOpen] = useState(false)
  const langRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (langRef.current && !langRef.current.contains(e.target as Node)) {
        setLangOpen(false)
      }
    }
    if (langOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [langOpen])

  const changeLang = (lang: string) => {
    i18n.changeLanguage(lang)
    setLangOpen(false)
  }

  return (
    <header className="h-14 border-b border-gray-200 bg-white px-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {showBack && (
          <button
            onClick={() => navigate('/')}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
        )}

        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-lg text-gray-900">
            {title || t('common:brand')}
          </span>
        </Link>
      </div>

      <div className="flex items-center gap-2">
        {onCreateNotebook && (
          <button
            onClick={onCreateNotebook}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            {t('common:createNotebook')}
          </button>
        )}

        <div ref={langRef} className="relative">
          <button
            onClick={() => setLangOpen(!langOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Globe className="w-5 h-5 text-gray-600" />
          </button>
          {langOpen && (
            <div className="absolute right-0 mt-1 w-36 bg-white border border-gray-200 rounded-lg shadow-lg z-50 py-1">
              <button
                onClick={() => changeLang('zh-TW')}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 ${i18n.language === 'zh-TW' ? 'text-primary-600 font-semibold' : 'text-gray-700'}`}
              >
                {t('common:language.zh-TW')}
              </button>
              <button
                onClick={() => changeLang('zh-CN')}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 ${i18n.language === 'zh-CN' ? 'text-primary-600 font-semibold' : 'text-gray-700'}`}
              >
                {t('common:language.zh-CN')}
              </button>
            </div>
          )}
        </div>

        <Link
          to="/settings"
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <Settings className="w-5 h-5 text-gray-600" />
        </Link>
      </div>
    </header>
  )
}
