# 数据模型设计 - SQLAlchemy + MySQL（支持未来扩展）

## 设计原则

### 平滑扩展策略
- **MVP阶段**：使用简单的字符串字段存储固定科目
- **未来扩展**：轻松迁移到自定义科目模型
- **核心思想**：API和服务层抽象，数据层灵活

---

## 1. MVP数据模型（当前实现）

### 1.1 Question模型 - 扩展友好设计

```python
# app/models/question.py
from app import db
from datetime import datetime
import uuid

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255))
    
    # ✅ MVP: 使用字符串而非枚举，便于未来扩展
    subject = db.Column(db.String(50), nullable=False, index=True)
    # 当前值: 'READING', 'WRITING', 'MATHS', 'THINKING_SKILLS'
    # 未来可以是: 'PIANO', 'HSC_PHYSICS', 'CUSTOM_ABC' 等任意值
    
    # JSON字段存储图片URLs和标签
    image_urls = db.Column(db.JSON, nullable=False)  # ["url1.jpg", "url2.jpg"]
    thumbnail_urls = db.Column(db.JSON)  # ["thumb1.jpg", "thumb2.jpg"]
    tags = db.Column(db.JSON, default=list)  # ["algebra", "equations"]
    
    difficulty = db.Column(db.Integer, default=3)  # 1-5
    status = db.Column(db.String(50), default='UNANSWERED')
    # 值: 'UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW'
    
    is_difficult = db.Column(db.Boolean, default=False, index=True)
    is_frequent_error = db.Column(db.Boolean, default=False, index=True)
    
    view_count = db.Column(db.Integer, default=0)
    answer_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    average_time = db.Column(db.Integer)
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', back_populates='questions')
    answers = db.relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='question', cascade='all, delete-orphan')
    notes = db.relationship('Note', back_populates='question', cascade='all, delete-orphan')
    
    # 索引设计（考虑未来扩展）
    __table_args__ = (
        db.Index('idx_user_subject', 'user_id', 'subject'),
        db.Index('idx_user_status', 'user_id', 'status'),
        db.Index('idx_difficult', 'is_difficult', 'subject'),
        db.Index('idx_frequent', 'is_frequent_error', 'subject'),
    )
    
    def to_dict(self, include_answers=False):
        data = {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'image_urls': self.image_urls,
            'thumbnail_urls': self.thumbnail_urls,
            'tags': self.tags or [],
            'difficulty': self.difficulty,
            'status': self.status,
            'is_difficult': self.is_difficult,
            'is_frequent_error': self.is_frequent_error,
            'view_count': self.view_count,
            'answer_count': self.answer_count,
            'correct_count': self.correct_count,
            'average_time': self.average_time,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_answers:
            data['answers'] = [a.to_dict() for a in self.answers]
        return data
    
    @property
    def correct_rate(self):
        """正确率"""
        if self.answer_count == 0:
            return None
        return round(self.correct_count / self.answer_count * 100, 2)
```

### 1.2 科目配置 - 代码层面管理

```python
# app/config.py

class Config:
    # ... 其他配置
    
    # MVP: 固定科目配置（未来可以从数据库读取）
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
    
    # 验证函数
    @staticmethod
    def is_valid_subject(subject):
        return subject in Config.SUBJECTS
    
    @staticmethod
    def get_subject_info(subject):
        return Config.SUBJECTS.get(subject)
```

### 1.3 服务层抽象 - 关键！

