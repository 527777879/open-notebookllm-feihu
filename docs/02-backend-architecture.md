# 后端架构

## 概述

后端基于 Flask 3.0，采用经典的 MVC 分层架构：

```
Controllers (路由层) → Services (业务逻辑层) → Models (数据模型层)
```

## 分层架构详解

### 1. 控制器层 (`controllers/`)

所有控制器使用 Flask Blueprint 注册，在 `controllers/__init__.py` 中统一注册到 Flask App。

| 控制器 | Blueprint 名 | URL 前缀 | 职责 |
|--------|-------------|----------|------|
| notebook_controller | `notebooks` | `/api/notebooks` | 笔记本 CRUD |
| folder_controller | `folders` | `/api/folders` | 资料夹 CRUD + 排序 |
| source_controller | `sources` | `/api/notebooks/<id>/sources` | 来源管理 + 搜索 |
| chat_controller | `chats` | `/api/notebooks/<id>/chats` | 对话 + SSE 串流 |
| studio_controller | `studio` | `/api/notebooks/<id>/studio` | 工作室输出 + Podcast + TTS |
| note_controller | `notes` | `/api/notebooks/<id>/notes` | 笔记 CRUD |
| settings_controller | `settings` | `/api/settings` | AI 提供商设置 |

### 2. 服务层 (`services/`)

业务逻辑核心，采用单例模式管理。

| 服务 | 文件 | 职责 |
|------|------|------|
| AIServiceManager | `ai_service_manager.py` | AI 提供商管理中枢 |
| RAGService | `rag_service.py` | RAG 检索增强生成 |
| SearchService | `search_service.py` | 混合搜索（全文+向量+RRF） |
| StudioService | `studio_service.py` | 工作室输出生成 |
| PodcastService | `podcast_service.py` | Podcast 播客生成 |
| AudioService | `audio_service.py` | 语音服务（STT + TTS） |
| FileParserService | `file_parser_service.py` | 文件解析 |
| WebScraperService | `web_scraper_service.py` | 网页抓取 |
| YouTubeService | `youtube_service.py` | YouTube 字幕提取 |

**单例模式实现方式**:

```python
_ai_service = None

def get_ai_service() -> AIServiceManager:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIServiceManager()
    return _ai_service
```

### 3. 模型层 (`models/`)

使用 SQLAlchemy ORM，7 个数据表 + 1 个 FTS5 虚拟表。详见 [数据模型文档](./04-data-models.md)。

## 应用入口 (`app.py`)

使用工厂模式创建 Flask 应用：

```python
def create_app(config_name=None):
    app = Flask(__name__)

    # 1. 加载配置
    app.config.from_object(config[config_name or 'development'])

    # 2. 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # 3. 注册蓝图
    from controllers import register_blueprints
    register_blueprints(app)

    # 4. 全局错误处理
    @app.errorhandler(404)
    @app.errorhandler(500)

    # 5. 系统路由
    @app.route('/')
    @app.route('/health')

    return app
```

## 配置管理 (`config.py`)

三环境配置体系：

| 环境 | 类 | 数据库 | DEBUG |
|------|-----|--------|-------|
| 开发 | DevelopmentConfig | SQLite 文件 | True |
| 生产 | ProductionConfig | SQLite 文件 | False |
| 测试 | TestingConfig | SQLite :memory: | False |

关键配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `AI_PROVIDER` | gemini | 预设 AI 提供商 |
| `CHUNK_SIZE` | 1000 | RAG 文本分块大小 |
| `CHUNK_OVERLAP` | 200 | 分块重叠字符数 |
| `TOP_K_RESULTS` | 5 | RAG 检索返回数量 |
| `MAX_CONTENT_LENGTH` | 52428800 | 上传文件大小限制 (50MB) |
| `CORS_ORIGINS` | localhost:3000,5173 | 允许的前端来源 |

## 中间件与安全

### CORS

通过 `flask-cors` 配置，限制来源为 `http://localhost:3000` 和 `http://localhost:5173`。

### 文件上传限制

- 最大 50MB (`MAX_CONTENT_LENGTH`)
- 仅允许特定文件扩展名

### 全局错误处理

404 和 500 错误统一返回 JSON 格式。

### 当前缺少的安全措施

- 无用户认证/授权
- 无 API Key 认证
- 无速率限制
- 无输入验证框架

## 异步与串流处理

项目没有使用专门的背景任务框架（如 Celery/RQ），所有 AI 调用都是同步阻塞的。

现有的串流/异步处理方式：

1. **SSE 串流对话**: 使用 `stream_with_context` 实现 Server-Sent Events
2. **串流 TTS**: 使用 Response 生成器串流输出音讯
3. **Edge TTS 异步**: 使用 `asyncio.new_event_loop()` 执行异步操作
4. **来源索引建立**: 上传后同步执行，异常仅记录日志不影响响应

### 潜在性能问题

- 向量嵌入建立（逐个调用 Embedding API）在来源上传时同步执行
- 简报配图生成逐页调用 AI 图片生成，耗时长
- 播客音讯生成逐段调用 TTS，耗时长

## 文件解析服务

| 格式 | 解析库 | 说明 |
|------|--------|------|
| PDF | PyPDF2 | 逐页提取文字 |
| TXT/MD | 内建 | 多编码尝试（utf-8/big5/gb2312/latin-1） |
| DOCX/DOC | python-docx | 段落 + 表格 |
| XLSX/XLS | openpyxl | 逐工作表逐行 |
| CSV | 内建 csv 模块 | 多编码尝试 |

## 网页抓取服务

- 使用 requests + BeautifulSoup
- 智能内容提取：优先查找 `<article>`, `<main>`, `[role="main"]` 等语义标签
- 移除导航/页尾/广告等无用元素
- 提取元数据（标题/描述/作者/发布日期/OG图片）
- 保留标题层级、列表、引用、代码块等格式

## YouTube 服务

- 支持多种 YouTube URL 格式（标准/短链接/嵌入）
- 字幕获取：优先使用 `youtube_transcript_api`，降级使用 `yt-dlp`
- 语言偏好：zh-TW > zh-Hant > zh > zh-Hans > en > ja > ko
- 手动字幕优先，自动生成字幕次之
- 提取影片信息：标题/频道/时长/缩图等

## PPTX 构建工具

文件: `utils/pptx_builder.py`

- 使用 python-pptx 库生成可编辑的 PPTX 文件
- 16:9 比例
- 支持背景图片、标题、内容文本框
- Base64 编码输出
