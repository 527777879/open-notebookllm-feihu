"""
OpenAI AI Provider
"""
import json
import logging
from typing import Generator, List, Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_provider import BaseTextProvider, BaseEmbeddingProvider, BaseImageProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseTextProvider, BaseEmbeddingProvider, BaseImageProvider):
    """OpenAI AI 提供者"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.1",
        embedding_model: str = "text-embedding-3-small",
        image_model: str = "dall-e-3",
        base_url: Optional[str] = None
    ):
        """
        初始化 OpenAI Provider

        Args:
            api_key: OpenAI API Key
            model: 文字生成模型名稱
            embedding_model: 嵌入模型名稱
            image_model: 圖片生成模型名稱
            base_url: API 基礎 URL (用於代理)
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=300.0,
            max_retries=2
        )
        self.model = model
        self.embedding_model = embedding_model
        self.image_model = image_model
        logger.info(f"OpenAI Provider 初始化完成，文字模型: {model}, 圖片模型: {image_model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """同步生成文字"""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI 生成失敗: {e}")
            raise

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """串流生成文字"""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI 串流生成失敗: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """生成 JSON 格式的回應"""
        try:
            messages = []

            json_system = "請用純 JSON 格式回應，不要包含任何其他文字或 markdown 標記。"
            if system_prompt:
                messages.append({"role": "system", "content": f"{system_prompt}\n\n{json_system}"})
            else:
                messages.append({"role": "system", "content": json_system})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenAI JSON 生成失敗: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_embedding(self, text: str) -> List[float]:
        """取得文字的向量嵌入"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"OpenAI 嵌入生成失敗: {e}")
            raise

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量取得文字的向量嵌入"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]

        except Exception as e:
            logger.error(f"OpenAI 批量嵌入生成失敗: {e}")
            raise

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
        使用 DALL-E 生成圖片

        Args:
            prompt: 圖片描述提示詞
            size: 圖片尺寸 (1024x1024, 1792x1024, 1024x1792)
            style: 圖片風格 (vivid, natural)

        Returns:
            圖片的 Base64 編碼或 URL
        """
        try:
            # DALL-E 3 支援的尺寸
            valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
            if size not in valid_sizes:
                size = "1024x1024"

            # 預設風格
            image_style = style if style in ["vivid", "natural"] else "vivid"

            response = self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=size,
                style=image_style,
                response_format="b64_json",
                n=1
            )

            # 返回 Base64 編碼
            return response.data[0].b64_json

        except Exception as e:
            logger.error(f"OpenAI 圖片生成失敗: {e}")
            raise

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
