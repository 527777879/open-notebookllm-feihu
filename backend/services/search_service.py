"""
搜尋服務 - 全文搜尋 + 向量搜尋混合模式（進階版）

支援功能：
- BM25 全文搜尋
- 向量語義搜尋
- Reciprocal Rank Fusion (RRF) 融合算法
- 查詢擴展 (Query Expansion)
- LLM Reranking 重排序
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text

from models import db, Source

logger = logging.getLogger(__name__)

# RRF 參數
RRF_K = 60  # RRF 常數，控制排名靠後結果的影響力


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
        vector_weight: float = 0.7,
        use_rrf: bool = True,
        use_query_expansion: bool = False,
        use_reranking: bool = False
    ) -> List[Dict[str, Any]]:
        """
        混合搜尋 - 結合全文搜尋和向量搜尋

        Args:
            query: 搜尋查詢
            source_ids: 限定來源 ID 列表
            notebook_id: 限定筆記本 ID
            top_k: 返回結果數量
            fulltext_weight: 全文搜尋權重（僅在非 RRF 模式使用）
            vector_weight: 向量搜尋權重（僅在非 RRF 模式使用）
            use_rrf: 是否使用 Reciprocal Rank Fusion（推薦）
            use_query_expansion: 是否使用查詢擴展
            use_reranking: 是否使用 LLM 重排序

        Returns:
            混合排序後的搜尋結果
        """
        from .rag_service import get_rag_service

        # 查詢擴展
        expanded_queries = [query]
        if use_query_expansion:
            expanded_queries = self._expand_query(query)
            logger.info(f"查詢擴展: {query} -> {expanded_queries}")

        all_fulltext_results = []
        all_vector_results = []

        # 對每個擴展查詢執行搜尋
        for q in expanded_queries:
            # 執行全文搜尋
            ft_results = self.fulltext_search(
                q, source_ids, notebook_id, limit=top_k * 2
            )
            all_fulltext_results.extend(ft_results)

            # 執行向量搜尋
            rag_service = get_rag_service()
            vec_results = rag_service.retrieve(
                q, source_ids, notebook_id, top_k=top_k * 2
            )
            all_vector_results.extend(vec_results)

        # 去重並保留最佳結果
        fulltext_results = self._deduplicate_results(all_fulltext_results, key="source_id")
        vector_results = self._deduplicate_vector_results(all_vector_results)

        # 根據選擇的算法合併結果
        if use_rrf:
            merged_results = self._rrf_fusion(fulltext_results, vector_results, top_k)
        else:
            merged_results = self._weighted_fusion(
                fulltext_results, vector_results,
                fulltext_weight, vector_weight, top_k
            )

        # LLM 重排序
        if use_reranking and merged_results:
            merged_results = self._rerank_results(query, merged_results, top_k)

        return merged_results

    def _expand_query(self, query: str) -> List[str]:
        """
        查詢擴展 - 使用 LLM 生成相關查詢變體

        Args:
            query: 原始查詢

        Returns:
            擴展後的查詢列表（包含原始查詢）
        """
        from .ai_service_manager import get_ai_service

        try:
            ai_service = get_ai_service()
            prompt = f"""請為以下搜尋查詢生成 2-3 個語義相似的變體，用於擴展搜尋範圍。

原始查詢：{query}

要求：
1. 保持相同的搜尋意圖
2. 使用不同的詞彙表達
3. 包含同義詞或相關術語

