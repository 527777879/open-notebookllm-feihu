"""
NoteBookLLM 服務層 - 整合多種 AI 服務
"""
from .ai_service_manager import AIServiceManager, get_ai_service, clear_ai_service
from .rag_service import RAGService, get_rag_service
from .file_parser_service import FileParserService, get_file_parser
from .studio_service import StudioService, get_studio_service
from .search_service import SearchService, get_search_service
from .web_scraper_service import WebScraperService, get_web_scraper
from .youtube_service import YouTubeService, get_youtube_service
from .audio_service import AudioService, get_audio_service
from .podcast_service import PodcastService, get_podcast_service

__all__ = [
    # AI 服務管理
    'AIServiceManager',
    'get_ai_service',
    'clear_ai_service',
    # RAG 服務
    'RAGService',
    'get_rag_service',
    # 文件解析
    'FileParserService',
    'get_file_parser',
    # 工作室輸出
    'StudioService',
    'get_studio_service',
    # 搜尋服務
    'SearchService',
    'get_search_service',
    # 網頁擷取
    'WebScraperService',
    'get_web_scraper',
    # YouTube 服務
    'YouTubeService',
    'get_youtube_service',
    # 音訊服務
    'AudioService',
    'get_audio_service',
    # 播客服務
    'PodcastService',
    'get_podcast_service',
]
