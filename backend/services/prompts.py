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

    # ============ 專業簡報生成提示詞 ============

    PRESENTATION_OUTLINE = """根據以下來源內容，生成一份專業的 PPT 大綱。

## 來源內容

{content}

---

你可以使用兩種格式組織內容：

1. 簡單格式（適用於短簡報，沒有大章節）：
[{{"title": "標題1", "points": ["要點1", "要點2"]}}, {{"title": "標題2", "points": ["要點1", "要點2"]}}]

2. 章節格式（適用於長簡報，有明確章節）：
[
    {{
    "part": "第一部分：引言",
    "pages": [
        {{"title": "歡迎", "points": ["要點1", "要點2"]}},
        {{"title": "概述", "points": ["要點1", "要點2"]}}
    ]
    }},
    {{
    "part": "第二部分：主要內容",
    "pages": [
        {{"title": "主題1", "points": ["要點1", "要點2"]}},
        {{"title": "主題2", "points": ["要點1", "要點2"]}}
    ]
    }}
]

選擇最適合內容的格式。當簡報有清晰的主要章節時使用章節格式。
除非特殊要求，第一頁應保持最簡潔，只包含標題、副標題和演講者資訊。

請生成約 {slide_count} 頁的大綱，只輸出 JSON 格式，不要包含其他文字。
**所有內容必須使用繁體中文**"""

    PRESENTATION_PAGE_DESCRIPTION = """我們正在為 PPT 的每一頁生成內容描述。

## 來源內容

{content}

---

## 完整大綱

{outline}

{part_info}

---

現在請為第 {page_index} 頁生成描述：
{page_outline}

{first_page_note}

【重要提示】生成的「頁面文字」部分會直接渲染到 PPT 頁面上，因此請務必注意：
1. 文字內容要簡潔精煉，每條要點控制在 15-25 字以內
2. 條理清晰，使用列表形式組織內容
3. 避免冗長的句子和複雜的表述
4. 確保內容可讀性強，適合在演示時展示
5. 不要包含任何額外的說明性文字或注釋

輸出格式示例：
頁面標題：{example_title}
{subtitle_example}

頁面文字：
- 要點一：簡潔有力的說明
- 要點二：清晰的內容描述
- 要點三：重點資訊呈現

**所有內容必須使用繁體中文**"""

    PRESENTATION_IMAGE_GENERATION = """你是一位專家級 UI/UX 演示設計師，專注於生成設計精良的 PPT 頁面。

當前 PPT 頁面的頁面描述如下：
<page_description>
{page_desc}
</page_description>

<reference_information>
整個 PPT 的大綱為：
{outline_text}

當前位於章節：{current_section}
</reference_information>

<design_guidelines>
- 要求文字清晰銳利，畫面為 4K 解析度，16:9 比例
- 配色和設計語言採用專業商務風格
- 根據內容自動設計最完美的構圖，不重不漏地渲染「頁面描述」中的文本
- 如非必要，禁止出現 markdown 格式符號（如 # 和 * 等）
- 使用大小恰當的裝飾性圖形或插畫對空缺位置進行填補
- 背景應簡潔專業，不要過於花俏
</design_guidelines>

{first_page_design_note}

PPT 文字請使用全繁體中文。"""

    PRESENTATION_TITLE_PAGE_DESIGN = """**注意：當前頁面為 PPT 的封面頁，請你採用專業的封面設計美學技巧，務必凸顯出頁面標題，分清主次，確保一下就能抓住觀眾的注意力。**"""