請直接返回 JSON 陣列格式，例如：
["變體1", "變體2", "變體3"]"""

            result = ai_service.generate_json(prompt)
            if isinstance(result, list):
                return [query] + result[:3]  # 原始查詢 + 最多 3 個變體
        except Exception as e:
            logger.warning(f"查詢擴展失敗: {e}")

        return [query]

    def _rrf_fusion(
        self,
        fulltext_results: List[Dict],
        vector_results: List[Tuple],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF) 融合算法

        RRF 分數 = Σ 1/(k + rank_i)
        其中 k 是常數（通常為 60），rank_i 是在第 i 個排名列表中的位置

        優點：
        - 不需要標準化分數
        - 對異常值更穩健
        - 自動平衡不同搜尋方法的貢獻
        """
        rrf_scores = {}

        # 處理全文搜尋結果的 RRF 分數
        for rank, r in enumerate(fulltext_results, 1):
            source_id = r["source_id"]
            rrf_score = 1.0 / (RRF_K + rank)

            if source_id not in rrf_scores:
                rrf_scores[source_id] = {
                    "source_id": source_id,
                    "source_name": r["source_name"],
                    "source_type": r.get("source_type", "unknown"),
                    "snippet": r["snippet"],
                    "rrf_score": rrf_score,
                    "fulltext_rank": rank,
                    "vector_rank": 999,
                    "fulltext_score": r.get("score", 0),
                    "vector_score": 0
                }
            else:
                rrf_scores[source_id]["rrf_score"] += rrf_score
                rrf_scores[source_id]["fulltext_rank"] = rank
                rrf_scores[source_id]["fulltext_score"] = r.get("score", 0)

        # 處理向量搜尋結果的 RRF 分數
        for rank, item in enumerate(vector_results, 1):
            chunk_text, similarity, source_id, source_name = item
            rrf_score = 1.0 / (RRF_K + rank)

            if source_id not in rrf_scores:
                source = Source.query.get(source_id)
                rrf_scores[source_id] = {
                    "source_id": source_id,
                    "source_name": source_name,
                    "source_type": source.type if source else "unknown",
                    "snippet": chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text,
                    "rrf_score": rrf_score,
                    "fulltext_rank": 999,
                    "vector_rank": rank,
                    "fulltext_score": 0,
                    "vector_score": similarity
                }
            else:
                rrf_scores[source_id]["rrf_score"] += rrf_score
                rrf_scores[source_id]["vector_rank"] = rank
                rrf_scores[source_id]["vector_score"] = similarity
                # 如果向量搜尋的片段更長更完整，更新 snippet
                if similarity > 0.6:
                    rrf_scores[source_id]["snippet"] = chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text

        # 按 RRF 分數排序
        sorted_results = sorted(
            rrf_scores.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )[:top_k]

        # 添加混合分數欄位（兼容性）
        for r in sorted_results:
            r["hybrid_score"] = r["rrf_score"]

        return sorted_results

    def _weighted_fusion(
        self,
        fulltext_results: List[Dict],
        vector_results: List[Tuple],
        fulltext_weight: float,
        vector_weight: float,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """加權融合算法（原始方法）"""
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

        sorted_results = sorted(
            merged.values(),
            key=lambda x: x["hybrid_score"],
            reverse=True
        )[:top_k]

        return sorted_results

    def _rerank_results(
        self,
        query: str,
        results: List[Dict],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        使用 LLM 進行重排序

        Args:
            query: 原始查詢
            results: 初步檢索結果
            top_k: 返回數量

        Returns:
            重排序後的結果
        """
        from .ai_service_manager import get_ai_service

        if not results:
            return results

        try:
            ai_service = get_ai_service()

            # 準備文檔列表
            docs_text = ""
            for i, r in enumerate(results[:15]):  # 最多處理 15 個結果
                snippet = r.get("snippet", "")[:200]
                docs_text += f"[{i}] {r.get('source_name', '未知')}: {snippet}\n\n"

            prompt = f"""請根據查詢的相關性對以下搜尋結果進行重新排序。

查詢：{query}

搜尋結果：
{docs_text}

請返回按相關性從高到低排序的文檔編號列表（JSON 陣列格式）。
只返回編號，例如：[2, 0, 5, 1, 3]

評判標準：
1. 與查詢的語義相關性
2. 資訊的完整性和準確性
3. 內容的具體程度"""

            reranked_indices = ai_service.generate_json(prompt)

            if isinstance(reranked_indices, list):
                # 根據重排序結果重新組織
                reranked_results = []
                seen = set()
                for idx in reranked_indices:
                    if isinstance(idx, int) and 0 <= idx < len(results) and idx not in seen:
                        result = results[idx].copy()
                        result["rerank_position"] = len(reranked_results) + 1
                        reranked_results.append(result)
                        seen.add(idx)

                # 添加未被重排序的結果
                for i, r in enumerate(results):
                    if i not in seen:
                        reranked_results.append(r)

                logger.info(f"LLM 重排序完成，結果順序已更新")
                return reranked_results[:top_k]

        except Exception as e:
            logger.warning(f"LLM 重排序失敗: {e}")

        return results[:top_k]

    def _deduplicate_results(
        self,
        results: List[Dict],
        key: str = "source_id"
    ) -> List[Dict]:
        """去重並保留最高分結果"""
        seen = {}
        for r in results:
            k = r.get(key)
            if k not in seen or r.get("score", 0) > seen[k].get("score", 0):
                seen[k] = r
        return list(seen.values())

    def _deduplicate_vector_results(
        self,
        results: List[Tuple]
    ) -> List[Tuple]:
        """向量搜尋結果去重"""
        seen = {}
        for item in results:
            chunk_text, similarity, source_id, source_name = item
            if source_id not in seen or similarity > seen[source_id][1]:
                seen[source_id] = item
        return list(seen.values())

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
