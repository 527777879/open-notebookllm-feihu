# API 端点完整文档

## 系统端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | API 信息与端点列表 |
| GET | `/health` | 健康检查 |

---

## 笔记本 (`/api/notebooks`)

### GET `/api/notebooks`

列出所有笔记本。

**响应**:
```json
[
  {
    "id": "uuid",
    "name": "笔记本名称",
    "description": "描述",
    "folder_id": "uuid | null",
    "order": 0,
    "source_count": 3,
    "note_count": 2,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### POST `/api/notebooks`

创建笔记本。

**请求**:
```json
{
  "name": "笔记本名称",
  "description": "描述（可选）"
}
```

**响应**: 201 Created，返回新笔记本对象

### GET `/api/notebooks/<id>`

获取单个笔记本（含来源列表）。

**响应**: 笔记本对象 + `sources` 数组

### PUT `/api/notebooks/<id>`

更新笔记本。

**请求**:
```json
{
  "name": "新名称",
  "description": "新描述"
}
```

### DELETE `/api/notebooks/<id>`

删除笔记本及其所有关联数据。

---

## 文件夹 (`/api/folders`)

### GET `/api/folders`

列出所有文件夹。

**查询参数**: `include_notebooks=true` (可选，含笔记本列表)

### POST `/api/folders`

创建文件夹。

**请求**:
```json
{
  "name": "文件夹名称",
  "emoji": "📁",
  "color": "#color"
}
```

### GET `/api/folders/<id>`

获取单个文件夹。

### PUT `/api/folders/<id>`

更新文件夹。

**请求**:
```json
{
  "name": "新名称",
  "emoji": "📂",
  "color": "#newcolor",
  "order": 1,
  "is_expanded": true
}
```

### DELETE `/api/folders/<id>`

删除文件夹，笔记本移至未分类。

### GET `/api/folders/<id>/notebooks`

获取文件夹内笔记本列表。

### PUT `/api/folders/<id>/notebooks/<notebook_id>`

将笔记本加入文件夹。

### DELETE `/api/folders/<id>/notebooks/<notebook_id>`

将笔记本从文件夹移出。

### PUT `/api/folders/reorder`

重新排序文件夹。

**请求**:
```json
{
  "folder_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### PUT `/api/folders/<id>/notebooks/reorder`

重新排序文件夹内笔记本。

**请求**:
```json
{
  "notebook_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### GET `/api/folders/with-notebooks`

获取所有文件夹及未分类笔记本的完整树状结构。

**响应**:
```json
{
  "folders": [
    {
      "id": "uuid",
      "name": "文件夹名",
      "emoji": "📁",
      "notebooks": [...]
    }
  ],
  "uncategorized_notebooks": [...]
}
```

---

## 来源 (`/api/notebooks/<id>/sources`)

### GET `/api/notebooks/<id>/sources`

列出笔记本的所有来源。

### POST `/api/notebooks/<id>/sources/upload`

上传文件来源（文档或音频）。

**请求**: `multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | 上传的文件 |
| stt_provider | string | 音频 STT 提供商（openai/groq/local，可选） |
| language | string | 音频语言（可选） |

**支持文件类型**: PDF, TXT, MD, DOCX, DOC, XLSX, XLS, CSV, MP3, WAV, M4A, OGG, FLAC, WEBM

### POST `/api/notebooks/<id>/sources/url`

添加网址来源。

**请求**:
```json
{
  "url": "https://example.com"
}
```

### POST `/api/notebooks/<id>/sources/youtube`

添加 YouTube 来源。

**请求**:
```json
{
  "url": "https://youtube.com/watch?v=xxx"
}
```

### POST `/api/notebooks/<id>/sources/text`

添加纯文本来源。

**请求**:
```json
{
  "name": "文本标题",
  "content": "文本内容"
}
```

### GET `/api/sources/<id>`

获取单个来源。

### DELETE `/api/sources/<id>`

删除来源。

### POST `/api/notebooks/<id>/search`

搜索笔记本内来源。

**请求**:
```json
{
  "query": "搜索关键词",
  "mode": "hybrid",
  "top_k": 10,
  "use_query_expansion": false,
  "use_reranking": false
}
```

**mode 可选值**: `hybrid` (默认) / `fulltext` / `vector`

**响应**:
```json
{
  "results": [
    {
      "source_id": "uuid",
      "source_name": "来源名称",
      "source_type": "pdf",
      "chunk_text": "匹配的文本片段",
      "score": 0.95
    }
  ],
  "total": 5,
  "mode": "hybrid"
}
```

### POST `/api/sources/reindex`

重建全文搜索索引。

**请求** (可选):
```json
{
  "notebook_id": "uuid"
}
```

不指定 notebook_id 则重建全部。

---

## 对话 (`/api/notebooks/<id>/chats`)

### GET `/api/notebooks/<id>/chats`

获取对话历史。

**响应**: ChatMessage 数组

### POST `/api/notebooks/<id>/chats`

发送对话消息（非串流）。

**请求**:
```json
{
  "message": "用户消息",
  "source_ids": ["uuid1", "uuid2"]
}
```

**响应**:
```json
{
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "AI 回复",
    "source_refs": [...]
  }
}
```

### POST `/api/notebooks/<id>/chats/stream`

发送对话消息（SSE 串流）。

**请求**: 同上

**响应**: Server-Sent Events

```
data: {"type": "chunk", "content": "AI"}

data: {"type": "chunk", "content": " 回复"}

data: {"type": "sources", "references": [...]}

data: {"type": "done", "message_id": "uuid", "message": {...}}

data: {"type": "error", "message": "错误信息"}
```

**事件类型**:
- `chunk`: 文本片段
- `sources`: 来源引用
- `done`: 生成完成
- `error`: 错误

### GET `/api/notebooks/<id>/suggested-questions`

获取建议问题。

**响应**:
```json
{
  "questions": ["问题1", "问题2", "问题3"]
}
```

### DELETE `/api/notebooks/<id>/chats/<message_id>`

删除单条对话消息。

### DELETE `/api/notebooks/<id>/chats/clear`

清空对话历史。

---

## 笔记 (`/api/notebooks/<id>/notes`)

### GET `/api/notebooks/<id>/notes`

列出笔记本的所有笔记。

### POST `/api/notebooks/<id>/notes`

创建笔记。

**请求**:
```json
{
  "title": "笔记标题",
  "content": "笔记内容"
}
```

### POST `/api/notebooks/<id>/notes/from-message`

将对话消息保存为笔记。

**请求**:
```json
{
  "message_id": "uuid"
}
```

### GET `/api/notes/<id>`

获取单个笔记。

### PUT `/api/notes/<id>`

更新笔记。

**请求**:
```json
{
  "title": "新标题",
  "content": "新内容"
}
```

### DELETE `/api/notes/<id>`

删除笔记。

---

## 工作室 (`/api/notebooks/<id>/studio`)

### 通用端点

### GET `/api/notebooks/<id>/studio/outputs`

列出工作室输出。

### GET `/api/notebooks/<id>/studio/outputs/<output_id>`

获取单个输出。

### DELETE `/api/notebooks/<id>/studio/outputs/<output_id>`

删除输出。

### POST `/api/notebooks/<id>/studio/generate`

通用生成端点。

**请求**:
```json
{
  "type": "mindmap",
  "source_ids": ["uuid1"],
  "options": {}
}
```

### 生成端点

所有生成端点共享类似的请求格式：

**请求**:
```json
{
  "source_ids": ["uuid1", "uuid2"]
}
```

| 端点 | type | 额外 options |
|------|------|-------------|
| POST `/studio/summary` | summary | - |
| POST `/studio/mindmap` | mindmap | - |
| POST `/studio/flowchart` | flowchart | - |
| POST `/studio/diagram` | diagram | `diagram_type`: architecture/sequence/class/er/network/auto |
| POST `/studio/flashcards` | flashcards | `count`: 数量, `difficulty`: easy/medium/hard/mixed |
| POST `/studio/quiz` | quiz | `count`: 数量, `difficulty`: easy/medium/hard/mixed |
| POST `/studio/report` | report | - |
| POST `/studio/datatable` | datatable | - |
| POST `/studio/infographic` | infographic | - |
| POST `/studio/presentation` | presentation | `include_pptx`: boolean |

### Podcast 端点

#### POST `/api/notebooks/<id>/studio/podcast`

生成完整播客（脚本+可选音频）。

**请求**:
```json
{
  "source_ids": ["uuid1"],
  "style": "conversational",
  "duration_minutes": 10,
  "speakers": [
    {
      "name": "主持人",
      "role": "引导对话",
      "personality": "友善热情",
      "voice": "alloy"
    }
  ],
  "generate_audio": true,
  "tts_provider": "openai"
}
```

**style 可选值**: conversational / educational / debate / interview / storytelling / panel

**tts_provider 可选值**: openai / edge / google

#### POST `/api/notebooks/<id>/studio/podcast/script`

仅生成播客脚本。

**请求**: 同上（不含 `generate_audio` 和 `tts_provider`）

#### POST `/api/notebooks/<id>/studio/podcast/audio`

从已有脚本生成音频。

**请求**:
```json
{
  "script": { "segments": [...] },
  "speakers": [...],
  "tts_provider": "openai"
}
```

#### GET `/api/notebooks/<id>/studio/podcast/voices`

获取可用语音列表。

**响应**:
```json
{
  "voices": [
    {
      "id": "alloy",
      "name": "Alloy",
      "provider": "openai",
      "language": "multilingual"
    }
  ]
}
```

### TTS 端点

#### POST `/api/notebooks/<id>/studio/tts`

文字转语音。

**请求**:
```json
{
  "text": "要转换的文本",
  "voice": "alloy",
  "provider": "openai"
}
```

**响应**:
```json
{
  "audio": "base64编码的音频",
  "format": "mp3"
}
```

#### POST `/api/notebooks/<id>/studio/tts/stream`

串流文字转语音。

**请求**: 同上

**响应**: 音频流（chunked transfer）

---

## 设置 (`/api/settings`)

### GET `/api/settings`

获取当前设置。

**响应**:
```json
{
  "current_provider": "gemini",
  "current_model": "gemini-1.5-flash",
  "providers": {
    "gemini": {"has_key": true},
    "openai": {"has_key": false},
    "anthropic": {"has_key": false},
    "ollama": {"has_key": false, "available": true},
    "groq": {"has_key": false},
    "deepseek": {"has_key": false}
  },
  "ready": true
}
```

### GET `/api/settings/providers`

获取可用提供商列表。

### PUT `/api/settings`

更新设置（运行时切换 Provider）。

**请求**:
```json
{
  "provider": "openai",
  "api_key": "sk-xxx",
  "model": "gpt-4o"
}
```

### POST `/api/settings/test-api`

测试 API 连线。

**请求**:
```json
{
  "provider": "gemini",
  "api_key": "xxx"
}
```

**响应**:
```json
{
  "success": true,
  "message": "连线成功",
  "provider": "gemini",
  "model": "gemini-1.5-flash"
}
```

### POST `/api/settings/reset`

重置 AI 服务。

### GET `/api/settings/models/<provider>`

获取指定提供商的可用模型列表。

**响应**:
```json
{
  "provider": "openai",
  "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
}
```

---

## 错误响应格式

所有 API 错误返回统一 JSON 格式：

```json
{
  "error": "错误描述"
}
```

常见 HTTP 状态码：
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误
