"""
DeepSeek Provider - 支援推理模型
"""
import logging
import json
from typing import Optional, Generator, List

from .base_provider import BaseTextProvider

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseTextProvider):
    """DeepSeek Provider - 支援推理模型 (R1/V4-Pro)"""

    # 推理模型集合
    REASONING_MODELS = {"deepseek-reasoner", "deepseek-v4-pro"}

    # JSON 生成降级模型（推理模型不适合结构化输出）
    JSON_FALLBACK_MODEL = "deepseek-v4-flash"

    # 可用模型
    AVAILABLE_MODELS = [
        "deepseek-chat",        # DeepSeek-V3 對話模型
        "deepseek-reasoner",    # DeepSeek-R1 推理模型
        "deepseek-v4-flash",    # DeepSeek-V4 快速對話模型
        "deepseek-v4-pro",      # DeepSeek-V4 推理模型
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

    def _is_reasoning_model(self) -> bool:
        """判斷當前模型是否為推理模型"""
        return self.model in self.REASONING_MODELS

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
        """串流生成文字（推理模型會先輸出思考過程，再輸出最終內容）"""
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
                delta = chunk.choices[0].delta

                # 推理模型：先輸出思考過程 (reasoning_content)
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    yield delta.reasoning_content

                # 最終回答內容 (content)
                if delta.content:
                    yield delta.content

        except Exception as e:
            logger.error(f"DeepSeek 串流生成失敗: {e}")
            raise

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """生成 JSON（推理模型自動降級為快速模型，避免超時和格式問題）"""
        json_system = "你必須以有效的 JSON 格式回應，不要添加任何其他文字或 markdown 標記。"
        if system_prompt:
            json_system = f"{system_prompt}\n\n{json_system}"

        # 推理模型不適合 JSON 結構化輸出，自動降級
        original_model = self.model
        if self._is_reasoning_model():
            self.model = self.JSON_FALLBACK_MODEL
            logger.info(f"generate_json: 推理模型 {original_model} 降級為 {self.model}")

        try:
            response = self.generate(prompt, json_system)
        finally:
            self.model = original_model

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
            # 如果當前已是推理模型則直接使用，否則切換到 deepseek-reasoner
            original_model = self.model
            if not self._is_reasoning_model():
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
