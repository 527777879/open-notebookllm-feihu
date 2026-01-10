"""
Podcast 播客生成服務 - 支援多人對話生成
"""
import logging
import json
import os
import tempfile
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SpeakerGender(Enum):
    """講者性別"""
    MALE = "male"
    FEMALE = "female"


@dataclass
class SpeakerProfile:
    """講者設定檔"""
    name: str
    gender: SpeakerGender
    voice: str  # TTS 語音 ID
    personality: str  # 個性描述
    role: str  # 角色 (host, guest, expert 等)
    speaking_style: str  # 說話風格


# 預設講者設定
DEFAULT_SPEAKERS = {
    "host_male": SpeakerProfile(
        name="小明",
        gender=SpeakerGender.MALE,
        voice="onyx",  # OpenAI 男聲
        personality="熱情、好奇、善於引導話題",
        role="host",
        speaking_style="親切自然，善於提問"
    ),
    "host_female": SpeakerProfile(
        name="小美",
        gender=SpeakerGender.FEMALE,
        voice="nova",  # OpenAI 女聲
        personality="專業、細心、善於總結",
        role="host",
        speaking_style="清晰有條理，善於歸納重點"
    ),
    "expert_male": SpeakerProfile(
        name="王教授",
        gender=SpeakerGender.MALE,
        voice="echo",
        personality="博學、嚴謹、有深度",
        role="expert",
        speaking_style="專業術語與白話解釋交替使用"
    ),
    "expert_female": SpeakerProfile(
        name="李博士",
        gender=SpeakerGender.FEMALE,
        voice="shimmer",
        personality="創新、活潑、善於舉例",
        role="expert",
        speaking_style="喜歡用生活化的例子說明複雜概念"
    ),
}


