"""
工作室輸出生成服務
"""
import json
import logging
from typing import Dict, Any, List, Optional

from .ai_service_manager import get_ai_service
from .prompts import StudioPrompts
from models import Source

logger = logging.getLogger(__name__)

# 嘗試導入 PPTX 建構器
try:
    from utils.pptx_builder import PPTXBuilder, is_pptx_available
    PPTX_EXPORT_AVAILABLE = is_pptx_available()
except ImportError:
    PPTX_EXPORT_AVAILABLE = False
    logger.warning("PPTX 導出功能不可用")


class StudioService:
    """工作室輸出生成服務"""

    def get_sources_content(self, source_ids: Optional[List[str]] = None, notebook_id: Optional[str] = None) -> str:
        """
        取得來源內容

        Args:
            source_ids: 指定的來源 ID 列表
            notebook_id: 筆記本 ID

        Returns:
            合併的來源內容
        """
        if source_ids:
            sources = Source.query.filter(Source.id.in_(source_ids)).all()
        elif notebook_id:
            sources = Source.query.filter_by(notebook_id=notebook_id).all()
        else:
            return ""

        content_parts = []
        for source in sources:
            content_parts.append(f"### 來源: {source.name}\n\n{source.content}")

        return "\n\n---\n\n".join(content_parts)

    def generate_summary(self, source_ids: Optional[List[str]] = None, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """生成摘要"""
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()
        prompt = StudioPrompts.SUMMARY.format(content=content)

        try:
            summary = ai_service.generate(prompt)
            return {"summary": summary, "type": "summary"}
        except Exception as e:
            logger.error(f"摘要生成失敗: {e}")
            return {"error": str(e)}

    def generate_mindmap(self, source_ids: Optional[List[str]] = None, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """生成心智圖（包含 JSON 和 Mermaid 格式）"""
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()
        prompt = StudioPrompts.MINDMAP.format(content=content)

        try:
            result = ai_service.generate_json(prompt)

            # 轉換為 Mermaid 格式
            mermaid_code = self._convert_to_mermaid(result)
            result["mermaid"] = mermaid_code

            # 兼容舊格式（如果使用新格式）
            if "central" in result and isinstance(result["central"], dict):
                result["central_text"] = result["central"].get("text", "")
            elif "central" in result and isinstance(result["central"], str):
                result["central_text"] = result["central"]

            return {"data": result, "type": "mindmap"}
        except Exception as e:
            logger.error(f"心智圖生成失敗: {e}")
            return {"error": str(e)}

    def _convert_to_mermaid(self, mindmap_data: Dict) -> str:
        """將心智圖 JSON 轉換為 Mermaid 格式"""
        lines = ["mindmap"]

        # 處理中心節點
        central = mindmap_data.get("central", {})
        if isinstance(central, dict):
            central_text = central.get("text", "中心主題")
        else:
            central_text = str(central)

        lines.append(f"  root(({central_text}))")

        # 處理分支
        branches = mindmap_data.get("branches", [])
        for branch in branches:
            self._add_mermaid_node(lines, branch, indent=2)

        return "\n".join(lines)

    def _add_mermaid_node(self, lines: list, node: Dict, indent: int = 2):
        """遞迴加入 Mermaid 節點"""
        # 取得節點文字（兼容新舊格式）
        text = node.get("text") or node.get("name", "")
        if not text:
            return

        # 生成縮排
        prefix = "  " * indent

        # 加入節點（使用圓角矩形）
        lines.append(f"{prefix}{text}")

        # 處理子節點
        children = node.get("children", [])
        for child in children:
            self._add_mermaid_node(lines, child, indent + 1)

    def generate_flashcards(self, count: int = 10, source_ids: Optional[List[str]] = None, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """生成學習卡"""
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()
        prompt = StudioPrompts.FLASHCARDS.format(content=content, count=count)

        try:
            result = ai_service.generate_json(prompt)
            return {"data": result, "type": "flashcards"}
        except Exception as e:
            logger.error(f"學習卡生成失敗: {e}")
            return {"error": str(e)}

    def generate_quiz(self, count: int = 10, source_ids: Optional[List[str]] = None, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """生成測驗"""
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()
        prompt = StudioPrompts.QUIZ.format(content=content, count=count)

        try:
            result = ai_service.generate_json(prompt)
            return {"data": result, "type": "quiz"}
        except Exception as e:
            logger.error(f"測驗生成失敗: {e}")
            return {"error": str(e)}

    def generate_report(self, source_ids: Optional[List[str]] = None, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """生成報告"""
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()
        prompt = StudioPrompts.REPORT.format(content=content)

        try:
            report = ai_service.generate(prompt)
            return {"content": report, "type": "report"}
        except Exception as e:
            logger.error(f"報告生成失敗: {e}")
            return {"error": str(e)}

    def generate_datatable(self, source_ids: Optional[List[str]] = None, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """生成資料表"""
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()
        prompt = StudioPrompts.DATATABLE.format(content=content)

        try:
            result = ai_service.generate_json(prompt)
            return {"data": result, "type": "datatable"}
        except Exception as e:
            logger.error(f"資料表生成失敗: {e}")
            return {"error": str(e)}

    def generate_presentation(
        self,
        source_ids: Optional[List[str]] = None,
        notebook_id: Optional[str] = None,
        slide_count: int = 8,
        with_images: bool = True,
        export_pptx: bool = False
    ) -> Dict[str, Any]:
        """
        生成專業簡報

        Args:
            source_ids: 來源 ID 列表
            notebook_id: 筆記本 ID
            slide_count: 簡報頁數
            with_images: 是否生成配圖
            export_pptx: 是否導出 PPTX 檔案

        Returns:
            簡報資料，包含文字內容和配圖
        """
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()

        try:
            # 步驟 1: 生成專業大綱
            logger.info("步驟 1: 生成簡報大綱")
            outline = self._generate_presentation_outline(content, slide_count, ai_service)

            # 步驟 2: 展開大綱為頁面列表
            pages = self._flatten_outline(outline)
            logger.info(f"大綱已展開為 {len(pages)} 頁")

            # 步驟 3: 為每頁生成詳細描述
            logger.info("步驟 2: 生成每頁描述")
            page_descriptions = self._generate_page_descriptions(content, outline, pages, ai_service)

            # 步驟 4: 組建簡報資料結構
            presentation_data = self._build_presentation_data(outline, pages, page_descriptions)

            # 步驟 5: 如果需要生成配圖
            if with_images:
                logger.info("步驟 3: 生成簡報配圖")
                presentation_data = self._generate_professional_slide_images(
                    presentation_data, outline, ai_service
                )

            # 步驟 6: 如果需要導出 PPTX
            if export_pptx and PPTX_EXPORT_AVAILABLE:
                logger.info("步驟 4: 導出 PPTX 檔案")
                pptx_base64 = self._export_to_pptx(presentation_data)
                presentation_data["pptx_file"] = pptx_base64

            return {"data": presentation_data, "type": "presentation"}

        except Exception as e:
            logger.error(f"簡報生成失敗: {e}")
            return {"error": str(e)}

    def _generate_presentation_outline(self, content: str, slide_count: int, ai_service) -> List[Dict]:
        """生成簡報大綱"""
        prompt = StudioPrompts.PRESENTATION_OUTLINE.format(
            content=content,
            slide_count=slide_count
        )
        outline = ai_service.generate_json(prompt)
        return outline

    def _flatten_outline(self, outline: List[Dict]) -> List[Dict]:
        """展開大綱結構為頁面列表"""
        pages = []
        for item in outline:
            if "part" in item and "pages" in item:
                # 這是一個章節，展開其頁面
                for page in item["pages"]:
                    page_with_part = page.copy()
                    page_with_part["part"] = item["part"]
                    pages.append(page_with_part)
            else:
                # 這是直接的頁面
                pages.append(item)
        return pages

    def _generate_page_descriptions(self, content: str, outline: List[Dict],
                                     pages: List[Dict], ai_service) -> List[str]:
        """為每頁生成詳細描述"""
        descriptions = []
        outline_json = json.dumps(outline, ensure_ascii=False, indent=2)

        for i, page in enumerate(pages):
            page_index = i + 1
            page_outline = json.dumps(page, ensure_ascii=False)

            # 判斷是否為第一頁
            is_first_page = (page_index == 1)
            first_page_note = "**除非特殊要求，第一頁的內容需要保持極簡，只放標題副標題以及演講人等，不添加任何其他素材。**" if is_first_page else ""
            subtitle_example = "副標題：簡報副標題" if is_first_page else ""

            # 取得章節資訊
            part_info = f"此頁面屬於：{page.get('part', '')}" if 'part' in page else ""

            prompt = StudioPrompts.PRESENTATION_PAGE_DESCRIPTION.format(
                content=content[:5000],  # 限制內容長度
                outline=outline_json,
                part_info=part_info,
                page_index=page_index,
                page_outline=page_outline,
                first_page_note=first_page_note,
                example_title=page.get('title', '範例標題'),
                subtitle_example=subtitle_example
            )

            try:
                description = ai_service.generate(prompt)
                descriptions.append(description.strip())
                logger.debug(f"第 {page_index} 頁描述生成完成")
            except Exception as e:
                logger.error(f"第 {page_index} 頁描述生成失敗: {e}")
                descriptions.append(f"頁面標題：{page.get('title', '未命名')}\n\n頁面文字：\n- 內容生成中...")

        return descriptions

    def _build_presentation_data(self, outline: List[Dict], pages: List[Dict],
                                  descriptions: List[str]) -> Dict[str, Any]:
        """組建簡報資料結構"""
        # 取得簡報標題
        title = "簡報"
        if pages and pages[0].get('title'):
            title = pages[0]['title']

        slides = []
        for i, (page, description) in enumerate(zip(pages, descriptions)):
            slide_data = {
                "slide_number": i + 1,
                "title": page.get('title', ''),
                "type": "title" if i == 0 else "content",
                "points": page.get('points', []),
                "description": description,
                "part": page.get('part', ''),
                "image": None
            }

            # 解析描述內容
            content_lines = []
            for line in description.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('• '):
                    content_lines.append(line)
                elif line.startswith('頁面文字：'):
                    continue
                elif not line.startswith('頁面標題：') and line:
                    content_lines.append(line)

            slide_data["content"] = '\n'.join(content_lines[:10])  # 最多 10 行
            slides.append(slide_data)

        return {
            "title": title,
            "slides": slides,
            "outline": outline,
            "total_pages": len(slides)
        }

    def _generate_professional_slide_images(self, presentation_data: Dict,
                                             outline: List[Dict], ai_service) -> Dict:
        """使用專業提示詞為簡報每頁生成配圖"""
        slides = presentation_data.get("slides", [])
        outline_text = self._generate_outline_text(outline)

        for slide in slides:
            page_index = slide.get("slide_number", 1)
            page_desc = slide.get("description", "")

            # 取得當前章節
            current_section = slide.get("part", "") or slide.get("title", "")

            # 判斷是否為封面頁
            is_title_page = (page_index == 1)
            first_page_design_note = StudioPrompts.PRESENTATION_TITLE_PAGE_DESIGN if is_title_page else ""

            # 生成專業圖片提示詞
            image_prompt = StudioPrompts.PRESENTATION_IMAGE_GENERATION.format(
                page_desc=page_desc,
                outline_text=outline_text,
                current_section=current_section,
                first_page_design_note=first_page_design_note
            )

            try:
                # 生成圖片
                image_base64 = ai_service.generate_image(
                    image_prompt,
                    size="1792x1024",  # 16:9 比例
                    style="vivid"
                )

                slide["image"] = image_base64
                slide["image_prompt"] = image_prompt
                logger.info(f"第 {page_index} 頁專業配圖生成成功")

            except Exception as e:
                logger.error(f"第 {page_index} 頁配圖生成失敗: {e}")
                slide["image"] = None
                slide["image_error"] = str(e)

        return presentation_data

    def _generate_outline_text(self, outline: List[Dict]) -> str:
        """將大綱轉換為文字格式"""
        text_parts = []
        for i, item in enumerate(outline, 1):
            if "part" in item and "pages" in item:
                text_parts.append(f"{i}. {item['part']}")
            else:
                text_parts.append(f"{i}. {item.get('title', '未命名')}")
        return "\n".join(text_parts)

    def _export_to_pptx(self, presentation_data: Dict) -> Optional[str]:
        """導出為 PPTX 檔案"""
        if not PPTX_EXPORT_AVAILABLE:
            logger.warning("PPTX 導出功能不可用")
            return None

        try:
            builder = PPTXBuilder()
            builder.build_from_presentation_data(presentation_data)
            return builder.save_to_base64()
        except Exception as e:
            logger.error(f"PPTX 導出失敗: {e}")
            return None

    def _generate_slide_images(self, presentation_data: Dict, ai_service) -> Dict:
        """
        為簡報每頁生成配圖（舊版方法，保留兼容性）

        Args:
            presentation_data: 簡報資料
            ai_service: AI 服務實例

        Returns:
            包含圖片的簡報資料
        """
        slides = presentation_data.get("slides", [])
        title = presentation_data.get("title", "簡報")

        for slide in slides:
            image_prompt = slide.get("image_prompt", "")

            # 跳過沒有 image_prompt 的頁面
            if not image_prompt:
                slide["image"] = None
                continue

            try:
                # 優化圖片提示詞
                enhanced_prompt = self._enhance_image_prompt(
                    image_prompt,
                    title,
                    slide.get("content", ""),
                    ai_service
                )

                # 生成圖片
                image_base64 = ai_service.generate_image(
                    enhanced_prompt,
                    size="1792x1024",  # 簡報常用的 16:9 比例
                    style="vivid"
                )

                slide["image"] = image_base64
                slide["enhanced_prompt"] = enhanced_prompt
                logger.info(f"第 {slide.get('slide_number')} 頁配圖生成成功")

            except Exception as e:
                logger.error(f"第 {slide.get('slide_number')} 頁配圖生成失敗: {e}")
                slide["image"] = None
                slide["image_error"] = str(e)

        return presentation_data

    def _enhance_image_prompt(
        self,
        original_prompt: str,
        topic: str,
        slide_content: str,
        ai_service
    ) -> str:
        """優化圖片生成提示詞"""
        try:
            prompt = StudioPrompts.IMAGE_PROMPT_ENHANCE.format(
                original_prompt=original_prompt,
                topic=topic,
                slide_content=slide_content[:200]  # 限制內容長度
            )
            enhanced = ai_service.generate(prompt)
            return enhanced.strip()
        except Exception as e:
            logger.warning(f"提示詞優化失敗，使用原始提示詞: {e}")
            return original_prompt

    def generate_infographic(
        self,
        source_ids: Optional[List[str]] = None,
        notebook_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成資訊圖表

        Args:
            source_ids: 來源 ID 列表
            notebook_id: 筆記本 ID

        Returns:
            資訊圖表資料，包含數據和配圖
        """
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()

        # 先提取資料表
        datatable_result = self.generate_datatable(source_ids, notebook_id)
        if "error" in datatable_result:
            return datatable_result

        # 生成資訊圖表配圖
        try:
            data = datatable_result.get("data", {})
            title = data.get("title", "資訊圖表")

            image_prompt = f"Professional infographic about {title}, data visualization, charts and graphs, modern flat design, clean layout, business style"

            image_base64 = ai_service.generate_image(
                image_prompt,
                size="1024x1024",
                style="vivid"
            )

            return {
                "data": data,
                "image": image_base64,
                "type": "infographic"
            }
        except Exception as e:
            logger.error(f"資訊圖表配圖生成失敗: {e}")
            return {
                "data": datatable_result.get("data"),
                "image": None,
                "type": "infographic",
                "image_error": str(e)
            }


# 全局實例
_studio_service: Optional[StudioService] = None


def get_studio_service() -> StudioService:
    """取得工作室服務實例"""
    global _studio_service
    if _studio_service is None:
        _studio_service = StudioService()
    return _studio_service
