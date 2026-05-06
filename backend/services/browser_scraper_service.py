"""
Playwright 無頭瀏覽器爬蟲服務 - 模擬真實用戶訪問，解決反爬問題
"""
import logging
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class BrowserScraperService:
    """使用 Playwright 無頭瀏覽器擷取網頁內容"""

    def __init__(self):
        self._browser = None
        self._playwright = None

    def _get_browser(self):
        """延遲啟動瀏覽器"""
        if self._browser is None:
            try:
                from playwright.sync_api import sync_playwright
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-gpu',
                        '--no-sandbox',
                    ]
                )
                logger.info("Playwright 瀏覽器已啟動")
            except Exception as e:
                logger.error(f"Playwright 瀏覽器啟動失敗: {e}")
                raise
        return self._browser

    def scrape_url(
        self,
        url: str,
        timeout: int = 30000,
        wait_ms: int = 3000
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        使用無頭瀏覽器擷取網頁內容

        Args:
            url: 網頁 URL
            timeout: 頁面載入超時（毫秒）
            wait_ms: 載入後額外等待時間（毫秒），用於 JS 渲染

        Returns:
            (提取的文字內容, 元數據, 錯誤訊息)
        """
        if not self._is_valid_url(url):
            return None, None, "無效的 URL"

        page = None
        try:
            browser = self._get_browser()
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='zh-TW',
            )
            page = context.new_page()

            # 移除 webdriver 標記，避免被偵測
            page.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')

            # 訪問頁面
            page.goto(url, timeout=timeout, wait_until='domcontentloaded')

            # 等待 JS 渲染完成
            page.wait_for_timeout(wait_ms)

            # 提取元數據
            metadata = self._extract_metadata(page, url)

            # 提取主要內容
            content = self._extract_content(page)

            context.close()

            if not content or len(content.strip()) < 50:
                return None, metadata, "無法提取有效內容"

            return content, metadata, None

        except Exception as e:
            logger.warning(f"Playwright 爬取失敗: {url} - {e}")
            # 確保資源釋放
            try:
                if page:
                    page.context.close()
            except Exception:
                pass
            return None, None, f"瀏覽器爬取失敗: {str(e)}"

    def _is_valid_url(self, url: str) -> bool:
        """驗證 URL 格式"""
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False

    def _extract_metadata(self, page, url: str) -> Dict[str, Any]:
        """從頁面提取元數據"""
        metadata = {
            'url': url,
            'domain': urlparse(url).netloc
        }

        try:
            title = page.title()
            if title:
                metadata['title'] = title.strip()
        except Exception:
            pass

        try:
            description = page.evaluate("""() => {
                const meta = document.querySelector('meta[name="description"]')
                    || document.querySelector('meta[property="og:description"]');
                return meta ? meta.content : null;
            }""")
            if description:
                metadata['description'] = description.strip()
        except Exception:
            pass

        return metadata

    def _extract_content(self, page) -> Optional[str]:
        """從頁面提取主要文字內容"""
        try:
            # 優先嘗試提取主要內容區域
            content = page.evaluate("""() => {
                // 常見的內容選擇器
                const selectors = [
                    'article', 'main', '[role="main"]',
                    '.post-content', '.article-content', '.entry-content',
                    '.content', '#content', '.post', '.article'
                ];

                let element = null;
                for (const sel of selectors) {
                    element = document.querySelector(sel);
                    if (element) break;
                }

                if (!element) {
                    element = document.body;
                }

                // 移除不需要的元素
                const removeSelectors = [
                    'script', 'style', 'noscript', 'iframe', 'svg',
                    'nav', 'footer', 'header', 'aside',
                    '.nav', '.navigation', '.menu', '.sidebar',
                    '.footer', '.header', '.advertisement', '.ads',
                    '.cookie-banner', '.popup', '.modal',
                    '.social-share', '.related-posts', '.comments'
                ];

                const clone = element.cloneNode(true);
                for (const sel of removeSelectors) {
                    clone.querySelectorAll(sel).forEach(el => el.remove());
                }

                // 提取文字
                return clone.innerText;
            }""")

            if content:
                # 清理多餘空白
                import re
                content = re.sub(r'\n{3,}', '\n\n', content)
                content = re.sub(r' {2,}', ' ', content)
                return content.strip()

        except Exception as e:
            logger.warning(f"內容提取失敗: {e}")

        return None

    def close(self):
        """關閉瀏覽器"""
        try:
            if self._browser:
                self._browser.close()
                self._browser = None
            if self._playwright:
                self._playwright.stop()
                self._playwright = None
            logger.info("Playwright 瀏覽器已關閉")
        except Exception as e:
            logger.warning(f"關閉瀏覽器失敗: {e}")


# 全域實例
_browser_scraper: Optional[BrowserScraperService] = None


def get_browser_scraper() -> BrowserScraperService:
    """取得瀏覽器爬蟲服務實例"""
    global _browser_scraper
    if _browser_scraper is None:
        _browser_scraper = BrowserScraperService()
    return _browser_scraper
