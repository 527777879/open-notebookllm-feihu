# 工作室功能

## 概述

工作室（Studio）是 NotebookLLM 的核心功能模块，支持 11 种 AI 生成输出类型。

**服务文件**: `backend/services/studio_service.py`
**控制器文件**: `backend/controllers/studio_controller.py`

## 输出类型总览

| 输出类型 | API 端点 | AI 交互方式 | 前端渲染方式 |
|---------|---------|------------|------------|
| summary | `/studio/summary` | generate() | Markdown 文本 |
| mindmap | `/studio/mindmap` | generate_json() | Mermaid.js |
| flowchart | `/studio/flowchart` | generate_json() | Draw.io XML |
| diagram | `/studio/diagram` | generate_json() | Draw.io XML |
| flashcards | `/studio/flashcards` | generate_json() | 卡片列表 |
| quiz | `/studio/quiz` | generate_json() | 题目列表 |
| report | `/studio/report` | generate() | Markdown 文本 |
| datatable | `/studio/datatable` | generate_json() | HTML 表格 |
| infographic | `/studio/infographic` | generate_json() + generate_image() | Chart.js |
| presentation | `/studio/presentation` | 多步骤 | 幻灯片卡片 + PPTX 导出 |
| podcast | `/studio/podcast` | 多步骤 | 对话脚本 + 音频播放 |

## 各输出类型详解

### 1. 摘要 (Summary)

**生成方式**: 单次 AI 文字生成

**输出格式**: Markdown 文本

**数据结构**:
```json
{
  "type": "summary",
  "data": {
    "content": "Markdown 格式的摘要内容"
  }
}
```

### 2. 心智图 (Mindmap)

**生成方式**: AI 生成 JSON 结构，后端转换为 Mermaid 格式

**输出格式**: JSON 结构 + Mermaid 代码

**数据结构**:
```json
{
  "type": "mindmap",
  "data": {
    "title": "心智图标题",
    "mermaid": "mindmap\n  root((标题))\n    分支1\n      子分支",
    "branches": [
      {
        "text": "分支名",
        "children": [{"text": "子分支名"}]
      }
    ],
    "stats": {
      "total_nodes": 15,
      "max_depth": 3
    }
  }
}
```

**前端渲染**: Mermaid.js 渲染，支持缩放(40%-200%)、复制代码、下载 SVG，渲染失败回退文本视图。

### 3. 流程图 (Flowchart)

**生成方式**: AI 生成 JSON，后端转换为 Draw.io XML

**输出格式**: Draw.io XML

**数据结构**:
```json
{
  "type": "flowchart",
  "data": {
    "xml": "<mxGraphModel>...</mxGraphModel>",
    "chart_type": "flowchart",
    "elements": [
      {"id": "1", "label": "开始", "type": "start"}
    ]
  }
}
```

**前端渲染**: react-drawio 嵌入 Draw.io 编辑器，支持编辑/查看切换、下载 SVG、全屏模式。

### 4. 架构图 (Diagram)

**生成方式**: AI 生成 JSON，后端转换为 Draw.io XML

**支持子类型**:
- `architecture` - 系统架构图
- `sequence` - 序列图
- `class` - 类图
- `er` - ER 图
- `network` - 网络拓扑图
- `auto` - 自动识别

**数据结构**:
```json
{
  "type": "diagram",
  "data": {
    "xml": "<mxGraphModel>...</mxGraphModel>",
    "chart_type": "architecture",
    "elements": [...]
  }
}
```

### 5. 学习卡 (Flashcards)

**生成方式**: AI 生成 JSON

**支持难度**: easy / medium / hard / mixed

**Bloom 认知层次**: Remember / Understand / Apply / Analyze / Evaluate / Create

**数据结构**:
```json
{
  "type": "flashcards",
  "data": {
    "cards": [
      {
        "id": 1,
        "question": "问题",
        "answer": "答案",
        "hint": "提示",
        "difficulty": "medium",
        "category": "分类",
        "bloom_level": "Understand"
      }
    ],
    "metadata": {
      "total": 10,
      "difficulty": "mixed",
      "categories": ["分类1", "分类2"]
    }
  }
}
```

**前端渲染**: 卡片列表，含难度标签、分类标签、认知层次、提示功能。

### 6. 测验 (Quiz)

**生成方式**: AI 生成 JSON

