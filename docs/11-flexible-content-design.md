# 灵活题目内容设计方案

## 1. 问题分析

### 1.1 真实场景

**一道题目可能包含**：
- 📝 **纯文字**：题目描述、问题陈述
- 🖼️ **单张图片**：数学图形、阅读材料配图
- 📸 **多张图片**：长题目的多页扫描、连续图片
- 📄 **PDF文件**：完整的阅读材料、写作范文
- 🎵 **音频**：音乐听力、语言学习（未来）
- 🎬 **视频**：实验演示、讲解视频（未来）
- 🔗 **组合**：文字说明 + 2张图片 + 1个PDF

### 1.2 设计目标

- ✅ **灵活性**：支持任意组合的内容类型
- ✅ **可扩展**：未来可轻松添加新类型
- ✅ **高效存储**：合理使用云存储
- ✅ **快速检索**：数据库索引优化
- ✅ **优秀体验**：前端展示美观易用

---

## 2. 数据模型设计

### 2.1 Question模型调整

```python
# app/models/question.py
from app import db
from datetime import datetime
import uuid

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255))
    subject = db.Column(db.String(50), nullable=False, index=True)
    
    # ✅ 新增：题目主体内容（结构化JSON）
    content = db.Column(db.JSON, nullable=False)
    """
    content结构示例:
    {
        "type": "mixed",  // 内容类型: text, image, images, mixed, pdf, etc.
        "items": [        // 内容块数组
            {
                "type": "text",
                "content": "解方程：2x + 5 = 15",
                "order": 0
            },
            {
                "type": "image",
                "url": "https://res.cloudinary.com/xxx/image1.jpg",
                "thumbnail_url": "https://res.cloudinary.com/xxx/thumb1.jpg",
                "width": 800,
                "height": 600,
                "caption": "图1：题目配图",
                "order": 1
            },
            {
                "type": "text",
                "content": "求x的值",
                "order": 2
            }
        ],
        "metadata": {
            "word_count": 15,
            "image_count": 1,
            "total_size_kb": 234
        }
    }
    """
    
    # ❌ 删除：简单的image_urls字段
    # image_urls = db.Column(db.JSON)
    
    # 保留：缩略图（用于列表展示的第一张图）
    thumbnail_url = db.Column(db.String(500))
    
    # 其他字段保持不变
    tags = db.Column(db.JSON, default=list)
    difficulty = db.Column(db.Integer, default=3)
    status = db.Column(db.String(50), default='UNANSWERED')
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
    
    def to_dict(self, include_answers=False):
        data = {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'content': self.content,  # 新：结构化内容
            'thumbnail_url': self.thumbnail_url,
            'tags': self.tags or [],
            'difficulty': self.difficulty,
            'status': self.status,
            'is_difficult': self.is_difficult,
            'is_frequent_error': self.is_frequent_error,
            'view_count': self.view_count,
            'answer_count': self.answer_count,
            'correct_count': self.correct_count,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_answers:
            data['answers'] = [a.to_dict() for a in self.answers]
        return data
    
    @property
    def content_summary(self):
        """内容摘要（用于列表展示）"""
        if not self.content:
            return {}
        
        items = self.content.get('items', [])
        text_items = [item for item in items if item['type'] == 'text']
        image_items = [item for item in items if item['type'] == 'image']
        
        return {
            'type': self.content.get('type'),
            'text_preview': text_items[0]['content'][:100] if text_items else None,
            'image_count': len(image_items),
            'first_image': image_items[0]['thumbnail_url'] if image_items else None
        }
```

---

## 3. 内容类型定义

### 3.1 支持的内容块类型

