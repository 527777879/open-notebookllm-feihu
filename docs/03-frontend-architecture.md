# 前端架构

## 概述

前端基于 React 18 + TypeScript + Vite 5，使用 Zustand 状态管理 + TailwindCSS 样式。

## 页面与路由

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | HomePage | 首页，展示文件夹与笔记本列表 |
| `/notebook/:id` | NotebookPage | 笔记本详情页，三栏布局 |
| `/settings` | SettingsPage | AI 提供商设置页 |

**启动画面 (SplashScreen)**: 首次加载时显示 Logo + 弹跳加载动画，持续 5 秒，使用 `sessionStorage` 确保同一会话只显示一次。

## 组件层级

```
App
├── SplashScreen                     启动画面
├── BrowserRouter
│   ├── Route "/" → HomePage
│   │   ├── Header                   顶部导航栏
│   │   ├── FolderSection            文件夹区块（内部组件）
│   │   │   └── NotebookCard         笔记本卡片
│   │   ├── NotebookCard             未分类笔记本卡片
│   │   └── Modal × 2               创建笔记本 / 创建文件夹
│   │
│   ├── Route "/notebook/:id" → NotebookPage
│   │   ├── Header (showBack)
│   │   └── ThreeColumnLayout
│   │       ├── SourcePanel          左栏 - 来源管理
│   │       ├── ChatPanel            中栏 - AI 对话
│   │       └── StudioPanel          右栏 - 工作室
│   │           ├── MindmapRenderer  心智图渲染器
│   │           ├── ChartRenderer    图表渲染器
│   │           └── DiagramRenderer  Draw.io 渲染器
│   │
│   └── Route "/settings" → SettingsPage
│       └── (内联表单 UI)
```

## 页面组件详解

### HomePage (`pages/HomePage.tsx`)

首页，管理文件夹和笔记本的展示与操作。

**功能**:
- 显示所有文件夹（可展开/收起）及其内含笔记本
- 显示未分类笔记本
- 创建/删除笔记本
- 创建/编辑/删除文件夹（含 Emoji 选择器）
- 拖放操作：将笔记本拖入文件夹或拖至"未分类"

**内部组件**:
- `FolderSection`: 文件夹区块，含展开/收起 Chevron、编辑/删除按钮
- `NotebookCard`: 笔记本卡片，显示名称、来源数量、更新时间

### NotebookPage (`pages/NotebookPage.tsx`)

笔记本详情页，核心工作区。

**数据加载流程**:
```
useEffect → fetchNotebook(id)
          → fetchSources(id)
          → fetchMessages(id)
          → fetchSuggestedQuestions(id)
```

**渲染**: 三栏布局 - 来源面板 + 对话面板 + 工作室面板

### SettingsPage (`pages/SettingsPage.tsx`)

AI 提供商设置页面。此页面未使用 Zustand store，而是直接调用 API + 本地 `useState` 管理状态。

**功能**:
- 显示当前 AI 服务状态
- 选择 AI 提供商（6 种）
- 输入 API Key
- 选择模型（动态获取）
- 测试 API 连线
- 保存设置

## 布局组件

### Header (`components/layout/Header.tsx`)

全局顶部导航栏。

**Props**:
- `title?`: 页面标题（默认 "NoteBookLLM"）
- `showBack?`: 是否显示返回按钮
- `onCreateNotebook?`: 创建笔记本回调

**元素**: Logo + 标题 / 返回按钮 + 创建按钮 + 设置链接

### ThreeColumnLayout (`components/layout/ThreeColumnLayout.tsx`)

可调整宽度的三栏布局。

**默认宽度**:
- 左栏: 280px（范围 200-500px）
- 右栏: 320px（范围 250-500px）
- 中栏最小 400px

**交互**: 左右分隔线可拖拽调整宽度

## 通用组件

### Button (`components/common/Button.tsx`)

使用 `forwardRef` 的可复用按钮组件。

**Props**:
- `variant`: `'primary' | 'secondary' | 'ghost' | 'danger'`
- `size`: `'sm' | 'md' | 'lg'`
- `loading`: 显示 Loader2 旋转图标

### Input (`components/common/Input.tsx`)

使用 `forwardRef` 的输入框组件。

**Props**: `error?` 错误信息字符串

### Modal (`components/common/Modal.tsx`)

模态对话框组件。

**Props**: `isOpen`, `onClose`, `title?`, `children`, `size?`（sm/md/lg）

**特性**: ESC 键关闭、点击遮罩关闭、锁定背景滚动、fade-in + slide-up 动画

### Loading (`components/common/Loading.tsx`)

加载指示器。**Props**: `fullscreen?`, `message?`, `className?`

