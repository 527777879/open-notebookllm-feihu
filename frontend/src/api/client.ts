import axios from 'axios'

// 建立 Axios 實例
const apiClient = axios.create({
  baseURL: '',
  timeout: 300000, // 5 分鐘超時（AI 生成可能較慢）
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    // FormData 時移除 Content-Type，讓瀏覽器自動設置
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 回應攔截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // 統一錯誤處理
    if (error.response) {
      // 伺服器回應錯誤
      console.error('API Error:', error.response.data)
    } else if (error.request) {
      // 請求發送失敗
      console.error('Network Error:', error.message)
    } else {
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient
