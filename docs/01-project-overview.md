# Open NotebookLLM - 项目概览

## 项目简介

Open NotebookLLM 是一个开源的 Google NotebookLM 复刻项目，支持多种 AI 提供商，具备 RAG 检索增强生成、Podcast 生成、语音转文字、工作室内容生成等功能。

- **项目仓库**: `https://github.com/ChatGPT3a01/open-notebookllm.git`
- **作者**: 阿亮老师
- **授权**: 仅供课程学员学习使用，禁止修改、转传、商业使用
- **界面语言**: 繁体中文

## 核心功能

- **笔记本管理**: 创建、编辑、删除笔记本，支持文件夹分类和排序
- **多格式来源**: 支持 PDF、TXT、DOCX、XLSX、CSV、网页、YouTube、音频等多种来源
- **RAG 智能问答**: 基于来源内容的 AI 对话，支持 SSE 串流响应
- **混合搜索**: FTS5 全文搜索 + 向量语义搜索 + RRF 融合
- **工作室输出**: 11 种 AI 生成内容（摘要/心智图/学习卡/测验/报告/简报/播客等）
- **Podcast 生成**: 多人对谈播客，6 种对话风格，支持 TTS 语音合成
- **多 AI 提供商**: Gemini / OpenAI / Anthropic / Ollama / Groq / DeepSeek

## 技术栈

### 后端

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| Web 框架 | Flask | 3.0.0 | HTTP API 服务器 |
| CORS | Flask-CORS | 4.0.0 | 跨域资源共享 |
| ORM | Flask-SQLAlchemy | 3.1.1 | 数据库 ORM |
| 数据库迁移 | Flask-Migrate | 4.0.5 | 数据库迁移管理 |
| 数据库 | SQLite + FTS5 | - | 关系数据库 + 全文搜索 |
| 环境变量 | python-dotenv | 1.0.0 | .env 文件加载 |
| AI - Google | google-generativeai / google-genai | >=0.3.0 / >=1.0.0 | Gemini API |
| AI - OpenAI | openai | >=1.0.0 | GPT-4o/DALL-E/Whisper/TTS |
| AI - Anthropic | anthropic | >=0.39.0 | Claude API |
| AI - Ollama | ollama | >=0.1.0 | 本地模型 |
| AI - Groq | groq | >=0.4.0 | 高速推理 |
| AI - DeepSeek | (via openai compat) | - | 推理模型 |
| 文档解析 | PyPDF2, python-docx, openpyxl, python-pptx | - | PDF/Word/Excel/PPTX |
| 网页抓取 | beautifulsoup4, trafilatura, requests | - | 网页内容提取 |
| YouTube | youtube-transcript-api, yt-dlp | - | 字幕提取 |
| 音频 | pydub, edge-tts | - | 音频处理与 TTS |
| 向量计算 | numpy | >=1.26.0 | 向量相似度计算 |
| 重试 | tenacity | >=8.2.0 | API 调用重试 |
| 数据验证 | pydantic | >=2.0.0 | 数据校验 |
| 图片 | Pillow | >=10.0.0 | 图片处理 |
| 生产部署 | gunicorn | >=21.0.0 | WSGI 服务器 |

### 前端

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| UI 框架 | React | 18.2.0 | 组件化 UI |
| 语言 | TypeScript | 5.2.2 | 类型安全 |
| 构建工具 | Vite | 5.1.4 | 开发服务器 + 构建 |
| 路由 | react-router-dom | 6.22.0 | 客户端路由 |
| 状态管理 | Zustand | 4.5.0 | 全局状态 |
| HTTP 客户端 | Axios | 1.6.7 | API 请求 |
| 样式 | TailwindCSS | 3.4.1 | 原子化 CSS |
| 图标 | lucide-react | 0.336.0 | 图标库 |
| Markdown | react-markdown + remark-gfm | 9.0.1 / 4.0.0 | Markdown 内容展示 |
| 心智图 | Mermaid.js | 10.9.0 | Mermaid 图表渲染 |
| 图表 | Chart.js + react-chartjs-2 | 4.5.1 / 5.3.1 | 数据可视化 |
| 流程图 | react-drawio | 1.0.7 | Draw.io 图表编辑 |
| 工具 | clsx + tailwind-merge | 2.1.0 / 2.2.1 | 类名合并 |

## 目录结构