### SplashScreen (`components/common/SplashScreen.tsx`)

启动画面。**Props**: `duration?`（默认 3000ms）, `onComplete`

## 业务组件

### SourcePanel (`components/source/SourcePanel.tsx`)

来源管理面板（左栏）。

**功能**:
- 搜索来源（按名称/URL 过滤）
- 按类型筛选（全部/PDF/Text/Web/YouTube/GDocs/音频）
- 多选来源（全选/取消全选）
- 5 种新增来源方式：文件上传、音频上传（可选 STT 提供商和语言）、URL、YouTube、纯文字

**图标映射**: PDF→FileText, Text→File, Web→Globe, YouTube→Youtube, GDocs→FileText, Audio→Music

### ChatPanel (`components/chat/ChatPanel.tsx`)

AI 对话面板（中栏）。

**功能**:
- 对话历史展示（用户消息 + AI 回复）
- SSE 串流消息实时显示
- Markdown 渲染（react-markdown + remark-gfm）
- 建议问题快捷按钮
- 导出对话为 Markdown 文件
- 每条 AI 消息：来源引用、复制、点赞/倒赞、收藏

**流式消息处理流程**:
```
用户输入 → sendStreamMessage(notebookId, message, selectedSourceIds)
        → chatApi.streamMessage (SSE)
        → onChunk → streamingContent 更新
        → onSources → currentSourceRefs 更新
        → onDone → 生成完整 assistantMessage
```

### StudioPanel (`components/studio/StudioPanel.tsx`)

工作室面板（右栏），核心功能最丰富的组件。

**12 种工作室工具**:

| 类型 | 标签 | 颜色 |
|------|------|------|
| summary | 语音摘要 | 紫色 |
| summary | 影片摘要 | 蓝色 |
| mindmap | 心智图 | 绿色 |
| flowchart | 流程图 | 青色 |
| diagram | 架构图 | 紫罗兰 |
| report | 报告 | 橙色 |
| flashcards | 学习卡 | 粉色 |
| quiz | 测验 | 青色 |
| infographic | 资讯图表 | 黄色 |
| presentation | 简报 | 靛蓝色 |
| datatable | 资料表 | 灰色 |
| podcast | Podcast | 红色 |

**子 Modal**:
- Podcast 设置 Modal: 选择对谈风格、时长、讲者设定、是否生成音频
- 难度选择 Modal: 用于学习卡和测验，可选数量和难度

**结果渲染**:
- `summary` / `report`: 纯文本
- `flashcards`: 卡片列表，含难度标签、分类标签、认知层次、提示
- `quiz`: 题目列表，5 种题型，含解释/提示/分数
- `mindmap` → `MindmapRenderer`
- `flowchart` / `diagram` → `DiagramRenderer`
- `podcast`: 脚本对话格式 + 音频播放器
- `presentation`: 幻灯片卡片列表
- `infographic` → `ChartRenderer`
- `datatable`: HTML 表格

### MindmapRenderer (`components/studio/MindmapRenderer.tsx`)

使用 Mermaid.js 渲染心智图。

**功能**: 缩放控制(40%-200%)、复制 Mermaid 代码、下载 SVG、渲染失败回退文本视图、节点统计

### ChartRenderer (`components/studio/ChartRenderer.tsx`)

使用 Chart.js 渲染数据可视化图表。

**支持类型**: Bar, Line, Pie, Doughnut, Radar, PolarArea, Scatter

**功能**: AI 生成图片、图表网格、每个图表含标题/描述/洞察、总结区块

### DiagramRenderer (`components/studio/DiagramRenderer.tsx`)

使用 react-drawio 嵌入 Draw.io 编辑器。

**功能**: 编辑/查看模式切换、复制 XML、下载 SVG、全屏模式、图表元素信息展示

## 状态管理 (Zustand)

4 个独立 Store，通过 `store/index.ts` 统一导出。

### notebookStore

```typescript
{
  notebooks: Notebook[]
  currentNotebook: Notebook | null
  isLoading: boolean
  error: string | null
}
```

**操作**: `fetchNotebooks`, `createNotebook`, `fetchNotebook`, `updateNotebook`, `deleteNotebook`, `setCurrentNotebook`, `clearError`

### folderStore

```typescript
{
  folders: Folder[]
  uncategorizedNotebooks: Notebook[]
  isLoading: boolean
  error: string | null
}
```

**操作**: `fetchFoldersWithNotebooks`, `createFolder`, `updateFolder`, `deleteFolder`, `toggleFolderExpand`, `moveNotebookToFolder`, `reorderFolders`

### sourceStore

```typescript
{
  sources: Source[]
  selectedIds: string[]
  filterType: SourceType | 'all'
  searchQuery: string
  isLoading: boolean
  isUploading: boolean
  error: string | null
}
```