```python
# app/services/subject_service.py
from app.config import Config

class SubjectService:
    """科目服务 - 提供统一的科目访问接口"""
    
    @staticmethod
    def get_all_subjects(user_id=None):
        """
        获取所有可用科目
        MVP: 返回固定的4门科目
        未来: 从数据库查询用户的自定义科目
        """
        # MVP实现
        return [
            {
                'id': subject_key,  # 未来会是数据库ID
                'name': info['name'],
                'display_name': info['display_name'],
                'display_name_zh': info['display_name_zh'],
                'color': info['color'],
                'icon': info['icon'],
                'description': info['description'],
                'is_custom': False  # 未来会有自定义科目
            }
            for subject_key, info in Config.SUBJECTS.items()
        ]
    
    @staticmethod
    def get_subject_by_name(subject_name):
        """
        根据名称获取科目信息
        MVP: 从配置文件读取
        未来: 从数据库查询
        """
        info = Config.get_subject_info(subject_name)
        if info:
            return {
                'id': subject_name,
                'name': info['name'],
                'display_name': info['display_name'],
                'color': info['color'],
                'icon': info['icon']
            }
        return None
    
    @staticmethod
    def validate_subject(subject_name):
        """
        验证科目是否有效
        MVP: 检查是否在固定列表中
        未来: 检查数据库中是否存在
        """
        return Config.is_valid_subject(subject_name)
    
    @staticmethod
    def get_user_subjects(user_id):
        """
        获取用户的科目列表（带统计）
        MVP: 返回固定科目 + 该用户的题目数量
        未来: 返回用户自定义的科目列表
        """
        from app.models import Question
        from app import db
        
        # 查询每个科目的题目数量
        subject_counts = db.session.query(
            Question.subject,
            db.func.count(Question.id).label('count')
        ).filter(
            Question.user_id == user_id
        ).group_by(Question.subject).all()
        
        count_dict = {subject: count for subject, count in subject_counts}
        
        # 组合结果
        subjects = SubjectService.get_all_subjects()
        for subject in subjects:
            subject['question_count'] = count_dict.get(subject['name'], 0)
        
        return subjects
```

### 1.4 API路由 - 使用服务层

```python
# app/routes/subjects.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.subject_service import SubjectService

bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')

@bp.route('', methods=['GET'])
@jwt_required()
def get_subjects():
    """
    获取用户的科目列表
    MVP: 返回固定的4门科目 + 题目统计
    未来: 返回用户自定义科目列表
    """
    user_id = get_jwt_identity()
    subjects = SubjectService.get_user_subjects(user_id)
    return jsonify(subjects), 200

@bp.route('/<subject_name>', methods=['GET'])
@jwt_required()
def get_subject(subject_name):
    """
    获取单个科目信息
    MVP: 从配置读取
    未来: 从数据库查询
    """
    subject = SubjectService.get_subject_by_name(subject_name)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404
    return jsonify(subject), 200
```

---

## 2. 未来扩展路径（Phase 2）

### 2.1 添加自定义科目模型

```python
# app/models/user_subject.py（未来添加）
from app import db
from datetime import datetime
import uuid

class UserSubject(db.Model):
    """用户自定义科目（Phase 2）"""
    __tablename__ = 'user_subjects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 科目信息
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # 自定义外观
    color = db.Column(db.String(20))
    icon = db.Column(db.String(50))
    
    # 顺序和可见性
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='custom_subjects')
```

### 2.2 数据迁移方案

```python
# migrations/versions/add_custom_subjects.py
"""
Phase 2迁移：从固定科目到自定义科目

迁移策略：
1. 添加 user_subjects 表
2. 为现有用户创建他们使用过的科目
3. Question.subject 保持字符串类型（向后兼容）
4. 可选：添加 Question.subject_id 外键（渐进式迁移）
"""

def upgrade():
    # 1. 创建 user_subjects 表
    op.create_table(
        'user_subjects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(100)),
        sa.Column('color', sa.String(20)),
        sa.Column('icon', sa.String(50)),
        sa.Column('sort_order', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )
    
    # 2. 为现有用户创建默认科目
    # 这个在应用层用Python代码执行更安全
    pass

def downgrade():
    op.drop_table('user_subjects')
```