**支持 5 种题型**:
1. **选择题** (multiple_choice) - 4 个选项
2. **判断题** (true_false)
3. **填空题** (fill_blank)
4. **配对题** (matching) - 左右配对
5. **简答题** (short_answer)

**支持难度**: easy / medium / hard / mixed

**数据结构**:
```json
{
  "type": "quiz",
  "data": {
    "questions": [
      {
        "id": 1,
        "type": "multiple_choice",
        "question": "题目",
        "options": ["A", "B", "C", "D"],
        "answer": "A",
        "explanation": "解析",
        "hint": "提示",
        "points": 10,
        "difficulty": "medium",
        "bloom_level": "Apply"
      }
    ],
    "metadata": {
      "total": 10,
      "total_points": 100,
      "difficulty": "mixed",
      "type_distribution": {"multiple_choice": 4, "true_false": 2, "fill_blank": 2, "matching": 1, "short_answer": 1}
    }
  }
}
```

### 7. 报告 (Report)

**生成方式**: 单次 AI 文字生成

**输出格式**: 结构化 Markdown 报告

**数据结构**:
```json
{
  "type": "report",
  "data": {
    "content": "Markdown 格式的报告内容"
  }
}
```

### 8. 资料表 (Datatable)

**生成方式**: AI 生成 JSON

**输出格式**: 结构化表格数据

**数据结构**:
```json
{
  "type": "datatable",
  "data": {
    "headers": ["列1", "列2", "列3"],
    "rows": [
      ["值1", "值2", "值3"]
    ],
    "title": "资料表标题"
  }
}
```

**前端渲染**: HTML 表格显示。

### 9. 资讯图表 (Infographic)

**生成方式**: AI 生成 Chart.js 配置 JSON + 可选 AI 配图

**支持图表类型**: Bar / Line / Pie / Doughnut / Radar / PolarArea / Scatter

**数据结构**:
```json
{
  "type": "infographic",
  "data": {
    "charts": [
      {
        "type": "bar",
        "title": "图表标题",
        "description": "图表描述",
        "config": {
          "labels": ["A", "B", "C"],
          "datasets": [
            {
              "label": "数据集1",
              "data": [10, 20, 30],
              "backgroundColor": ["#color1", "#color2", "#color3"]
            }
          ]
        },
        "insights": ["洞察1", "洞察2"]
      }
    ],
    "summary": {
      "key_findings": ["发现1", "发现2"],
      "recommended_actions": ["建议1", "建议2"]
    },
    "images": ["base64图片1"],
    "metadata": {
      "total_charts": 2,
      "chart_types": ["bar", "pie"]
    }
  }
}
```

**前端渲染**: Chart.js 渲染图表 + AI 图片展示 + 洞察/总结区块。

### 10. 简报 (Presentation)

**生成方式**: 多步骤 AI 生成（最复杂的工作室功能）

**生成流程**:
```
1. 生成 PPT 大纲 (generate_json)
   → 返回标题 + 主题 + 页面大纲

2. 展开大纲为页面列表
   → 逐页定义标题和要点

3. 为每页生成详细描述 (逐页调用 generate)
   → 展开每页内容

4. 组建简报数据结构
   → 整合所有页面

5. AI 图片生成 (逐页 generate_image)
   → 为每页生成 1792x1024 配图

6. [可选] 导出为 PPTX 文件
   → 使用 pptx_builder.py 生成
```

**数据结构**:
```json
{
  "type": "presentation",
  "data": {
    "title": "简报标题",
    "subtitle": "副标题",
    "theme": "主题描述",
    "slides": [
      {
        "id": 1,
        "title": "页面标题",
        "content": "页面内容",
        "image": "base64图片",
        "notes": "讲者备注"
      }
    ],
    "pptx": "base64编码的PPTX文件"
  }
}
```

**前端渲染**: 幻灯片卡片列表，含标题/内容/图片/备注。

### 11. 播客 (Podcast)