**操作**: `fetchSources`, `uploadFile`, `addUrl`, `addYoutube`, `addText`, `deleteSource`, `toggleSelection`, `selectAll`, `clearSelection`, `setFilter`, `setSearchQuery`, `getFilteredSources`, `getSelectedSources`

### chatStore

```typescript
{
  messages: ChatMessage[]
  isLoading: boolean
  isStreaming: boolean
  streamingContent: string
  suggestedQuestions: string[]
  currentSourceRefs: SourceReference[]
  error: string | null
}
```

**操作**: `fetchMessages`, `sendMessage`, `sendStreamMessage`, `fetchSuggestedQuestions`, `deleteMessage`, `clearMessages`, `clearError`

## API 层

### client.ts - Axios 实例

- 基础 URL: 空（由 Vite 代理处理）
- 超时: 300 秒（5 分钟，AI 生成可能较慢）
- 请求拦截器: FormData 时自动移除 Content-Type
- 响应拦截器: 统一错误日志

### 各模块 API

| 模块 | 文件 | 端点前缀 |
|------|------|---------|
| 笔记本 | `api/notebooks.ts` | `/api/notebooks` |
| 文件夹 | `api/folders.ts` | `/api/folders` |
| 来源 | `api/sources.ts` | `/api/notebooks/:id/sources` |
| 对话 | `api/chat.ts` | `/api/notebooks/:id/chats` |
| 工作室 | `api/studio.ts` | `/api/notebooks/:id/studio` |
| 设置 | `api/settings.ts` | `/api/settings` |

**SSE 协议**: `chat.ts` 中的 `streamMessage` 使用原生 `fetch` + `ReadableStream`，支持 4 种事件类型: `chunk`, `sources`, `done`, `error`

## 类型系统 (`types/index.ts`)

共 36 个接口/类型，主要分类：

### 数据模型
- `Folder`, `Notebook`, `Source`, `ChatMessage`, `SourceReference`, `Note`, `StudioOutput`

### 工作室输出
- `MindmapData` / `MindmapBranch`
- `FlashcardsData` / `Flashcard` / `FlashcardsMetadata`
- `QuizData` / `QuizQuestion` / `QuizMetadata`
- `InfographicData` / `ChartConfig` / `ChartDataset`
- `PodcastData` / `PodcastScript` / `PodcastSegment` / `PodcastSpeaker` / `PodcastVoice` / `PodcastStyle`
- `DiagramData` / `DiagramElement`

### AI 配置
- `AIProvider` (联合类型), `AIProviderInfo`, `Settings`, `ProvidersResponse`

### 搜索
- `SearchResult`, `SearchResponse`

### 通用
- `ApiResponse<T>`, `TTSRequest`, `TTSResponse`

## 样式方案

### Tailwind CSS 配置

**自定义颜色**:
- `primary`: Indigo 色系（50-900），主色调 `#4F46E5`
- `surface`: 背景色系（primary: `#F8FAFC`, secondary: `#FFFFFF`, tertiary: `#F1F5F9`）

**自定义圆角**: `card` (12px), `panel` (16px)

**自定义阴影**: `soft`, `card`, `hover`（hover 含 primary 色调）

**自定义动画**: `fade-in`, `slide-up`, `pulse-slow`

**插件**: `@tailwindcss/typography`

### 全局样式 (`index.css`)

- 自定义滚动条（6px 宽，圆角）
- `.panel`: 白色背景 + 圆角 + 阴影
- `.card`: 白色背景 + hover 阴影变化
- `.btn` / `.btn-primary` / `.btn-secondary` / `.btn-ghost`: 按钮样式
- `.input`: 输入框样式
- `.animate-shimmer`: 骨架屏闪光动画
- `.markdown-content`: Markdown 内容样式（prose + 自定义覆盖）

### 工具函数 (`utils/cn.ts`)

```typescript
cn(...inputs)  // = twMerge(clsx(inputs))  合并 Tailwind 类名
```

## 数据流模式

```
React Component
    │
    ├── 调用 Zustand Store action
    │       │
    │       └── Store 调用 API 函数 (api/*.ts)
    │               │
    │               └── Axios → 后端 API
    │
    └── Store 更新 → Component 重渲染
```

### 特殊模式

1. **Store 驱动**: 大部分数据通过 Zustand Store 管理
2. **API 层分离**: 每个 API 模块独立
3. **乐观更新**: 创建操作先更新 UI，后端响应后替换
4. **SettingsPage 本地管理**: 直接 API 调用 + 本地 useState
5. **流式对话**: SSE 串流 + `streamingContent` 临时状态
