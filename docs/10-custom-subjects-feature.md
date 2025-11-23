# 自定义科目功能设计

## 1. 需求分析

### 1.1 用户需求

**核心需求**：用户可以自定义自己的学习科目，不局限于NSW精英中学的4门科目。

**使用场景**：
- **HSC学生**：6门HSC科目（English, Maths, Chemistry, Physics, Economics, Business）
- **音乐学生**：钢琴、小提琴、乐理等
- **语言学习者**：英语、法语、西班牙语等
- **小学生**：语文、数学、英语、科学等
- **职业考试**：会计、法律、医学等专业考试科目
- **技能练习**：编程语言、设计工具等

### 1.2 产品优势

通过自定义科目功能，平台可以：
- ✅ 扩大用户群体（不限于NSW考生）
- ✅ 提升产品灵活性
- ✅ 提供更个性化的体验
- ✅ 增加长期使用价值

---

## 2. 设计方案

### 2.1 核心概念

#### 科目模板（Subject Template）
系统预设的科目模板，用户可以直接选择：

**NSW Selective Exam模板**：
- Reading
- Writing  
- Maths
- Thinking Skills

**HSC模板**：
- English
- Maths Advanced/Extension
- Physics
- Chemistry
- Economics
- Business Studies
- Biology
- History
- ...（可扩展）

**音乐模板**：
- Piano
- Violin
- Music Theory
- Vocal

**通用模板**：
- Custom Subject 1
- Custom Subject 2
- ...

#### 用户科目（User Subject）
用户基于模板创建或完全自定义的科目：
- 可以选择模板
- 可以自定义名称
- 可以自定义颜色/图标
- 可以随时添加/删除/修改

---

## 3. 数据模型调整

### 3.1 新增SubjectTemplate模型

```python
# app/models/subject_template.py
from app import db
from datetime import datetime
import uuid

class SubjectTemplate(db.Model):
    """科目模板"""
    __tablename__ = 'subject_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)  # "Reading", "Piano"等
    display_name = db.Column(db.String(100))  # 显示名称（支持多语言）
    category = db.Column(db.String(50))  # "NSW_SELECTIVE", "HSC", "MUSIC", "LANGUAGE"等
    
    # 默认配置
    default_color = db.Column(db.String(20))  # "#f97316"
    default_icon = db.Column(db.String(50))  # "book", "music-note", "calculator"
    
    is_system = db.Column(db.Boolean, default=True)  # 系统预设还是用户创建
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'category': self.category,
            'default_color': self.default_color,
            'default_icon': self.default_icon
        }
```

### 3.2 新增UserSubject模型

```python
# app/models/user_subject.py
from app import db
from datetime import datetime
import uuid

class UserSubject(db.Model):
    """用户自定义科目"""
    __tablename__ = 'user_subjects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    template_id = db.Column(db.String(36), db.ForeignKey('subject_templates.id'))  # 可选，基于模板创建
    
    # 科目信息
    name = db.Column(db.String(100), nullable=False)  # 用户自定义名称
    display_name = db.Column(db.String(100))  # 显示名称
    description = db.Column(db.Text)
    
    # 自定义外观
    color = db.Column(db.String(20))  # 自定义颜色
    icon = db.Column(db.String(50))  # 自定义图标
    
    # 顺序和可见性
    sort_order = db.Column(db.Integer, default=0)  # 显示顺序
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    is_pinned = db.Column(db.Boolean, default=False)  # 是否置顶
    
    # 统计（冗余字段，提升性能）
    question_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='subjects')
    template = db.relationship('SubjectTemplate')
    
    __table_args__ = (
        db.Index('idx_user_active', 'user_id', 'is_active'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'is_pinned': self.is_pinned,
            'question_count': self.question_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

### 3.3 修改Question模型

```python
# app/models/question.py (修改部分)
class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255))
    
    # ❌ 删除：固定的subject枚举
    # subject = db.Column(db.Enum('READING', 'WRITING', 'MATHS', 'THINKING_SKILLS'))
    
    # ✅ 新增：关联到用户科目
    subject_id = db.Column(db.String(36), db.ForeignKey('user_subjects.id'), nullable=False, index=True)
    
    # ... 其他字段保持不变
    
    # 关系
    subject = db.relationship('UserSubject', backref='questions')
    
    # 索引调整
    __table_args__ = (
        db.Index('idx_user_subject', 'user_id', 'subject_id'),
        # ... 其他索引
    )
