"""
RAG (檢索增強生成) 服務
"""
import logging
from typing import List, Tuple, Optional
import numpy as np

from models import db, Source, Embedding
from .ai_service_manager import get_ai_service
from config import get_config

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 檢索增強生成服務"""

    def __init__(self):
        config = get_config()
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        self.top_k = config.TOP_K_RESULTS

    def process_source(self, source: Source) -> List[Embedding]:
        """
        處理來源並建立向量嵌入

        Args:
            source: 來源物件

        Returns:
            嵌入列表
        """
        ai_service = get_ai_service()

        # 1. 分割文本
        chunks = self._split_text(source.content)
        logger.info(f"來源 {source.id} 分割為 {len(chunks)} 個片段")

        # 2. 建立嵌入
        embeddings = []
        for i, chunk in enumerate(chunks):
            try:
                vector = ai_service.get_embedding(chunk)
                embedding = Embedding(
                    source_id=source.id,
                    chunk_index=i,
                    chunk_text=chunk,
                    embedding=np.array(vector, dtype=np.float32).tobytes()
                )
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"片段 {i} 嵌入生成失敗: {e}")
                continue

        # 3. 儲存到資料庫
        if embeddings:
            db.session.add_all(embeddings)
            db.session.commit()
            logger.info(f"已儲存 {len(embeddings)} 個嵌入")

        return embeddings

    def retrieve(
        self,
        query: str,
        source_ids: Optional[List[str]] = None,
        notebook_id: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[str, float, str, str]]:
        """
        檢索相關文本片段

        Args:
            query: 查詢文字
            source_ids: 指定的來源 ID 列表 (可選)
            notebook_id: 筆記本 ID (當 source_ids 為空時使用)
            top_k: 返回結果數量

        Returns:
            (片段文字, 相似度分數, 來源 ID, 來源名稱) 元組列表
        """
        ai_service = get_ai_service()
        top_k = top_k or self.top_k

        # 1. 取得查詢向量
        query_vector = np.array(ai_service.get_embedding(query), dtype=np.float32)

        # 2. 查詢嵌入
        query_obj = Embedding.query

        if source_ids:
            query_obj = query_obj.filter(Embedding.source_id.in_(source_ids))
        elif notebook_id:
            # 取得筆記本下所有來源的 ID
            sources = Source.query.filter_by(notebook_id=notebook_id).all()
            source_id_list = [s.id for s in sources]
            if source_id_list:
                query_obj = query_obj.filter(Embedding.source_id.in_(source_id_list))
            else:
                return []

        embeddings = query_obj.all()

        if not embeddings:
            logger.warning("沒有找到任何嵌入")
            return []

        # 3. 計算相似度
        results = []
        for emb in embeddings:
            emb_vector = np.frombuffer(emb.embedding, dtype=np.float32)
            similarity = self._cosine_similarity(query_vector, emb_vector)

            # 取得來源名稱
            source = Source.query.get(emb.source_id)
            source_name = source.name if source else "未知來源"

            results.append((emb.chunk_text, similarity, emb.source_id, source_name))

        # 4. 排序並返回 top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def build_context(
        self,
        query: str,
        source_ids: Optional[List[str]] = None,
        notebook_id: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> Tuple[str, List[dict]]:
        """
        建立 RAG 上下文

        Args:
            query: 查詢文字
            source_ids: 指定的來源 ID 列表
            notebook_id: 筆記本 ID
            top_k: 結果數量

        Returns:
            (上下文文字, 來源引用列表)
        """
        results = self.retrieve(query, source_ids, notebook_id, top_k)

        if not results:
            return "", []

        # 建立上下文
        context_parts = []
        source_refs = []

        for i, (chunk_text, similarity, source_id, source_name) in enumerate(results):
            context_parts.append(f"[來源 {i+1}: {source_name}]\n{chunk_text}")
            source_refs.append({
                "source_id": source_id,
                "source_name": source_name,
                "chunk_text": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                "similarity": float(similarity)
            })

        context = "\n\n---\n\n".join(context_parts)
        return context, source_refs

    def _split_text(self, text: str) -> List[str]:
        """
        分割文本為重疊的塊

        Args:
            text: 原始文字

        Returns:
            文字片段列表
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # 嘗試在句號或換行處斷開
            if end < len(text):
                # 找最近的斷句點
                break_points = [
                    text.rfind('。', start, end),
                    text.rfind('\n', start, end),
                    text.rfind('. ', start, end),
                    text.rfind('！', start, end),
                    text.rfind('？', start, end),
                ]
                best_break = max(break_points)
                if best_break > start + self.chunk_size // 2:
                    end = best_break + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """計算餘弦相似度"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def delete_source_embeddings(self, source_id: str):
        """刪除來源的所有嵌入"""
        Embedding.query.filter_by(source_id=source_id).delete()
        db.session.commit()
        logger.info(f"已刪除來源 {source_id} 的所有嵌入")


# 全局實例
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """取得 RAG 服務實例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
