# 数据模型

## 数据库概览

- **数据库**: SQLite（通过 SQLAlchemy ORM）
- **位置**: `backend/instance/database.db`
- **全文搜索**: SQLite FTS5 虚拟表

## 数据表关系图

```
Folder (1) ───────< (N) Notebook (1) ───────< (N) Source (1) ───< (N) Embedding
                        │
                        ├──< (N) ChatMessage
                        ├──< (N) Note
                        └──< (N) StudioOutput
```

- **Folder**: 资料夹包含多个 Notebook，Notebook 可不属任何资料夹（未分类）
- **Notebook**: 核心实体，关联 Source、ChatMessage、Note、StudioOutput
- **Source**: 存储来源内容，每个 Source 可有多个 Embedding
- **Embedding**: 文本分块的向量嵌入，存储为 numpy float32 二进制序列化

## 数据表详细 Schema

### folders - 文件夹

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String(36) | PK | UUID |
| name | String(100) | NOT NULL | 文件夹名称 |
| emoji | String(10) | default='📁' | 图标 |
| color | String(20) | nullable | 颜色标签 |
| order | Integer | default=0 | 排序 |
| is_expanded | Boolean | default=True | 是否展开 |
| created_at | DateTime | auto | 创建时间 |
| updated_at | DateTime | auto | 更新时间 |

### notebooks - 笔记本

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String(36) | PK | UUID |
| name | String(255) | NOT NULL | 笔记本名称 |
| description | Text | nullable | 描述 |
| folder_id | String(36) | FK(folders.id) | 所属文件夹 |
| order | Integer | default=0 | 排序 |
| created_at | DateTime | auto | 创建时间 |
| updated_at | DateTime | auto | 更新时间 |

**关系**:
- `folder`: 多对一 → Folder
- `sources`: 一对多 → Source
- `chat_messages`: 一对多 → ChatMessage
- `notes`: 一对多 → Note
- `studio_outputs`: 一对多 → StudioOutput

### sources - 来源

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String(36) | PK | UUID |
| notebook_id | String(36) | FK(notebooks.id), NOT NULL | 所属笔记本 |
| type | String(20) | NOT NULL | 类型 |
| name | String(500) | NOT NULL | 来源名称 |
| url | String(2000) | nullable | 网址 |
| content | Text | NOT NULL | 提取的文字内容 |
| file_path | String(500) | nullable | 原始文件路径 |
| source_metadata | JSON | nullable | 元数据 |
| status | String(20) | default='completed' | 状态 |
| error_message | Text | nullable | 错误信息 |
| created_at | DateTime | auto | 创建时间 |
| updated_at | DateTime | auto | 更新时间 |

**type 枚举值**: `pdf`, `txt`, `docx`, `web`, `youtube`, `gdocs`, `text`, `audio`

**status 枚举值**: `pending`, `processing`, `completed`, `failed`

**关系**:
- `notebook`: 多对一 → Notebook
- `embeddings`: 一对多 → Embedding

### embeddings - 向量嵌入

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String(36) | PK | UUID |
| source_id | String(36) | FK(sources.id), NOT NULL | 所属来源 |
| chunk_index | Integer | NOT NULL | 文本分块索引 |
| chunk_text | Text | NOT NULL | 分块文本 |
| embedding | LargeBinary | NOT NULL | 向量嵌入（numpy float32 序列化） |
| created_at | DateTime | auto | 创建时间 |

**关系**:
- `source`: 多对一 → Source

**向量存储方式**: 使用 numpy float32 数组序列化为 LargeBinary，检索时反序列化并计算余弦相似度。

### chat_messages - 对话消息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String(36) | PK | UUID |
| notebook_id | String(36) | FK(notebooks.id), NOT NULL | 所属笔记本 |
| role | String(20) | NOT NULL | 角色 |
| content | Text | NOT NULL | 消息内容 |
| source_refs | JSON | nullable | 来源引用 |
| used_source_ids | JSON | nullable | 使用的来源 ID 列表 |
| created_at | DateTime | auto | 创建时间 |

**role 枚举值**: `user`, `assistant`

**source_refs 格式**:
```json
[{"source_id": "uuid", "chunk_text": "引用文本"}]
```

**关系**:
- `notebook`: 多对一 → Notebook

### notes - 笔记

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String(36) | PK | UUID |
| notebook_id | String(36) | FK(notebooks.id), NOT NULL | 所属笔记本 |
| title | String(255) | nullable | 标题 |
| content | Text | NOT NULL | 内容 |
| from_message_id | String(36) | nullable | 来源对话消息 ID |
| created_at | DateTime | auto | 创建时间 |
| updated_at | DateTime | auto | 更新时间 |

**关系**:
- `notebook`: 多对一 → Notebook

### studio_outputs - 工作室输出

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String(36) | PK | UUID |
| notebook_id | String(36) | FK(notebooks.id), NOT NULL | 所属笔记本 |
| type | String(50) | NOT NULL | 输出类型 |
| title | String(255) | nullable | 标题 |
| data | JSON | NOT NULL | 输出内容（JSON） |
| source_ids | JSON | nullable | 使用的来源 ID 列表 |
| created_at | DateTime | auto | 创建时间 |

**type 枚举值**: `audio_overview`, `video_summary`, `mindmap`, `report`, `flashcards`, `quiz`, `infographic`, `presentation`, `datatable`, `podcast`, `flowchart`, `diagram`

**关系**:
- `notebook`: 多对一 → Notebook

**data 字段 JSON 结构**因类型而异，详见 [工作室功能文档](./06-studio-features.md)。

### sources_fts - FTS5 全文搜索虚拟表

| 字段 | 说明 |
|------|------|
| source_id | 来源 ID |
| name | 来源名称 |
| content | 来源文字内容 |

这是 SQLite FTS5 虚拟表，用于全文搜索。使用 BM25 算法评分。

## 数据流向

### 来源处理流程

```
用户上传 → SourceController
  → FileParserService.parse() / WebScraperService.scrape() / YouTubeService.extract()
  → Source 实例创建 (status=processing)
  → RAGService.process_source()
    → 文本分割 (chunk_size=1000, overlap=200)
    → AI Provider.get_embeddings() 获取向量
    → Embedding 实例批量创建
  → SearchService.update_fts_index() 更新全文索引
  → Source 状态更新为 completed
```

### 对话消息流程

```
用户发送消息 → ChatController
  → ChatMessage 实例创建 (role=user)
  → RAGService.build_context()
    → RAGService.retrieve() 向量检索
    → 格式化上下文
  → AI Provider.generate_stream() / generate()
  → ChatMessage 实例创建 (role=assistant, source_refs)
```
