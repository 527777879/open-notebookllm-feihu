import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import NotebookPage from './pages/NotebookPage'
import SettingsPage from './pages/SettingsPage'
import SplashScreen from './components/common/SplashScreen'

function App() {
  const [showSplash, setShowSplash] = useState(true)
  const [hasShownSplash, setHasShownSplash] = useState(false)

  // 檢查是否已經顯示過啟動畫面（同一個 session）
  useEffect(() => {
    const splashShown = sessionStorage.getItem('splashShown')
    if (splashShown) {
      setShowSplash(false)
      setHasShownSplash(true)
    }
  }, [])

  const handleSplashComplete = () => {
    setShowSplash(false)
    setHasShownSplash(true)
    sessionStorage.setItem('splashShown', 'true')
  }

  return (
    <>
      {showSplash && !hasShownSplash && (
        <SplashScreen duration={5000} onComplete={handleSplashComplete} />
      )}
      <div className={showSplash && !hasShownSplash ? 'invisible' : 'visible'}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/notebook/:id" element={<NotebookPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </BrowserRouter>
      </div>
    </>
  )
}

export default App