```python
# app/models/content_types.py

class ContentBlockType:
    """内容块类型"""
    TEXT = 'text'           # 文本
    IMAGE = 'image'         # 单张图片
    PDF = 'pdf'             # PDF文件
    AUDIO = 'audio'         # 音频（未来）
    VIDEO = 'video'         # 视频（未来）
    CODE = 'code'           # 代码片段（未来）
    LATEX = 'latex'         # LaTeX数学公式（未来）

class QuestionContentType:
    """题目整体内容类型（快捷标识）"""
    TEXT_ONLY = 'text_only'         # 纯文字
    IMAGE_ONLY = 'image_only'       # 单张图片
    IMAGES_ONLY = 'images_only'     # 多张图片
    MIXED = 'mixed'                 # 混合内容
    PDF = 'pdf'                     # PDF文档
```

### 3.2 内容块Schema定义

```python
# app/schemas/content_schema.py
from marshmallow import Schema, fields, validate

class TextBlockSchema(Schema):
    """文本块"""
    type = fields.Str(required=True, validate=validate.Equal('text'))
    content = fields.Str(required=True)
    order = fields.Int(required=True)
    format = fields.Str(missing='plain')  # plain, markdown, html

class ImageBlockSchema(Schema):
    """图片块"""
    type = fields.Str(required=True, validate=validate.Equal('image'))
    url = fields.Url(required=True)
    thumbnail_url = fields.Url()
    width = fields.Int()
    height = fields.Int()
    caption = fields.Str()
    order = fields.Int(required=True)
    file_size_kb = fields.Int()

class PdfBlockSchema(Schema):
    """PDF块"""
    type = fields.Str(required=True, validate=validate.Equal('pdf'))
    url = fields.Url(required=True)
    filename = fields.Str(required=True)
    page_count = fields.Int()
    file_size_kb = fields.Int()
    thumbnail_url = fields.Url()  # PDF首页预览图
    order = fields.Int(required=True)

class QuestionContentSchema(Schema):
    """题目内容整体结构"""
    type = fields.Str(required=True)  # text_only, image_only, mixed, etc.
    items = fields.List(fields.Dict(), required=True)  # 内容块数组
    metadata = fields.Dict()  # 元数据（字数、图片数等）
```

---

## 4. 云端存储方案

### 4.1 Cloudinary存储结构

```
cloudinary/selective-exam/
├── users/
│   └── {user_id}/
│       ├── questions/
│       │   └── {question_id}/
│       │       ├── image_001.jpg          # 原图
│       │       ├── image_001_thumb.jpg    # 缩略图
│       │       ├── image_002.jpg
│       │       ├── image_002_thumb.jpg
│       │       └── document.pdf
│       └── answers/
│           └── {answer_id}/
│               └── ...
```

### 4.2 文件命名规范

```python
# app/services/upload_service.py

class UploadService:
    
    @staticmethod
    def generate_file_path(user_id, question_id, file_type, index=0):
        """
        生成云端文件路径
        
        Examples:
            users/user123/questions/q456/image_001.jpg
            users/user123/questions/q456/image_001_thumb.jpg
            users/user123/questions/q456/document.pdf
        """
        timestamp = int(datetime.now().timestamp())
        
        if file_type == 'image':
            return f"users/{user_id}/questions/{question_id}/image_{index:03d}_{timestamp}"
        elif file_type == 'pdf':
            return f"users/{user_id}/questions/{question_id}/document_{timestamp}"
        elif file_type == 'thumbnail':
            return f"users/{user_id}/questions/{question_id}/image_{index:03d}_{timestamp}_thumb"
```

### 4.3 Cloudinary配置

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

