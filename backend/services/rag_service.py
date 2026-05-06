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

    # Embedding 模型的最大 token 限制（按字符估算：1 token ≈ 1.5 中文字符）
    MAX_EMBEDDING_CHARS = 350
    # 实时抓取网页内容的最大长度（避免过长消耗 token）
    MAX_LIVE_SCRAPED_CHARS = 8000

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

        # 2. 確保每個片段不超過 embedding 模型的 token 限制
        safe_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.MAX_EMBEDDING_CHARS:
                safe_chunks.append(chunk)
            else:
                # 對超長片段進一步分割
                sub_chunks = self._split_text(chunk)
                safe_chunks.extend(sub_chunks)

        if len(safe_chunks) != len(chunks):
            logger.info(f"來源 {source.id} 超長片段已再分割: {len(chunks)} → {len(safe_chunks)} 個片段")

        # 3. 建立嵌入
        embeddings = []
        for i, chunk in enumerate(safe_chunks):
            # 最終安全截斷：確保不超限
            if len(chunk) > self.MAX_EMBEDDING_CHARS:
                chunk = chunk[:self.MAX_EMBEDDING_CHARS]
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

        對於 web 類型來源（僅保存了 URL + 摘要），會實時抓取完整網頁內容。

        Args:
            query: 查詢文字
            source_ids: 指定的來源 ID 列表
            notebook_id: 筆記本 ID
            top_k: 結果數量

        Returns:
            (上下文文字, 來源引用列表)
        """
        try:
            results = self.retrieve(query, source_ids, notebook_id, top_k)
        except Exception as e:
            logger.warning(f"RAG 檢索失敗，跳過上下文建立: {e}")
            return "", []

        if not results:
            return "", []

        # 收集需要实时抓取的 web 来源
        # web 类型来源保存的是 URL + 摘要，对话时需要实时抓取完整网页内容
        web_source_ids = set()
        for chunk_text, similarity, source_id, source_name in results:
            source = Source.query.get(source_id)
            if source and source.type == 'web' and source.url:
                # 内容较短或来自搜索摘要，需要实时抓取完整内容
                # 仅当内容已经很长（> 8000 字）时跳过，说明已有完整网页内容
                if not source.content or len(source.content) < 8000:
                    web_source_ids.add(source_id)

        # 批量实时抓取 web 来源的完整内容
        live_contents = {}
        if web_source_ids:
            live_contents = self._fetch_web_sources(web_source_ids)

        # 建立上下文
        context_parts = []
        source_refs = []
        seen_web_sources = set()  # 去重：同一个 web source 只输出一次完整内容

        for i, (chunk_text, similarity, source_id, source_name) in enumerate(results):
            source = Source.query.get(source_id)

            # 如果是 web 来源且已实时抓取到完整内容
            if source and source.type == 'web' and source_id in live_contents:
                if source_id not in seen_web_sources:
                    seen_web_sources.add(source_id)
                    full_content = live_contents[source_id]
                    context_parts.append(f"[來源 {i+1}: {source_name} (網頁完整內容，來源: {source.url})]\n{full_content}")
                # 同一 source 的后续 chunk 跳过，避免重复输出完整网页
                source_refs.append({
                    "source_id": source_id,
                    "source_name": source_name,
                    "chunk_text": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                    "similarity": float(similarity),
                    "url": source.url,
                    "live_fetched": True
                })
            else:
                context_parts.append(f"[來源 {i+1}: {source_name}]\n{chunk_text}")
                source_refs.append({
                    "source_id": source_id,
                    "source_name": source_name,
                    "chunk_text": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                    "similarity": float(similarity)
                })

        context = "\n\n---\n\n".join(context_parts)
        return context, source_refs

    def _fetch_web_sources(self, source_ids: set) -> dict:
        """
        实时抓取 web 来源的完整网页内容

        Args:
            source_ids: 需要抓取的来源 ID 集合

        Returns:
            {source_id: 完整网页内容文本}
        """
        from .web_scraper_service import get_web_scraper

        web_scraper = get_web_scraper()
        contents = {}

        for source_id in source_ids:
            source = Source.query.get(source_id)
            if not source or not source.url:
                continue

            try:
                logger.info(f"實時抓取網頁: {source.url}")
                scraped_content, metadata, error = web_scraper.scrape_url(source.url)
                if scraped_content and len(scraped_content.strip()) > 50:
                    # 截断过长内容
                    if len(scraped_content) > self.MAX_LIVE_SCRAPED_CHARS:
                        scraped_content = scraped_content[:self.MAX_LIVE_SCRAPED_CHARS] + "\n...(內容已截斷)"
                    contents[source_id] = scraped_content
                    logger.info(f"網頁抓取成功: {source.url} ({len(scraped_content)} 字)")
                else:
                    logger.warning(f"網頁抓取內容不足: {source.url} - {error}")
            except Exception as e:
                logger.warning(f"網頁實時抓取失敗: {source.url} - {e}")

        return contents

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
