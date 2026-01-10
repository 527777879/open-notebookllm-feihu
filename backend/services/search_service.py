"""
搜尋服務 - 全文搜尋 + 向量搜尋混合模式
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text

from models import db, Source

logger = logging.getLogger(__name__)


class SearchService:
    """搜尋服務 - 支援全文搜尋和混合搜尋"""

    def __init__(self):
        self._fts_initialized = False

    def init_fts(self):
        """初始化全文搜尋虛擬表"""
        if self._fts_initialized:
            return

        try:
            # 建立 FTS5 虛擬表
            db.session.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS sources_fts USING fts5(
                    source_id,
                    name,
                    content,
                    tokenize='unicode61'
                )
            """))
            db.session.commit()
            self._fts_initialized = True
            logger.info("FTS5 全文搜尋索引初始化完成")
        except Exception as e:
            logger.warning(f"FTS5 初始化失敗 (可能已存在): {e}")
            self._fts_initialized = True

    def index_source(self, source: Source):
        """將來源加入全文搜尋索引"""
        self.init_fts()

        try:
            # 先刪除舊索引
            db.session.execute(
                text("DELETE FROM sources_fts WHERE source_id = :source_id"),
                {"source_id": source.id}
            )

            # 新增索引
            db.session.execute(
                text("""
                    INSERT INTO sources_fts (source_id, name, content)
                    VALUES (:source_id, :name, :content)
                """),
                {
                    "source_id": source.id,
                    "name": source.name,
                    "content": source.content or ""
                }
            )
            db.session.commit()
            logger.info(f"來源 {source.id} 已加入全文搜尋索引")
        except Exception as e:
            logger.error(f"索引來源失敗: {e}")
            db.session.rollback()

    def remove_source_index(self, source_id: str):
        """從全文搜尋索引移除來源"""
        try:
            db.session.execute(
                text("DELETE FROM sources_fts WHERE source_id = :source_id"),
                {"source_id": source_id}
            )
            db.session.commit()
        except Exception as e:
            logger.error(f"移除索引失敗: {e}")

    def fulltext_search(
        self,
        query: str,
        source_ids: Optional[List[str]] = None,
        notebook_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        全文搜尋

        Args:
            query: 搜尋關鍵字
            source_ids: 限定來源 ID 列表
            notebook_id: 限定筆記本 ID
            limit: 結果數量上限

        Returns:
            搜尋結果列表
        """
        self.init_fts()

        # 處理搜尋詞，支援中文
        search_terms = self._prepare_search_query(query)
        if not search_terms:
            return []

        try:
            # 基礎 FTS 查詢
            sql = """
                SELECT
                    source_id,
                    snippet(sources_fts, 2, '<mark>', '</mark>', '...', 64) as snippet,
                    bm25(sources_fts) as score
                FROM sources_fts
                WHERE sources_fts MATCH :query
            """

            params = {"query": search_terms, "limit": limit}

            # 如果有來源限制，需要過濾
            if source_ids:
                placeholders = ",".join([f":sid{i}" for i in range(len(source_ids))])
                sql += f" AND source_id IN ({placeholders})"
                for i, sid in enumerate(source_ids):
                    params[f"sid{i}"] = sid

            sql += " ORDER BY score LIMIT :limit"

            result = db.session.execute(text(sql), params)
            rows = result.fetchall()

            # 組裝結果
            results = []
            for row in rows:
                source = Source.query.get(row[0])
                if source:
                    # 如果有 notebook_id 限制，過濾不符合的
                    if notebook_id and source.notebook_id != notebook_id:
                        continue

                    results.append({
                        "source_id": source.id,
                        "source_name": source.name,
                        "source_type": source.type,
                        "snippet": row[1],
                        "score": abs(row[2]),  # bm25 回傳負數，取絕對值
                        "search_type": "fulltext"
                    })

            return results

        except Exception as e:
            logger.error(f"全文搜尋失敗: {e}")
            return []

    def _prepare_search_query(self, query: str) -> str:
        """準備 FTS5 搜尋查詢"""
        # 移除特殊字符
        query = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', query)
        terms = query.split()

        if not terms:
            return ""

        # 使用 OR 連接多個詞
        return " OR ".join(terms)

    def hybrid_search(
        self,
        query: str,
        source_ids: Optional[List[str]] = None,
        notebook_id: Optional[str] = None,
        top_k: int = 10,
        fulltext_weight: float = 0.3,
        vector_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        混合搜尋 - 結合全文搜尋和向量搜尋

        Args:
            query: 搜尋查詢
            source_ids: 限定來源 ID 列表
            notebook_id: 限定筆記本 ID
            top_k: 返回結果數量
            fulltext_weight: 全文搜尋權重
            vector_weight: 向量搜尋權重

        Returns:
            混合排序後的搜尋結果
        """
        from .rag_service import get_rag_service

        # 執行全文搜尋
        fulltext_results = self.fulltext_search(
            query, source_ids, notebook_id, limit=top_k * 2
        )

        # 執行向量搜尋
        rag_service = get_rag_service()
        vector_results = rag_service.retrieve(
            query, source_ids, notebook_id, top_k=top_k * 2
        )

        # 合併結果
        merged = {}

        # 處理全文搜尋結果
        for i, r in enumerate(fulltext_results):
            key = r["source_id"]
            if key not in merged:
                merged[key] = {
                    "source_id": r["source_id"],
                    "source_name": r["source_name"],
                    "source_type": r.get("source_type", "unknown"),
                    "snippet": r["snippet"],
                    "fulltext_score": r["score"],
                    "fulltext_rank": i + 1,
                    "vector_score": 0,
                    "vector_rank": 999
                }
            else:
                merged[key]["fulltext_score"] = r["score"]
                merged[key]["fulltext_rank"] = i + 1

        # 處理向量搜尋結果
        for i, (chunk_text, similarity, source_id, source_name) in enumerate(vector_results):
            if source_id not in merged:
                source = Source.query.get(source_id)
                merged[source_id] = {
                    "source_id": source_id,
                    "source_name": source_name,
                    "source_type": source.type if source else "unknown",
                    "snippet": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                    "fulltext_score": 0,
                    "fulltext_rank": 999,
                    "vector_score": similarity,
                    "vector_rank": i + 1
                }
            else:
                merged[source_id]["vector_score"] = similarity
                merged[source_id]["vector_rank"] = i + 1
                # 如果向量搜尋的片段更相關，更新 snippet
                if similarity > 0.7:
                    merged[source_id]["snippet"] = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text

        # 計算混合分數
        max_fulltext = max([r.get("fulltext_score", 0) for r in merged.values()]) or 1
        max_vector = max([r.get("vector_score", 0) for r in merged.values()]) or 1

        for r in merged.values():
            normalized_ft = r.get("fulltext_score", 0) / max_fulltext
            normalized_vec = r.get("vector_score", 0) / max_vector
            r["hybrid_score"] = (
                fulltext_weight * normalized_ft +
                vector_weight * normalized_vec
            )

        # 排序並返回
        sorted_results = sorted(
            merged.values(),
            key=lambda x: x["hybrid_score"],
            reverse=True
        )[:top_k]

        return sorted_results

    def reindex_all(self, notebook_id: Optional[str] = None):
        """重建所有來源的全文搜尋索引"""
        self.init_fts()

        query = Source.query
        if notebook_id:
            query = query.filter_by(notebook_id=notebook_id)

        sources = query.all()
        count = 0

        for source in sources:
            try:
                self.index_source(source)
                count += 1
            except Exception as e:
                logger.error(f"索引來源 {source.id} 失敗: {e}")

        logger.info(f"已重建 {count} 個來源的全文搜尋索引")
        return count


# 全局實例
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """取得搜尋服務實例"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
