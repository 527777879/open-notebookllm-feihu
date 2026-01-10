"""
DeepSeek Provider - 支援推理模型
"""
import logging
import json
from typing import Optional, Generator, List

from .base_provider import BaseTextProvider

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseTextProvider):
    """DeepSeek Provider - 支援推理模型 (R1)"""

    # 可用模型
    AVAILABLE_MODELS = [
        "deepseek-chat",        # DeepSeek-V3 對話模型
        "deepseek-reasoner",    # DeepSeek-R1 推理模型
    ]

    API_BASE = "https://api.deepseek.com"

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        max_tokens: int = 4096
    ):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    @property
    def client(self):
        """延遲初始化 client (使用 OpenAI 相容 API)"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=f"{self.API_BASE}/v1"
                )
            except ImportError:
                raise ImportError("openai 套件未安裝，請執行: pip install openai")
        return self._client

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文字"""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens
            )

            content = response.choices[0].message.content

            # 如果是推理模型，可能包含思考過程
            if hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning = response.choices[0].message.reasoning_content
                if reasoning:
                    logger.debug(f"推理過程: {reasoning[:200]}...")

            return content

        except Exception as e:
            logger.error(f"DeepSeek 生成失敗: {e}")
            raise

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """串流生成文字"""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"DeepSeek 串流生成失敗: {e}")
            raise

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """生成 JSON"""
        json_system = "你必須以有效的 JSON 格式回應，不要添加任何其他文字或 markdown 標記。"
        if system_prompt:
            json_system = f"{system_prompt}\n\n{json_system}"

        response = self.generate(prompt, json_system)

        # 清理回應
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        return json.loads(response.strip())

    def generate_with_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        使用推理模型生成，同時返回推理過程

        Returns:
            {"content": "最終答案", "reasoning": "思考過程"}
        """
        try:
            # 使用推理模型
            original_model = self.model
            self.model = "deepseek-reasoner"

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens
            )

            self.model = original_model

            result = {
                "content": response.choices[0].message.content,
                "reasoning": None
            }

            # 提取推理過程
            if hasattr(response.choices[0].message, 'reasoning_content'):
                result["reasoning"] = response.choices[0].message.reasoning_content

            return result

        except Exception as e:
            logger.error(f"DeepSeek 推理生成失敗: {e}")
            self.model = original_model
            raise

    def chat(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None
    ) -> str:
        """多輪對話"""
        try:
            formatted_messages = []

            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})

            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"DeepSeek 對話失敗: {e}")
            raise

    @classmethod
    def list_models(cls) -> List[str]:
        """列出可用模型"""
        return cls.AVAILABLE_MODELS
