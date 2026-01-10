"""
工作室控制器 - 支援多種內容生成（含 Podcast 播客）
"""
from flask import request, jsonify, Response
from . import studio_bp
from models import db, Notebook, StudioOutput
from services.studio_service import get_studio_service
from services.podcast_service import get_podcast_service
from services.audio_service import get_audio_service


@studio_bp.route('/<notebook_id>/studio/outputs', methods=['GET'])
def list_outputs(notebook_id):
    """取得工作室輸出列表"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    outputs = StudioOutput.query.filter_by(notebook_id=notebook_id).order_by(StudioOutput.created_at.desc()).all()

    return jsonify({
        'success': True,
        'data': [o.to_dict() for o in outputs]
    })


@studio_bp.route('/<notebook_id>/studio/summary', methods=['POST'])
def generate_summary(notebook_id):
    """生成摘要"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')

    studio_service = get_studio_service()
    result = studio_service.generate_summary(source_ids=source_ids, notebook_id=notebook_id)

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    # 儲存輸出
    output = StudioOutput(
        notebook_id=notebook_id,
        type='summary',
        title='摘要',
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/mindmap', methods=['POST'])
def generate_mindmap(notebook_id):
    """生成心智圖"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')

    studio_service = get_studio_service()
    result = studio_service.generate_mindmap(source_ids=source_ids, notebook_id=notebook_id)

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    output = StudioOutput(
        notebook_id=notebook_id,
        type='mindmap',
        title='心智圖',
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/flashcards', methods=['POST'])
def generate_flashcards(notebook_id):
    """
    生成學習卡

    Request body:
    {
        "source_ids": ["id1", "id2"],  // 可選，指定來源
        "count": 10,                    // 可選，學習卡數量
        "difficulty": "mixed"           // 可選，難度設定: easy/medium/hard/mixed
    }
    """
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')
    count = data.get('count', 10)
    difficulty = data.get('difficulty', 'mixed')

    studio_service = get_studio_service()
    result = studio_service.generate_flashcards(
        count=count,
        source_ids=source_ids,
        notebook_id=notebook_id,
        difficulty=difficulty
    )

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    # 標題包含難度資訊
    difficulty_labels = {'easy': '簡單', 'medium': '中等', 'hard': '困難', 'mixed': '混合'}
    title = f"學習卡 ({difficulty_labels.get(difficulty, '混合')}難度)"

    output = StudioOutput(
        notebook_id=notebook_id,
        type='flashcards',
        title=title,
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/quiz', methods=['POST'])
def generate_quiz(notebook_id):
    """
    生成測驗

    Request body:
    {
        "source_ids": ["id1", "id2"],  // 可選，指定來源
        "count": 10,                    // 可選，測驗題數量
        "difficulty": "mixed"           // 可選，難度設定: easy/medium/hard/mixed
    }
    """
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')
    count = data.get('count', 10)
    difficulty = data.get('difficulty', 'mixed')

    studio_service = get_studio_service()
    result = studio_service.generate_quiz(
        count=count,
        source_ids=source_ids,
        notebook_id=notebook_id,
        difficulty=difficulty
    )

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    # 標題包含難度資訊
    difficulty_labels = {'easy': '簡單', 'medium': '中等', 'hard': '困難', 'mixed': '混合'}
    title = f"測驗 ({difficulty_labels.get(difficulty, '混合')}難度)"

    output = StudioOutput(
        notebook_id=notebook_id,
        type='quiz',
        title=title,
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/report', methods=['POST'])
def generate_report(notebook_id):
    """生成報告"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')

    studio_service = get_studio_service()
    result = studio_service.generate_report(source_ids=source_ids, notebook_id=notebook_id)

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    output = StudioOutput(
        notebook_id=notebook_id,
        type='report',
        title='報告',
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/datatable', methods=['POST'])
def generate_datatable(notebook_id):
    """生成資料表"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')

    studio_service = get_studio_service()
    result = studio_service.generate_datatable(source_ids=source_ids, notebook_id=notebook_id)

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    output = StudioOutput(
        notebook_id=notebook_id,
        type='datatable',
        title='資料表',
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/presentation', methods=['POST'])
def generate_presentation(notebook_id):
    """生成簡報（含配圖）"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')
    slide_count = data.get('slide_count', 8)
    with_images = data.get('with_images', True)

    studio_service = get_studio_service()
    result = studio_service.generate_presentation(
        source_ids=source_ids,
        notebook_id=notebook_id,
        slide_count=slide_count,
        with_images=with_images
    )

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    output = StudioOutput(
        notebook_id=notebook_id,
        type='presentation',
        title='簡報',
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/infographic', methods=['POST'])
def generate_infographic(notebook_id):
    """
    生成資訊圖表（Chart.js 數據視覺化）

    Request body:
    {
        "source_ids": ["id1", "id2"],  // 可選，指定來源
        "with_ai_image": false          // 可選，是否額外生成 AI 裝飾圖片
    }

    Response:
    {
        "data": {
            "title": "圖表標題",
            "description": "圖表說明",
            "charts": [
                {
                    "id": "chart1",
                    "title": "子圖表標題",
                    "type": "bar/line/pie/radar/...",
                    "config": { /* Chart.js 配置 */ }
                }
            ],
            "summary": {
                "key_findings": ["發現1", "發現2"],
                "recommendations": ["建議1"]
            }
        }
    }
    """
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')
    with_ai_image = data.get('with_ai_image', False)

    studio_service = get_studio_service()
    result = studio_service.generate_infographic(
        source_ids=source_ids,
        notebook_id=notebook_id,
        with_ai_image=with_ai_image
    )

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    # 取得圖表數量和類型
    charts = result.get('charts', [])
    chart_types = list(set([c.get('type', 'bar') for c in charts]))
    title = result.get('data', {}).get('title', '資訊圖表')

    output = StudioOutput(
        notebook_id=notebook_id,
        type='infographic',
        title=f"{title} ({len(charts)} 個圖表)",
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/flowchart', methods=['POST'])
def generate_flowchart(notebook_id):
    """
    生成流程圖（draw.io 格式）

    Request body:
    {
        "source_ids": ["id1", "id2"]  // 可選，指定來源
    }

    Response:
    {
        "data": {
            "title": "流程圖標題",
            "description": "說明",
            "xml": "<mxGraphModel>...</mxGraphModel>",
            "type": "flowchart"
        }
    }
    """
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')

    studio_service = get_studio_service()
    result = studio_service.generate_flowchart(
        source_ids=source_ids,
        notebook_id=notebook_id
    )

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    title = result.get('title', '流程圖')

    output = StudioOutput(
        notebook_id=notebook_id,
        type='flowchart',
        title=title,
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/diagram', methods=['POST'])
def generate_diagram(notebook_id):
    """
    生成架構圖/系統圖（draw.io 格式）

    Request body:
    {
        "source_ids": ["id1", "id2"],  // 可選，指定來源
        "diagram_type": "auto"          // 可選，圖表類型: auto/architecture/sequence/class/er/network
    }

    Response:
    {
        "data": {
            "title": "架構圖標題",
            "description": "說明",
            "xml": "<mxGraphModel>...</mxGraphModel>",
            "type": "diagram",
            "diagram_type": "architecture"
        }
    }
    """
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')
    diagram_type = data.get('diagram_type', 'auto')

    studio_service = get_studio_service()
    result = studio_service.generate_diagram(
        source_ids=source_ids,
        notebook_id=notebook_id,
        diagram_type=diagram_type
    )

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    title = result.get('title', '架構圖')
    actual_type = result.get('diagram_type', diagram_type)
    type_labels = {
        'architecture': '架構圖',
        'sequence': '時序圖',
        'class': '類別圖',
        'er': 'ER 圖',
        'network': '網路圖',
        'auto': '系統圖'
    }

    output = StudioOutput(
        notebook_id=notebook_id,
        type='diagram',
        title=f"{title} ({type_labels.get(actual_type, actual_type)})",
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/generate', methods=['POST'])
def generate_output(notebook_id):
    """通用生成端點"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    output_type = data.get('type')
    source_ids = data.get('source_ids')

    if not output_type:
        return jsonify({'success': False, 'error': '請指定輸出類型'}), 400

    studio_service = get_studio_service()

    # 根據類型調用對應方法
    difficulty = data.get('difficulty', 'mixed')
    type_methods = {
        'summary': lambda: studio_service.generate_summary(source_ids=source_ids, notebook_id=notebook_id),
        'mindmap': lambda: studio_service.generate_mindmap(source_ids=source_ids, notebook_id=notebook_id),
        'flashcards': lambda: studio_service.generate_flashcards(count=data.get('count', 10), source_ids=source_ids, notebook_id=notebook_id, difficulty=difficulty),
        'quiz': lambda: studio_service.generate_quiz(count=data.get('count', 10), source_ids=source_ids, notebook_id=notebook_id, difficulty=difficulty),
        'report': lambda: studio_service.generate_report(source_ids=source_ids, notebook_id=notebook_id),
        'datatable': lambda: studio_service.generate_datatable(source_ids=source_ids, notebook_id=notebook_id),
        'presentation': lambda: studio_service.generate_presentation(source_ids=source_ids, notebook_id=notebook_id, slide_count=data.get('slide_count', 8), with_images=data.get('with_images', True)),
        'infographic': lambda: studio_service.generate_infographic(source_ids=source_ids, notebook_id=notebook_id, with_ai_image=data.get('with_ai_image', False)),
        'flowchart': lambda: studio_service.generate_flowchart(source_ids=source_ids, notebook_id=notebook_id),
        'diagram': lambda: studio_service.generate_diagram(source_ids=source_ids, notebook_id=notebook_id, diagram_type=data.get('diagram_type', 'auto')),
    }

    if output_type not in type_methods:
        return jsonify({'success': False, 'error': f'不支援的輸出類型: {output_type}'}), 400

    result = type_methods[output_type]()

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 400

    # 儲存輸出
    type_titles = {
        'summary': '摘要',
        'mindmap': '心智圖',
        'flashcards': '學習卡',
        'quiz': '測驗',
        'report': '報告',
        'datatable': '資料表',
        'presentation': '簡報',
        'infographic': '資訊圖表',
        'flowchart': '流程圖',
        'diagram': '架構圖',
    }

    output = StudioOutput(
        notebook_id=notebook_id,
        type=output_type,
        title=type_titles.get(output_type, output_type),
        data=result,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/outputs/<output_id>', methods=['GET'])
def get_output(notebook_id, output_id):
    """取得單一輸出"""
    output = StudioOutput.query.filter_by(id=output_id, notebook_id=notebook_id).first()

    if not output:
        return jsonify({'success': False, 'error': '輸出不存在'}), 404

    return jsonify({
        'success': True,
        'data': output.to_dict()
    })


@studio_bp.route('/<notebook_id>/studio/outputs/<output_id>', methods=['DELETE'])
def delete_output(notebook_id, output_id):
    """刪除輸出"""
    output = StudioOutput.query.filter_by(id=output_id, notebook_id=notebook_id).first()

    if not output:
        return jsonify({'success': False, 'error': '輸出不存在'}), 404

    db.session.delete(output)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '輸出已刪除'
    })


# ==================== Podcast 播客 API ====================

@studio_bp.route('/<notebook_id>/studio/podcast', methods=['POST'])
def generate_podcast(notebook_id):
    """
    生成播客（腳本 + 可選音訊）

    Request body:
    {
        "source_ids": ["id1", "id2"],  // 可選，指定來源
        "speakers": [                   // 可選，講者設定
            {"name": "小明", "role": "host", "personality": "熱情好奇"},
            {"name": "小美", "role": "co-host", "personality": "專業細心"}
        ],
        "duration_minutes": 10,         // 可選，目標時長
        "style": "conversational",      // 可選，風格
        "with_audio": true,             // 可選，是否生成音訊
        "speaker_voices": {             // 可選，講者語音映射
            "小明": "onyx",
            "小美": "nova"
        }
    }
    """
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')
    speakers = data.get('speakers')
    duration_minutes = data.get('duration_minutes', 10)
    style = data.get('style', 'conversational')
    with_audio = data.get('with_audio', False)
    speaker_voices = data.get('speaker_voices')

    # 取得來源內容
    from services.studio_service import get_studio_service
    studio_service = get_studio_service()
    content = studio_service.get_sources_content(source_ids=source_ids, notebook_id=notebook_id)

    if not content:
        return jsonify({'success': False, 'error': '沒有可用的來源內容'}), 400

    podcast_service = get_podcast_service()

    # 生成完整播客
    result = podcast_service.generate_full_podcast(
        content=content,
        speakers=speakers,
        duration_minutes=duration_minutes,
        style=style,
        with_audio=with_audio,
        speaker_voices=speaker_voices
    )

    if result.get('error') and not result.get('script'):
        return jsonify({'success': False, 'error': result['error']}), 400

    # 儲存輸出（不包含音訊資料，太大）
    output_data = {
        'type': 'podcast',
        'script': result.get('script'),
        'has_audio': result.get('audio') is not None,
        'error': result.get('error')
    }

    output = StudioOutput(
        notebook_id=notebook_id,
        type='podcast',
        title=result.get('script', {}).get('title', '播客'),
        data=output_data,
        source_ids=source_ids
    )
    db.session.add(output)
    db.session.commit()

    # 回應包含 audio_base64（如果有）
    response_data = output.to_dict()
    if result.get('audio_base64'):
        response_data['audio_base64'] = result['audio_base64']

    return jsonify({
        'success': True,
        'data': response_data
    })


@studio_bp.route('/<notebook_id>/studio/podcast/script', methods=['POST'])
def generate_podcast_script(notebook_id):
    """僅生成播客腳本（不含音訊）"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    source_ids = data.get('source_ids')
    speakers = data.get('speakers')
    duration_minutes = data.get('duration_minutes', 10)
    style = data.get('style', 'conversational')

    # 取得來源內容
    from services.studio_service import get_studio_service
    studio_service = get_studio_service()
    content = studio_service.get_sources_content(source_ids=source_ids, notebook_id=notebook_id)

    if not content:
        return jsonify({'success': False, 'error': '沒有可用的來源內容'}), 400

    podcast_service = get_podcast_service()
    script, error = podcast_service.generate_podcast_script(
        content=content,
        speakers=speakers,
        duration_minutes=duration_minutes,
        style=style
    )

    if error:
        return jsonify({'success': False, 'error': error}), 400

    return jsonify({
        'success': True,
        'data': {
            'script': script
        }
    })


@studio_bp.route('/<notebook_id>/studio/podcast/audio', methods=['POST'])
def generate_podcast_audio(notebook_id):
    """從腳本生成播客音訊"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json() or {}
    script = data.get('script')
    speaker_voices = data.get('speaker_voices')

    if not script:
        return jsonify({'success': False, 'error': '腳本為必填'}), 400

    podcast_service = get_podcast_service()
    audio_data, error = podcast_service.generate_podcast_audio(
        script=script,
        speaker_voices=speaker_voices
    )

    if error:
        return jsonify({'success': False, 'error': error}), 400

    import base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    return jsonify({
        'success': True,
        'data': {
            'audio_base64': audio_base64,
            'format': 'mp3'
        }
    })


@studio_bp.route('/<notebook_id>/studio/podcast/voices', methods=['GET'])
def get_podcast_voices(notebook_id):
    """取得可用的播客語音列表"""
    podcast_service = get_podcast_service()

    return jsonify({
        'success': True,
        'data': {
            'voices': podcast_service.get_available_voices(),
            'styles': podcast_service.get_style_options()
        }
    })


# ==================== TTS API ====================

@studio_bp.route('/<notebook_id>/studio/tts', methods=['POST'])
def text_to_speech(notebook_id):
    """文字轉語音"""
    data = request.get_json() or {}
    text = data.get('text')
    voice = data.get('voice', 'alloy')
    provider = data.get('provider', 'openai')

    if not text:
        return jsonify({'success': False, 'error': '文字為必填'}), 400

    audio_service = get_audio_service()
    audio_data, error = audio_service.text_to_speech(
        text=text,
        voice=voice,
        provider=provider
    )

    if error:
        return jsonify({'success': False, 'error': error}), 400

    import base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    return jsonify({
        'success': True,
        'data': {
            'audio_base64': audio_base64,
            'format': 'mp3'
        }
    })


@studio_bp.route('/<notebook_id>/studio/tts/stream', methods=['POST'])
def text_to_speech_stream(notebook_id):
    """文字轉語音（串流）"""
    data = request.get_json() or {}
    text = data.get('text')
    voice = data.get('voice', 'alloy')

    if not text:
        return jsonify({'success': False, 'error': '文字為必填'}), 400

    audio_service = get_audio_service()

    def generate():
        for chunk in audio_service.text_to_speech_stream(text, voice):
            yield chunk

    return Response(
        generate(),
        mimetype='audio/mpeg',
        headers={
            'Content-Disposition': 'attachment; filename=speech.mp3'
        }
    )