```python
# scripts/migrate_to_custom_subjects.py
"""Phase 2迁移脚本"""
from app import create_app, db
from app.models import User, Question
from app.models.user_subject import UserSubject
from app.config import Config

def migrate():
    app = create_app()
    with app.app_context():
        # 为每个有题目的用户创建科目
        users_subjects = db.session.query(
            Question.user_id,
            Question.subject
        ).distinct().all()
        
        created_subjects = {}
        
        for user_id, subject_name in users_subjects:
            # 获取科目配置
            config = Config.get_subject_info(subject_name)
            if not config:
                continue
            
            # 检查是否已创建
            key = (user_id, subject_name)
            if key in created_subjects:
                continue
            
            # 创建UserSubject
            user_subject = UserSubject(
                user_id=user_id,
                name=subject_name,
                display_name=config['display_name'],
                color=config['color'],
                icon=config['icon']
            )
            db.session.add(user_subject)
            created_subjects[key] = user_subject.id
        
        db.session.commit()
        print(f"Created {len(created_subjects)} user subjects")

if __name__ == '__main__':
    migrate()
```

### 2.3 服务层更新（Phase 2）

```python
# app/services/subject_service.py（Phase 2版本）

class SubjectService:
    
    @staticmethod
    def get_all_subjects(user_id=None):
        """
        Phase 2: 从数据库读取用户的自定义科目
        """
        if user_id:
            # 查询用户的自定义科目
            subjects = UserSubject.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(UserSubject.sort_order).all()
            
            return [s.to_dict() for s in subjects]
        else:
            # 返回系统预设科目（供新用户选择）
            return [
                {
                    'id': subject_key,
                    'name': info['name'],
                    'display_name': info['display_name'],
                    'color': info['color'],
                    'icon': info['icon'],
                    'is_system': True
                }
                for subject_key, info in Config.SUBJECTS.items()
            ]
    
    @staticmethod
    def create_user_subject(user_id, name, display_name=None, color=None, icon=None):
        """Phase 2: 为用户创建自定义科目"""
        subject = UserSubject(
            user_id=user_id,
            name=name,
            display_name=display_name or name,
            color=color or Config.DEFAULT_SUBJECT_COLOR,
            icon=icon or Config.DEFAULT_SUBJECT_ICON
        )
        db.session.add(subject)
        db.session.commit()
        return subject
```

---

## 3. 前端适配

### 3.1 MVP前端 - 硬编码配置

```javascript
// src/utils/subjects.js（MVP版本）

export const SUBJECTS = {
  READING: {
    name: 'READING',
    displayName: 'Reading',
    displayNameZh: '阅读理解',
    color: '#f97316',
    icon: 'book'
  },
  WRITING: {
    name: 'WRITING',
    displayName: 'Writing',
    displayNameZh: '写作',
    color: '#a855f7',
    icon: 'pencil'
  },
  MATHS: {
    name: 'MATHS',
    displayName: 'Maths',
    displayNameZh: '数学',
    color: '#10b981',
    icon: 'calculator'
  },
  THINKING_SKILLS: {
    name: 'THINKING_SKILLS',
    displayName: 'Thinking Skills',
    displayNameZh: '思维技能',
    color: '#6366f1',
    icon: 'brain'
  }
}

export const getSubjectInfo = (subjectName) => {
  return SUBJECTS[subjectName]
}

export const getAllSubjects = () => {
  return Object.values(SUBJECTS)
}
```

### 3.2 Phase 2前端 - API驱动

```javascript
// src/api/subjects.js（Phase 2版本）
import apiClient from './client'

export const subjectAPI = {
  // 获取用户的科目列表（从API）
  getUserSubjects: () => apiClient.get('/subjects'),
  
  // 获取系统预设模板
  getTemplates: () => apiClient.get('/subject-templates'),
  
  // 创建自定义科目
  createSubject: (data) => apiClient.post('/subjects', data),
  
  // 更新科目
  updateSubject: (id, data) => apiClient.patch(`/subjects/${id}`, data),
  
  // 删除科目
  deleteSubject: (id) => apiClient.delete(`/subjects/${id}`)
}
```

