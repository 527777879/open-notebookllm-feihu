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

    MINDMAP = """根據以下內容生成專業的心智圖結構。

## 來源內容

{content}

---

請用以下 JSON 格式返回心智圖結構：

```json
{{
    "central": {{
        "text": "中心主題",
        "description": "主題簡短說明",
        "icon": "lightbulb"
    }},
    "branches": [
        {{
            "text": "主分支1",
            "description": "分支說明（選填）",
            "color": "#4CAF50",
            "icon": "folder",
            "children": [
                {{
                    "text": "子節點1-1",
                    "description": "節點說明（選填）",
                    "children": []
                }},
                {{
                    "text": "子節點1-2",
                    "children": [
                        {{"text": "三級節點", "children": []}}
                    ]
                }}
            ]
        }},
        {{
            "text": "主分支2",
            "color": "#2196F3",
            "icon": "star",
            "children": []
        }}
    ],
    "metadata": {{
        "title": "心智圖標題",
        "totalNodes": 10,
        "maxDepth": 3
    }}
}}
```

## 顏色建議（每個主分支使用不同顏色）
- 綠色系: #4CAF50, #8BC34A, #CDDC39
- 藍色系: #2196F3, #03A9F4, #00BCD4
- 紫色系: #9C27B0, #673AB7, #3F51B5
- 橘色系: #FF9800, #FF5722, #F44336
- 青色系: #009688, #00BCD4, #4DD0E1

## 圖標建議（根據內容選擇適合的圖標）
- 概念類: lightbulb, idea, brain, puzzle
- 資料類: folder, file, database, chart
- 行動類: rocket, flag, target, check
- 人物類: user, users, team, person
- 物件類: star, heart, bookmark, tag

## 注意事項
1. **所有文字必須使用繁體中文**
2. 中心主題應精準概括整體內容（5-15 字）
3. 主分支 3-6 個，代表主要分類
4. 每個分支的子節點 2-5 個
5. 層級最多 4 層（中心 → 主分支 → 子節點 → 三級節點）
6. 每個主分支使用不同顏色
7. description 用於補充說明，保持簡潔（10-30 字）
8. 確保邏輯層次清晰，同級節點相關性高"""

    FLASHCARDS = """根據以下內容生成 {count} 張學習卡，難度要求：{difficulty}。

## 來源內容

{content}

---

## Bloom 認知層次指南

請根據難度要求，設計不同認知層次的問題：

**簡單 (easy)** - 記憶與理解層次：
- 定義是什麼？
- 列舉/描述...
- 解釋...的含義

**中等 (medium)** - 應用與分析層次：
- 如何應用...？
- 比較...和...的差異
- 分析...的原因

**困難 (hard)** - 評估與創造層次：
- 評估...的優缺點
- 如果...會發生什麼？
- 設計一個...的方案

---

請用以下 JSON 格式返回學習卡：

```json
{{
    "cards": [
        {{
            "front": "問題或概念",
            "back": "答案或解釋",
            "difficulty": "easy/medium/hard",
            "category": "分類標籤",
            "cognitive_level": "記憶/理解/應用/分析/評估/創造",
            "hint": "提示（選填）"
        }}
    ],
    "metadata": {{
        "total_cards": 10,
        "difficulty_distribution": {{
            "easy": 3,
            "medium": 4,
            "hard": 3
        }},
        "categories": ["分類1", "分類2"],
        "recommended_study_order": [0, 1, 2, 3]
    }}
}}
```

## 學習卡設計要求

1. **所有內容必須使用繁體中文**
2. **問題設計原則**：
   - 一張卡片只問一個概念
   - 問題要具體明確，避免模糊
   - 使用疑問句或填空形式
3. **答案設計原則**：
   - 簡潔但完整
   - 包含關鍵詞或要點
   - 複雜答案使用條列式
4. **難度分布**：
   - 簡單難度：基礎定義和事實
   - 中等難度：概念應用和比較
   - 困難難度：綜合分析和評估
5. **分類標籤**：根據知識點主題分類
6. **提示**：為困難題目提供思考方向（選填）"""

    QUIZ = """根據以下內容生成 {count} 道測驗題，難度要求：{difficulty}。

## 來源內容

{content}

---

## 題型說明

請混合使用以下題型，創建多元化的測驗：

### 1. 選擇題 (multiple_choice)
- 單選題：4 個選項，1 個正確答案
- 適合測試概念理解和事實記憶

### 2. 判斷題 (true_false)
- 判斷陳述的真偽
- 適合測試對細節的掌握

### 3. 填空題 (fill_blank)
- 在句子中填入正確的詞彙或概念
- 適合測試關鍵術語的記憶

### 4. 配對題 (matching)
- 將左側項目與右側項目配對
- 適合測試概念之間的關聯

### 5. 簡答題 (short_answer)
- 簡短回答問題（僅供自我練習）
- 適合測試綜合理解能力

---

## Bloom 認知層次與難度對應

**簡單 (easy)** - 記憶與理解：
- 題目類型：定義、列舉、基本概念
- 認知層次：記憶、理解

**中等 (medium)** - 應用與分析：
- 題目類型：應用場景、比較分析、因果關係
- 認知層次：應用、分析

**困難 (hard)** - 評估與創造：
- 題目類型：情境判斷、綜合評估、問題解決
- 認知層次：評估、創造

---

請用以下 JSON 格式返回測驗題：

```json
{{
    "quiz_title": "測驗標題",
    "description": "測驗說明",
    "questions": [
        {{
            "id": 1,
            "type": "multiple_choice",
            "difficulty": "easy/medium/hard",
            "cognitive_level": "記憶/理解/應用/分析/評估/創造",
            "category": "分類標籤",
            "question": "問題內容？",
            "options": ["選項A", "選項B", "選項C", "選項D"],
            "correct": "A",
            "explanation": "詳細解釋為什麼這個答案是正確的",
            "hint": "提示（選填）",
            "points": 10
        }},
        {{
            "id": 2,
            "type": "true_false",
            "difficulty": "easy",
            "cognitive_level": "理解",
            "category": "分類標籤",
            "question": "這是一個判斷題陳述。",
            "correct": true,
            "explanation": "解釋",
            "points": 5
        }},
        {{
            "id": 3,
            "type": "fill_blank",
            "difficulty": "medium",
            "cognitive_level": "應用",
            "category": "分類標籤",
            "question": "______ 是指在軟體開發中用於版本控制的系統。",
            "correct": "Git",
            "alternatives": ["git", "GIT"],
            "explanation": "Git 是目前最流行的分散式版本控制系統",
            "points": 10
        }},
        {{
            "id": 4,
            "type": "matching",
            "difficulty": "medium",
            "cognitive_level": "分析",
            "category": "分類標籤",
            "question": "請將以下概念與其定義配對",
            "left_items": ["項目1", "項目2", "項目3"],
            "right_items": ["定義A", "定義B", "定義C"],
            "correct_pairs": {{"項目1": "定義A", "項目2": "定義B", "項目3": "定義C"}},
            "explanation": "配對說明",
            "points": 15
        }},
        {{
            "id": 5,
            "type": "short_answer",
            "difficulty": "hard",
            "cognitive_level": "評估",
            "category": "分類標籤",
            "question": "請簡述...的優缺點",
            "sample_answer": "參考答案要點：1. ... 2. ... 3. ...",
            "key_points": ["要點1", "要點2", "要點3"],
            "explanation": "評分標準說明",
            "points": 20
        }}
    ],
    "metadata": {{
        "total_questions": 10,
        "total_points": 100,
        "time_limit_minutes": 15,
        "passing_score": 60,
        "difficulty_distribution": {{
            "easy": 3,
            "medium": 4,
            "hard": 3
        }},
        "type_distribution": {{
            "multiple_choice": 4,
            "true_false": 2,
            "fill_blank": 2,
            "matching": 1,
            "short_answer": 1
        }},
        "categories": ["分類1", "分類2"]
    }}
}}
```

## 測驗設計要求

1. **所有內容必須使用繁體中文**
2. **題目設計原則**：
   - 基於來源內容，不編造資訊
   - 問題清晰明確，避免歧義
   - 選項長度相近，避免暗示正確答案
   - 錯誤選項要合理，避免明顯錯誤
3. **難度分布建議**：
   - 簡單題：30%（基礎概念確認）
   - 中等題：50%（應用與分析）
   - 困難題：20%（綜合評估）
4. **題型分布建議**：
   - 選擇題為主（40-50%）
   - 穿插其他題型增加多樣性
5. **解釋說明**：
   - 每題必須有解釋
   - 說明正確答案的原因
   - 指出常見錯誤的陷阱"""

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

    INFOGRAPHIC = """根據以下內容分析數據特徵，生成適合視覺化的資訊圖表配置。

## 來源內容

{content}

---

## 任務說明

請分析來源內容，提取可視覺化的數據，並自動選擇最適合的圖表類型。

## 圖表類型選擇指南

根據數據特徵選擇最適合的圖表類型：

| 數據特徵 | 推薦圖表 | 適用場景 |
|---------|---------|---------|
| 分類比較 | bar（柱狀圖） | 比較不同類別的數值大小 |
| 時間序列 | line（折線圖） | 顯示數據隨時間的變化趨勢 |
| 佔比分布 | pie/doughnut（圓餅圖） | 顯示各部分佔整體的比例 |
| 多維度比較 | radar（雷達圖） | 比較多個維度的綜合表現 |
| 數據分布 | scatter（散點圖） | 顯示兩個變數之間的關係 |
| 流程/層級 | bar（堆疊柱狀圖） | 顯示組成結構 |

## 輸出格式

請用以下 JSON 格式返回，此格式與 Chart.js 兼容：

```json
{{
    "title": "資訊圖表標題",
    "description": "圖表說明（2-3 句話描述數據洞察）",
    "data_source": "數據來源說明",
    "charts": [
        {{
            "id": "chart1",
            "title": "圖表1標題",
            "type": "bar",
            "description": "此圖表顯示...",
            "insights": ["洞察1", "洞察2"],
            "config": {{
                "type": "bar",
                "data": {{
                    "labels": ["類別1", "類別2", "類別3", "類別4"],
                    "datasets": [
                        {{
                            "label": "數據系列1",
                            "data": [12, 19, 3, 5],
                            "backgroundColor": [
                                "rgba(54, 162, 235, 0.8)",
                                "rgba(255, 99, 132, 0.8)",
                                "rgba(255, 206, 86, 0.8)",
                                "rgba(75, 192, 192, 0.8)"
                            ],
                            "borderColor": [
                                "rgba(54, 162, 235, 1)",
                                "rgba(255, 99, 132, 1)",
                                "rgba(255, 206, 86, 1)",
                                "rgba(75, 192, 192, 1)"
                            ],
                            "borderWidth": 1
                        }}
                    ]
                }},
                "options": {{
                    "responsive": true,
                    "plugins": {{
                        "legend": {{
                            "position": "top"
                        }},
                        "title": {{
                            "display": true,
                            "text": "圖表1標題"
                        }}
                    }},
                    "scales": {{
                        "y": {{
                            "beginAtZero": true
                        }}
                    }}
                }}
            }}
        }},
        {{
            "id": "chart2",
            "title": "圖表2標題",
            "type": "pie",
            "description": "此圖表顯示佔比分布...",
            "insights": ["洞察1"],
            "config": {{
                "type": "pie",
                "data": {{
                    "labels": ["項目A", "項目B", "項目C"],
                    "datasets": [
                        {{
                            "data": [30, 50, 20],
                            "backgroundColor": [
                                "rgba(255, 99, 132, 0.8)",
                                "rgba(54, 162, 235, 0.8)",
                                "rgba(255, 206, 86, 0.8)"
                            ]
                        }}
                    ]
                }},
                "options": {{
                    "responsive": true,
                    "plugins": {{
                        "legend": {{
                            "position": "right"
                        }}
                    }}
                }}
            }}
        }}
    ],
    "summary": {{
        "key_findings": [
            "關鍵發現1",
            "關鍵發現2",
            "關鍵發現3"
        ],
        "recommendations": [
            "建議1",
            "建議2"
        ]
    }},
    "metadata": {{
        "total_charts": 2,
        "chart_types": ["bar", "pie"],
        "data_points": 10
    }}
}}
```

## 設計要求

1. **所有文字內容必須使用繁體中文**
2. **數據準確性**：
   - 只使用來源內容中明確提到的數據
   - 如果沒有具體數值，可以根據描述推斷相對比例
   - 標註數據來源
3. **圖表選擇**：
   - 根據數據特徵選擇最適合的圖表類型
   - 優先選擇能清楚傳達資訊的圖表
   - 可生成 1-3 個圖表，從不同角度呈現數據
4. **配色方案**：
   - 使用專業、協調的配色
   - 確保對比度足夠，便於閱讀
   - 推薦配色：藍色系、綠色系、橙色系
5. **洞察說明**：
   - 每個圖表提供 1-3 個關鍵洞察
   - 總結中提供整體發現和建議

## 常用配色方案

```
藍色系: rgba(54, 162, 235, 0.8)
紅色系: rgba(255, 99, 132, 0.8)
黃色系: rgba(255, 206, 86, 0.8)
綠色系: rgba(75, 192, 192, 0.8)
紫色系: rgba(153, 102, 255, 0.8)
橙色系: rgba(255, 159, 64, 0.8)
灰色系: rgba(201, 203, 207, 0.8)
```"""

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


