"""
Podcast 播客生成服務 - 支援多人對話生成

功能特點：
- 專業的腳本生成提示詞（開場/主體/結尾三段式）
- 支援多個 TTS 提供商（OpenAI, Edge TTS, Google）
- 長篇內容分段處理，維持對話連貫性
- 豐富的對話風格選項
- 音訊正規化和停頓控制
"""
import logging
import json
import os
import io
import asyncio
import tempfile
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

from .prompts import PodcastPrompts

logger = logging.getLogger(__name__)


class TTSProvider(Enum):
    """TTS 提供商"""
    OPENAI = "openai"
    EDGE = "edge"  # 免費
    GOOGLE = "google"


class SpeakerGender(Enum):
    """講者性別"""
    MALE = "male"
    FEMALE = "female"


@dataclass
class SpeakerProfile:
    """講者設定檔"""
    name: str
    gender: SpeakerGender
    personality: str
    role: str
    speaking_style: str
    # 各提供商的語音 ID
    voice_openai: str = "alloy"
    voice_edge: str = "zh-TW-HsiaoChenNeural"
    voice_google: str = "zh-TW-Standard-A"


# 預設講者設定 - 更豐富的語音選項
DEFAULT_SPEAKERS = {
    "host_male": SpeakerProfile(
        name="小明",
        gender=SpeakerGender.MALE,
        personality="熱情、好奇、善於引導話題",
        role="host",
        speaking_style="親切自然，善於提問",
        voice_openai="onyx",
        voice_edge="zh-TW-YunJheNeural",
        voice_google="zh-TW-Standard-B"
    ),
    "host_female": SpeakerProfile(
        name="小美",
        gender=SpeakerGender.FEMALE,
        personality="專業、細心、善於總結",
        role="co-host",
        speaking_style="清晰有條理，善於歸納重點",
        voice_openai="nova",
        voice_edge="zh-TW-HsiaoChenNeural",
        voice_google="zh-TW-Standard-A"
    ),
    "expert_male": SpeakerProfile(
        name="王教授",
        gender=SpeakerGender.MALE,
        personality="博學、嚴謹、有深度",
        role="expert",
        speaking_style="專業術語與白話解釋交替使用",
        voice_openai="echo",
        voice_edge="zh-TW-YunJheNeural",
        voice_google="zh-TW-Standard-C"
    ),
    "expert_female": SpeakerProfile(
        name="李博士",
        gender=SpeakerGender.FEMALE,
        personality="創新、活潑、善於舉例",
        role="expert",
        speaking_style="喜歡用生活化的例子說明複雜概念",
        voice_openai="shimmer",
        voice_edge="zh-TW-HsiaoYuNeural",
        voice_google="zh-TW-Standard-A"
    ),
}

# Edge TTS 可用語音列表（繁體中文）
EDGE_VOICES = {
    "zh-TW-HsiaoChenNeural": {"gender": "female", "name": "曉臻", "style": "親切"},
    "zh-TW-YunJheNeural": {"gender": "male", "name": "雲哲", "style": "沉穩"},
    "zh-TW-HsiaoYuNeural": {"gender": "female", "name": "曉雨", "style": "活潑"},
}


