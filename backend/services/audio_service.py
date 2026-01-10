"""
音訊服務 - STT (語音轉文字) 和 TTS (文字轉語音)
"""
import logging
import os
import tempfile
import base64
from typing import Optional, Tuple, Dict, Any, List, Generator
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioService:
    """音訊服務 - 語音轉文字 (STT) 和文字轉語音 (TTS)"""

    SUPPORTED_AUDIO_FORMATS = {
        'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac'
    }

    def __init__(self):
        self._whisper_model = None

    # ==================== STT (語音轉文字) ====================

    def transcribe_file(
        self,
        file_path: str,
        language: str = None,
        provider: str = 'openai'
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        將音檔轉換為文字

        Args:
            file_path: 音檔路徑
            language: 語言代碼 (例如 'zh', 'en', 'ja')
            provider: 使用的服務 ('openai', 'groq', 'local')

        Returns:
            (轉錄文字, 元數據, 錯誤訊息)
        """
        if not os.path.exists(file_path):
            return None, None, "檔案不存在"

        ext = Path(file_path).suffix.lower().lstrip('.')
        if ext not in self.SUPPORTED_AUDIO_FORMATS:
            return None, None, f"不支援的音檔格式: {ext}"

        if provider == 'openai':
            return self._transcribe_openai(file_path, language)
        elif provider == 'groq':
            return self._transcribe_groq(file_path, language)
        elif provider == 'local':
            return self._transcribe_local(file_path, language)
        else:
            return None, None, f"不支援的 STT 提供商: {provider}"

    def _transcribe_openai(
        self,
        file_path: str,
        language: str = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """使用 OpenAI Whisper API 轉錄"""
        try:
            from openai import OpenAI
            from config import get_config

            config = get_config()
            if not config.OPENAI_API_KEY:
                return None, None, "OpenAI API Key 未設定"

            client = OpenAI(api_key=config.OPENAI_API_KEY)

            with open(file_path, 'rb') as audio_file:
                params = {
                    'model': 'whisper-1',
                    'file': audio_file,
                    'response_format': 'verbose_json',
                }
                if language:
                    params['language'] = language

                response = client.audio.transcriptions.create(**params)

            metadata = {
                'duration': getattr(response, 'duration', None),
                'language': getattr(response, 'language', language),
                'provider': 'openai'
            }

            return response.text, metadata, None

        except ImportError:
            return None, None, "openai 套件未安裝，請執行: pip install openai"
        except Exception as e:
            logger.error(f"OpenAI 轉錄失敗: {e}")
            return None, None, f"轉錄失敗: {str(e)}"

    def _transcribe_groq(
        self,
        file_path: str,
        language: str = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """使用 Groq Whisper API 轉錄 (更快速)"""
        try:
            from groq import Groq
            from config import get_config

            config = get_config()
            groq_key = os.getenv('GROQ_API_KEY', '')
            if not groq_key:
                return None, None, "Groq API Key 未設定"

            client = Groq(api_key=groq_key)

            with open(file_path, 'rb') as audio_file:
                params = {
                    'model': 'whisper-large-v3',
                    'file': audio_file,
                    'response_format': 'verbose_json',
                }
                if language:
                    params['language'] = language

                response = client.audio.transcriptions.create(**params)

            metadata = {
                'duration': getattr(response, 'duration', None),
                'language': getattr(response, 'language', language),
                'provider': 'groq'
            }

            return response.text, metadata, None

        except ImportError:
            return None, None, "groq 套件未安裝，請執行: pip install groq"
        except Exception as e:
            logger.error(f"Groq 轉錄失敗: {e}")
            return None, None, f"轉錄失敗: {str(e)}"

    def _transcribe_local(
        self,
        file_path: str,
        language: str = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """使用本地 Whisper 模型轉錄"""
        try:
            import whisper

            if self._whisper_model is None:
                logger.info("載入本地 Whisper 模型...")
                self._whisper_model = whisper.load_model("base")

            result = self._whisper_model.transcribe(
                file_path,
                language=language,
                verbose=False
            )

            metadata = {
                'language': result.get('language'),
                'duration': result.get('duration'),
                'provider': 'local'
            }

            return result['text'], metadata, None

        except ImportError:
            return None, None, "whisper 套件未安裝，請執行: pip install openai-whisper"
        except Exception as e:
            logger.error(f"本地轉錄失敗: {e}")
            return None, None, f"轉錄失敗: {str(e)}"

    # ==================== TTS (文字轉語音) ====================

    def text_to_speech(
        self,
        text: str,
        voice: str = 'alloy',
        provider: str = 'openai',
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        將文字轉換為語音

        Args:
            text: 要轉換的文字
            voice: 語音選擇
            provider: 使用的服務 ('openai', 'google')
            output_format: 輸出格式

        Returns:
            (音訊資料, 錯誤訊息)
        """
        if provider == 'openai':
            return self._tts_openai(text, voice, output_format)
        elif provider == 'google':
            return self._tts_google(text, voice, output_format)
        else:
            return None, f"不支援的 TTS 提供商: {provider}"

    def _tts_openai(
        self,
        text: str,
        voice: str = 'alloy',
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """使用 OpenAI TTS"""
        try:
            from openai import OpenAI
            from config import get_config

            config = get_config()
            if not config.OPENAI_API_KEY:
                return None, "OpenAI API Key 未設定"

            client = OpenAI(api_key=config.OPENAI_API_KEY)

            # OpenAI TTS 支援的語音: alloy, echo, fable, onyx, nova, shimmer
            valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
            if voice not in valid_voices:
                voice = 'alloy'

            response = client.audio.speech.create(
                model='tts-1',
                voice=voice,
                input=text,
                response_format=output_format
            )

            return response.content, None

        except ImportError:
            return None, "openai 套件未安裝"
        except Exception as e:
            logger.error(f"OpenAI TTS 失敗: {e}")
            return None, f"TTS 失敗: {str(e)}"

    def _tts_google(
        self,
        text: str,
        voice: str = 'zh-TW-Standard-A',
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """使用 Google Cloud TTS"""
        try:
            from google.cloud import texttospeech

            client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            # 解析語音名稱
            lang_code = '-'.join(voice.split('-')[:2]) if '-' in voice else 'zh-TW'

            voice_params = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                name=voice
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )

            return response.audio_content, None

        except ImportError:
            return None, "google-cloud-texttospeech 套件未安裝"
        except Exception as e:
            logger.error(f"Google TTS 失敗: {e}")
            return None, f"TTS 失敗: {str(e)}"

    def text_to_speech_stream(
        self,
        text: str,
        voice: str = 'alloy',
        provider: str = 'openai'
    ) -> Generator[bytes, None, None]:
        """
        串流方式將文字轉換為語音

        Args:
            text: 要轉換的文字
            voice: 語音選擇
            provider: 使用的服務

        Yields:
            音訊資料片段
        """
        try:
            from openai import OpenAI
            from config import get_config

            config = get_config()
            if not config.OPENAI_API_KEY:
                return

            client = OpenAI(api_key=config.OPENAI_API_KEY)

            with client.audio.speech.with_streaming_response.create(
                model='tts-1',
                voice=voice,
                input=text,
            ) as response:
                for chunk in response.iter_bytes(chunk_size=4096):
                    yield chunk

        except Exception as e:
            logger.error(f"TTS 串流失敗: {e}")

    def save_audio(self, audio_data: bytes, output_path: str) -> bool:
        """儲存音訊資料到檔案"""
        try:
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            return True
        except Exception as e:
            logger.error(f"儲存音訊失敗: {e}")
            return False

    def audio_to_base64(self, audio_data: bytes) -> str:
        """將音訊資料轉換為 Base64"""
        return base64.b64encode(audio_data).decode('utf-8')


# 全局實例
_audio_service: Optional[AudioService] = None


def get_audio_service() -> AudioService:
    """取得音訊服務實例"""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
