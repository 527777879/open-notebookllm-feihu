"""
來源控制器 - 支援多種來源類型
"""
import os
import uuid
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from . import source_bp, notebook_bp
from models import db, Notebook, Source
from services.file_parser_service import get_file_parser
from services.rag_service import get_rag_service
from services.search_service import get_search_service
from services.web_scraper_service import get_web_scraper
from services.youtube_service import get_youtube_service
from services.audio_service import get_audio_service

# 支援的音檔格式
AUDIO_EXTENSIONS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac'}


def allowed_file(filename):
    """檢查文件是否允許上傳"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    all_extensions = current_app.config['ALLOWED_EXTENSIONS'] | AUDIO_EXTENSIONS
    return ext in all_extensions


@notebook_bp.route('/<notebook_id>/sources', methods=['GET'])
def list_sources(notebook_id):
    """取得筆記本的所有來源"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    sources = Source.query.filter_by(notebook_id=notebook_id).order_by(Source.created_at.desc()).all()

    return jsonify({
        'success': True,
        'data': [s.to_dict() for s in sources]
    })


@notebook_bp.route('/<notebook_id>/sources/upload', methods=['POST'])
def upload_source(notebook_id):
    """上傳文件來源（支援文件和音檔）"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '沒有上傳文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '沒有選擇文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '不支援的文件格式'}), 400

    # 儲存文件
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)

    # 判斷文件類型
    ext = filename.rsplit('.', 1)[1].lower()

    # 如果是音檔，使用語音轉文字
    if ext in AUDIO_EXTENSIONS:
        audio_service = get_audio_service()
        stt_provider = request.form.get('stt_provider', 'openai')
        language = request.form.get('language')

        content, metadata, error = audio_service.transcribe_file(
            file_path, language=language, provider=stt_provider
        )

        if error:
            os.remove(file_path)
            return jsonify({'success': False, 'error': error}), 400

        source = Source(
            notebook_id=notebook_id,
            type='audio',
            name=filename,
            content=content,
            file_path=file_path,
            metadata={
                'original_filename': filename,
                'file_size': os.path.getsize(file_path),
                'duration': metadata.get('duration'),
                'language': metadata.get('language'),
                'stt_provider': stt_provider
            }
        )
    else:
        # 解析文件
        file_parser = get_file_parser()
        content, error = file_parser.parse_file(file_path, filename)

        if error:
            os.remove(file_path)
            return jsonify({'success': False, 'error': error}), 400

        type_map = {
            'pdf': 'pdf',
            'txt': 'text',
            'md': 'text',
            'docx': 'gdocs',
            'doc': 'gdocs',
            'xlsx': 'gdocs',
            'xls': 'gdocs',
            'csv': 'gdocs'
        }

        source = Source(
            notebook_id=notebook_id,
            type=type_map.get(ext, 'text'),
            name=filename,
            content=content,
            file_path=file_path,
            metadata={
                'original_filename': filename,
                'file_size': os.path.getsize(file_path)
            }
        )

    db.session.add(source)
    db.session.commit()

    # 建立向量嵌入和全文索引
    try:
        rag_service = get_rag_service()
        rag_service.process_source(source)

        search_service = get_search_service()
        search_service.index_source(source)
    except Exception as e:
        current_app.logger.error(f"索引建立失敗: {e}")

    return jsonify({
        'success': True,
        'data': source.to_dict()
    }), 201


@notebook_bp.route('/<notebook_id>/sources/url', methods=['POST'])
def add_url_source(notebook_id):
    """新增網址來源（使用改進的網頁擷取服務）"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': '網址為必填'}), 400

    try:
        web_scraper = get_web_scraper()
        content, metadata, error = web_scraper.scrape_url(url)

        if error:
            return jsonify({'success': False, 'error': error}), 400

        title = metadata.get('title') or url[:100]

        # 建立來源
        source = Source(
            notebook_id=notebook_id,
            type='web',
            name=title[:200],
            url=url,
            content=content,
            metadata=metadata
        )

        db.session.add(source)
        db.session.commit()

        # 建立向量嵌入和全文索引
        try:
            rag_service = get_rag_service()
            rag_service.process_source(source)

            search_service = get_search_service()
            search_service.index_source(source)
        except Exception as e:
            current_app.logger.error(f"索引建立失敗: {e}")

        return jsonify({
            'success': True,
            'data': source.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': f'網頁抓取失敗: {str(e)}'}), 400


@notebook_bp.route('/<notebook_id>/sources/youtube', methods=['POST'])
def add_youtube_source(notebook_id):
    """新增 YouTube 來源（使用改進的 YouTube 服務）"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'YouTube 網址為必填'}), 400

    try:
        youtube_service = get_youtube_service()
        content, metadata, error = youtube_service.process_youtube_url(url)

        if error:
            return jsonify({'success': False, 'error': error}), 400

        title = metadata.get('title') or f"YouTube Video ({metadata.get('video_id', 'unknown')})"

        # 建立來源
        source = Source(
            notebook_id=notebook_id,
            type='youtube',
            name=title[:200],
            url=url,
            content=content,
            metadata=metadata
        )

        db.session.add(source)
        db.session.commit()

        # 建立向量嵌入和全文索引
        try:
            rag_service = get_rag_service()
            rag_service.process_source(source)

            search_service = get_search_service()
            search_service.index_source(source)
        except Exception as e:
            current_app.logger.error(f"索引建立失敗: {e}")

        return jsonify({
            'success': True,
            'data': source.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@notebook_bp.route('/<notebook_id>/sources/text', methods=['POST'])
def add_text_source(notebook_id):
    """新增純文字來源"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    name = data.get('name', '未命名文字')
    content = data.get('content')

    if not content:
        return jsonify({'success': False, 'error': '內容為必填'}), 400

    source = Source(
        notebook_id=notebook_id,
        type='text',
        name=name,
        content=content
    )

    db.session.add(source)
    db.session.commit()

    # 建立向量嵌入
    try:
        rag_service = get_rag_service()
        rag_service.process_source(source)
    except Exception as e:
        current_app.logger.error(f"向量嵌入建立失敗: {e}")

    return jsonify({
        'success': True,
        'data': source.to_dict()
    }), 201


@source_bp.route('/sources/<source_id>', methods=['GET'])
def get_source(source_id):
    """取得單一來源"""
    source = Source.query.get(source_id)
    if not source:
        return jsonify({'success': False, 'error': '來源不存在'}), 404

    return jsonify({
        'success': True,
        'data': source.to_dict(include_content=True)
    })


@source_bp.route('/sources/<source_id>', methods=['DELETE'])
def delete_source(source_id):
    """刪除來源"""
    source = Source.query.get(source_id)
    if not source:
        return jsonify({'success': False, 'error': '來源不存在'}), 404

    # 刪除文件
    if source.file_path and os.path.exists(source.file_path):
        os.remove(source.file_path)

    # 刪除嵌入
    rag_service = get_rag_service()
    rag_service.delete_source_embeddings(source_id)

    # 刪除全文索引
    search_service = get_search_service()
    search_service.remove_source_index(source_id)

    db.session.delete(source)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '來源已刪除'
    })