class CloudinaryService:
    
    @staticmethod
    def upload_image(file, user_id, question_id, index=0):
        """上传图片，自动生成缩略图"""
        public_id = UploadService.generate_file_path(user_id, question_id, 'image', index)
        
        # 上传原图
        result = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            folder='selective-exam',
            resource_type='image',
            format='jpg',
            quality='auto:good'
        )
        
        # 生成缩略图URL（Cloudinary transformation）
        thumbnail_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=400,
            height=300,
            crop='fill',
            quality='auto:low'
        )
        
        return {
            'url': result['secure_url'],
            'thumbnail_url': thumbnail_url,
            'width': result['width'],
            'height': result['height'],
            'file_size_kb': result['bytes'] // 1024
        }
    
    @staticmethod
    def upload_pdf(file, user_id, question_id):
        """上传PDF文件"""
        public_id = UploadService.generate_file_path(user_id, question_id, 'pdf')
        
        # 上传PDF
        result = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            folder='selective-exam',
            resource_type='auto',  # 自动检测类型
        )
        
        # 生成PDF首页预览图（Cloudinary可以将PDF转为图片）
        thumbnail_url = cloudinary.CloudinaryImage(public_id).build_url(
            page=1,  # 第一页
            format='jpg',
            width=400,
            height=300,
            crop='fill'
        )
        
        return {
            'url': result['secure_url'],
            'thumbnail_url': thumbnail_url,
            'filename': result.get('original_filename'),
            'page_count': result.get('pages'),  # PDF页数
            'file_size_kb': result['bytes'] // 1024
        }
```

---

## 5. API设计

### 5.1 创建题目API（支持多种内容格式）

```python
# app/routes/questions.py

@bp.route('', methods=['POST'])
@jwt_required()
def create_question():
    """
    创建题目 - 支持灵活内容
    
    请求格式（multipart/form-data）:
    {
        "subject": "MATHS",
        "title": "代数方程",
        "tags": ["algebra", "equations"],
        "difficulty": 4,
        "content": {
            "type": "mixed",
            "items": [
                {"type": "text", "content": "解方程", "order": 0},
                {"type": "image_upload", "file_index": 0, "order": 1},
                {"type": "text", "content": "求x的值", "order": 2}
            ]
        }
    }
    
    文件: files[0], files[1], ...
    """
    user_id = get_jwt_identity()
    
    # 解析JSON数据
    data = json.loads(request.form.get('data'))
    files = request.files.getlist('files')
    
    # 创建Question记录（先保存以获取ID）
    question = Question(
        user_id=user_id,
        subject=data['subject'],
        title=data.get('title'),
        tags=data.get('tags', []),
        difficulty=data.get('difficulty', 3),
        content={'type': 'processing', 'items': []}  # 临时
    )
    db.session.add(question)
    db.session.flush()
    
    # 处理内容块
    content_items = []
    file_index = 0
    
    for item in data['content']['items']:
        if item['type'] == 'text':
            content_items.append({
                'type': 'text',
                'content': item['content'],
                'order': item['order']
            })
        
        elif item['type'] == 'image_upload':
            # 上传图片
            file = files[file_index]
            upload_result = CloudinaryService.upload_image(
                file, user_id, question.id, file_index
            )
            
            content_items.append({
                'type': 'image',
                'url': upload_result['url'],
                'thumbnail_url': upload_result['thumbnail_url'],
                'width': upload_result['width'],
                'height': upload_result['height'],
                'file_size_kb': upload_result['file_size_kb'],
                'order': item['order']
            })
            
            # 设置问题缩略图（第一张图片）
            if not question.thumbnail_url:
                question.thumbnail_url = upload_result['thumbnail_url']
            
            file_index += 1
        
        elif item['type'] == 'pdf_upload':
            # 上传PDF
            file = files[file_index]
            upload_result = CloudinaryService.upload_pdf(
                file, user_id, question.id
            )
            
            content_items.append({
                'type': 'pdf',
                'url': upload_result['url'],
                'thumbnail_url': upload_result['thumbnail_url'],
                'filename': upload_result['filename'],
                'page_count': upload_result.get('page_count'),
                'file_size_kb': upload_result['file_size_kb'],
                'order': item['order']
            })
            
            if not question.thumbnail_url:
                question.thumbnail_url = upload_result['thumbnail_url']
            
            file_index += 1
    
    # 更新完整content
    question.content = {
        'type': data['content']['type'],
        'items': content_items,
        'metadata': {
            'text_count': sum(1 for i in content_items if i['type'] == 'text'),
            'image_count': sum(1 for i in content_items if i['type'] == 'image'),
            'pdf_count': sum(1 for i in content_items if i['type'] == 'pdf')
        }
    }
    
    db.session.commit()
    
    return jsonify(question.to_dict()), 201
