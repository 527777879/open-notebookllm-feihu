"""
YouTube 影片服務 - 提取字幕和影片資訊
"""
import logging
import re
from typing import Optional, Tuple, Dict, Any, List
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class YouTubeService:
    """YouTube 影片服務"""

    # YouTube URL 模式
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]

    def extract_video_id(self, url: str) -> Optional[str]:
        """從 URL 提取影片 ID"""
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # 嘗試從 query string 提取
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc:
            qs = parse_qs(parsed.query)
            if 'v' in qs:
                return qs['v'][0]

        return None

    def get_video_info(self, video_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        取得影片資訊

        Args:
            video_id: YouTube 影片 ID

        Returns:
            (影片資訊, 錯誤訊息)
        """
        try:
            from yt_dlp import YoutubeDL

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f'https://www.youtube.com/watch?v={video_id}',
                    download=False
                )

                return {
                    'video_id': video_id,
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),
                    'channel': info.get('channel') or info.get('uploader'),
                    'channel_id': info.get('channel_id'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'thumbnail': info.get('thumbnail'),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                }, None

        except ImportError:
            return None, "yt-dlp 未安裝，請執行: pip install yt-dlp"
        except Exception as e:
            logger.error(f"取得影片資訊失敗: {e}")
            return None, f"取得影片資訊失敗: {str(e)}"

    def get_transcript(self, video_id: str, languages: List[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        取得影片字幕/轉錄文字

        Args:
            video_id: YouTube 影片 ID
            languages: 偏好語言列表，例如 ['zh-TW', 'zh', 'en']

        Returns:
            (字幕文字, 錯誤訊息)
        """
        if languages is None:
            languages = ['zh-TW', 'zh-Hant', 'zh', 'zh-Hans', 'en', 'ja', 'ko']

        # 方法 1: 使用 youtube_transcript_api
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

            try:
                # 嘗試取得指定語言的字幕
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                transcript = None

                # 優先嘗試手動字幕
                for lang in languages:
                    try:
                        transcript = transcript_list.find_transcript([lang])
                        break
                    except NoTranscriptFound:
                        continue

                # 如果沒有手動字幕，嘗試自動生成的
                if not transcript:
                    try:
                        transcript = transcript_list.find_generated_transcript(languages)
                    except NoTranscriptFound:
                        pass

                # 如果還是沒有，取得任何可用的字幕
                if not transcript:
                    for t in transcript_list:
                        transcript = t
                        break

                if transcript:
                    transcript_data = transcript.fetch()
                    text_parts = [entry['text'] for entry in transcript_data]
                    return '\n'.join(text_parts), None

            except TranscriptsDisabled:
                return None, "此影片已停用字幕"
            except NoTranscriptFound:
                pass

        except ImportError:
            logger.warning("youtube_transcript_api 未安裝")

        # 方法 2: 使用 yt-dlp 下載字幕
        try:
            from yt_dlp import YoutubeDL
            import tempfile
            import os

            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': languages,
                    'subtitlesformat': 'vtt',
                    'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                }

                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

                # 找尋下載的字幕檔
                for lang in languages:
                    for ext in ['vtt', 'srt']:
                        sub_file = os.path.join(tmpdir, f'{video_id}.{lang}.{ext}')
                        if os.path.exists(sub_file):
                            with open(sub_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            return self._parse_subtitle(content, ext), None

                return None, "無法取得字幕"

        except ImportError:
            return None, "yt-dlp 未安裝，請執行: pip install yt-dlp"
        except Exception as e:
            return None, f"取得字幕失敗: {str(e)}"

    def _parse_subtitle(self, content: str, format: str) -> str:
        """解析字幕檔，提取純文字"""
        lines = content.split('\n')
        text_lines = []

        if format == 'vtt':
            # 跳過 VTT 標頭
            in_cue = False
            for line in lines:
                line = line.strip()
                if '-->' in line:
                    in_cue = True
                    continue
                if in_cue and line and not line.startswith('WEBVTT'):
                    # 移除 VTT 標籤
                    clean = re.sub(r'<[^>]+>', '', line)
                    if clean:
                        text_lines.append(clean)
                if not line:
                    in_cue = False

        elif format == 'srt':
            for line in lines:
                line = line.strip()
                # 跳過數字行和時間行
                if line.isdigit() or '-->' in line or not line:
                    continue
                text_lines.append(line)

        # 移除重複行
        unique_lines = []
        prev = None
        for line in text_lines:
            if line != prev:
                unique_lines.append(line)
                prev = line

        return '\n'.join(unique_lines)

    def process_youtube_url(self, url: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        處理 YouTube URL，取得影片資訊和字幕

        Args:
            url: YouTube URL

        Returns:
            (字幕內容, 元數據, 錯誤訊息)
        """
        # 提取影片 ID
        video_id = self.extract_video_id(url)
        if not video_id:
            return None, None, "無效的 YouTube URL"

        # 取得影片資訊
        info, info_error = self.get_video_info(video_id)
        if info_error:
            logger.warning(f"取得影片資訊失敗: {info_error}")
            info = {'video_id': video_id, 'title': f'YouTube 影片 {video_id}'}

        # 取得字幕
        transcript, trans_error = self.get_transcript(video_id)

        if not transcript:
            return None, info, trans_error or "無法取得字幕內容"

        # 組合內容
        content_parts = []

        if info.get('title'):
            content_parts.append(f"# {info['title']}")

        if info.get('channel'):
            content_parts.append(f"頻道: {info['channel']}")

        if info.get('description'):
            desc = info['description'][:500]
            if len(info['description']) > 500:
                desc += '...'
            content_parts.append(f"\n## 影片說明\n{desc}")

        content_parts.append(f"\n## 字幕內容\n{transcript}")

        metadata = {
            'video_id': video_id,
            'url': url,
            'title': info.get('title'),
            'channel': info.get('channel'),
            'duration': info.get('duration'),
            'upload_date': info.get('upload_date'),
            'thumbnail': info.get('thumbnail'),
        }

        return '\n\n'.join(content_parts), metadata, None


# 全局實例
_youtube_service: Optional[YouTubeService] = None


def get_youtube_service() -> YouTubeService:
    """取得 YouTube 服務實例"""
    global _youtube_service
    if _youtube_service is None:
        _youtube_service = YouTubeService()
    return _youtube_service
