"""
Flask应用工厂
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import os

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()


def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    
    # 导入模型以确保Flask-Migrate能检测到
    from app import models
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    from app.routes import auth, items, collections, upload, analytics, answer, tags
    app.register_blueprint(auth.bp)
    app.register_blueprint(items.bp)
    app.register_blueprint(collections.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(answer.bp)
    app.register_blueprint(tags.bp)
    
    # 健康检查路由
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Server is running'}, 200
    
    @app.route('/')
    def index():
        return {
            'message': 'NSW Selective School Exam Platform API',
            'version': '0.1.0',
            'status': 'development'
        }, 200
    
    return app
