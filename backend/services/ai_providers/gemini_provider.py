"""
Gemini AI Provider
支援文字生成、嵌入向量、圖片生成（使用多模態模型）
"""
import base64
import io
import json
import logging
from typing import Generator, List, Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_provider import BaseTextProvider, BaseEmbeddingProvider, BaseImageProvider

logger = logging.getLogger(__name__)

# 嘗試導入新版 SDK
try:
    from google import genai as genai_client
    from google.genai import types as genai_types
    HAS_NEW_SDK = True
except ImportError:
    HAS_NEW_SDK = False
    logger.warning("新版 google-genai SDK 未安裝，圖片生成功能可能受限")


class GeminiProvider(BaseTextProvider, BaseEmbeddingProvider, BaseImageProvider):
    """Gemini AI 提供者"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        embedding_model: str = "models/embedding-001",
        image_model: str = "gemini-2.0-flash-exp-image-generation"
    ):
        """
        初始化 Gemini Provider

        Args:
            api_key: Gemini API Key
            model: 文字生成模型名稱
            embedding_model: 嵌入模型名稱
            image_model: 圖片生成模型名稱（多模態模型，用於生成圖片）
        """
        genai.configure(api_key=api_key)
        self.api_key = api_key
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        self.embedding_model = embedding_model
        self.image_model = image_model

        # 初始化新版 SDK 的 Client（用於圖片生成）
        self._genai_client = None
        if HAS_NEW_SDK:
            try:
                self._genai_client = genai_client.Client(api_key=api_key)
                logger.info(f"新版 GenAI Client 初始化完成，圖片模型: {image_model}")
            except Exception as e:
                logger.warning(f"新版 GenAI Client 初始化失敗: {e}")

        logger.info(f"Gemini Provider 初始化完成，文字模型: {model}, 圖片模型: {image_model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """同步生成文字"""
        try:
            messages = []

            if system_prompt:
                # Gemini 使用對話方式處理系統提示
                messages.append({"role": "user", "parts": [system_prompt]})
                messages.append({"role": "model", "parts": ["了解，我會按照指示進行。"]})

            messages.append({"role": "user", "parts": [prompt]})

            response = self.model.generate_content(messages)
            return response.text

        except Exception as e:
            logger.error(f"Gemini 生成失敗: {e}")
            raise

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """串流生成文字"""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "user", "parts": [system_prompt]})
                messages.append({"role": "model", "parts": ["了解，我會按照指示進行。"]})

            messages.append({"role": "user", "parts": [prompt]})

            response = self.model.generate_content(messages, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini 串流生成失敗: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """生成 JSON 格式的回應"""
        json_prompt = f"""請用 JSON 格式回應，不要包含任何其他文字或 markdown 標記。

{prompt}"""

        if system_prompt:
            system_prompt = f"{system_prompt}\n\n重要：請用純 JSON 格式回應。"
        else:
            system_prompt = "重要：請用純 JSON 格式回應，不要包含任何其他文字或 markdown 標記。"

        response = self.generate(json_prompt, system_prompt)

        # 清理回應，移除可能的 markdown 標記
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {e}, 原始回應: {response}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_embedding(self, text: str) -> List[float]:
        """取得文字的向量嵌入"""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']

        except Exception as e:
            logger.error(f"Gemini 嵌入生成失敗: {e}")
            raise

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量取得文字的向量嵌入"""
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None
    ) -> str:
        """
        使用 Gemini 多模態模型生成圖片

        Args:
            prompt: 圖片描述提示詞
            size: 圖片尺寸 (例如 "1024x1024", "1920x1080")
            style: 圖片風格

        Returns:
            圖片的 Base64 編碼
        """
        if not HAS_NEW_SDK or not self._genai_client:
            logger.error("新版 google-genai SDK 未安裝或初始化失敗")
            raise Exception("圖片生成功能需要安裝 google-genai 套件：pip install google-genai")

        try:
            # 構建提示詞
            full_prompt = prompt
            if style:
                full_prompt = f"{prompt}, {style} style"

            # 解析尺寸並獲取寬高比
            width, height = map(int, size.split('x'))
            aspect_ratio = self._get_aspect_ratio(width, height)

            logger.info(f"使用多模態模型生成圖片: {self.image_model}, 寬高比: {aspect_ratio}")
            logger.debug(f"提示詞: {full_prompt[:100]}...")

            # 使用多模態方式生成圖片
            response = self._genai_client.models.generate_content(
                model=self.image_model,
                contents=[full_prompt],
                config=genai_types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE'],
                    image_config=genai_types.ImageConfig(
                        aspect_ratio=aspect_ratio
                    )
                )
            )

            # 從回應中提取圖片
            last_image = None
            for i, part in enumerate(response.parts):
                if part.text is not None:
                    logger.debug(f"Part {i}: TEXT - {part.text[:50] if len(part.text) > 50 else part.text}")
                else:
                    try:
                        image = part.as_image()
                        if image:
                            logger.debug(f"成功從 part {i} 提取圖片")
                            last_image = image
                    except Exception as e:
                        logger.debug(f"Part {i}: 提取圖片失敗 - {str(e)}")

            if last_image:
                # 將 PIL Image 轉換為 Base64
                buffer = io.BytesIO()
                last_image.save(buffer, format='PNG')
                buffer.seek(0)
                return base64.b64encode(buffer.read()).decode('utf-8')

            raise Exception("圖片生成失敗：回應中沒有找到圖片")

        except Exception as e:
            logger.error(f"Gemini 圖片生成失敗: {e}")
            raise

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """根據尺寸返回寬高比"""
        ratio = width / height
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        else:
            return "1:1"

    def generate_images(
        self,
        prompts: List[str],
        size: str = "1024x1024",
        style: Optional[str] = None
    ) -> List[str]:
        """批量生成圖片"""
        images = []
        for prompt in prompts:
            try:
                image = self.generate_image(prompt, size, style)
                images.append(image)
            except Exception as e:
                logger.error(f"批量生成圖片失敗: {e}")
                images.append("")
        return images
