"""
NoteBookLLM 資料庫模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


def generate_uuid():
    """生成 UUID"""
    return str(uuid.uuid4())


# 匯出所有模型
from .folder import Folder
from .notebook import Notebook
from .source import Source
from .embedding import Embedding
from .chat_message import ChatMessage
from .note import Note
from .studio_output import StudioOutput

__all__ = [
    'db',
    'generate_uuid',
    'Folder',
    'Notebook',
    'Source',
    'Embedding',
    'ChatMessage',
    'Note',
    'StudioOutput'
]
