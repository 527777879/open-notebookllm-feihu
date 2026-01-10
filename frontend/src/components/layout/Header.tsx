import { Link, useNavigate } from 'react-router-dom'
import { BookOpen, Settings, Plus, ArrowLeft } from 'lucide-react'

interface HeaderProps {
  title?: string
  showBack?: boolean
  onCreateNotebook?: () => void
}

export default function Header({ title, showBack, onCreateNotebook }: HeaderProps) {
  const navigate = useNavigate()

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
            {title || 'NoteBookLLM'}
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
            建立筆記本
          </button>
        )}

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
