"""
AI 服務管理器 - 支援多個 AI 提供商
"""
import logging
import os
from threading import Lock
from typing import Optional, Union, Dict, Any, List

from config import get_config
from .ai_providers import (
    GeminiProvider, OpenAIProvider, AnthropicProvider,
    OllamaProvider, GroqProvider, DeepSeekProvider,
    BaseTextProvider, BaseEmbeddingProvider, BaseImageProvider,
    PROVIDER_MAP
)

logger = logging.getLogger(__name__)

# 全局單例
_instance: Optional['AIServiceManager'] = None
_lock = Lock()


class AIServiceManager:
    """
    AI 服務管理器
    管理多個 AI Provider 的初始化和切換
    """

    # 支援的提供商列表
    SUPPORTED_PROVIDERS = ['gemini', 'openai', 'anthropic', 'ollama', 'groq', 'deepseek']

    def __init__(self):
        self._text_provider: Optional[BaseTextProvider] = None
        self._embedding_provider: Optional[BaseEmbeddingProvider] = None
        self._image_provider: Optional[BaseImageProvider] = None
        self._provider_type: Optional[str] = None
        self._provider_configs: Dict[str, Dict[str, Any]] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """初始化 AI Providers"""
        config = get_config()
        provider_type = config.AI_PROVIDER.lower()

        # 儲存各提供商配置
        self._load_provider_configs()

        # 初始化預設提供商
        if provider_type == 'openai':
            self._init_openai_provider(config)
        elif provider_type == 'anthropic':
            self._init_anthropic_provider()
        elif provider_type == 'ollama':
            self._init_ollama_provider()
        elif provider_type == 'groq':
            self._init_groq_provider()
        elif provider_type == 'deepseek':
            self._init_deepseek_provider()
        else:
            self._init_gemini_provider(config)

        self._provider_type = provider_type

    def _load_provider_configs(self):
        """載入各提供商配置"""
        self._provider_configs = {
            'gemini': {
                'api_key': os.getenv('GEMINI_API_KEY', ''),
                'model': os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'),
                'embedding_model': os.getenv('GEMINI_EMBEDDING_MODEL', 'models/embedding-001'),
            },
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', ''),
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
                'embedding_model': os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small'),
            },
            'anthropic': {
                'api_key': os.getenv('ANTHROPIC_API_KEY', ''),
                'model': os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514'),
            },
            'ollama': {
                'host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
                'model': os.getenv('OLLAMA_MODEL', 'llama3.2'),
                'embedding_model': os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text'),
            },
            'groq': {
                'api_key': os.getenv('GROQ_API_KEY', ''),
                'model': os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            },
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
                'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            },
        }

    def _init_gemini_provider(self, config):
        """初始化 Gemini Provider"""
        if not config.GEMINI_API_KEY:
            logger.warning("Gemini API Key 未設置")
            return

        try:
            provider = GeminiProvider(
                api_key=config.GEMINI_API_KEY,
                model=config.GEMINI_MODEL,
                embedding_model=config.GEMINI_EMBEDDING_MODEL,
                image_model=config.GEMINI_IMAGE_MODEL
            )
            self._text_provider = provider
            self._embedding_provider = provider
            self._image_provider = provider
            logger.info("Gemini Provider 初始化成功")
        except Exception as e:
            logger.error(f"Gemini Provider 初始化失敗: {e}")

    def _init_openai_provider(self, config):
        """初始化 OpenAI Provider"""
        if not config.OPENAI_API_KEY:
            logger.warning("OpenAI API Key 未設置")
            return

        try:
            provider = OpenAIProvider(
                api_key=config.OPENAI_API_KEY,
                model=config.OPENAI_MODEL,
                embedding_model=config.OPENAI_EMBEDDING_MODEL,
                image_model=config.OPENAI_IMAGE_MODEL
            )
            self._text_provider = provider
            self._embedding_provider = provider
            self._image_provider = provider
            logger.info("OpenAI Provider 初始化成功")
        except Exception as e:
            logger.error(f"OpenAI Provider 初始化失敗: {e}")

    def _init_anthropic_provider(self):
        """初始化 Anthropic Provider"""
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning("Anthropic API Key 未設置")
            return

        try:
            provider = AnthropicProvider(
                api_key=api_key,
                model=os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
            )
            self._text_provider = provider
            # Anthropic 不支援 embedding，需要用其他提供商
            self._init_fallback_embedding()
            logger.info("Anthropic Provider 初始化成功")
        except Exception as e:
            logger.error(f"Anthropic Provider 初始化失敗: {e}")

    def _init_ollama_provider(self):
        """初始化 Ollama Provider"""
        try:
            provider = OllamaProvider(
                host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
                model=os.getenv('OLLAMA_MODEL', 'llama3.2'),
                embedding_model=os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
            )

            if not provider.is_available():
                logger.warning("Ollama 服務不可用")
                return

            self._text_provider = provider
            self._embedding_provider = provider
            logger.info("Ollama Provider 初始化成功")
        except Exception as e:
            logger.error(f"Ollama Provider 初始化失敗: {e}")

    def _init_groq_provider(self):
        """初始化 Groq Provider"""
        api_key = os.getenv('GROQ_API_KEY', '')
        if not api_key:
            logger.warning("Groq API Key 未設置")
            return

        try:
            provider = GroqProvider(
                api_key=api_key,
                model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
            )
            self._text_provider = provider
            # Groq 不支援 embedding，需要用其他提供商
            self._init_fallback_embedding()
            logger.info("Groq Provider 初始化成功")
        except Exception as e:
            logger.error(f"Groq Provider 初始化失敗: {e}")

    def _init_deepseek_provider(self):
        """初始化 DeepSeek Provider"""
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        if not api_key:
            logger.warning("DeepSeek API Key 未設置")
            return

        try:
            provider = DeepSeekProvider(
                api_key=api_key,
                model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
            )
            self._text_provider = provider
            # DeepSeek 不支援 embedding，需要用其他提供商
            self._init_fallback_embedding()
            logger.info("DeepSeek Provider 初始化成功")
        except Exception as e:
            logger.error(f"DeepSeek Provider 初始化失敗: {e}")

    @staticmethod
    def _is_valid_api_key(key: str) -> bool:
        """檢查 API Key 是否有效（非空且非佔位符）"""
        if not key:
            return False
        placeholders = ['your-', '-here', 'replace-', 'example', 'placeholder', 'xxx']
        return not any(p in key.lower() for p in placeholders)

    def _init_fallback_embedding(self):
        """初始化備用 embedding provider"""
        config = get_config()

        # 最優先：使用獨立 Embedding 配置（支援任何 OpenAI 相容 API）
        if self._is_valid_api_key(config.EMBEDDING_API_KEY) and config.EMBEDDING_API_BASE and config.EMBEDDING_MODEL:
            try:
                self._embedding_provider = OpenAIProvider(
                    api_key=config.EMBEDDING_API_KEY,
                    model=config.EMBEDDING_MODEL,
                    embedding_model=config.EMBEDDING_MODEL,
                    base_url=config.EMBEDDING_API_BASE
                )
                logger.info(f"使用獨立 Embedding 配置: {config.EMBEDDING_API_BASE} / {config.EMBEDDING_MODEL}")
                return
            except Exception as e:
                logger.warning(f"獨立 Embedding 配置初始化失敗: {e}")

        # 其次使用 OpenAI embedding
        if self._is_valid_api_key(config.OPENAI_API_KEY):
            try:
                self._embedding_provider = OpenAIProvider(
                    api_key=config.OPENAI_API_KEY,
                    model=config.OPENAI_MODEL,
                    embedding_model=config.OPENAI_EMBEDDING_MODEL
                )
                logger.info("使用 OpenAI 作為 embedding 備用")
                return
            except:
                pass

        # 再使用 Gemini
        if self._is_valid_api_key(config.GEMINI_API_KEY):
            try:
                self._embedding_provider = GeminiProvider(
                    api_key=config.GEMINI_API_KEY,
                    model=config.GEMINI_MODEL,
                    embedding_model=config.GEMINI_EMBEDDING_MODEL
                )
                logger.info("使用 Gemini 作為 embedding 備用")
                return
            except:
                pass

        # 最後嘗試 Ollama
        try:
            ollama = OllamaProvider()
            if ollama.is_available():
                self._embedding_provider = ollama
                logger.info("使用 Ollama 作為 embedding 備用")
        except:
            logger.warning("無法初始化 embedding provider，RAG 功能將不可用")

    @property
    def text_provider(self) -> Optional[BaseTextProvider]:
        """取得文字生成 Provider"""
        return self._text_provider

    @property
    def embedding_provider(self) -> Optional[BaseEmbeddingProvider]:
        """取得嵌入 Provider"""
        return self._embedding_provider

    @property
    def image_provider(self) -> Optional[BaseImageProvider]:
        """取得圖片生成 Provider"""
        return self._image_provider

    @property
    def provider_type(self) -> Optional[str]:
        """取得當前 Provider 類型"""
        return self._provider_type

    @property
    def is_ready(self) -> bool:
        """檢查 Provider 是否就緒"""
        return self._text_provider is not None

    def switch_provider(
        self,
        provider_type: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        切換 AI Provider

        Args:
            provider_type: 提供商類型
            api_key: API Key
            model: 模型名稱 (可選)
            **kwargs: 其他提供商特定參數
        """
        provider_type = provider_type.lower()

        if provider_type not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"不支援的提供商: {provider_type}")

        config = get_config()

        if provider_type == 'gemini':
            key = api_key or config.GEMINI_API_KEY
            provider = GeminiProvider(
                api_key=key,
                model=model or config.GEMINI_MODEL,
                embedding_model=config.GEMINI_EMBEDDING_MODEL,
                image_model=config.GEMINI_IMAGE_MODEL
            )
            self._text_provider = provider
            self._embedding_provider = provider
            self._image_provider = provider

        elif provider_type == 'openai':
            key = api_key or config.OPENAI_API_KEY
            provider = OpenAIProvider(
                api_key=key,
                model=model or config.OPENAI_MODEL,
                embedding_model=config.OPENAI_EMBEDDING_MODEL,
                image_model=config.OPENAI_IMAGE_MODEL
            )
            self._text_provider = provider
            self._embedding_provider = provider
            self._image_provider = provider

        elif provider_type == 'anthropic':
            key = api_key or os.getenv('ANTHROPIC_API_KEY', '')
            provider = AnthropicProvider(
                api_key=key,
                model=model or os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
            )
            self._text_provider = provider
            self._init_fallback_embedding()

        elif provider_type == 'ollama':
            provider = OllamaProvider(
                host=kwargs.get('host', os.getenv('OLLAMA_HOST', 'http://localhost:11434')),
                model=model or os.getenv('OLLAMA_MODEL', 'llama3.2'),
                embedding_model=kwargs.get('embedding_model', 'nomic-embed-text')
            )
            self._text_provider = provider
            self._embedding_provider = provider

        elif provider_type == 'groq':
            key = api_key or os.getenv('GROQ_API_KEY', '')
            provider = GroqProvider(
                api_key=key,
                model=model or os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
            )
            self._text_provider = provider
            self._init_fallback_embedding()

        elif provider_type == 'deepseek':
            key = api_key or os.getenv('DEEPSEEK_API_KEY', '')
            provider = DeepSeekProvider(
                api_key=key,
                model=model or os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
            )
            self._text_provider = provider
            self._init_fallback_embedding()

        self._provider_type = provider_type
        logger.info(f"已切換至 {provider_type} Provider")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文字"""
        if not self._text_provider:
            raise RuntimeError("AI Provider 未初始化")
        return self._text_provider.generate(prompt, system_prompt)

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None):
        """串流生成文字"""
        if not self._text_provider:
            raise RuntimeError("AI Provider 未初始化")
        return self._text_provider.generate_stream(prompt, system_prompt)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """生成 JSON"""
        if not self._text_provider:
            raise RuntimeError("AI Provider 未初始化")
        return self._text_provider.generate_json(prompt, system_prompt)

    def get_embedding(self, text: str):
        """取得向量嵌入"""
        if not self._embedding_provider:
            raise RuntimeError("Embedding Provider 未初始化")
        return self._embedding_provider.get_embedding(text)

    def get_embeddings(self, texts: list):
        """批量取得向量嵌入"""
        if not self._embedding_provider:
            raise RuntimeError("Embedding Provider 未初始化")
        return self._embedding_provider.get_embeddings(texts)

    def generate_image(self, prompt: str, size: str = "1024x1024", style: Optional[str] = None) -> str:
        """生成圖片"""
        if not self._image_provider:
            raise RuntimeError("Image Provider 未初始化")
        return self._image_provider.generate_image(prompt, size, style)

    def generate_images(self, prompts: list, size: str = "1024x1024", style: Optional[str] = None) -> list:
        """批量生成圖片"""
        if not self._image_provider:
            raise RuntimeError("Image Provider 未初始化")
        return self._image_provider.generate_images(prompts, size, style)

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """取得可用的提供商列表"""
        config = get_config()
        providers = []

        # Gemini
        providers.append({
            'id': 'gemini',
            'name': 'Google Gemini',
            'available': self._is_valid_api_key(config.GEMINI_API_KEY),
            'supports_embedding': True,
            'supports_image': True,
            'models': ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-1.5-pro']
        })

        # OpenAI
        providers.append({
            'id': 'openai',
            'name': 'OpenAI',
            'available': self._is_valid_api_key(config.OPENAI_API_KEY),
            'supports_embedding': True,
            'supports_image': True,
            'models': ['gpt-4o', 'gpt-4.1', 'gpt-4-turbo', 'gpt-3.5-turbo']
        })

        # Anthropic
        providers.append({
            'id': 'anthropic',
            'name': 'Anthropic Claude',
            'available': self._is_valid_api_key(os.getenv('ANTHROPIC_API_KEY', '')),
            'supports_embedding': False,
            'supports_image': False,
            'models': AnthropicProvider.AVAILABLE_MODELS
        })

        # Ollama
        ollama_available = False
        try:
            ollama = OllamaProvider()
            ollama_available = ollama.is_available()
        except:
            pass

        providers.append({
            'id': 'ollama',
            'name': 'Ollama (本地)',
            'available': ollama_available,
            'supports_embedding': True,
            'supports_image': False,
            'models': ['llama3.2', 'llama3.1', 'mistral', 'mixtral', 'qwen2.5']
        })

        # Groq
        providers.append({
            'id': 'groq',
            'name': 'Groq (高速)',
            'available': self._is_valid_api_key(os.getenv('GROQ_API_KEY', '')),
            'supports_embedding': False,
            'supports_image': False,
            'models': GroqProvider.AVAILABLE_MODELS
        })

        # DeepSeek
        providers.append({
            'id': 'deepseek',
            'name': 'DeepSeek (推理)',
            'available': self._is_valid_api_key(os.getenv('DEEPSEEK_API_KEY', '')),
            'supports_embedding': False,
            'supports_image': False,
            'models': DeepSeekProvider.AVAILABLE_MODELS
        })

        return providers

    def get_current_config(self) -> Dict[str, Any]:
        """取得當前配置"""
        return {
            'provider': self._provider_type,
            'is_ready': self.is_ready,
            'has_embedding': self._embedding_provider is not None,
            'has_image': self._image_provider is not None,
        }


def get_ai_service(force_new: bool = False) -> AIServiceManager:
    """
    取得 AI 服務管理器單例

    Args:
        force_new: 是否強制建立新實例

    Returns:
        AIServiceManager 實例
    """
    global _instance

    if force_new:
        with _lock:
            _instance = None
            logger.info("強制重建 AI 服務管理器")

    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = AIServiceManager()
                logger.info("AI 服務管理器已初始化")

    return _instance


def clear_ai_service():
    """清除 AI 服務管理器單例"""
    global _instance
    with _lock:
        _instance = None
        logger.info("AI 服務管理器已清除")
