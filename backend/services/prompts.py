"""
提示詞模板
"""


class ChatPrompts:
    """對話提示詞"""

    SYSTEM = """你是 NoteBookLLM 智能助手，專門根據用戶提供的來源資料回答問題。

## 回答規則

1. **基於來源**: 只根據提供的來源資料回答，不要編造信息
2. **明確說明**: 如果來源資料中沒有相關信息，請明確說明「根據提供的資料，沒有找到相關信息」
3. **引用來源**: 回答時請引用相關的來源，格式如「根據 [來源名稱]...」
4. **使用繁體中文**: 所有回答都使用繁體中文
5. **結構清晰**: 使用標題、列表等方式組織回答，讓內容易於閱讀
6. **準確簡潔**: 提供準確、有用的回答，避免冗長

## 回答格式

- 使用 Markdown 格式
- 適當使用標題 (##, ###)
- 使用列表組織多個要點
- 引用來源時使用「根據 [來源名稱]」的格式
"""

    RAG_TEMPLATE = """請根據以下來源資料回答問題。

## 來源資料

{context}

---

## 用戶問題

{question}

---

請根據以上來源資料提供詳細、準確的回答。如果來源資料中沒有相關信息，請明確說明。"""

    SUGGESTED_QUESTIONS = """根據以下來源資料，生成 3-5 個用戶可能會問的問題。

## 來源資料

{context}

---

請生成具體、有意義的問題，這些問題應該：
1. 與來源資料內容直接相關
2. 有助於深入理解資料內容
3. 涵蓋不同的主題面向

請用 JSON 陣列格式返回，例如：
["問題1？", "問題2？", "問題3？"]"""