```
open-notebookllm/
├── .env.example                    # 环境变量模板
├── .gitignore                      # Git 忽略规则
├── README.md                       # 项目说明
├── logo.jpg                        # 项目 Logo
├── 啟動指南.md                      # 启动指南
│
├── backend/                        # Flask 后端 (Python)
│   ├── .env                        # 后端环境变量
│   ├── app.py                      # Flask 应用入口
│   ├── config.py                   # 配置管理
│   ├── requirements.txt            # Python 依赖
│   ├── instance/
│   │   └── database.db             # SQLite 数据库
│   ├── models/                     # 数据库模型层
│   │   ├── __init__.py             # 模型导出与 SQLAlchemy 初始化
│   │   ├── folder.py               # 资料夹模型
│   │   ├── notebook.py             # 笔记本模型
│   │   ├── source.py               # 来源模型
│   │   ├── embedding.py            # 向量嵌入模型
│   │   ├── chat_message.py         # 对话消息模型
│   │   ├── note.py                 # 笔记模型
│   │   └── studio_output.py        # 工作室输出模型
│   ├── controllers/                # API 路由控制器层
│   │   ├── __init__.py             # Blueprint 注册
│   │   ├── notebook_controller.py  # 笔记本 CRUD
│   │   ├── folder_controller.py    # 资料夹 CRUD + 排序
│   │   ├── source_controller.py    # 来源管理 + 搜索
│   │   ├── chat_controller.py      # 对话 + SSE 串流
│   │   ├── studio_controller.py    # 工作室输出 + Podcast + TTS
│   │   ├── note_controller.py      # 笔记 CRUD
│   │   └── settings_controller.py  # AI 提供商设置
│   ├── services/                   # 业务逻辑服务层
│   │   ├── __init__.py             # 服务导出
│   │   ├── ai_service_manager.py   # AI 服务管理器（核心中枢）
│   │   ├── ai_providers/           # AI Provider 抽象层
│   │   │   ├── __init__.py         # Provider 导出 + 映射表
│   │   │   ├── base_provider.py    # 抽象基类（Text/Embedding/Image）
│   │   │   ├── gemini_provider.py  # Google Gemini
│   │   │   ├── openai_provider.py  # OpenAI
│   │   │   ├── anthropic_provider.py # Anthropic Claude
│   │   │   ├── ollama_provider.py  # Ollama 本地模型
│   │   │   ├── groq_provider.py    # Groq 高速推理
│   │   │   └── deepseek_provider.py # DeepSeek 推理
│   │   ├── rag_service.py          # RAG 检索增强生成服务
│   │   ├── search_service.py       # 混合搜索服务
│   │   ├── studio_service.py       # 工作室输出生成服务
│   │   ├── podcast_service.py      # Podcast 播客生成服务
│   │   ├── audio_service.py        # 语音服务（STT + TTS）
│   │   ├── file_parser_service.py  # 文件解析服务
│   │   ├── web_scraper_service.py  # 网页抓取服务
│   │   ├── youtube_service.py      # YouTube 字幕提取服务
│   │   └── prompts.py             # 提示词模板
│   └── utils/
│       ├── __init__.py
│       └── pptx_builder.py         # PPTX 文件生成工具
│
├── frontend/                        # React 前端 (TypeScript)
│   ├── index.html                  # HTML 入口
│   ├── package.json                # NPM 依赖
│   ├── vite.config.ts              # Vite 配置（含代理）
│   ├── tailwind.config.js          # TailwindCSS 配置
│   ├── postcss.config.js           # PostCSS 配置
│   ├── tsconfig.json               # TypeScript 配置
│   ├── public/
│   │   ├── favicon.svg             # 网站图标
│   │   └── logo.jpg                # Logo 图片
│   └── src/
│       ├── main.tsx                # React 入口
│       ├── App.tsx                 # 根组件 + 路由
│       ├── index.css               # 全局样式
│       ├── api/                    # API 客户端层
│       │   ├── client.ts           # Axios 实例配置
│       │   ├── notebooks.ts        # 笔记本 API
│       │   ├── folders.ts          # 资料夹 API
│       │   ├── sources.ts          # 来源 API
│       │   ├── chat.ts             # 对话 API
│       │   ├── studio.ts           # 工作室 + Podcast + TTS API
│       │   └── settings.ts         # 设置 API
│       ├── pages/                  # 页面组件
│       │   ├── HomePage.tsx        # 首页
│       │   ├── NotebookPage.tsx    # 笔记本详情页（三栏布局）
│       │   └── SettingsPage.tsx    # 设置页
│       ├── components/             # UI 组件
│       │   ├── chat/ChatPanel.tsx  # 对话面板
│       │   ├── common/             # 通用组件
│       │   ├── layout/             # 布局组件
│       │   ├── source/SourcePanel.tsx # 来源面板
│       │   └── studio/             # 工作室面板及渲染器
│       ├── store/                  # Zustand 状态管理
│       │   ├── index.ts           # Store 导出
│       │   ├── notebookStore.ts   # 笔记本 Store
│       │   ├── folderStore.ts     # 资料夹 Store
│       │   ├── sourceStore.ts     # 来源 Store
│       │   └── chatStore.ts       # 对话 Store
│       ├── types/index.ts         # TypeScript 类型定义
│       └── utils/cn.ts            # Tailwind 类名合并工具
│
├── uploads/                        # 上传文件存储目录
└── docs/                           # 文档目录
```

