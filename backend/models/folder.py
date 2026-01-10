"""
資料夾模型
"""
import uuid
from datetime import datetime
from . import db


class Folder(db.Model):
    """資料夾模型 - 用於組織筆記本"""

    __tablename__ = 'folders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    emoji = db.Column(db.String(10), default='📁')  # 資料夾圖示
    color = db.Column(db.String(20), default=None)  # 可選的顏色標籤
    order = db.Column(db.Integer, default=0)  # 排序順序
    is_expanded = db.Column(db.Boolean, default=True)  # 是否展開
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯：一個資料夾有多個筆記本
    notebooks = db.relationship('Notebook', backref='folder', lazy='dynamic')

    def to_dict(self, include_notebooks=False):
        """轉換為字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'color': self.color,
            'order': self.order,
            'is_expanded': self.is_expanded,
            'notebook_count': self.notebooks.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_notebooks:
            data['notebooks'] = [nb.to_dict() for nb in self.notebooks.order_by('order', 'created_at')]

        return data

    def __repr__(self):
        return f'<Folder {self.emoji} {self.name}>'
