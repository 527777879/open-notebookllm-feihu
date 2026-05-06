# AI 服务与 RAG 流程

## AI 服务管理器 (AIServiceManager)

**文件**: `backend/services/ai_service_manager.py`

采用**单例模式 + 线程锁**，管理三个 Provider 角色：

- `_text_provider` - 文字生成（所有提供商支持）
- `_embedding_provider` - 向量嵌入（部分提供商支持）
- `_image_provider` - 图片生成（仅 Gemini/OpenAI 支持）

### 核心接口

```python
class AIServiceManager:
    # 切换提供商
    def switch_provider(self, provider_name, api_key=None, model=None)

    # 文字生成
    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096) -> str
    def generate_stream(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096) -> Generator
    def generate_json(self, prompt, system_prompt=None, temperature=0.7) -> dict

    # 向量嵌入
    def get_embedding(self, text) -> list[float]
    def get_embeddings(self, texts) -> list[list[float]]

    # 图片生成
    def generate_image(self, prompt, size="1024x1024") -> str  # Base64
    def generate_images(self, prompts) -> list[str]
```

### 提供商切换流程

```
switch_provider(provider_name, api_key, model)
  → 实例化对应的 Provider（如 GeminiProvider）
  → 设置 _text_provider = 新 Provider
  → 检查新 Provider 是否支持 embedding
    → 支持: _embedding_provider = 新 Provider
    → 不支持: 自动降级（优先级：OpenAI > Gemini > Ollama）
  → 检查新 Provider 是否支持 image
    → 支持: _image_provider = 新 Provider
    → 不支持: _image_provider = None（图片功能不可用）
```

## AI Provider 抽象层

**文件**: `backend/services/ai_providers/`

### 抽象基类

三个独立的 ABC 抽象基类，具体 Provider 可以同时实现多个：

```
BaseTextProvider (ABC)
    generate()
    generate_stream()
    generate_json()

BaseEmbeddingProvider (ABC)
    get_embedding()
    get_embeddings()

BaseImageProvider (ABC)
    generate_image()
    generate_images()
```

### 提供商能力矩阵

| 提供商 | 文字生成 | 串流生成 | JSON 生成 | 向量嵌入 | 图片生成 | 批量嵌入 |
|--------|---------|---------|----------|---------|---------|---------|
| **Gemini** | Yes | Yes | Yes(提示词) | Yes | Yes(多模态) | Yes(逐个) |
| **OpenAI** | Yes | Yes | Yes(原生) | Yes | Yes(DALL-E 3) | Yes(原生) |
| **Anthropic** | Yes | Yes | Yes(提示词) | No(降级) | No | No |
| **Ollama** | Yes | Yes | Yes(提示词) | Yes | No | Yes(逐个) |
| **Groq** | Yes | Yes | Yes(提示词) | No(降级) | No | No |
| **DeepSeek** | Yes | Yes | Yes(提示词) | No(降级) | No | No |

### JSON 生成方式差异

| 提供商 | 方式 | 说明 |
|--------|------|------|
| OpenAI | 原生 | `response_format={"type": "json_object"}` |
| 其他 | 提示词 | 提示词引导 + 后处理清理 markdown 标记 |

### 各 Provider 特殊实现

#### GeminiProvider
- 图片生成使用多模态模型 `gemini-2.0-flash-exp-image-generation`
- 需要 `google-genai` 新版 SDK
- JSON 生成通过提示词 + `response_mime_type="application/json"`

#### OpenAIProvider
- JSON 生成使用原生 `response_format={"type": "json_object"}`
- 图片生成使用 DALL-E 3 (1792x1024)
- 批量嵌入使用原生 API

#### AnthropicProvider
- 仅支持文字生成
- JSON 生成通过提示词引导
- 不支持 embedding，需 fallback

#### OllamaProvider
- 本地运行，不需要 API Key
- 支持 embedding
- JSON 生成通过提示词引导

#### GroqProvider
- 高速推理
- 仅支持文字生成
- 不支持 embedding，需 fallback

#### DeepSeekProvider
- 支持推理模型 (`deepseek-reasoner`)
- 可获取 `reasoning_content` 思考过程
- 不支持 embedding，需 fallback

### 重试机制

