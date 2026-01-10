"""
筆記模型
"""
from datetime import datetime
from . import db, generate_uuid


class Note(db.Model):
    """筆記"""
    __tablename__ = 'notes'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    notebook_id = db.Column(db.String(36), db.ForeignKey('notebooks.id'), nullable=False)

    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)

    # 來源訊息 ID (如果是從對話儲存的)
    from_message_id = db.Column(db.String(36), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'notebook_id': self.notebook_id,
            'title': self.title,
            'content': self.content,
            'from_message_id': self.from_message_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Note {self.title or self.content[:30]}...>'
