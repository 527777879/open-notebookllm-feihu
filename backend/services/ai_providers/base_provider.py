"""
AI Provider 抽象基類
"""
from abc import ABC, abstractmethod
from typing import Generator, List, Optional


class BaseTextProvider(ABC):
    """文字生成 AI 提供者抽象基類"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        同步生成文字

        Args:
            prompt: 用戶提示詞
            system_prompt: 系統提示詞 (可選)

        Returns:
            生成的文字內容
        """
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """
        串流生成文字

        Args:
            prompt: 用戶提示詞
            system_prompt: 系統提示詞 (可選)

        Yields:
            文字片段
        """
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """
        生成 JSON 格式的回應

        Args:
            prompt: 用戶提示詞
            system_prompt: 系統提示詞 (可選)

        Returns:
            解析後的 JSON 字典
        """
        pass


class BaseEmbeddingProvider(ABC):
    """向量嵌入 AI 提供者抽象基類"""

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """
        取得文字的向量嵌入

        Args:
            text: 要嵌入的文字

        Returns:
            向量嵌入列表
        """
        pass

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        批量取得文字的向量嵌入

        Args:
            texts: 要嵌入的文字列表

        Returns:
            向量嵌入列表的列表
        """
        pass


class BaseImageProvider(ABC):
    """圖片生成 AI 提供者抽象基類"""

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None
    ) -> str:
        """
        生成圖片

        Args:
            prompt: 圖片描述提示詞
            size: 圖片尺寸 (如 "1024x1024", "1792x1024")
            style: 圖片風格 (如 "vivid", "natural")

        Returns:
            圖片的 Base64 編碼或 URL
        """
        pass

    @abstractmethod
    def generate_images(
        self,
        prompts: List[str],
        size: str = "1024x1024",
        style: Optional[str] = None
    ) -> List[str]:
        """
        批量生成圖片

        Args:
            prompts: 圖片描述提示詞列表
            size: 圖片尺寸
            style: 圖片風格

        Returns:
            圖片的 Base64 編碼或 URL 列表
        """
        pass