# ==================== 搜尋 API ====================

@notebook_bp.route('/<notebook_id>/search', methods=['POST'])
def search_sources(notebook_id):
    """搜尋筆記本內的來源（混合搜尋）"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    query = data.get('query', '')
    search_type = data.get('type', 'hybrid')  # 'hybrid', 'fulltext', 'vector'
    top_k = data.get('top_k', 10)
    source_ids = data.get('source_ids')  # 可選：限定搜尋範圍

    if not query:
        return jsonify({'success': False, 'error': '搜尋查詢為必填'}), 400

    search_service = get_search_service()

    if search_type == 'fulltext':
        results = search_service.fulltext_search(
            query, source_ids=source_ids, notebook_id=notebook_id, limit=top_k
        )
    elif search_type == 'vector':
        rag_service = get_rag_service()
        raw_results = rag_service.retrieve(
            query, source_ids=source_ids, notebook_id=notebook_id, top_k=top_k
        )
        results = [
            {
                "source_id": r[2],
                "source_name": r[3],
                "snippet": r[0][:200] + "..." if len(r[0]) > 200 else r[0],
                "score": r[1],
                "search_type": "vector"
            }
            for r in raw_results
        ]
    else:  # hybrid
        results = search_service.hybrid_search(
            query, source_ids=source_ids, notebook_id=notebook_id, top_k=top_k
        )

    return jsonify({
        'success': True,
        'data': {
            'query': query,
            'type': search_type,
            'results': results
        }
    })


@source_bp.route('/sources/reindex', methods=['POST'])
def reindex_sources():
    """重建全文搜尋索引"""
    data = request.get_json() or {}
    notebook_id = data.get('notebook_id')

    search_service = get_search_service()
    count = search_service.reindex_all(notebook_id)

    return jsonify({
        'success': True,
        'message': f'已重建 {count} 個來源的索引'
    })


@source_bp.route('/sources/reembed', methods=['POST'])
def reembed_sources():
    """重建向量嵌入（刪除舊嵌入並重新分塊、嵌入）"""
    data = request.get_json() or {}
    source_id = data.get('source_id')
    notebook_id = data.get('notebook_id')

    rag_service = get_rag_service()

    if source_id:
        # 重建單一來源
        source = Source.query.get(source_id)
        if not source:
            return jsonify({'success': False, 'error': '來源不存在'}), 404

        rag_service.delete_source_embeddings(source_id)
        embeddings = rag_service.process_source(source)

        return jsonify({
            'success': True,
            'message': f'已重建嵌入，共 {len(embeddings)} 個片段'
        })

    elif notebook_id:
        # 重建整個筆記本的所有來源
        sources = Source.query.filter_by(notebook_id=notebook_id).all()
        total = 0
        for source in sources:
            rag_service.delete_source_embeddings(source.id)
            embeddings = rag_service.process_source(source)
            total += len(embeddings)

        return jsonify({
            'success': True,
            'message': f'已重建 {len(sources)} 個來源的嵌入，共 {total} 個片段'
        })

    else:
        return jsonify({'success': False, 'error': '請提供 source_id 或 notebook_id'}), 400


# ==================== Web Search API ====================

@source_bp.route('/web-search', methods=['POST'])
def web_search():
    """使用 Tavily API 搜尋網路"""
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'success': False, 'error': '搜尋查詢為必填'}), 400

    from services.web_search_service import get_web_search_service
    search_service = get_web_search_service()
    result = search_service.search(query)

    if result.get('error'):
        return jsonify({'success': False, 'error': result['error']}), 400

    return jsonify({
        'success': True,
        'data': result
    })


@notebook_bp.route('/<notebook_id>/sources/web-search-results', methods=['POST'])
def save_web_search_results(notebook_id):
    """批量保存網路搜尋結果為來源（驗證 URL 可達性，保存 URL + 摘要）"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    results = data.get('results', [])

    if not results:
        return jsonify({'success': False, 'error': '沒有選擇搜尋結果'}), 400

    saved = []
    failed = []

    for item in results:
        url = item.get('url', '')
        title = item.get('title', '') or url[:100]
        summary = item.get('content', '')
        raw_content = item.get('raw_content', '')

        if not url:
            failed.append({'title': title, 'reason': '缺少 URL'})
            continue

        # 驗證 URL 是否可爬取（快速檢查，只確認頁面可載入）
        try:
            web_scraper = get_web_scraper()
            # 使用 Playwright 快速驗證，超時 15 秒，等待 1 秒
            from services.browser_scraper_service import get_browser_scraper
            browser_scraper = get_browser_scraper()
            scrape_content, scrape_meta, scrape_error = browser_scraper.scrape_url(url, timeout=15000, wait_ms=1000)
            if scrape_error and not scrape_content:
                current_app.logger.warning(f"URL 驗證失敗: {url} - {scrape_error}")
                failed.append({'title': title, 'reason': f'網頁無法訪問: {scrape_error[:80]}'})
                continue
        except ImportError:
            # Playwright 未安裝，跳過驗證
            pass
        except Exception as e:
            # 驗證失敗不阻止保存，只記錄警告
            current_app.logger.warning(f"URL 驗證異常（仍嘗試保存）: {url} - {e}")

        try:
            # 優先使用 raw_content（Tavily advanced 搜索的完整網頁內容），否則使用摘要
            if raw_content and len(raw_content.strip()) > len(summary):
                source_content = f"# {title}\n\n來源: {url}\n\n{raw_content}"
            elif summary:
                source_content = f"# {title}\n\n來源: {url}\n\n{summary}"
            else:
                source_content = f"# {title}\n\n來源: {url}"

            source = Source(
                notebook_id=notebook_id,
                type='web',
                name=title[:200],
                url=url,
                content=source_content,
                metadata={
                    'url': url,
                    'title': title,
                    'source': 'web_search',
                }
            )

            db.session.add(source)
            db.session.commit()

            # 建立向量嵌入和全文索引
            try:
                rag_service = get_rag_service()
                rag_service.process_source(source)
                search_service = get_search_service()
                search_service.index_source(source)
            except Exception as e:
                current_app.logger.error(f"索引建立失敗: {e}")

            saved.append(source.to_dict())
        except Exception as e:
            failed.append({'title': title, 'reason': str(e)})
            current_app.logger.error(f"保存搜索結果失敗: {e}")

    return jsonify({
        'success': True,
        'data': {
            'saved': saved,
            'failed': failed,
            'total': len(results),
            'saved_count': len(saved),
            'failed_count': len(failed),
        }
    })
