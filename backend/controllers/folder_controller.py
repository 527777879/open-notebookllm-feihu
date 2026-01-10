"""
資料夾控制器
"""
from flask import request, jsonify
from . import folder_bp
from models import db, Folder, Notebook


@folder_bp.route('', methods=['GET'])
def list_folders():
    """取得所有資料夾"""
    include_notebooks = request.args.get('include_notebooks', 'false').lower() == 'true'

    folders = Folder.query.order_by(Folder.order, Folder.created_at).all()

    return jsonify({
        'success': True,
        'data': [f.to_dict(include_notebooks=include_notebooks) for f in folders]
    })


@folder_bp.route('', methods=['POST'])
def create_folder():
    """建立資料夾"""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'success': False, 'error': '請提供資料夾名稱'}), 400

    # 取得最大 order 值
    max_order = db.session.query(db.func.max(Folder.order)).scalar() or 0

    folder = Folder(
        name=data['name'],
        emoji=data.get('emoji', '📁'),
        color=data.get('color'),
        order=max_order + 1
    )

    db.session.add(folder)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': folder.to_dict()
    }), 201


@folder_bp.route('/<folder_id>', methods=['GET'])
def get_folder(folder_id):
    """取得單一資料夾"""
    folder = Folder.query.get(folder_id)

    if not folder:
        return jsonify({'success': False, 'error': '資料夾不存在'}), 404

    include_notebooks = request.args.get('include_notebooks', 'true').lower() == 'true'

    return jsonify({
        'success': True,
        'data': folder.to_dict(include_notebooks=include_notebooks)
    })


@folder_bp.route('/<folder_id>', methods=['PUT'])
def update_folder(folder_id):
    """更新資料夾"""
    folder = Folder.query.get(folder_id)

    if not folder:
        return jsonify({'success': False, 'error': '資料夾不存在'}), 404

    data = request.get_json()

    if data.get('name'):
        folder.name = data['name']
    if 'emoji' in data:
        folder.emoji = data['emoji']
    if 'color' in data:
        folder.color = data['color']
    if 'order' in data:
        folder.order = data['order']
    if 'is_expanded' in data:
        folder.is_expanded = data['is_expanded']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': folder.to_dict()
    })


@folder_bp.route('/<folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    """刪除資料夾（筆記本移至未分類）"""
    folder = Folder.query.get(folder_id)

    if not folder:
        return jsonify({'success': False, 'error': '資料夾不存在'}), 404

    # 將資料夾內的筆記本移至未分類
    Notebook.query.filter_by(folder_id=folder_id).update({'folder_id': None})

    db.session.delete(folder)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '資料夾已刪除'
    })


@folder_bp.route('/<folder_id>/notebooks', methods=['GET'])
def get_folder_notebooks(folder_id):
    """取得資料夾內的筆記本"""
    folder = Folder.query.get(folder_id)

    if not folder:
        return jsonify({'success': False, 'error': '資料夾不存在'}), 404

    notebooks = Notebook.query.filter_by(folder_id=folder_id).order_by(Notebook.order, Notebook.created_at).all()

    return jsonify({
        'success': True,
        'data': [nb.to_dict() for nb in notebooks]
    })


@folder_bp.route('/<folder_id>/notebooks/<notebook_id>', methods=['PUT'])
def add_notebook_to_folder(folder_id, notebook_id):
    """將筆記本加入資料夾"""
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({'success': False, 'error': '資料夾不存在'}), 404

    notebook = Notebook.query.get(notebook_id)
    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不存在'}), 404

    # 取得資料夾內最大 order
    max_order = db.session.query(db.func.max(Notebook.order)).filter(Notebook.folder_id == folder_id).scalar() or 0

    notebook.folder_id = folder_id
    notebook.order = max_order + 1
    db.session.commit()

    return jsonify({
        'success': True,
        'data': notebook.to_dict()
    })


@folder_bp.route('/<folder_id>/notebooks/<notebook_id>', methods=['DELETE'])
def remove_notebook_from_folder(folder_id, notebook_id):
    """將筆記本從資料夾移出（移至未分類）"""
    notebook = Notebook.query.filter_by(id=notebook_id, folder_id=folder_id).first()

    if not notebook:
        return jsonify({'success': False, 'error': '筆記本不在此資料夾中'}), 404

    notebook.folder_id = None
    notebook.order = 0
    db.session.commit()

    return jsonify({
        'success': True,
        'data': notebook.to_dict()
    })


@folder_bp.route('/reorder', methods=['PUT'])
def reorder_folders():
    """重新排序資料夾"""
    data = request.get_json()

    if not data or not isinstance(data.get('folder_ids'), list):
        return jsonify({'success': False, 'error': '請提供 folder_ids 陣列'}), 400

    folder_ids = data['folder_ids']

    for index, folder_id in enumerate(folder_ids):
        Folder.query.filter_by(id=folder_id).update({'order': index})

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '排序已更新'
    })


@folder_bp.route('/<folder_id>/notebooks/reorder', methods=['PUT'])
def reorder_notebooks_in_folder(folder_id):
    """重新排序資料夾內的筆記本"""
    folder = Folder.query.get(folder_id)
    if not folder:
        return jsonify({'success': False, 'error': '資料夾不存在'}), 404

    data = request.get_json()

    if not data or not isinstance(data.get('notebook_ids'), list):
        return jsonify({'success': False, 'error': '請提供 notebook_ids 陣列'}), 400

    notebook_ids = data['notebook_ids']

    for index, notebook_id in enumerate(notebook_ids):
        Notebook.query.filter_by(id=notebook_id, folder_id=folder_id).update({'order': index})

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '排序已更新'
    })


@folder_bp.route('/with-notebooks', methods=['GET'])
def get_folders_with_notebooks():
    """取得所有資料夾及未分類筆記本（用於首頁顯示）"""
    # 取得所有資料夾
    folders = Folder.query.order_by(Folder.order, Folder.created_at).all()

    # 取得未分類的筆記本
    uncategorized_notebooks = Notebook.query.filter_by(folder_id=None).order_by(Notebook.order, Notebook.created_at).all()

    return jsonify({
        'success': True,
        'data': {
            'folders': [f.to_dict(include_notebooks=True) for f in folders],
            'uncategorized': [nb.to_dict() for nb in uncategorized_notebooks]
        }
    })
