"""
工作室輸出生成服務
"""
import logging
from typing import Dict, Any, List, Optional

from .ai_service_manager import get_ai_service
from .prompts import StudioPrompts
from models import Source

logger = logging.getLogger(__name__)


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
        """生成心智圖"""
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()
        prompt = StudioPrompts.MINDMAP.format(content=content)

        try:
            result = ai_service.generate_json(prompt)
            return {"data": result, "type": "mindmap"}
        except Exception as e:
            logger.error(f"心智圖生成失敗: {e}")
            return {"error": str(e)}

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
        with_images: bool = True
    ) -> Dict[str, Any]:
        """
        生成簡報

        Args:
            source_ids: 來源 ID 列表
            notebook_id: 筆記本 ID
            slide_count: 簡報頁數
            with_images: 是否生成配圖

        Returns:
            簡報資料，包含文字內容和配圖
        """
        content = self.get_sources_content(source_ids, notebook_id)
        if not content:
            return {"error": "沒有可用的來源內容"}

        ai_service = get_ai_service()

        # 生成簡報大綱
        prompt = StudioPrompts.PRESENTATION.format(content=content, slide_count=slide_count)

        try:
            result = ai_service.generate_json(prompt)

            # 如果需要生成配圖
            if with_images and result.get("slides"):
                result = self._generate_slide_images(result, ai_service)

            return {"data": result, "type": "presentation"}
        except Exception as e:
            logger.error(f"簡報生成失敗: {e}")
            return {"error": str(e)}

    def _generate_slide_images(self, presentation_data: Dict, ai_service) -> Dict:
        """
        為簡報每頁生成配圖

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
