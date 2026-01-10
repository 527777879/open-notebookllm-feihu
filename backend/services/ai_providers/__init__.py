"""
AI Provider 抽象層 - 支援多個 AI 提供商
"""
from .base_provider import BaseTextProvider, BaseEmbeddingProvider, BaseImageProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .groq_provider import GroqProvider
from .deepseek_provider import DeepSeekProvider

__all__ = [
    # 基礎類別
    'BaseTextProvider',
    'BaseEmbeddingProvider',
    'BaseImageProvider',
    # 提供商
    'GeminiProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'OllamaProvider',
    'GroqProvider',
    'DeepSeekProvider',
]

# 提供商映射
PROVIDER_MAP = {
    'gemini': GeminiProvider,
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
    'ollama': OllamaProvider,
    'groq': GroqProvider,
    'deepseek': DeepSeekProvider,
}
