"""
Web Search Service - Tavily API 包裝
"""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WebSearchService:
    """Web search service using Tavily API"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        """延遲初始化 Tavily client"""
        if self._client is None:
            api_key = os.getenv('TAVILY_API_KEY', '')
            if not api_key:
                raise ValueError("TAVILY_API_KEY 未配置")
            from tavily import TavilyClient
            self._client = TavilyClient(api_key=api_key)
        return self._client

    def search(self, query: str, max_results: int = 10, search_depth: str = "advanced") -> Dict[str, Any]:
        """
        使用 Tavily 搜尋網路

        Args:
            query: 搜尋查詢字串
            max_results: 最大結果數（預設 10）
            search_depth: "basic"（1 積分）或 "advanced"（2 積分，返回更完整內容）

        Returns:
            {
                "query": str,
                "results": [{"title": str, "url": str, "content": str, "raw_content": str, "score": float}],
                "answer": Optional[str]
            }
        """
        try:
            client = self._get_client()
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=True,
                include_raw_content=True
            )
            return response
        except ValueError as e:
            logger.error(f"Tavily 配置錯誤: {e}")
            return {"query": query, "results": [], "error": str(e)}
        except Exception as e:
            logger.error(f"網路搜尋失敗: {e}")
            return {"query": query, "results": [], "error": f"搜尋失敗: {str(e)}"}


# 全域實例
_web_search_service: Optional[WebSearchService] = None


def get_web_search_service() -> WebSearchService:
    """取得 Web Search 服務實例"""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