所有 Provider 使用 `tenacity` 实现统一重试：

- 重试次数: 3 次
- 退避策略: 指数退避
- 重试条件: API 异常

## RAG 服务 (RAGService)

**文件**: `backend/services/rag_service.py`

### 工作流程

```
来源内容 → process_source()
              │
              ├── 文本分割 (chunk_size=1000, overlap=200)
              │     └── 智能断句：优先在句号/换行/问号处断开
              │
              ├── 向量嵌入 (AI Provider.get_embeddings)
              │
              └── 存储到 embeddings 表

用户查询 → retrieve()
              │
              ├── 获取查询向量 (AI Provider embedding)
              ├── 查询 Embedding 表
              ├── 计算余弦相似度
              └── 返回 top_k 结果

           → build_context()
              │
              ├── 调用 retrieve()
              └── 格式化为引用文本 (context + source_refs)
```

### 文本分割策略

```python
def split_text(text, chunk_size=1000, overlap=200):
    # 1. 固定大小分割
    # 2. 智能断句：在 chunk_size 范围内，优先在以下位置断开：
    #    - 句号 (。)
    #    - 换行符 (\n)
    #    - 问号 (？)
    #    - 感叹号 (！)
    # 3. 重叠 overlap 字符，保持上下文连贯
```

### 余弦相似度计算

```python
def cosine_similarity(a, b):
    # numpy 向量计算
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

### RAG 对话流程

```
用户查询 + 来源内容
  → RAGService.build_context() 构建上下文
  → ChatPrompts.RAG_TEMPLATE 格式化
  → AI Service.generate_stream() 生成回答
  → 附加来源引用 (source_refs)
```

## 混合搜索服务 (SearchService)

**文件**: `backend/services/search_service.py`

### 搜索架构

```
SearchService.hybrid_search()
    │
    ├── [可选] Query Expansion (LLM 扩展查询)
    │       └── 生成 2-3 个语义变体
    │
    ├── 全文搜索 (FTS5 + BM25)
    │       └── SELECT ... FROM sources_fts WHERE sources_fts MATCH ?
    │           ORDER BY bm25(sources_fts)
    │
    ├── 向量搜索 (RAGService.retrieve)
    │       └── 余弦相似度 top_k
    │
    ├── 结果融合
    │       ├── RRF 融合 (推荐)
    │       │   └── score = Σ 1/(k + rank_i), k=60
    │       └── 加权融合 (旧版)
    │           └── score = fulltext_weight * 0.3 + vector_weight * 0.7
    │
    └── [可选] LLM Reranking (智能重排序)
```

### RRF 融合算法

Reciprocal Rank Fusion (RRF) 是推荐的融合算法：

```
score(doc) = Σ 1/(k + rank_i(doc))

其中：
- k = 60 (常数，减少高排名结果的权重优势)
- rank_i(doc) = 文档在第 i 个排序列表中的排名
```

**优势**:
- 无需归一化分数
- 对排名不敏感
- 两种搜索结果自然融合

### 搜索模式

| 模式 | 说明 |
|------|------|
| `hybrid` | 全文 + 向量 + 融合 (默认) |
| `fulltext` | 仅全文搜索 (FTS5) |
| `vector` | 仅向量搜索 |

### 查询扩展 (Query Expansion)

使用 LLM 生成同义查询变体，扩展搜索覆盖范围：

```
原始查询 → LLM 生成 2-3 个语义变体
→ 对每个变体执行搜索
→ 合并去重结果
```

### LLM Reranking

使用 LLM 对搜索结果重新排序：

```
搜索结果 → LLM 评估每个结果的相关性
→ 按 LLM 评分重新排序
```

## 提示词模板 (prompts.py)

**文件**: `backend/services/prompts.py`

### ChatPrompts - 对话提示词

- `RAG_TEMPLATE`: RAG 对话模板，包含上下文 + 来源引用格式
- `SUGGESTED_QUESTIONS`: 建议问题生成模板

### StudioPrompts - 工作室提示词

每种输出类型有对应的提示词模板，详见 [工作室功能文档](./06-studio-features.md)。

### PodcastPrompts - 播客提示词

- 6 种对话风格模板
- 长文本分段处理模板
- 讲者交替保证逻辑
