"""
筆記控制器
"""
from flask import request, jsonify
from . import note_bp, notebook_bp
from models import db, Notebook, Note, ChatMessage


@notebook_bp.route('/<notebook_id>/notes', methods=['GET'])
def list_notes(notebook_id):
    """取得筆記本的所有筆記"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    notes = Note.query.filter_by(notebook_id=notebook_id).order_by(Note.updated_at.desc()).all()

    return jsonify({
        'success': True,
        'data': [n.to_dict() for n in notes]
    })


@notebook_bp.route('/<notebook_id>/notes', methods=['POST'])
def create_note(notebook_id):
    """建立筆記"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({'success': False, 'error': '筆記內容為必填'}), 400

    note = Note(
        notebook_id=notebook_id,
        title=data.get('title'),
        content=data['content'],
        from_message_id=data.get('from_message_id')
    )

    db.session.add(note)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': note.to_dict()
    }), 201


@notebook_bp.route('/<notebook_id>/notes/from-message', methods=['POST'])
def save_message_to_note(notebook_id):
    """將對話訊息儲存為筆記"""
    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    data = request.get_json()
    message_id = data.get('message_id')

    if not message_id:
        return jsonify({'success': False, 'error': '訊息 ID 為必填'}), 400

    message = ChatMessage.query.get(message_id)
    if not message:
        return jsonify({'success': False, 'error': '訊息不存在'}), 404

    # 建立筆記
    note = Note(
        notebook_id=notebook_id,
        title=data.get('title', '從對話儲存'),
        content=message.content,
        from_message_id=message_id
    )

    db.session.add(note)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': note.to_dict()
    }), 201


@note_bp.route('/notes/<note_id>', methods=['GET'])
def get_note(note_id):
    """取得單一筆記"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'success': False, 'error': '筆記不存在'}), 404

    return jsonify({
        'success': True,
        'data': note.to_dict()
    })


@note_bp.route('/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    """更新筆記"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'success': False, 'error': '筆記不存在'}), 404

    data = request.get_json()

    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': note.to_dict()
    })


@note_bp.route('/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """刪除筆記"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'success': False, 'error': '筆記不存在'}), 404

    db.session.delete(note)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '筆記已刪除'
    })