```javascript
// src/stores/subjects.js（Phase 2版本）
import { defineStore } from 'pinia'
import { subjectAPI } from '@/api/subjects'

export const useSubjectStore = defineStore('subjects', {
  state: () => ({
    subjects: [],  // 从API加载，而非硬编码
    loading: false
  }),

  actions: {
    async fetchSubjects() {
      this.loading = true
      try {
        const response = await subjectAPI.getUserSubjects()
        this.subjects = response.data
      } finally {
        this.loading = false
      }
    },

    async createSubject(subjectData) {
      const response = await subjectAPI.createSubject(subjectData)
      this.subjects.push(response.data)
      return response.data
    }
  },

  getters: {
    getSubjectInfo: (state) => (subjectName) => {
      return state.subjects.find(s => s.name === subjectName)
    }
  }
})
```

---

## 4. 扩展检查清单

### MVP → Phase 2 迁移步骤

#### 后端
- [ ] 创建 `UserSubject` 模型
- [ ] 数据库迁移（添加表）
- [ ] 运行迁移脚本（为现有用户创建科目）
- [ ] 更新 `SubjectService`（从数据库读取）
- [ ] 添加科目管理API（创建、更新、删除）
- [ ] 测试向后兼容性

#### 前端
- [ ] 更新 `subjectStore`（从API获取）
- [ ] 添加科目管理页面
- [ ] 更新科目选择器（支持自定义）
- [ ] 测试所有使用科目的组件

#### 数据
- [ ] 备份生产数据库
- [ ] 在测试环境验证迁移
- [ ] 生产环境迁移
- [ ] 验证数据完整性

---

## 5. 设计优势总结

### ✅ MVP阶段优势
- **简单快速**：固定科目，配置在代码中
- **零数据库开销**：不需要额外表
- **快速验证**：专注核心价值

### ✅ 扩展阶段优势
- **平滑迁移**：字符串字段可以直接复用
- **向后兼容**：API设计保持一致
- **服务抽象**：前端无感知切换
- **数据保留**：所有历史数据完整保留

### ✅ 关键设计决策

1. **Question.subject使用String而非Enum**
   - ✅ 灵活：可以存储任意科目名
   - ✅ 扩展：无需修改数据库字段类型
   - ✅ 兼容：迁移后无需修改历史数据

2. **服务层抽象（SubjectService）**
   - ✅ 统一接口：前端始终调用相同方法
   - ✅ 易切换：MVP和Phase 2切换只需改服务实现
   - ✅ 可测试：服务层易于单元测试

3. **配置驱动的科目信息**
   - ✅ MVP：从Config读取
   - ✅ Phase 2：从数据库读取
   - ✅ 前端无感知：都是通过API获取

---

## 6. 完整示例代码

### MVP使用示例

```python
# 创建题目 - MVP
from app.services.subject_service import SubjectService

# 验证科目
if SubjectService.validate_subject('READING'):
    question = Question(
        subject='READING',  # 简单字符串
        title='Title',
        user_id=user_id
    )
    db.session.add(question)
    db.session.commit()
```

### Phase 2使用示例

```python
# 创建题目 - Phase 2（代码完全相同！）
from app.services.subject_service import SubjectService

# 验证科目（服务内部现在查数据库）
if SubjectService.validate_subject('PIANO'):
    question = Question(
        subject='PIANO',  # 仍然是字符串
        title='Title',
        user_id=user_id
    )
    db.session.add(question)
    db.session.commit()
```

**关键点**：应用代码无需修改，服务层内部逻辑变化即可！

---

## 7. 总结

### 设计哲学
> **"简单开始，平滑扩展，不过度设计"**

- MVP专注于核心价值验证
- 数据模型为未来留有余地
- 服务层提供稳定抽象
- 前端通过API解耦

这个设计让您可以：
1. ✅ **现在**：快速开发MVP，固定4门科目
2. ✅ **未来**：2-3周即可升级到自定义科目
3. ✅ **始终**：保持代码清晰、可维护

**无需现在做任何额外工作，只需按照这个设计实现即可！**