class PodcastService:
    """Podcast 播客生成服務"""

    # 長篇內容分段閾值（字數）
    LONG_CONTENT_THRESHOLD = 3000
    SEGMENT_TARGET_WORDS = 1500

    def __init__(self):
        self.speakers: Dict[str, SpeakerProfile] = DEFAULT_SPEAKERS.copy()

    def generate_podcast_script(
        self,
        content: str,
        speakers: List[Dict[str, Any]] = None,
        duration_minutes: int = 10,
        style: str = "conversational",
        language: str = "zh-TW"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        生成播客腳本（使用專業提示詞）

        Args:
            content: 來源內容
            speakers: 講者設定列表
            duration_minutes: 目標時長（分鐘）
            style: 風格
            language: 語言

        Returns:
            (腳本資料, 錯誤訊息)
        """
        from .ai_service_manager import get_ai_service

        # 預設兩位講者
        if not speakers or len(speakers) < 1:
            speakers = [
                {"name": "小明", "role": "host", "personality": "熱情好奇，善於引導話題"},
                {"name": "小美", "role": "co-host", "personality": "專業細心，善於總結"}
            ]

        # 確保最多 4 位講者
        speakers = speakers[:4]

        # 估算字數（中文約 150-200 字/分鐘口語）
        target_words = duration_minutes * 180

        # 建立講者描述
        speakers_desc = self._build_speakers_description(speakers)

        # 取得風格指引
        style_guide = PodcastPrompts.STYLE_GUIDES.get(
            style,
            PodcastPrompts.STYLE_GUIDES["conversational"]
        )

        # 判斷是否為長篇內容
        if len(content) > self.LONG_CONTENT_THRESHOLD:
            return self._generate_long_form_script(
                content, speakers_desc, style_guide,
                duration_minutes, target_words
            )
        else:
            return self._generate_standard_script(
                content, speakers_desc, style_guide,
                duration_minutes, target_words
            )

    def _build_speakers_description(self, speakers: List[Dict[str, Any]]) -> str:
        """建立講者描述文字"""
        desc_parts = []
        for s in speakers:
            role = s.get('role', 'speaker')
            personality = s.get('personality', PodcastPrompts.SPEAKER_PERSONALITY_TEMPLATES.get(role, '專業'))
            desc_parts.append(f"- **{s['name']}** ({role}): {personality}")
        return "\n".join(desc_parts)

    def _generate_standard_script(
        self,
        content: str,
        speakers_desc: str,
        style_guide: str,
        duration_minutes: int,
        target_words: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """生成標準長度腳本"""
        from .ai_service_manager import get_ai_service

        prompt = PodcastPrompts.SCRIPT_GENERATION.format(
            content=content[:8000],
            speakers_desc=speakers_desc,
            style_guide=style_guide,
            duration_minutes=duration_minutes,
            target_words=target_words
        )

        try:
            ai_service = get_ai_service()
            result = ai_service.generate_json(prompt)

            if not result or 'segments' not in result:
                return None, "腳本生成失敗：無效的回應格式"

            # 後處理：確保對話交替
            result['segments'] = self._ensure_alternating_speakers(result['segments'])

            return result, None

        except Exception as e:
            logger.error(f"播客腳本生成失敗: {e}")
            return None, f"腳本生成失敗: {str(e)}"

    def _generate_long_form_script(
        self,
        content: str,
        speakers_desc: str,
        style_guide: str,
        duration_minutes: int,
        target_words: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """生成長篇內容腳本（分段處理）"""
        from .ai_service_manager import get_ai_service

        logger.info(f"長篇內容分段處理，內容長度: {len(content)} 字")

        # 將內容分段
        sections = self._split_content_into_sections(content)
        logger.info(f"內容已分為 {len(sections)} 段")

        # 計算每段目標字數
        words_per_section = target_words // len(sections)

        all_segments = []
        previous_dialogue = ""

        ai_service = get_ai_service()

        for i, section in enumerate(sections):
            logger.info(f"生成第 {i+1}/{len(sections)} 段對話")

            if i == 0:
                # 第一段使用完整提示詞
                prompt = PodcastPrompts.SCRIPT_GENERATION.format(
                    content=section,
                    speakers_desc=speakers_desc,
                    style_guide=style_guide,
                    duration_minutes=duration_minutes // len(sections),
                    target_words=words_per_section
                )
            else:
                # 後續段使用續寫提示詞
                prompt = PodcastPrompts.SCRIPT_CONTINUATION.format(
                    content=content[:2000],  # 提供原始內容摘要
                    speakers_desc=speakers_desc,
                    previous_dialogue=previous_dialogue,
                    current_section=section,
                    target_words=words_per_section
                )

            try:
                result = ai_service.generate_json(prompt)

                if i == 0 and isinstance(result, dict):
                    # 第一段保存標題等資訊
                    script_meta = {
                        "title": result.get("title", "播客節目"),
                        "description": result.get("description", ""),
                        "keywords": result.get("keywords", []),
                        "summary": result.get("summary", "")
                    }
                    segments = result.get("segments", [])
                elif isinstance(result, list):
                    segments = result
                else:
                    segments = result.get("segments", []) if isinstance(result, dict) else []

                all_segments.extend(segments)

                # 保存最後幾段對話作為上下文
                if segments:
                    last_dialogues = segments[-3:] if len(segments) >= 3 else segments
                    previous_dialogue = "\n".join([
                        f"{s['speaker']}: {s['text']}" for s in last_dialogues
                    ])

            except Exception as e:
                logger.error(f"第 {i+1} 段生成失敗: {e}")
                continue

        if not all_segments:
            return None, "長篇腳本生成失敗：沒有成功生成任何段落"

        # 組合最終結果
        final_result = script_meta if 'script_meta' in dir() else {
            "title": "播客節目",
            "description": "",
            "keywords": [],
            "summary": ""
        }
        final_result["segments"] = self._ensure_alternating_speakers(all_segments)

        return final_result, None

    def _split_content_into_sections(self, content: str) -> List[str]:
        """將長內容分割成段落"""
        # 嘗試按段落分割
        paragraphs = content.split('\n\n')

        sections = []
        current_section = ""

        for para in paragraphs:
            if len(current_section) + len(para) < self.SEGMENT_TARGET_WORDS:
                current_section += para + "\n\n"
            else:
                if current_section:
                    sections.append(current_section.strip())
                current_section = para + "\n\n"

        if current_section:
            sections.append(current_section.strip())

        # 確保至少有一段
        if not sections:
            sections = [content]

        return sections

    def _ensure_alternating_speakers(self, segments: List[Dict]) -> List[Dict]:
        """確保講者交替發言，合併連續同一講者的發言"""
        if not segments:
            return segments

        merged = []
        for seg in segments:
            if merged and merged[-1]['speaker'] == seg['speaker']:
                # 合併同一講者的連續發言
                merged[-1]['text'] += " " + seg['text']
            else:
                merged.append(seg.copy())

        return merged

    def generate_podcast_audio(
        self,
        script: Dict[str, Any],
        speaker_voices: Dict[str, str] = None,
        tts_provider: str = "openai",
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        將播客腳本轉換為音訊

        Args:
            script: 播客腳本
            speaker_voices: 講者語音映射
            tts_provider: TTS 提供商 (openai, edge, google)
            output_format: 輸出格式

        Returns:
            (音訊資料, 錯誤訊息)
        """
        if not script or 'segments' not in script:
            return None, "無效的腳本格式"

        segments = script['segments']
        if not segments:
            return None, "腳本沒有內容"

        # 根據提供商選擇生成方法
        if tts_provider == "edge":
            return self._generate_audio_edge(segments, speaker_voices, output_format)
        elif tts_provider == "google":
            return self._generate_audio_google(segments, speaker_voices, output_format)
        else:
            return self._generate_audio_openai(segments, speaker_voices, output_format)

    def _generate_audio_openai(
        self,
        segments: List[Dict],
        speaker_voices: Dict[str, str] = None,
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """使用 OpenAI TTS 生成音訊"""
        from .audio_service import get_audio_service

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

        for i, seg in enumerate(segments):
            speaker = seg['speaker']
            text = seg['text']
            voice = default_voices.get(speaker, 'alloy')

            logger.info(f"生成片段 {i+1}/{len(segments)}: {speaker} ({voice})")

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

    def _generate_audio_edge(
        self,
        segments: List[Dict],
        speaker_voices: Dict[str, str] = None,
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """使用 Edge TTS 生成音訊（免費）"""
        try:
            import edge_tts
        except ImportError:
            return None, "edge-tts 未安裝，請執行 pip install edge-tts"

        # 預設語音映射
        default_voices = {
            "小明": "zh-TW-YunJheNeural",
            "小美": "zh-TW-HsiaoChenNeural",
            "王教授": "zh-TW-YunJheNeural",
            "李博士": "zh-TW-HsiaoYuNeural",
        }

        if speaker_voices:
            default_voices.update(speaker_voices)

        # 收集所有講者
        unique_speakers = list(set(seg['speaker'] for seg in segments))
        available_voices = list(EDGE_VOICES.keys())

        for i, speaker in enumerate(unique_speakers):
            if speaker not in default_voices:
                default_voices[speaker] = available_voices[i % len(available_voices)]

        async def generate_all():
            audio_parts = []

            for i, seg in enumerate(segments):
                speaker = seg['speaker']
                text = seg['text']
                voice = default_voices.get(speaker, "zh-TW-HsiaoChenNeural")

                logger.info(f"Edge TTS 生成片段 {i+1}/{len(segments)}: {speaker}")

                try:
                    communicate = edge_tts.Communicate(text, voice)
                    audio_data = b""

                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data += chunk["data"]

                    if audio_data:
                        audio_parts.append(audio_data)

                except Exception as e:
                    logger.warning(f"Edge TTS 片段 {i+1} 生成失敗: {e}")
                    continue

            return audio_parts

        try:
            # 執行異步生成
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_parts = loop.run_until_complete(generate_all())
            loop.close()

            if not audio_parts:
                return None, "Edge TTS 沒有成功生成任何音訊片段"

            combined_audio = self._combine_audio(audio_parts, output_format)
            return combined_audio, None

        except Exception as e:
            logger.error(f"Edge TTS 生成失敗: {e}")
            return None, f"Edge TTS 生成失敗: {str(e)}"

    def _generate_audio_google(
        self,
        segments: List[Dict],
        speaker_voices: Dict[str, str] = None,
        output_format: str = 'mp3'
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """使用 Google Cloud TTS 生成音訊"""
        try:
            from google.cloud import texttospeech
        except ImportError:
            return None, "google-cloud-texttospeech 未安裝"

        # TODO: 實作 Google Cloud TTS
        return None, "Google Cloud TTS 尚未實作，請使用 openai 或 edge"

    def _combine_audio(
        self,
        audio_parts: List[bytes],
        format: str = 'mp3',
        pause_duration: int = 400
    ) -> bytes:
        """合併多段音訊，加入停頓"""
        try:
            from pydub import AudioSegment

            combined = AudioSegment.empty()

            for i, part in enumerate(audio_parts):
                try:
                    segment = AudioSegment.from_file(io.BytesIO(part), format=format)

                    # 正規化音量
                    segment = segment.normalize()

                    # 加入停頓（講者切換時停頓較長）
                    combined += segment + AudioSegment.silent(duration=pause_duration)

                except Exception as e:
                    logger.warning(f"片段 {i+1} 處理失敗: {e}")
                    continue

            # 輸出
            output = io.BytesIO()
            combined.export(output, format=format, bitrate="192k")
            return output.getvalue()

        except ImportError:
            logger.warning("pydub 未安裝，使用簡單串接方式")
            return b''.join(audio_parts)

    def generate_full_podcast(
        self,
        content: str,
        speakers: List[Dict[str, Any]] = None,
        duration_minutes: int = 10,
        style: str = "conversational",
        with_audio: bool = True,
        tts_provider: str = "openai",
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
            tts_provider: TTS 提供商
            speaker_voices: 講者語音映射

        Returns:
            包含腳本和音訊的結果
        """
        result = {
            "type": "podcast",
            "script": None,
            "audio": None,
            "audio_base64": None,
            "tts_provider": tts_provider,
            "error": None
        }

        # 生成腳本
        logger.info("開始生成播客腳本")
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
        logger.info(f"腳本生成完成，共 {len(script.get('segments', []))} 段對話")

        # 生成音訊
        if with_audio:
            logger.info(f"開始生成音訊 (提供商: {tts_provider})")
            audio_data, audio_error = self.generate_podcast_audio(
                script=script,
                speaker_voices=speaker_voices,
                tts_provider=tts_provider
            )

            if audio_error:
                result["error"] = f"腳本生成成功，但音訊生成失敗: {audio_error}"
            elif audio_data:
                result["audio"] = audio_data
                import base64
                result["audio_base64"] = base64.b64encode(audio_data).decode('utf-8')
                logger.info("音訊生成完成")

        return result

    def get_available_voices(self, provider: str = "openai") -> List[Dict[str, str]]:
        """取得可用的 TTS 語音列表"""
        if provider == "edge":
            return [
                {"id": voice_id, "name": info["name"], "gender": info["gender"], "description": info["style"]}
                for voice_id, info in EDGE_VOICES.items()
            ]
        else:
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
            {"id": "storytelling", "name": "故事式", "description": "敘事方式呈現內容"},
            {"id": "panel", "name": "座談式", "description": "多位專家各抒己見"},
        ]

    def get_tts_providers(self) -> List[Dict[str, str]]:
        """取得可用的 TTS 提供商"""
        providers = [
            {"id": "openai", "name": "OpenAI", "description": "高品質，需 API Key"},
        ]

        # 檢查 Edge TTS 是否可用
        try:
            import edge_tts
            providers.append({
                "id": "edge",
                "name": "Edge TTS",
                "description": "免費，微軟語音"
            })
        except ImportError:
            pass

        return providers


# 全局實例
_podcast_service: Optional[PodcastService] = None


def get_podcast_service() -> PodcastService:
    """取得播客服務實例"""
    global _podcast_service
    if _podcast_service is None:
        _podcast_service = PodcastService()
    return _podcast_service