```

---

## 4. API设计

### 4.1 科目模板API

```python
# GET /api/subject-templates
# 获取所有可用的科目模板
{
  "templates": [
    {
      "category": "NSW_SELECTIVE",
      "name": "NSW Selective Exam",
      "subjects": [
        {"id": "...", "name": "Reading", "color": "#f97316", "icon": "book"},
        {"id": "...", "name": "Writing", "color": "#a855f7", "icon": "pencil"},
        {"id": "...", "name": "Maths", "color": "#10b981", "icon": "calculator"},
        {"id": "...", "name": "Thinking Skills", "color": "#6366f1", "icon": "brain"}
      ]
    },
    {
      "category": "HSC",
      "name": "HSC Subjects",
      "subjects": [
        {"id": "...", "name": "English", "color": "#...", "icon": "..."},
        {"id": "...", "name": "Maths Advanced", "color": "#...", "icon": "..."},
        // ...更多
      ]
    },
    {
      "category": "MUSIC",
      "name": "Music & Instruments",
      "subjects": [
        {"id": "...", "name": "Piano", "color": "#...", "icon": "piano"},
        {"id": "...", "name": "Violin", "color": "#...", "icon": "violin"}
      ]
    }
  ]
}
```

### 4.2 用户科目管理API

```python
# GET /api/subjects
# 获取当前用户的所有科目
[
  {
    "id": "user-subject-1",
    "name": "Reading",
    "display_name": "阅读理解",
    "color": "#f97316",
    "icon": "book",
    "question_count": 45,
    "sort_order": 0,
    "is_pinned": true
  },
  {
    "id": "user-subject-2", 
    "name": "Piano Grade 5",
    "display_name": "钢琴5级",
    "color": "#ec4899",
    "icon": "piano",
    "question_count": 12,
    "sort_order": 1
  }
]

# POST /api/subjects
# 创建新科目（基于模板或完全自定义）
{
  "template_id": "template-id",  // 可选，基于模板
  "name": "Piano",
  "display_name": "钢琴练习",
  "color": "#ec4899",
  "icon": "piano"
}

# PATCH /api/subjects/<id>
# 更新科目
{
  "display_name": "钢琴6级",
  "color": "#f472b6",
  "sort_order": 2
}

# DELETE /api/subjects/<id>
# 删除科目（会提示是否同时删除该科目下的所有题目）

# POST /api/subjects/reorder
# 重新排序科目
{
  "subject_ids": ["id1", "id3", "id2", "id4"]
}
```

### 4.3 题目API调整

```python
# POST /api/questions
# 创建题目时使用subject_id
{
  "subject_id": "user-subject-1",  // 不再是固定的枚举值
  "title": "代数问题",
  "image_urls": ["..."],
  "tags": ["algebra"],
  "difficulty": 4
}

# GET /api/questions?subject_id=xxx
# 按用户科目筛选
```

---

## 5. 用户体验流程

### 5.1 首次使用流程

```
用户注册
    ↓
欢迎页面：选择学习目标
    ├─ NSW Selective Exam → 自动创建4门科目
    ├─ HSC → 让用户选择6门科目
    ├─ Music → 选择乐器
    └─ Custom → 自己创建科目
    ↓
进入Dashboard
```

### 5.2 科目管理流程

```
Dashboard → 科目管理
    ↓
查看当前科目列表
    ├─ 从模板添加科目
    ├─ 自定义创建科目
    ├─ 编辑科目（名称、颜色、图标）
    ├─ 重新排序
    └─ 删除科目（需确认）
