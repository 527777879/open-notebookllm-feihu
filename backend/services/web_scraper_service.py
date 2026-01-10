"""
網頁擷取服務 - 將 URL 轉換為來源內容
"""
import logging
import re
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraperService:
    """網頁擷取服務"""

    # 常見的無用元素選擇器
    REMOVE_SELECTORS = [
        'script', 'style', 'noscript', 'iframe', 'svg',
        'nav', 'footer', 'header', 'aside',
        '.nav', '.navigation', '.menu', '.sidebar',
        '.footer', '.header', '.advertisement', '.ads',
        '.cookie-banner', '.popup', '.modal',
        '#nav', '#navigation', '#menu', '#sidebar',
        '#footer', '#header', '#comments'
    ]

    # 主要內容選擇器（優先順序）
    CONTENT_SELECTORS = [
        'article',
        'main',
        '[role="main"]',
        '.post-content',
        '.article-content',
        '.entry-content',
        '.content',
        '#content',
        '.post',
        '.article'
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        })

    def scrape_url(self, url: str, timeout: int = 30) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        擷取網頁內容

        Args:
            url: 網頁 URL
            timeout: 請求超時時間

        Returns:
            (提取的文字內容, 元數據, 錯誤訊息)
        """
        # 驗證 URL
        if not self._is_valid_url(url):
            return None, None, "無效的 URL"

        try:
            # 發送請求
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()

            # 檢測編碼
            response.encoding = response.apparent_encoding or 'utf-8'

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取元數據
            metadata = self._extract_metadata(soup, url)

            # 移除無用元素
            self._remove_unwanted_elements(soup)

            # 提取主要內容
            content = self._extract_content(soup)

            if not content or len(content.strip()) < 100:
                return None, metadata, "無法提取有效內容"

            return content, metadata, None

        except requests.Timeout:
            return None, None, "請求超時"
        except requests.RequestException as e:
            return None, None, f"請求失敗: {str(e)}"
        except Exception as e:
            logger.error(f"網頁擷取失敗: {e}")
            return None, None, f"擷取失敗: {str(e)}"

    def _is_valid_url(self, url: str) -> bool:
        """驗證 URL 格式"""
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """提取網頁元數據"""
        metadata = {
            'url': url,
            'domain': urlparse(url).netloc
        }

        # 標題
        title = None
        if soup.title:
            title = soup.title.string
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content')
        metadata['title'] = title.strip() if title else None

        # 描述
        description = None
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content')
        if not description:
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                description = og_desc.get('content')
        metadata['description'] = description.strip() if description else None

        # 作者
        author = None
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            author = meta_author.get('content')
        metadata['author'] = author.strip() if author else None

        # 發布日期
        pub_date = None
        for attr in ['article:published_time', 'datePublished', 'pubdate']:
            meta_date = soup.find('meta', property=attr) or soup.find('meta', attrs={'name': attr})
            if meta_date:
                pub_date = meta_date.get('content')
                break
        metadata['published_date'] = pub_date

        # 圖片
        og_image = soup.find('meta', property='og:image')
        if og_image:
            image_url = og_image.get('content')
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            metadata['image'] = image_url

        return metadata

    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """移除無用元素"""
        for selector in self.REMOVE_SELECTORS:
            for element in soup.select(selector):
                element.decompose()

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取主要內容"""
        content_element = None

        # 嘗試找主要內容區域
        for selector in self.CONTENT_SELECTORS:
            content_element = soup.select_one(selector)
            if content_element:
                break

        # 如果找不到，使用 body
        if not content_element:
            content_element = soup.body or soup

        # 提取文字
        text_parts = []

        for element in content_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td', 'th', 'blockquote', 'pre', 'code']):
            text = element.get_text(strip=True)
            if text and len(text) > 1:
                # 根據標籤類型添加格式
                tag = element.name
                if tag.startswith('h'):
                    level = int(tag[1])
                    text = '#' * level + ' ' + text
                elif tag == 'li':
                    text = '• ' + text
                elif tag == 'blockquote':
                    text = '> ' + text
                elif tag in ('pre', 'code'):
                    text = '```\n' + text + '\n```'

                text_parts.append(text)

        content = '\n\n'.join(text_parts)

        # 清理多餘空白
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)

        return content.strip()

    def get_page_title(self, url: str) -> Optional[str]:
        """快速取得網頁標題"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            if soup.title:
                return soup.title.string.strip()

            og_title = soup.find('meta', property='og:title')
            if og_title:
                return og_title.get('content', '').strip()

            return None
        except Exception:
            return None


# 全局實例
_web_scraper: Optional[WebScraperService] = None


def get_web_scraper() -> WebScraperService:
    """取得網頁擷取服務實例"""
    global _web_scraper
    if _web_scraper is None:
        _web_scraper = WebScraperService()
    return _web_scraper
