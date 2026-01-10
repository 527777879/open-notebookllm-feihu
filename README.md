# Open NotebookLLM

開源版 NotebookLM 複刻專案，支援多種 AI 提供商，具備 RAG 檢索、Podcast 生成、語音轉文字等功能。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)

## 功能特色

- **多 AI 提供商支援**：Gemini、OpenAI、Anthropic、Ollama、Groq、DeepSeek
- **RAG 智能問答**：基於上傳文件的智能對話
- **多格式來源支援**：PDF、Word、Excel、網頁、YouTube、音檔
- **Podcast 生成**：多人對話播客，支援 TTS 語音合成
- **工作室功能**：摘要、心智圖、學習卡、測驗、簡報、資訊圖表
- **AI 配圖**：簡報和資訊圖表支援 AI 自動生成配圖
- **混合搜尋**：全文搜尋 + 向量語意搜尋

---

## 環境需求

| 項目 | 版本 |
|------|------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |
| FFmpeg | 可選，用於音檔處理 |

---

## 快速開始

### 步驟 1：Clone 專案

```bash
git clone https://github.com/ChatGPT3a01/open-notebookllm.git
cd open-notebookllm
```

### 步驟 2：設定環境變數

```bash
# Windows
copy .env.example backend\.env

# macOS/Linux
cp .env.example backend/.env
```

編輯 `backend/.env` 檔案，填入 API Key：

```env
# 選擇 AI Provider (gemini / openai / anthropic / ollama / groq / deepseek)
AI_PROVIDER=gemini

# ===== Gemini 設定 =====
GEMINI_API_KEY=你的-Gemini-API-Key
GEMINI_MODEL=gemini-2.0-flash

# ===== OpenAI 設定 =====
OPENAI_API_KEY=你的-OpenAI-API-Key
OPENAI_MODEL=gpt-4o

# ===== Anthropic 設定 =====
ANTHROPIC_API_KEY=你的-Anthropic-API-Key
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ===== Ollama 設定（本地模型，無需 API Key）=====
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# ===== Groq 設定 =====
GROQ_API_KEY=你的-Groq-API-Key
GROQ_MODEL=llama-3.3-70b-versatile

# ===== DeepSeek 設定 =====
DEEPSEEK_API_KEY=你的-DeepSeek-API-Key
DEEPSEEK_MODEL=deepseek-chat
```

**取得 API Key：**
| 提供商 | 申請連結 |
|--------|----------|
| Gemini | https://aistudio.google.com/app/apikey |
| OpenAI | https://platform.openai.com/api-keys |
| Anthropic | https://console.anthropic.com/settings/keys |
| Ollama | https://ollama.ai/download （本地安裝，無需 API Key） |
| Groq | https://console.groq.com/keys |
| DeepSeek | https://platform.deepseek.com/api_keys |

### 步驟 3：安裝後端依賴

```bash
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 步驟 4：安裝前端依賴

開啟**新的終端機視窗**：

```bash
cd frontend
npm install
```

### 步驟 5：啟動應用程式

**啟動後端**（在 backend 目錄，虛擬環境已啟動）：
```bash
python app.py
```
後端運行於 http://localhost:5000

**啟動前端**（在另一個終端機，frontend 目錄）：
```bash
npm run dev
```
前端運行於 http://localhost:5173

### 步驟 6：開始使用

1. 開啟瀏覽器訪問 `http://localhost:5173`
2. 建立筆記本
3. 新增來源（上傳文件、貼上網址、YouTube 連結等）
4. 與 AI 對話，AI 會根據來源內容回答
5. 使用工作室生成摘要、心智圖、Podcast 等

---

## AI 提供商比較

| 提供商 | 特色 | 嵌入向量 | 圖片生成 | 需要 API Key |
|--------|------|:--------:|:--------:|:------------:|
| **Gemini** | Google 多模態模型 | ✅ | ✅ | 是 |
| **OpenAI** | GPT-4o/4.1 + DALL-E 3 | ✅ | ✅ | 是 |
| **Anthropic** | Claude Sonnet/Opus 長上下文 | ❌* | ❌ | 是 |
| **Ollama** | 本地模型，免費無限使用 | ✅ | ❌ | 否 |
| **Groq** | 超高速推理 | ❌* | ❌ | 是 |
| **DeepSeek** | R1 推理模型 | ❌* | ❌ | 是 |

