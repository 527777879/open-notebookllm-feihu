"""
對話控制器
"""
import json
from flask import request, jsonify, Response, stream_with_context
from . import chat_bp
from models import db, Notebook, ChatMessage
from services.ai_service_manager import get_ai_service
from services.rag_service import get_rag_service
from services.prompts import ChatPrompts, get_language_instruction


@chat_bp.route('/<notebook_id>/chats', methods=['GET'])
def list_messages(notebook_id):
    """取得對話歷史"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    messages = ChatMessage.query.filter_by(notebook_id=notebook_id).order_by(ChatMessage.created_at.asc()).all()

    return jsonify({
        'success': True,
        'data': [m.to_dict() for m in messages]
    })


@chat_bp.route('/<notebook_id>/chats', methods=['POST'])
def send_message(notebook_id):
    """發送對話訊息 (非串流)"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    message = data.get('message')
    source_ids = data.get('source_ids')
    locale = data.get('locale', 'zh-TW')
    language = get_language_instruction(locale)  # 可選，指定來源

    if not message:
        return jsonify({'success': False, 'error': '訊息為必填'}), 400

    # 儲存用戶訊息
    user_message = ChatMessage(
        notebook_id=notebook_id,
        role='user',
        content=message,
        used_source_ids=source_ids
    )
    db.session.add(user_message)
    db.session.commit()

    try:
        # RAG 檢索
        rag_service = get_rag_service()
        context, source_refs = rag_service.build_context(
            query=message,
            source_ids=source_ids,
            notebook_id=notebook_id
        )

        # 生成回應
        ai_service = get_ai_service()

        if context:
            prompt = ChatPrompts.RAG_TEMPLATE.format(context=context, question=message, language=language)
        else:
            prompt = message

        response = ai_service.generate(prompt, ChatPrompts.SYSTEM.format(language=language))

        # 儲存助手回應
        assistant_message = ChatMessage(
            notebook_id=notebook_id,
            role='assistant',
            content=response,
            source_refs=source_refs,
            used_source_ids=source_ids
        )
        db.session.add(assistant_message)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': assistant_message.to_dict()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@chat_bp.route('/<notebook_id>/chats/stream', methods=['POST'])
def stream_message(notebook_id):
    """串流對話訊息 (SSE)"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    message = data.get('message')
    source_ids = data.get('source_ids')
    locale = data.get('locale', 'zh-TW')
    language = get_language_instruction(locale)

    if not message:
        return jsonify({'success': False, 'error': '訊息為必填'}), 400

    def generate():
        # 儲存用戶訊息
        user_message = ChatMessage(
            notebook_id=notebook_id,
            role='user',
            content=message,
            used_source_ids=source_ids
        )
        db.session.add(user_message)
        db.session.commit()

        try:
            # RAG 檢索
            rag_service = get_rag_service()
            context, source_refs = rag_service.build_context(
                query=message,
                source_ids=source_ids,
                notebook_id=notebook_id
            )

            # 發送來源引用
            if source_refs:
                yield f"data: {json.dumps({'type': 'sources', 'references': source_refs})}\n\n"

            # 生成回應
            ai_service = get_ai_service()

            if context:
                prompt = ChatPrompts.RAG_TEMPLATE.format(context=context, question=message, language=language)
            else:
                prompt = message

            system_prompt = ChatPrompts.SYSTEM.format(language=language)
            full_response = ""
            for chunk in ai_service.generate_stream(prompt, system_prompt):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            # 儲存助手回應
            assistant_message = ChatMessage(
                notebook_id=notebook_id,
                role='assistant',
                content=full_response,
                source_refs=source_refs,
                used_source_ids=source_ids
            )
            db.session.add(assistant_message)
            db.session.commit()

            yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_message.id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@chat_bp.route('/<notebook_id>/suggested-questions', methods=['GET'])
def get_suggested_questions(notebook_id):
    """取得建議問題"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    try:
        # 取得來源內容摘要
        from models import Source
        sources = Source.query.filter_by(notebook_id=notebook_id).limit(3).all()

        if not sources:
            return jsonify({
                'success': True,
                'data': []
            })

        # 取得部分內容用於生成建議問題
        content_parts = []
        for source in sources:
            content_parts.append(f"來源: {source.name}\n{source.content[:1000]}")

        context = "\n\n---\n\n".join(content_parts)

        locale = request.args.get('locale', 'zh-TW')
        language = get_language_instruction(locale)

        ai_service = get_ai_service()
        prompt = ChatPrompts.SUGGESTED_QUESTIONS.format(context=context, language=language)

        result = ai_service.generate_json(prompt)

        # 確保結果是列表
        if isinstance(result, list):
            questions = result
        elif isinstance(result, dict) and 'questions' in result:
            questions = result['questions']
        else:
            questions = []

        return jsonify({
            'success': True,
            'data': questions[:5]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@chat_bp.route('/<notebook_id>/chats/<message_id>', methods=['DELETE'])
def delete_message(notebook_id, message_id):
    """刪除對話訊息"""
    message = ChatMessage.query.filter_by(id=message_id, notebook_id=notebook_id).first()

    if not message:
        return jsonify({'success': False, 'error': '訊息不存在'}), 404

    db.session.delete(message)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '訊息已刪除'
    })


@chat_bp.route('/<notebook_id>/chats/clear', methods=['DELETE'])
def clear_messages(notebook_id):
    """清空對話歷史"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    ChatMessage.query.filter_by(notebook_id=notebook_id).delete()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '對話歷史已清空'
    })
