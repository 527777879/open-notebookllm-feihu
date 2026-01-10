"""
向量嵌入模型
"""
from datetime import datetime
from . import db, generate_uuid


class Embedding(db.Model):
    """向量嵌入"""
    __tablename__ = 'embeddings'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    source_id = db.Column(db.String(36), db.ForeignKey('sources.id'), nullable=False)

    chunk_index = db.Column(db.Integer, nullable=False)  # 文本分塊索引
    chunk_text = db.Column(db.Text, nullable=False)  # 分塊文本
    embedding = db.Column(db.LargeBinary, nullable=False)  # 向量嵌入 (numpy array 序列化)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'source_id': self.source_id,
            'chunk_index': self.chunk_index,
            'chunk_text': self.chunk_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Embedding {self.source_id}:{self.chunk_index}>'
