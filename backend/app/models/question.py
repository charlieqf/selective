from app import db
from datetime import datetime
import json

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))  # 可选标题
    
    # 核心字段
    subject = db.Column(db.String(50), nullable=False, index=True)  # READING, WRITING, MATHS, THINKING_SKILLS
    difficulty = db.Column(db.Integer, default=3)  # 1-5, default 3
    status = db.Column(db.String(20), default='UNANSWERED')  # UNANSWERED, ANSWERED, MASTERED, NEED_REVIEW
    
    # 内容字段 (JSON存储)
    # 存储图片对象列表: [{"url": "...", "public_id": "..."}]
    # MySQL 8.0+ 支持 JSON 类型，SQLite 也支持（通过扩展或文本）
    # SQLAlchemy 的 JSON 类型会自动处理序列化/反序列化
    images = db.Column(db.JSON)  
    # 存储题目描述/OCR文本
    content_text = db.Column(db.Text)
    
    # 元数据
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 统计数据
    attempts = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    
    # 约束
    __table_args__ = (
        db.CheckConstraint('difficulty >= 1 AND difficulty <= 5', name='check_difficulty_range'),
        db.CheckConstraint("status IN ('UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW')", name='check_status_valid'),
    )
    
    def set_images(self, images_list):
        # SQLAlchemy JSON类型自动处理列表，无需手动json.dumps
        self.images = images_list
        
    def get_images(self):
        # SQLAlchemy JSON类型自动返回列表，无需手动json.loads
        return self.images if self.images else []
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'difficulty': self.difficulty,
            'status': self.status,
            'images': self.get_images(),
            'content_text': self.content_text,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat(),
            'attempts': self.attempts
        }
