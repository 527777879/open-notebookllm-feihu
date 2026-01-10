"""
NoteBookLLM Flask 應用入口
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config
from models import db


def create_app():
    """建立 Flask 應用"""

    app = Flask(__name__)

    # 載入配置
    config = get_config()
    app.config.from_object(config)

    # 設定日誌
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 初始化 CORS
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)

    # 初始化資料庫
    db.init_app(app)

    # 確保上傳目錄存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 註冊藍圖
    from controllers import notebook_bp, folder_bp, source_bp, chat_bp, studio_bp, note_bp, settings_bp

    app.register_blueprint(notebook_bp)
    app.register_blueprint(folder_bp)
    app.register_blueprint(source_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(studio_bp)
    app.register_blueprint(note_bp)
    app.register_blueprint(settings_bp)

    # 建立資料庫表
    with app.app_context():
        db.create_all()
        app.logger.info("資料庫初始化完成")

    # 健康檢查端點
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'NoteBookLLM API'
        })

    # 根路由
    @app.route('/')
    def index():
        return jsonify({
            'name': 'NoteBookLLM API',
            'version': '1.0.0',
            'endpoints': {
                'notebooks': '/api/notebooks',
                'folders': '/api/folders',
                'sources': '/api/notebooks/<id>/sources',
                'chat': '/api/notebooks/<id>/chats',
                'studio': '/api/notebooks/<id>/studio',
                'notes': '/api/notebooks/<id>/notes',
                'settings': '/api/settings',
                'health': '/health'
            }
        })

    # 全局錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '找不到資源'
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f"伺服器錯誤: {error}")
        return jsonify({
            'success': False,
            'error': '伺服器內部錯誤'
        }), 500

    return app


# 建立應用實例
app = create_app()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )
