import { Loader2 } from 'lucide-react'
import { cn } from '@/utils/cn'

interface LoadingProps {
  fullscreen?: boolean
  message?: string
  className?: string
}

export default function Loading({ fullscreen, message, className }: LoadingProps) {
  if (fullscreen) {
    return (
      <div className="fixed inset-0 bg-white/80 flex items-center justify-center z-50">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
          {message && (
            <p className="text-gray-600">{message}</p>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className={cn('flex items-center justify-center p-8', className)}>
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
        {message && (
          <p className="text-sm text-gray-600">{message}</p>
        )}
      </div>
    </div>
  )
}