class PodcastPrompts:
    """Podcast 播客生成提示詞"""

    SCRIPT_GENERATION = """你是一位專業的播客節目腳本作家，擅長創作引人入勝的對話內容。

## 來源內容
<source_content>
{content}
</source_content>

## 講者設定
{speakers_desc}

## 節目設定
- 節目風格: {style_guide}
- 目標時長: 約 {duration_minutes} 分鐘（約 {target_words} 字）
- 語言: 繁體中文

## 腳本結構要求

### 開場（約 10% 篇幅）
- 主持人開場白，介紹今天的主題
- 營造輕鬆愉快的氛圍
- 簡短預告今天要討論的重點

### 主體（約 80% 篇幅）
- 深入討論來源內容的核心要點
- 自然的對話互動，包含：
  - 提問與回答
  - 舉例說明
  - 個人見解分享
  - 適當的幽默和輕鬆時刻
- 確保每位講者都有充分的發言機會
- 使用過渡語句連接不同話題

### 結尾（約 10% 篇幅）
- 總結今天討論的重點
- 給聽眾的行動建議或思考問題
- 預告或告別語

## 對話技巧要求
1. **自然流暢**: 加入語氣詞如「嗯」「對」「是啊」「哇」等
2. **互動感強**: 講者之間要有真實的互動和回應
3. **節奏適當**: 避免單人長篇大論，保持對話節奏
4. **情緒豐富**: 根據內容調整語氣（好奇、驚訝、認同、思考等）
5. **易於理解**: 複雜概念用簡單的話解釋，可用類比或例子

## 輸出格式
請以 JSON 格式輸出，所有文字內容必須使用繁體中文：

```json
{{
    "title": "播客節目標題",
    "description": "節目簡介（2-3 句話）",
    "segments": [
        {{
            "speaker": "講者名稱",
            "text": "講者說的話（自然口語化）",
            "emotion": "情緒標記"
        }}
    ],
    "keywords": ["關鍵字1", "關鍵字2"],
    "summary": "節目內容摘要"
}}
```

情緒標記選項：neutral（平靜）、excited（興奮）、curious（好奇）、thoughtful（沉思）、surprised（驚訝）、amused（有趣）、serious（嚴肅）、warm（溫暖）

請直接輸出 JSON，不要加任何其他說明。"""

    SCRIPT_CONTINUATION = """你正在續寫一段播客對話腳本。

## 原始來源內容
<source_content>
{content}
</source_content>

## 講者設定
{speakers_desc}

## 之前的對話（保持連貫性）
<previous_dialogue>
{previous_dialogue}
</previous_dialogue>

## 本段需要討論的內容
<current_section>
{current_section}
</current_section>

## 要求
1. 延續之前的對話風格和氛圍
2. 自然地過渡到新話題
3. 保持講者的個性一致性
4. 目標字數：約 {target_words} 字

請以相同的 JSON segments 格式輸出這一段的對話，只輸出 segments 陣列：

```json
[
    {{
        "speaker": "講者名稱",
        "text": "講者說的話",
        "emotion": "情緒標記"
    }}
]
```"""

    STYLE_GUIDES = {
        "conversational": """【對話式】
- 像朋友間的輕鬆閒聊
- 可以有玩笑和調侃
- 分享個人經驗和感受
- 互相補充和發散話題""",

        "educational": """【教育式】
- 一位是講解者，一位是學習者
- 學習者適時提出疑問
- 講解者用淺顯易懂的方式說明
- 包含知識點的總結和複習""",

        "debate": """【辯論式】
- 呈現不同觀點和立場
- 有理有據地討論
- 尊重但堅持自己的觀點
- 最後尋求共識或總結分歧""",

        "interview": """【訪談式】
- 主持人引導話題走向
- 專家/嘉賓深入分享見解
- 追問細節和背後故事
- 為聽眾提煉重點""",

        "storytelling": """【故事式】
- 以敘事方式呈現內容
- 營造場景和氛圍
- 有起承轉合的結構
- 引發聽眾的情感共鳴""",

        "panel": """【座談式】
- 多位專家各抒己見
- 主持人串場和總結
- 不同角度看同一問題
- 互相啟發和碰撞"""
    }

    SPEAKER_PERSONALITY_TEMPLATES = {
        "host": "熱情開朗、善於引導話題、會照顧每位講者的發言機會",
        "co-host": "配合默契、適時補充、偶爾調侃增加趣味",
        "expert": "專業嚴謹、深入淺出、喜歡舉例說明",
        "guest": "分享親身經歷、提供獨特視角、真誠表達感受",
        "curious": "好奇心強、愛問問題、代表聽眾發問",
        "skeptic": "理性質疑、追求事實、提出不同觀點"
    }