> *不支援嵌入向量的提供商會自動使用備援提供商

---

## 支援的來源類型

| 類型 | 說明 | 檔案格式 |
|------|------|----------|
| PDF | PDF 文件 | `.pdf` |
| Text | 純文字文件 | `.txt`, `.md` |
| Word | Word 文件 | `.docx`, `.doc` |
| Excel | 試算表 | `.xlsx`, `.xls`, `.csv` |
| Web | 網頁連結 | URL |
| YouTube | YouTube 影片字幕 | YouTube URL |
| 音檔 | 語音轉文字 (STT) | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.webm` |

---

## 工作室輸出類型

| 類型 | 說明 | AI 配圖 |
|------|------|:-------:|
| 摘要 | 來源內容摘要 | - |
| 心智圖 | 視覺化概念關聯圖 | - |
| 報告 | 結構化報告文件 | - |
| 學習卡 | 問答學習卡片 | - |
| 測驗 | 選擇題測驗 | - |
| 資訊圖表 | 數據視覺化 | ✅ |
| 簡報 | 簡報大綱 + 配圖 | ✅ |
| **Podcast** | 多人對話播客 (1-4 人) | - |

---

## 可選：安裝 FFmpeg（音檔處理）

### Windows

1. 下載 [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases)（選擇 `ffmpeg-master-latest-win64-gpl.zip`）
2. 解壓縮到 `C:\ffmpeg`
3. 將 `C:\ffmpeg\bin` 加入系統 PATH
4. 驗證安裝：`ffmpeg -version`

### macOS

```bash
brew install ffmpeg
```

### Linux

```bash
sudo apt install ffmpeg
```

---

## 專案結構

```
open-notebookllm/
├── backend/                    # Flask 後端 (Python)
│   ├── app.py                 # 應用入口
│   ├── config.py              # 配置管理
│   ├── requirements.txt       # Python 依賴
│   ├── models/                # 資料庫模型
│   ├── services/              # 商業邏輯服務
│   │   ├── ai_providers/      # AI Provider 抽象層
│   │   ├── rag_service.py     # RAG 檢索服務
│   │   ├── podcast_service.py # Podcast 生成
│   │   └── studio_service.py  # 工作室輸出生成
│   └── controllers/           # API 端點控制器
│
├── frontend/                   # React 前端 (TypeScript)
│   ├── src/
│   │   ├── pages/             # 頁面元件
│   │   ├── components/        # UI 元件
│   │   ├── store/             # Zustand 狀態管理
│   │   └── api/               # API 客戶端
│   ├── package.json
│   └── vite.config.ts
│
├── uploads/                    # 上傳檔案儲存目錄
└── .env.example               # 環境變數範本
```

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端框架 | Flask 3.0 |
| 資料庫 | SQLite + SQLAlchemy + FTS5 |
| 前端框架 | React 18 + TypeScript |
| 建置工具 | Vite |
| 樣式 | TailwindCSS |
| 狀態管理 | Zustand |
| AI 文字 API | Gemini / OpenAI / Anthropic / Ollama / Groq / DeepSeek |
| AI 圖片 API | Gemini 多模態 / DALL-E 3 |
| 語音轉文字 | OpenAI Whisper / Groq Whisper |
| 文字轉語音 | OpenAI TTS / Google Cloud TTS |

---

## 常見問題

### Q: 後端啟動時出現 ModuleNotFoundError？
**A:** 確保已在虛擬環境中執行 `pip install -r requirements.txt`。

### Q: 前端無法連接後端？
**A:** 確認後端正在 `http://localhost:5000` 運行。

### Q: API Key 無效？
**A:**
1. 確認 `.env` 檔案位於 `backend/` 目錄中
2. 在設定頁面使用「測試連線」功能驗證

### Q: Ollama 無法連線？
**A:**
1. 確認 Ollama 服務已啟動：`ollama serve`
2. 確認模型已下載：`ollama pull llama3.2`

---

## 開發指令

```bash
# 後端開發模式（自動重載）
cd backend && flask run --debug

# 前端開發模式
cd frontend && npm run dev

# 前端建置生產版本
cd frontend && npm run build
```

---

## 授權

本專案採用 MIT 授權，僅供學習和個人使用。

