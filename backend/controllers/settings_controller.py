"""
設定控制器 - 支援多 AI 提供商
"""
import os
from flask import request, jsonify
from . import settings_bp
from services.ai_service_manager import get_ai_service, clear_ai_service
from config import get_config


@settings_bp.route('', methods=['GET'])
def get_settings():
    """取得設定"""
    config = get_config()
    ai_service = get_ai_service()

    return jsonify({
        'success': True,
        'data': {
            'ai_provider': config.AI_PROVIDER,
            'gemini_model': config.GEMINI_MODEL,
            'openai_model': config.OPENAI_MODEL,
            'has_gemini_key': bool(config.GEMINI_API_KEY),
            'has_openai_key': bool(config.OPENAI_API_KEY),
            'has_anthropic_key': bool(os.getenv('ANTHROPIC_API_KEY', '')),
            'has_groq_key': bool(os.getenv('GROQ_API_KEY', '')),
            'has_deepseek_key': bool(os.getenv('DEEPSEEK_API_KEY', '')),
            'provider_ready': ai_service.is_ready,
            'current_provider': ai_service.provider_type,
            'current_config': ai_service.get_current_config()
        }
    })


@settings_bp.route('/providers', methods=['GET'])
def get_providers():
    """取得可用的 AI 提供商列表"""
    ai_service = get_ai_service()
    providers = ai_service.get_available_providers()

    return jsonify({
        'success': True,
        'data': {
            'current_provider': ai_service.provider_type,
            'providers': providers
        }
    })


@settings_bp.route('', methods=['PUT'])
def update_settings():
    """更新設定（運行時切換 Provider）"""
    data = request.get_json()

    provider = data.get('provider')
    api_key = data.get('api_key')
    model = data.get('model')

    if not provider:
        return jsonify({'success': False, 'error': 'provider 為必填'}), 400

    # Ollama 不需要 API Key
    if provider.lower() != 'ollama' and not api_key:
        # 檢查是否已有 API Key 在環境變數中
        env_key_map = {
            'gemini': 'GEMINI_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'groq': 'GROQ_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
        }
        env_key = env_key_map.get(provider.lower())
        if env_key and not os.getenv(env_key):
            return jsonify({'success': False, 'error': f'{provider} API Key 未設定'}), 400

    try:
        ai_service = get_ai_service()
        ai_service.switch_provider(provider, api_key, model)

        return jsonify({
            'success': True,
            'message': f'已切換至 {provider}',
            'data': {
                'provider': provider,
                'provider_ready': ai_service.is_ready,
                'config': ai_service.get_current_config()
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@settings_bp.route('/test-api', methods=['POST'])
def test_api():
    """測試 API 連線"""
    data = request.get_json()

    provider = data.get('provider')
    api_key = data.get('api_key')

    if not provider:
        return jsonify({'success': False, 'error': 'provider 為必填'}), 400

    try:
        test_provider = None
        provider_lower = provider.lower()

        if provider_lower == 'gemini':
            from services.ai_providers.gemini_provider import GeminiProvider
            test_provider = GeminiProvider(api_key=api_key)

        elif provider_lower == 'openai':
            from services.ai_providers.openai_provider import OpenAIProvider
            test_provider = OpenAIProvider(api_key=api_key)

        elif provider_lower == 'anthropic':
            from services.ai_providers.anthropic_provider import AnthropicProvider
            test_provider = AnthropicProvider(api_key=api_key)

        elif provider_lower == 'ollama':
            from services.ai_providers.ollama_provider import OllamaProvider
            test_provider = OllamaProvider()
            if not test_provider.is_available():
                return jsonify({'success': False, 'error': 'Ollama 服務不可用，請確認已啟動'}), 400

        elif provider_lower == 'groq':
            from services.ai_providers.groq_provider import GroqProvider
            test_provider = GroqProvider(api_key=api_key)

        elif provider_lower == 'deepseek':
            from services.ai_providers.deepseek_provider import DeepSeekProvider
            test_provider = DeepSeekProvider(api_key=api_key)

        else:
            return jsonify({'success': False, 'error': f'不支援的提供商: {provider}'}), 400

        # 簡單測試
        result = test_provider.generate("Hello, please reply with 'OK' only.")

        return jsonify({
            'success': True,
            'message': f'{provider} API 連線成功',
            'response': result[:100]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'API 連線失敗: {str(e)}'}), 400


@settings_bp.route('/reset', methods=['POST'])
def reset_service():
    """重置 AI 服務"""
    try:
        clear_ai_service()
        ai_service = get_ai_service(force_new=True)

        return jsonify({
            'success': True,
            'message': 'AI 服務已重置',
            'data': {
                'provider_ready': ai_service.is_ready,
                'current_provider': ai_service.provider_type,
                'config': ai_service.get_current_config()
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@settings_bp.route('/models/<provider>', methods=['GET'])
def get_provider_models(provider):
    """取得指定提供商的可用模型列表"""
    provider_lower = provider.lower()

    models = []

    if provider_lower == 'gemini':
        models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']

    elif provider_lower == 'openai':
        models = ['gpt-4o', 'gpt-4.1', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']

    elif provider_lower == 'anthropic':
        from services.ai_providers.anthropic_provider import AnthropicProvider
        models = AnthropicProvider.AVAILABLE_MODELS

    elif provider_lower == 'ollama':
        # 嘗試取得本地已安裝的模型
        try:
            from services.ai_providers.ollama_provider import OllamaProvider
            ollama = OllamaProvider()
            if ollama.is_available():
                models = ollama.list_local_models()
            if not models:
                models = ['llama3.2', 'llama3.1', 'mistral', 'mixtral', 'qwen2.5', 'phi3']
        except:
            models = ['llama3.2', 'llama3.1', 'mistral', 'mixtral', 'qwen2.5', 'phi3']

    elif provider_lower == 'groq':
        from services.ai_providers.groq_provider import GroqProvider
        models = GroqProvider.AVAILABLE_MODELS

    elif provider_lower == 'deepseek':
        from services.ai_providers.deepseek_provider import DeepSeekProvider
        models = DeepSeekProvider.AVAILABLE_MODELS

    else:
        return jsonify({'success': False, 'error': f'不支援的提供商: {provider}'}), 400

    return jsonify({
        'success': True,
        'data': {
            'provider': provider,
            'models': models
        }
    })