```

### 5.2 简化上传API（仅图片快捷上传）

```python
@bp.route('/quick-upload', methods=['POST'])
@jwt_required()
def quick_upload_question():
    """
    快捷上传 - MVP常用场景
    仅上传图片（1-5张），自动创建image-only题目
    """
    user_id = get_jwt_identity()
    
    subject = request.form.get('subject')
    title = request.form.get('title')
    files = request.files.getlist('images')
    
    # 创建Question
    question = Question(
        user_id=user_id,
        subject=subject,
        title=title,
        content={'type': 'processing', 'items': []}
    )
    db.session.add(question)
    db.session.flush()
    
    # 批量上传图片
    content_items = []
    for index, file in enumerate(files):
        upload_result = CloudinaryService.upload_image(
            file, user_id, question.id, index
        )
        
        content_items.append({
            'type': 'image',
            'url': upload_result['url'],
            'thumbnail_url': upload_result['thumbnail_url'],
            'width': upload_result['width'],
            'height': upload_result['height'],
            'order': index
        })
        
        if index == 0:
            question.thumbnail_url = upload_result['thumbnail_url']
    
    # 确定content type
    content_type = 'image_only' if len(files) == 1 else 'images_only'
    
    question.content = {
        'type': content_type,
        'items': content_items,
        'metadata': {
            'image_count': len(files)
        }
    }
    
    db.session.commit()
    
    return jsonify(question.to_dict()), 201
```

---

## 6. 前端设计

### 6.1 题目上传组件（灵活模式）

```vue
<!-- QuestionUploadFlexible.vue -->
<template>
  <div class="question-upload">
    <h2>上传题目</h2>
    
    <!-- 内容块编辑器 -->
    <div class="content-blocks">
      <draggable v-model="contentBlocks" @end="updateOrder">
        <div 
          v-for="(block, index) in contentBlocks"
          :key="block.id"
          class="content-block"
        >
          <!-- 文本块 -->
          <div v-if="block.type === 'text'" class="text-block">
            <textarea
              v-model="block.content"
              placeholder="输入文字内容..."
              rows="3"
            />
            <button @click="removeBlock(index)">删除</button>
          </div>
          
          <!-- 图片块 -->
          <div v-else-if="block.type === 'image'" class="image-block">
            <img v-if="block.preview" :src="block.preview" />
            <input 
              type="file" 
              accept="image/*"
              @change="handleImageUpload($event, index)"
            />
            <input 
              v-model="block.caption" 
              placeholder="图片说明（可选）"
            />
            <button @click="removeBlock(index)">删除</button>
          </div>
          
          <!-- PDF块 -->
          <div v-else-if="block.type === 'pdf'" class="pdf-block">
            <span v-if="block.filename">{{ block.filename }}</span>
            <input 
              type="file" 
              accept=".pdf"
              @change="handlePdfUpload($event, index)"
            />
            <button @click="removeBlock(index)">删除</button>
          </div>
        </div>
      </draggable>
    </div>
    
    <!-- 添加内容块按钮 -->
    <div class="add-block-buttons">
      <n-button @click="addTextBlock">
        <template #icon><TextIcon /></template>
        添加文字
      </n-button>
      <n-button @click="addImageBlock">
        <template #icon><ImageIcon /></template>
        添加图片
      </n-button>
      <n-button @click="addPdfBlock">
        <template #icon><FileIcon /></template>
        添加PDF
      </n-button>
    </div>
    
    <!-- 题目信息 -->
    <n-form>
      <n-form-item label="科目">
        <n-select v-model:value="subject" :options="subjectOptions" />
      </n-form-item>
      <n-form-item label="标题（可选）">
        <n-input v-model:value="title" />
      </n-form-item>
      <n-form-item label="难度">
        <n-rate v-model:value="difficulty" :count="5" />
      </n-form-item>
    </n-form>
    
    <!-- 提交 -->
    <n-button type="primary" @click="submitQuestion" :loading="uploading">
      创建题目
    </n-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { questionAPI } from '@/api/questions'