```

---

## 6. 前端UI设计

### 6.1 科目选择器组件

```vue
<!-- SubjectSelector.vue -->
<template>
  <div class="subject-selector">
    <h2>选择你的学习科目</h2>
    
    <!-- 模板选择 -->
    <div class="templates">
      <div 
        v-for="template in templates" 
        :key="template.category"
        class="template-card"
      >
        <h3>{{ template.name }}</h3>
        <div class="subjects-grid">
          <div 
            v-for="subject in template.subjects"
            :key="subject.id"
            class="subject-item"
            :style="{ borderColor: subject.color }"
            @click="addSubject(subject)"
          >
            <Icon :name="subject.icon" :color="subject.color" />
            <span>{{ subject.name }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 自定义创建 -->
    <button @click="createCustomSubject">
      + 创建自定义科目
    </button>
  </div>
</template>
```

### 6.2 Dashboard科目卡片（动态生成）

```vue
<!-- DashboardView.vue -->
<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    
    <!-- 动态科目卡片 -->
    <div class="subjects-grid">
      <SubjectCard
        v-for="subject in userSubjects"
        :key="subject.id"
        :subject="subject"
        @click="goToSubject(subject)"
      />
    </div>
  </div>
</template>

<script setup>
import { useSubjectStore } from '@/stores/subjects'
const subjectStore = useSubjectStore()
const userSubjects = computed(() => subjectStore.activeSubjects)
</script>
```

### 6.3 科目管理页面

```vue
<!-- SubjectManageView.vue -->
<template>
  <div class="subject-manage">
    <h1>管理科目</h1>
    
    <!-- 可拖拽排序的科目列表 -->
    <draggable v-model="subjects" @end="saveOrder">
      <div 
        v-for="subject in subjects"
        :key="subject.id"
        class="subject-row"
      >
        <DragHandle />
        <div class="subject-info">
          <Icon :name="subject.icon" :color="subject.color" />
          <span>{{ subject.display_name }}</span>
          <span class="count">{{ subject.question_count }} 题</span>
        </div>
        <div class="actions">
          <button @click="editSubject(subject)">编辑</button>
          <button @click="deleteSubject(subject)">删除</button>
        </div>
      </div>
    </draggable>
    
    <button @click="showTemplates">从模板添加</button>
    <button @click="createCustom">自定义创建</button>
  </div>
</template>
```

---

## 7. 数据迁移策略

### 7.1 从固定科目迁移到自定义科目

```python
# migrations/migrate_to_custom_subjects.py
from app import db, create_app
from app.models import Question, UserSubject, SubjectTemplate

def migrate():
    app = create_app()
    with app.app_context():
        # 1. 为每个用户创建他们使用过的科目
        users = db.session.query(Question.user_id, Question.subject)\
            .distinct()\
            .all()
        
        subject_mapping = {}  # 旧subject -> 新subject_id
        
        for user_id, old_subject in users:
            # 查找对应的模板
            template = SubjectTemplate.query.filter_by(name=old_subject).first()
            
            # 为用户创建科目
            user_subject = UserSubject(
                user_id=user_id,
                template_id=template.id if template else None,
                name=old_subject,
                display_name=template.display_name if template else old_subject,
                color=template.default_color if template else '#6b7280',
                icon=template.default_icon if template else 'book'
            )
            db.session.add(user_subject)
            db.session.flush()
            
            subject_mapping[(user_id, old_subject)] = user_subject.id
        
        # 2. 更新所有Question的subject_id
        questions = Question.query.all()
        for question in questions:
            key = (question.user_id, question.subject)
            question.subject_id = subject_mapping[key]
        
        db.session.commit()
        print("Migration completed!")
```

---

## 8. 实施建议

### 8.1 分阶段实施

#### Phase 1: MVP（当前开发中）
- ✅ 保持固定的4门科目（简化MVP）
- ✅ 完成核心功能开发

#### Phase 2: 自定义科目（在MVP之后）
- [ ] 添加SubjectTemplate和UserSubject模型
- [ ] 实现科目管理API
- [ ] 开发科目选择和管理UI
- [ ] 数据迁移

#### Phase 3: 模板扩展
- [ ] 添加更多预设模板（HSC、音乐等）
- [ ] 社区模板分享（可选）

### 8.2 向后兼容

```python
# 在过渡期，可以同时支持新旧两种方式
class Question(db.Model):
    # 新字段
    subject_id = db.Column(db.String(36), db.ForeignKey('user_subjects.id'), index=True)
    
    # 临时保留旧字段，用于数据迁移验证
    _legacy_subject = db.Column('subject', db.String(50))  
    
    @property
    def subject_name(self):
        """统一的访问方式"""
        if self.subject_id:
            return self.subject.name
        return self._legacy_subject
```

---

## 9. 配置建议

### 9.1 系统配置

```python
# config.py
class Config:
    # 科目相关配置
    MAX_SUBJECTS_PER_USER = 20  # 每个用户最多创建20个科目
    DEFAULT_SUBJECT_COLOR = '#6b7280'
    DEFAULT_SUBJECT_ICON = 'book'
    
    # 预设模板
    ENABLE_NSW_TEMPLATE = True
    ENABLE_HSC_TEMPLATE = True
    ENABLE_MUSIC_TEMPLATE = True
```

### 9.2 种子数据（科目模板）

```python
# seeds/subject_templates.py
NSW_SELECTIVE_TEMPLATES = [
    {'name': 'Reading', 'display_name': '阅读理解', 'color': '#f97316', 'icon': 'book'},
    {'name': 'Writing', 'display_name': '写作', 'color': '#a855f7', 'icon': 'pencil'},
    {'name': 'Maths', 'display_name': '数学', 'color': '#10b981', 'icon': 'calculator'},
    {'name': 'Thinking Skills', 'display_name': '思维技能', 'color': '#6366f1', 'icon': 'brain'}
]

HSC_TEMPLATES = [
    {'name': 'English', 'color': '#ef4444', 'icon': 'book'},
    {'name': 'Maths Advanced', 'color': '#10b981', 'icon': 'calculator'},
    {'name': 'Physics', 'color': '#3b82f6', 'icon': 'atom'},
    # ...更多
]

MUSIC_TEMPLATES = [
    {'name': 'Piano', 'color': '#ec4899', 'icon': 'piano'},
    {'name': 'Violin', 'color': '#f59e0b', 'icon': 'violin'},
    # ...更多
]
```

---

## 10. 优势总结

### 10.1 产品优势
- ✅ **扩大市场**：不限于NSW考生
- ✅ **提升灵活性**：适应各种学习场景
- ✅ **增强粘性**：用户可长期使用
- ✅ **差异化竞争**：市面上少有如此灵活的产品

### 10.2 技术优势
- ✅ **可扩展**：轻松添加新模板
- ✅ **个性化**：每个用户独特配置
- ✅ **数据隔离**：用户间科目互不影响

### 10.3 用户体验优势
- ✅ **降低门槛**：提供模板快速开始
- ✅ **自由度高**：完全自定义
- ✅ **视觉丰富**：自定义颜色和图标

---

## 11. 风险与挑战

### 11.1 技术挑战
- 数据迁移复杂度增加
- 查询性能需要优化（用户科目关联）
- 前端动态渲染复杂度

### 11.2 用户体验挑战
- 首次使用流程变长（需选择科目）
- 科目管理界面需要直观易用

### 11.3 应对策略
- **MVP阶段**：保持固定科目，验证核心价值
- **Phase 2**：再实现自定义科目
- **提供默认模板**：简化用户选择
- **性能优化**：合理索引和缓存

---

## 12. 总结与建议

### 建议实施路径

**短期（MVP）**：
- 保持当前固定4门科目设计
- 专注于核心功能完善
- 验证产品价值

**中期（Phase 2）**：
- 实现自定义科目功能
- 提供NSW和HSC两个模板
- 数据平滑迁移

**长期（Phase 3+）**：
- 扩展更多模板
- 社区模板分享
- AI智能推荐科目

这个扩展非常有价值，但**建议在MVP完成后再实施**，确保核心功能稳定后再扩展！