## 整体架构

```
┌───────────────────────────────────────────────────────────┐
│                    前端 (React + Vite)                      │
│                                                             │
│  HomePage ──┐                                               │
│  NotebookPage ──┤── Zustand Stores ── API Client (Axios)   │
│  SettingsPage ─┘                                             │
└─────────────────────────┬─────────────────────────────────┘
                          │ HTTP / SSE
                          ▼
┌───────────────────────────────────────────────────────────┐
│                 后端 (Flask + SQLAlchemy)                   │
│                                                             │
│  Controllers (Blueprints)                                   │
│       │                                                     │
│       ▼                                                     │
│  Services Layer                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │  AIServiceManager (中枢)                          │       │
│  │    text_provider / embedding_provider /            │       │
│  │    image_provider                                  │       │
│  │  ┌───────────────────────────────────────────┐   │       │
│  │  │  AI Providers (抽象层)                      │   │       │
│  │  │  Gemini | OpenAI | Anthropic | Ollama       │   │       │
│  │  │  Groq | DeepSeek                            │   │       │
│  │  └───────────────────────────────────────────┘   │       │
│  │  RAGService | SearchService | StudioService       │       │
│  │  PodcastService | AudioService | FileParser...    │       │
│  └─────────────────────┬───────────────────────────┘       │
│                          │                                  │
│  Models (SQLAlchemy) ────┼──── SQLite + FTS5                │
└───────────────────────────────────────────────────────────┘
```

## 入口点与启动

### 后端

- **入口文件**: `backend/app.py`
- **启动命令**: `python app.py`
- **默认端口**: 5000
- **启动方式**: `create_app()` 工厂模式

### 前端

- **入口文件**: `frontend/src/main.tsx`
- **启动命令**: `npm run dev`
- **默认端口**: 3000
- **API 代理**: Vite 将 `/api` 和 `/health` 请求代理至 `http://localhost:5000`

### 路由

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | HomePage | 首页（笔记本和资料夹管理） |
| `/notebook/:id` | NotebookPage | 笔记本详情页（三栏布局） |
| `/settings` | SettingsPage | AI 提供商设置页 |

## 关键配置文件

| 文件 | 说明 |
|------|------|
| `.env.example` | 所有环境变量说明模板 |
| `backend/.env` | 实际使用的后端环境变量 |
| `backend/config.py` | Config/DevelopmentConfig/ProductionConfig/TestingConfig |
| `frontend/vite.config.ts` | 端口、代理、别名 |
| `frontend/tailwind.config.js` | 主题色、圆角、阴影、动画 |
| `frontend/tsconfig.json` | TS 编译选项 |
| `backend/requirements.txt` | 所有 Python 包 |
| `frontend/package.json` | 所有 NPM 包 |

## 设计模式

1. **全局单例模式**: 所有 Service 使用模块级全局变量 + getter 函数（`_instance` + `get_xxx_service()`）
2. **Provider 抽象层**: ABC 抽象基类定义 Text/Embedding/Image 三种 Provider 接口
3. **Embedding Fallback**: 不支持 embedding 的 Provider 自动按优先级 OpenAI -> Gemini -> Ollama 降级
4. **混合搜索策略**: RRF (Reciprocal Rank Fusion) 融合全文搜索和向量搜索结果
5. **SSE 串流**: 对话功能使用 Server-Sent Events 实时返回 AI 生成内容
6. **三栏布局**: 笔记本页面使用 ThreeColumnLayout（来源/对话/工作室）
7. **Vite 代理**: 开发模式下避免 CORS 问题