import draggable from 'vuedraggable'

const contentBlocks = ref([])
const subject = ref('')
const title = ref('')
const difficulty = ref(3)
const uploading = ref(false)

let blockIdCounter = 0

const addTextBlock = () => {
  contentBlocks.value.push({
    id: `block_${blockIdCounter++}`,
    type: 'text',
    content: '',
    order: contentBlocks.value.length
  })
}

const addImageBlock = () => {
  contentBlocks.value.push({
    id: `block_${blockIdCounter++}`,
    type: 'image',
    file: null,
    preview: null,
    caption: '',
    order: contentBlocks.value.length
  })
}

const addPdfBlock = () => {
  contentBlocks.value.push({
    id: `block_${blockIdCounter++}`,
    type: 'pdf',
    file: null,
    filename: '',
    order: contentBlocks.value.length
  })
}

const handleImageUpload = (event, index) => {
  const file = event.target.files[0]
  if (file) {
    contentBlocks.value[index].file = file
    // 生成预览
    const reader = new FileReader()
    reader.onload = (e) => {
      contentBlocks.value[index].preview = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handlePdfUpload = (event, index) => {
  const file = event.target.files[0]
  if (file) {
    contentBlocks.value[index].file = file
    contentBlocks.value[index].filename = file.name
  }
}

const removeBlock = (index) => {
  contentBlocks.value.splice(index, 1)
  updateOrder()
}

const updateOrder = () => {
  contentBlocks.value.forEach((block, index) => {
    block.order = index
  })
}

const submitQuestion = async () => {
  uploading.value = true
  
  try {
    // 准备FormData
    const formData = new FormData()
    
    // 添加JSON数据
    const questionData = {
      subject: subject.value,
      title: title.value,
      difficulty: difficulty.value,
      content: {
        type: detectContentType(),
        items: contentBlocks.value.map(block => {
          if (block.type === 'text') {
            return {
              type: 'text',
              content: block.content,
              order: block.order
            }
          } else if (block.type === 'image') {
            return {
              type: 'image_upload',
              caption: block.caption,
              order: block.order
            }
          } else if (block.type === 'pdf') {
            return {
              type: 'pdf_upload',
              order: block.order
            }
          }
        })
      }
    }
    
    formData.append('data', JSON.stringify(questionData))
    
    // 添加文件
    contentBlocks.value.forEach(block => {
      if (block.file) {
        formData.append('files', block.file)
      }
    })
    
    // 提交
    await questionAPI.createQuestion(formData)
    
    // 成功后跳转
    router.push('/questions')
  } catch (error) {
    console.error('Upload failed:', error)
  } finally {
    uploading.value = false
  }
}

const detectContentType = () => {
  const hasText = contentBlocks.value.some(b => b.type === 'text')
  const hasImage = contentBlocks.value.some(b => b.type === 'image')
  const hasPdf = contentBlocks.value.some(b => b.type === 'pdf')
  
  if (hasText || hasImage && hasPdf) return 'mixed'
  if (hasPdf) return 'pdf'
  if (contentBlocks.value.length === 1 && hasImage) return 'image_only'
  if (hasImage) return 'images_only'
  return 'text_only'
}
</script>
```

### 6.2 题目快捷上传组件（MVP简化版）

```vue
<!-- QuestionUploadQuick.vue - MVP推荐 -->
<template>
  <div class="quick-upload">
    <h2>快速上传题目</h2>
    
    <!-- 拍照/选择图片 -->
    <div class="image-upload-zone">
      <input
        type="file"
        accept="image/*"
        multiple
        capture="environment"
        @change="handleFiles"
        ref="fileInput"
        hidden
      />
      
      <n-button size="large" @click="$refs.fileInput.click()">
        <template #icon><CameraIcon /></template>
        拍照上传 (可选多张)
      </n-button>
      
      <!-- 图片预览 -->
      <div v-if="images.length" class="image-previews">
        <draggable v-model="images">
          <div v-for="(img, index) in images" :key="index" class="preview-card">
            <img :src="img.preview" />
            <button @click="removeImage(index)">×</button>
          </div>
        </draggable>
      </div>
    </div>
    
    <!-- 简单信息 -->
    <n-form>
      <n-form-item label="科目">
        <n-select v-model:value="subject" :options="subjectOptions" />
      </n-form-item>
      <n-form-item label="难度">
        <n-rate v-model:value="difficulty" />
      </n-form-item>
    </n-form>
    
    <n-button type="primary" block size="large" @click="submit">
      上传 {{ images.length }} 张图片
    </n-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { questionAPI } from '@/api/questions'
import draggable from 'vuedraggable'

const images = ref([])
const subject = ref('')
const difficulty = ref(3)

const handleFiles = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      images.value.push({
        file,
        preview: e.target.result
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeImage = (index) => {
  images.value.splice(index, 1)
}

const submit = async () => {
  const formData = new FormData()
  formData.append('subject', subject.value)
  formData.append('difficulty', difficulty.value)
  
  images.value.forEach(img => {
    formData.append('images', img.file)
  })
  
  await questionAPI.quickUpload(formData)
  router.push('/questions')
}
</script>
```

### 6.3 题目展示组件

```vue
<!-- QuestionDetailView.vue -->
<template>
  <div class="question-detail">
    <h1>{{ question.title }}</h1>
    
    <!-- 动态渲染内容块 -->
    <div class="question-content">
      <div
        v-for="(item, index) in question.content.items"
        :key="index"
        class="content-item"
      >
        <!-- 文本块 -->
        <div v-if="item.type === 'text'" class="text-content">
          <p>{{ item.content }}</p>
        </div>
        
        <!-- 图片块 -->
        <div v-else-if="item.type === 'image'" class="image-content">
          <img 
            :src="item.url" 
            :alt="item.caption"
            @click="openImageViewer(item.url)"
          />
          <p v-if="item.caption" class="caption">{{ item.caption }}</p>
        </div>
        
        <!-- PDF块 -->
        <div v-else-if="item.type === 'pdf'" class="pdf-content">
          <div class="pdf-preview">
            <img :src="item.thumbnail_url" />
            <div class="pdf-info">
              <span>{{ item.filename }}</span>
              <span>{{ item.page_count }} 页</span>
            </div>
          </div>
          <n-button @click="openPdf(item.url)">
            打开PDF
          </n-button>
        </div>
      </div>
    </div>
  </div>
</template>
```

---

## 7. 优势总结

### ✅ 灵活性
- 支持任意组合的内容类型
- 易于添加新类型（音频、视频等）

### ✅ 性能优化
- Cloudinary自动优化图片
- 生成缩略图，列表页快速加载
- PDF转图片预览

### ✅ 用户体验
- 所见即所得的编辑器
- 拖拽排序内容块
- 快捷模式（仅图片）降低门槛

### ✅ 数据结构
- JSON灵活存储，易于扩展
- 每个内容块独立，易于管理
- 元数据方便统计和检索

---

## 8. MVP实施建议

### Phase 1: MVP（推荐）
**仅支持图片上传（简化开发）**
- 使用快捷上传组件
- content结构仍然保留（但只有image类型）
- 未来平滑扩展

### Phase 2: 增强
**支持文字+图片混合**
- 添加文本块
- 灵活上传组件

### Phase 3: 完整
**支持PDF、音频等**
- 完整的多媒体支持

---

## 9. 总结

这个设计允许：
1. **MVP简单**：先只支持图片
2. **架构灵活**：JSON content字段可随时扩展
3. **体验优秀**：不同内容类型有专门展示方式
4. **性能高效**：云端存储+缩略图优化

**建议**：MVP阶段使用"快捷上传"，未来再启用"灵活模式"！
