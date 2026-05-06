"""
NoteBookLLM 配置管理
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Config:
    """基礎配置"""

    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 資料庫配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "database.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False},
        'pool_pre_ping': True,
    }

    # 上傳配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(BASE_DIR), 'uploads'))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc', 'xlsx', 'xls', 'csv', 'md'}

    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')

    # AI Provider 配置
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')  # gemini 或 openai

    # Gemini 配置
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    GEMINI_EMBEDDING_MODEL = os.getenv('GEMINI_EMBEDDING_MODEL', 'models/embedding-001')
    GEMINI_IMAGE_MODEL = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.0-flash-exp-image-generation')

    # OpenAI 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5.1')
    OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    OPENAI_IMAGE_MODEL = os.getenv('OPENAI_IMAGE_MODEL', 'dall-e-3')

    # 獨立 Embedding 配置（用於 DeepSeek/Groq/Anthropic 等不支援 embedding 的提供商）
    # 支援任何 OpenAI 相容的 embedding API（如 SiliconFlow、Jina 等）
    EMBEDDING_API_KEY = os.getenv('EMBEDDING_API_KEY', '')
    EMBEDDING_API_BASE = os.getenv('EMBEDDING_API_BASE', '')  # e.g. https://api.siliconflow.cn/v1
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', '')  # e.g. BAAI/bge-large-zh-v1.5

    # RAG 配置
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 400))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 80))
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', 5))

    # Tavily Web Search 配置
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')

    # 日誌配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """取得當前配置"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)