class PodcastService:
    """Podcast 播客生成服務"""

    def __init__(self):
        self.speakers: Dict[str, SpeakerProfile] = DEFAULT_SPEAKERS.copy()

    def generate_podcast_script(
        self,
        content: str,
        speakers: List[Dict[str, Any]] = None,
        duration_minutes: int = 10,
        style: str = "conversational",
        language: str = "zh-TW"
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        生成播客腳本

        Args:
            content: 來源內容
            speakers: 講者設定列表，每個包含 name, personality, role
            duration_minutes: 目標時長（分鐘）
            style: 風格 (conversational, educational, debate, interview)
            language: 語言

        Returns:
            (腳本片段列表, 錯誤訊息)
        """
        from .ai_service_manager import get_ai_service

        # 預設兩位講者
        if not speakers or len(speakers) < 1:
            speakers = [
                {"name": "小明", "role": "host", "personality": "熱情好奇"},
                {"name": "小美", "role": "co-host", "personality": "專業細心"}
            ]

        # 確保最多 4 位講者
        speakers = speakers[:4]

        # 估算字數（中文約 150-200 字/分鐘）
        target_words = duration_minutes * 180

        # 建立講者描述
        speakers_desc = "\n".join([
            f"- {s['name']} ({s['role']}): {s.get('personality', '專業')}"
            for s in speakers
        ])

        # 建立風格指引
        style_guides = {
            "conversational": "輕鬆自然的對話風格，像朋友間的討論",
            "educational": "教育性質，一方講解另一方提問和回應",
            "debate": "辯論風格，呈現不同觀點和討論",
            "interview": "訪談風格，主持人提問專家回答"
        }
        style_guide = style_guides.get(style, style_guides["conversational"])

        prompt = f"""你是一位專業的播客腳本作家。請根據以下內容生成一段播客對話腳本。

## 來源內容
{content[:8000]}

## 講者設定
{speakers_desc}

## 要求
1. **所有內容必須使用繁體中文**
2. 風格: {style_guide}
3. 目標字數: 約 {target_words} 字
4. 對話要自然流暢，包含適當的語氣詞和過渡
5. 確保內容準確反映來源資料的重點
6. 每位講者都要有發言機會
7. title、description 和所有 text 都必須是繁體中文

## 輸出格式
請以 JSON 格式輸出，格式如下：
{{
    "title": "播客標題",
    "description": "簡短描述",
    "segments": [
        {{
            "speaker": "講者名稱",
            "text": "講者說的話",
            "emotion": "情緒/語氣 (neutral, excited, curious, thoughtful 等)"
        }},
        ...
    ]
}}

請直接輸出 JSON，不要加任何其他說明。"""

        try:
            ai_service = get_ai_service()
            result = ai_service.generate_json(prompt)

            if not result or 'segments' not in result:
                return None, "腳本生成失敗：無效的回應格式"

            return result, None

        except Exception as e:
            logger.error(f"播客腳本生成失敗: {e}")
            return None, f"腳本生成失敗: {str(e)}"

    def generate_podcast_audio(
        self,
        script: Dict[str, Any],
        speaker_voices: Dict[str, str] = None,
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        將播客腳本轉換為音訊

        Args:
            script: 播客腳本（包含 segments）
            speaker_voices: 講者名稱對應語音的映射
            output_format: 輸出格式

        Returns:
            (音訊資料, 錯誤訊息)
        """
        from .audio_service import get_audio_service

        if not script or 'segments' not in script:
            return None, "無效的腳本格式"

        segments = script['segments']
        if not segments:
            return None, "腳本沒有內容"

        audio_service = get_audio_service()

        # 預設語音映射
        default_voices = {
            "小明": "onyx",
            "小美": "nova",
            "王教授": "echo",
            "李博士": "shimmer",
        }

        if speaker_voices:
            default_voices.update(speaker_voices)

        # 收集所有講者並分配語音
        unique_speakers = list(set(seg['speaker'] for seg in segments))
        available_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

        for i, speaker in enumerate(unique_speakers):
            if speaker not in default_voices:
                default_voices[speaker] = available_voices[i % len(available_voices)]

        # 生成每個片段的音訊
        audio_parts = []
        temp_files = []

        try:
            for i, seg in enumerate(segments):
                speaker = seg['speaker']
                text = seg['text']
                voice = default_voices.get(speaker, 'alloy')

                logger.info(f"生成片段 {i+1}/{len(segments)}: {speaker}")

                audio_data, error = audio_service.text_to_speech(
                    text=text,
                    voice=voice,
                    provider='openai',
                    output_format=output_format
                )

                if error:
                    logger.warning(f"片段 {i+1} 生成失敗: {error}")
                    continue

                if audio_data:
                    audio_parts.append(audio_data)

            if not audio_parts:
                return None, "沒有成功生成任何音訊片段"

            # 合併音訊
            combined_audio = self._combine_audio(audio_parts, output_format)

            return combined_audio, None

        except Exception as e:
            logger.error(f"播客音訊生成失敗: {e}")
            return None, f"音訊生成失敗: {str(e)}"

        finally:
            # 清理臨時檔案
            for f in temp_files:
                try:
                    os.unlink(f)
                except:
                    pass

    def _combine_audio(self, audio_parts: List[bytes], format: str = 'mp3') -> bytes:
        """合併多段音訊"""
        try:
            from pydub import AudioSegment
            import io

            combined = AudioSegment.empty()

            for part in audio_parts:
                segment = AudioSegment.from_file(io.BytesIO(part), format=format)
                # 加入短暫停頓
                combined += segment + AudioSegment.silent(duration=300)

            # 輸出
            output = io.BytesIO()
            combined.export(output, format=format)
            return output.getvalue()

        except ImportError:
            # 如果沒有 pydub，直接串接（可能有問題但至少能用）
            logger.warning("pydub 未安裝，使用簡單串接方式")
            return b''.join(audio_parts)

    def generate_full_podcast(
        self,
        content: str,
        speakers: List[Dict[str, Any]] = None,
        duration_minutes: int = 10,
        style: str = "conversational",
        with_audio: bool = True,
        speaker_voices: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        生成完整播客（腳本 + 音訊）

        Args:
            content: 來源內容
            speakers: 講者設定
            duration_minutes: 目標時長
            style: 風格
            with_audio: 是否生成音訊
            speaker_voices: 講者語音映射

        Returns:
            包含腳本和音訊的結果
        """
        result = {
            "type": "podcast",
            "script": None,
            "audio": None,
            "audio_base64": None,
            "error": None
        }

        # 生成腳本
        script, script_error = self.generate_podcast_script(
            content=content,
            speakers=speakers,
            duration_minutes=duration_minutes,
            style=style
        )

        if script_error:
            result["error"] = script_error
            return result

        result["script"] = script

        # 生成音訊
        if with_audio:
            audio_data, audio_error = self.generate_podcast_audio(
                script=script,
                speaker_voices=speaker_voices
            )

            if audio_error:
                result["error"] = f"腳本生成成功，但音訊生成失敗: {audio_error}"
            elif audio_data:
                result["audio"] = audio_data
                # 轉換為 base64 方便前端使用
                import base64
                result["audio_base64"] = base64.b64encode(audio_data).decode('utf-8')

        return result

    def get_available_voices(self) -> List[Dict[str, str]]:
        """取得可用的 TTS 語音列表"""
        return [
            {"id": "alloy", "name": "Alloy", "gender": "neutral", "description": "中性平衡"},
            {"id": "echo", "name": "Echo", "gender": "male", "description": "男聲，沉穩"},
            {"id": "fable", "name": "Fable", "gender": "neutral", "description": "中性，故事感"},
            {"id": "onyx", "name": "Onyx", "gender": "male", "description": "男聲，深沉"},
            {"id": "nova", "name": "Nova", "gender": "female", "description": "女聲，活潑"},
            {"id": "shimmer", "name": "Shimmer", "gender": "female", "description": "女聲，柔和"},
        ]

    def get_style_options(self) -> List[Dict[str, str]]:
        """取得可用的播客風格"""
        return [
            {"id": "conversational", "name": "對話式", "description": "輕鬆自然的雙人對話"},
            {"id": "educational", "name": "教育式", "description": "一方講解一方提問"},
            {"id": "debate", "name": "辯論式", "description": "呈現不同觀點的討論"},
            {"id": "interview", "name": "訪談式", "description": "主持人訪問專家"},
        ]


# 全局實例
_podcast_service: Optional[PodcastService] = None


def get_podcast_service() -> PodcastService:
    """取得播客服務實例"""
    global _podcast_service
    if _podcast_service is None:
        _podcast_service = PodcastService()
    return _podcast_service
