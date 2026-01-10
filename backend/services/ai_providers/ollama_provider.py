"""
Ollama 本地模型 Provider
"""
import logging
import json
from typing import Optional, Generator, List

from .base_provider import BaseTextProvider, BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseTextProvider, BaseEmbeddingProvider):
    """Ollama 本地模型 Provider"""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2",
        embedding_model: str = "nomic-embed-text"
    ):
        self.host = host.rstrip('/')
        self.model = model
        self.embedding_model = embedding_model
        self._client = None

    @property
    def client(self):
        """延遲初始化 client"""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.host)
            except ImportError:
                raise ImportError("ollama 套件未安裝，請執行: pip install ollama")
        return self._client

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文字"""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat(
                model=self.model,
                messages=messages
            )

            return response['message']['content']

        except Exception as e:
            logger.error(f"Ollama 生成失敗: {e}")
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

            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

        except Exception as e:
            logger.error(f"Ollama 串流生成失敗: {e}")
            raise

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """生成 JSON"""
        json_system = "你必須以有效的 JSON 格式回應，不要添加任何其他文字。"
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

    def get_embedding(self, text: str) -> List[float]:
        """取得文字嵌入"""
        try:
            response = self.client.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            return response['embedding']

        except Exception as e:
            logger.error(f"Ollama 嵌入失敗: {e}")
            raise

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量取得嵌入"""
        return [self.get_embedding(text) for text in texts]

    def list_local_models(self) -> List[str]:
        """列出本地已安裝的模型"""
        try:
            response = self.client.list()
            return [model['name'] for model in response.get('models', [])]
        except Exception as e:
            logger.error(f"列出模型失敗: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """下載模型"""
        try:
            self.client.pull(model_name)
            return True
        except Exception as e:
            logger.error(f"下載模型失敗: {e}")
            return False

    def is_available(self) -> bool:
        """檢查 Ollama 服務是否可用"""
        try:
            import requests
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
