"""
工作室輸出模型
"""
from datetime import datetime
from . import db, generate_uuid


class StudioOutput(db.Model):
    """工作室輸出"""
    __tablename__ = 'studio_outputs'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    notebook_id = db.Column(db.String(36), db.ForeignKey('notebooks.id'), nullable=False)

    # 輸出類型: audio_overview, video_summary, mindmap, report, flashcards, quiz, infographic, presentation, datatable
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=True)

    # 輸出內容 (JSON)
    data = db.Column(db.JSON, nullable=False)

    # 使用的來源 ID 列表
    source_ids = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'notebook_id': self.notebook_id,
            'type': self.type,
            'title': self.title,
            'data': self.data,
            'source_ids': self.source_ids,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<StudioOutput {self.type}: {self.title}>'
