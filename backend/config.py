"""
Flask应用配置
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change'
    
    # 数据库配置
    # 优先使用环境变量，如果未配置则使用SQLite（本地开发）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///selective.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Cloudinary配置
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # 科目配置（MVP: 固定4门科目）
    SUBJECTS = {
        'READING': {
            'name': 'READING',
            'display_name': 'Reading',
            'display_name_zh': '阅读理解',
            'color': '#f97316',
            'icon': 'book',
            'description': 'Reading comprehension and analysis'
        },
        'WRITING': {
            'name': 'WRITING',
            'display_name': 'Writing',
            'display_name_zh': '写作',
            'color': '#a855f7',
            'icon': 'pencil',
            'description': 'Creative and analytical writing'
        },
        'MATHS': {
            'name': 'MATHS',
            'display_name': 'Maths',
            'display_name_zh': '数学',
            'color': '#10b981',
            'icon': 'calculator',
            'description': 'Mathematical reasoning and problem solving'
        },
        'THINKING_SKILLS': {
            'name': 'THINKING_SKILLS',
            'display_name': 'Thinking Skills',
            'display_name_zh': '思维技能',
            'color': '#6366f1',
            'icon': 'brain',
            'description': 'Critical thinking and logic'
        }
    }
    
    @staticmethod
    def is_valid_subject(subject):
        """验证科目是否有效"""
        return subject in Config.SUBJECTS
    
    @staticmethod
    def get_subject_info(subject):
        """获取科目信息"""
        return Config.SUBJECTS.get(subject)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # SQLite不支持pool参数,移除或覆盖
    SQLALCHEMY_ENGINE_OPTIONS = {}


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