class StudioPrompts:
    """工作室輸出提示詞"""

    SUMMARY = """請為以下內容生成一份清晰、有條理的摘要。

## 來源內容

{content}

---

## 摘要要求

1. 涵蓋所有關鍵要點
2. 邏輯清晰，結構合理
3. 使用繁體中文
4. 長度適中（300-500字）
5. 適合口頭朗讀（用於語音摘要）

請直接提供摘要內容，使用 Markdown 格式。"""

    MINDMAP = """根據以下內容生成心智圖結構。

## 來源內容

{content}

---

請用以下 JSON 格式返回心智圖結構：

```json
{{
    "central": "中心主題",
    "branches": [
        {{
            "name": "主分支1",
            "children": [
                {{"name": "子節點1-1", "children": []}},
                {{"name": "子節點1-2", "children": []}}
            ]
        }},
        {{
            "name": "主分支2",
            "children": [
                {{"name": "子節點2-1", "children": []}}
            ]
        }}
    ]
}}
```

注意：
1. **所有節點名稱必須使用繁體中文**
2. 中心主題應概括整體內容
3. 主分支不超過 6 個
4. 每個分支的子節點不超過 5 個
5. 層級不超過 3 層"""

    FLASHCARDS = """根據以下內容生成 {count} 張學習卡。

## 來源內容

{content}

---

請用以下 JSON 格式返回學習卡：

```json
{{
    "cards": [
        {{"front": "問題或概念", "back": "答案或解釋"}},
        {{"front": "問題或概念", "back": "答案或解釋"}}
    ]
}}
```

學習卡要求：
1. **所有內容必須使用繁體中文**
2. 問題清晰具體
3. 答案準確簡潔
4. 涵蓋內容的重要知識點
5. 難度適中，適合複習使用"""

    QUIZ = """根據以下內容生成 {count} 道測驗題。

## 來源內容

{content}

---

請用以下 JSON 格式返回測驗題：

```json
{{
    "questions": [
        {{
            "type": "multiple_choice",
            "question": "問題內容？",
            "options": ["選項A", "選項B", "選項C", "選項D"],
            "correct": "A",
            "explanation": "解釋為什麼這個答案是正確的"
        }},
        {{
            "type": "true_false",
            "question": "這是一個判斷題陳述。",
            "correct": true,
            "explanation": "解釋"
        }}
    ]
}}
```

測驗題要求：
1. **所有內容必須使用繁體中文**
2. 問題基於來源內容
3. 選項有明確區別
4. 包含正確答案說明
5. 混合使用選擇題和判斷題"""

    REPORT = """根據以下內容生成一份詳細的研究報告。

## 來源內容

{content}

---

## 報告格式

請按照以下結構生成報告（使用 Markdown 格式）：

# 報告標題

## 摘要
（簡要概述報告的主要內容和結論）

## 背景與目的
（介紹主題背景和報告目的）

## 主要發現
（詳細分析來源內容中的重要發現）

### 發現一
...

### 發現二
...

## 詳細分析
（深入分析各個主題）

## 結論與建議
（總結報告並提出建議）

## 參考來源
（列出使用的來源）

---

報告要求：
1. 內容準確，基於來源資料
2. 結構清晰，邏輯連貫
3. 語言專業，使用繁體中文
4. 長度適中（1000-2000字）"""

    DATATABLE = """根據以下內容提取結構化資料，生成資料表。

## 來源內容

{content}

---

請分析內容並提取可結構化的資料，用以下 JSON 格式返回：

```json
{{
    "title": "資料表標題",
    "description": "資料表說明",
    "columns": [
        {{"key": "column1", "label": "欄位1"}},
        {{"key": "column2", "label": "欄位2"}},
        {{"key": "column3", "label": "欄位3"}}
    ],
    "rows": [
        {{"column1": "值1", "column2": "值2", "column3": "值3"}},
        {{"column1": "值4", "column2": "值5", "column3": "值6"}}
    ]
}}
```

要求：
1. **所有內容必須使用繁體中文**
2. 識別內容中可結構化的資料
3. 欄位命名清晰
4. 資料準確完整"""

    PRESENTATION = """根據以下內容生成一份專業的簡報大綱。

## 來源內容

{content}

---

請生成一份 {slide_count} 頁的簡報，用以下 JSON 格式返回：

```json
{{
    "title": "簡報標題",
    "subtitle": "副標題（選填）",
    "slides": [
        {{
            "slide_number": 1,
            "title": "標題頁",
            "type": "title",
            "content": "簡報主題介紹",
            "image_prompt": "A professional title slide background with abstract business elements, modern and clean design"
        }},
        {{
            "slide_number": 2,
            "title": "目錄",
            "type": "toc",
            "content": "1. 第一章\\n2. 第二章\\n3. 第三章",
            "image_prompt": ""
        }},
        {{
            "slide_number": 3,
            "title": "章節標題",
            "type": "content",
            "content": "• 要點一\\n• 要點二\\n• 要點三",
            "speaker_notes": "講者備註說明",
            "image_prompt": "Illustration representing [主題關鍵字], professional business style, clean background"
        }},
        {{
            "slide_number": 4,
            "title": "結論",
            "type": "conclusion",
            "content": "總結要點",
            "image_prompt": "Professional conclusion slide with success and achievement theme"
        }}
    ]
}}
```

簡報要求：
1. **所有文字內容必須使用繁體中文**（title, content, speaker_notes 都用繁體中文）
2. 內容基於來源資料
3. 每頁聚焦一個重點
4. 使用條列式呈現
5. 文字精簡，適合口頭報告
6. 只有 image_prompt 使用英文（用於 AI 生成配圖）
7. image_prompt 要具體描述圖片風格和內容，方便 AI 生成相關圖片
8. 目錄頁(toc)不需要配圖，image_prompt 留空

重要：除了 image_prompt 之外，所有內容都必須是繁體中文！"""

    IMAGE_PROMPT_ENHANCE = """請將以下簡報配圖描述優化為更具體的 AI 圖片生成提示詞。

原始描述：{original_prompt}
簡報主題：{topic}
頁面內容：{slide_content}

請生成一個具體、詳細的英文圖片提示詞，包含：
1. 具體的視覺元素
2. 風格描述（如：modern, professional, minimalist）
3. 色調建議
4. 構圖方式

只返回優化後的英文提示詞，不要其他說明。"""