详见下方 [Podcast 生成](#podcast-生成) 章节。

## Podcast 生成

**服务文件**: `backend/services/podcast_service.py`

### 脚本生成

**特性**:
- 支持 1-4 位讲者
- 6 种对话风格
- 三段式结构：开场(10%) → 主体(80%) → 结尾(10%)
- 长文本自动分段（>3000字时分段，每段约1500字）
- 确保讲者交替发言

### 对话风格

| 风格 | 说明 |
|------|------|
| conversational | 轻松对谈 |
| educational | 教育讲解 |
| debate | 辩论讨论 |
| interview | 专访形式 |
| storytelling | 故事叙述 |
| panel | 座谈会 |

### 讲者设定

```json
{
  "speakers": [
    {
      "name": "主持人",
      "role": "引导对话",
      "personality": "友善热情",
      "voice": "alloy"
    },
    {
      "name": "专家",
      "role": "提供专业见解",
      "personality": "严谨理性",
      "voice": "onyx"
    }
  ]
}
```

### 脚本数据结构

```json
{
  "type": "podcast",
  "data": {
    "title": "播客标题",
    "script": {
      "segments": [
        {
          "speaker": "主持人",
          "text": "欢迎收听...",
          "emotion": "热情"
        },
        {
          "speaker": "专家",
          "text": "确实如此...",
          "emotion": "认真"
        }
      ]
    },
    "speakers": [...],
    "style": "conversational",
    "duration_minutes": 10
  }
}
```

### 音频生成

**3 种 TTS 提供商**:

| 提供商 | 说明 | 语音选项 |
|--------|------|---------|
| OpenAI | 高品质，需 API Key | alloy / echo / fable / onyx / nova / shimmer |
| Edge TTS | 免费，微软语音 | zh-TW 三种语音 |
| Google Cloud TTS | 尚未实作 | - |

### 音频处理管线

```
PodcastService.generate_full_podcast()
  │
  ├── 步骤1: 生成脚本
  │     ├── 短内容: 单次 AI 调用
  │     └── 长内容: 分段处理
  │           ├── 首段: 完整提示（含上下文+角色+风格+结构要求）
  │           └── 后续段: 续写提示（含前文摘要+继续要求）
  │
  ├── 步骤2: 确保讲者交替发言
  │     └── 检测连续同一讲者 -> 插入其他讲者的过渡语
  │
  └── 步骤3: 生成音频（可选）
        ├── 根据 TTS 提供商分发
        │   ├── openai: 逐段调用 OpenAI TTS
        │   └── edge: 异步调用 Edge TTS
        │
        ├── pydub 合并多段音频
        ├── 音量正规化
        ├── 讲者切换间加入 400ms 停顿
        └── 输出 192kbps MP3 (Base64)
```

### API 端点

| 端点 | 说明 |
|------|------|
| `POST /studio/podcast` | 生成完整播客（脚本+可选音频） |
| `POST /studio/podcast/script` | 仅生成脚本 |
| `POST /studio/podcast/audio` | 从已有脚本生成音频 |
| `GET /studio/podcast/voices` | 获取可用语音列表 |

## 语音服务 (AudioService)

**文件**: `backend/services/audio_service.py`

### STT (语音转文字)

| 提供商 | 模型 | 说明 |
|--------|------|------|
| OpenAI | whisper-1 | 主推方案 |
| Groq | whisper-large-v3 | 更快速 |
| Local | whisper base 模型 | 本地运行，不需 API Key |

**音频上传管线**:
```
用户上传音频 → source_controller.upload_source()
  → 判断音频格式 (mp3/mp4/wav/m4a/webm/ogg/flac)
  → AudioService.transcribe_file()
    → 根据 provider 分发
  → 创建 Source(type='audio')
  → RAG 处理 + 全文索引
```

### TTS (文字转语音)

| 提供商 | 模型 | 说明 |
|--------|------|------|
| OpenAI | tts-1 | 6 种语音 |
| OpenAI Stream | tts-1 | 串流输出 |
| Google Cloud | - | 需要 GCP 凭证 |
| Edge TTS | - | 免费微软语音 |

**TTS API 端点**:

| 端点 | 说明 |
|------|------|
| `POST /studio/tts` | 文字转语音（返回 Base64 音频） |
| `POST /studio/tts/stream` | 串流文字转语音 |

## 通用生成端点

`POST /studio/generate` 是通用生成入口，根据 `type` 参数分派到对应生成方法：

```json
{
  "type": "mindmap",
  "source_ids": ["uuid1", "uuid2"],
  "options": {
    "difficulty": "medium"
  }
}
```

**支持的 type 值**: summary, mindmap, flashcards, quiz, report, datatable, presentation, infographic, flowchart, diagram, podcast
