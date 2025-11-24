# Implementation Plan - Week 3: Backend API & Frontend Foundation

## Goal Description

**Week 3专注于建立坚实的基础设施**,为Week 4的UI重构做准备。根据团队反馈,原计划工作量过大,现拆分为两周:

- **Week 3** (本周): 后端API、组件库、布局系统、基础优化
- **Week 4** (下周): Dashboard重构、高级功能、深度测试

### Week 3 核心目标

1. **后端API扩展**: 添加统计、推荐、排序支持
2. **前端组件库**: 创建5个可复用组件
3. **布局系统**: 实现MainLayout和AuthLayout
4. **全局样式**: 建立设计系统
5. **增量改进**: 优化登录/注册/题目列表页面

## User Review Required

> [!IMPORTANT]
> **工作量评估**:
> - 后端API开发: 2-3天
> - 前端组件库: 2-3天
> - 布局系统: 1-2天
> - 页面增量改进: 1-2天
> - **总计**: 约7天全职工作

> [!WARNING]
> **Week 3 vs Week 4 分工**:
> - **Week 3**: 基础设施(组件、布局、API)+ 简单页面优化
> - **Week 4**: 复杂功能(Dashboard、高级筛选)+ 深度测试
> - 这样可以在Week 3结束时获得设计反馈,Week 4再调整

> [!CAUTION]
> **依赖关系**:
> - 前端组件库依赖全局样式
> - 页面优化依赖组件库和布局系统
> - Week 4的Dashboard依赖Week 3的后端API

---

## Proposed Changes

### Backend API Extensions (后端优先)

#### [MODIFY] [questions.py](file:///c:/work/me/selective/backend/app/routes/questions.py)
扩展题目列表API,添加排序参数。

**变更**:
- `GET /api/questions`: 添加 `sort_by` 和 `sort_direction` 参数
  - `sort_by`: `created_at`(默认), `difficulty`, `updated_at`
  - `sort_direction`: `desc`(默认), `asc`

**实现**:
```python
@bp.route('', methods=['GET'])
@jwt_required()
def get_questions():
    # ... 现有代码 ...
    
    # 添加排序参数
    sort_by = request.args.get('sort_by', 'created_at')
    sort_direction = request.args.get('sort_direction', 'desc')
    
    # 验证参数
    allowed_sort_fields = ['created_at', 'difficulty', 'updated_at']
    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'
    
    # 应用排序
    if sort_direction == 'asc':
        query = query.order_by(getattr(Question, sort_by).asc())
    else:
        query = query.order_by(getattr(Question, sort_by).desc())
    
    # ... 分页代码 ...
```

#### [NEW] [analytics.py](file:///c:/work/me/selective/backend/app/routes/analytics.py)
创建统计分析API蓝图。

**端点1**: `GET /api/analytics/stats`
```python
from flask import Blueprint, jsonify, request  # 添加request导入
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.question import Question
from sqlalchemy import func

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    
    # 总体统计
    total = Question.query.filter_by(author_id=user_id).count()
    answered = Question.query.filter_by(author_id=user_id).filter(
        Question.status.in_(['ANSWERED', 'MASTERED'])
    ).count()
    mastered = Question.query.filter_by(author_id=user_id, status='MASTERED').count()
    need_review = Question.query.filter_by(author_id=user_id, status='NEED_REVIEW').count()
    
    # 按科目统计 - 使用数据库中的大写枚举值
    by_subject = {}
    subjects = ['READING', 'WRITING', 'MATHS', 'THINKING_SKILLS']
    for subject in subjects:
        subject_total = Question.query.filter_by(author_id=user_id, subject=subject).count()
        subject_answered = Question.query.filter_by(author_id=user_id, subject=subject).filter(
            Question.status.in_(['ANSWERED', 'MASTERED'])
        ).count()
        subject_mastered = Question.query.filter_by(author_id=user_id, subject=subject, status='MASTERED').count()
        by_subject[subject] = {
            'total': subject_total,
            'answered': subject_answered,
            'mastered': subject_mastered
        }
    
    # 按难度统计
    by_difficulty = {}
    for i in range(1, 6):
        count = Question.query.filter_by(author_id=user_id, difficulty=i).count()
        by_difficulty[str(i)] = count
    
    return jsonify({
        'total_questions': total,
        'answered_questions': answered,
        'mastered_questions': mastered,
        'need_review_questions': need_review,
        'by_subject': by_subject,
        'by_difficulty': by_difficulty
    }), 200
```

**端点2**: `GET /api/analytics/recommendations`
```python
@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 10, type=int)
    subject = request.args.get('subject')
    
    # 简化推荐逻辑(Week 5会完善)
    query = Question.query.filter_by(author_id=user_id)
    
    if subject:
        query = query.filter_by(subject=subject)
    
    # 优先级: NEED_REVIEW > UNANSWERED, 按难度升序
    need_review = query.filter_by(status='NEED_REVIEW').order_by(Question.difficulty.asc()).limit(limit).all()
    
    if len(need_review) < limit:
        remaining = limit - len(need_review)
        unanswered = query.filter_by(status='UNANSWERED').order_by(Question.difficulty.asc()).limit(remaining).all()
        recommendations = need_review + unanswered
    else:
        recommendations = need_review
    
    from app.schemas.question import QuestionSchema
    schema = QuestionSchema(many=True)
    return jsonify(schema.dump(recommendations)), 200
```

#### [MODIFY] [__init__.py](file:///c:/work/me/selective/backend/app/__init__.py)
注册analytics蓝图。

```python
from app.routes import analytics
app.register_blueprint(analytics.bp)
```

---

### Frontend API Client

#### [NEW] [analytics.js](file:///c:/work/me/selective/frontend/src/api/analytics.js)
```javascript
import client from './client'

export const analyticsApi = {
  getStats: () => client.get('/analytics/stats'),
  getRecommendations: (params) => client.get('/analytics/recommendations', { params })
}
```

#### [MODIFY] [questions.js](file:///c:/work/me/selective/frontend/src/api/questions.js)
添加排序参数支持,保持default export与现有代码一致。

```javascript
import apiClient from './client'

// 保持default export,与现有store导入一致
export default {
  getQuestions(params) {
    // params可以包含: page, per_page, subject, difficulty, status, sort_by, sort_direction
    return apiClient.get('/questions', { params })
  },
  
  createQuestion(data) {
    return apiClient.post('/questions', data)
  },
  
  getQuestion(id) {
    return apiClient.get(`/questions/${id}`)
  },
  
  updateQuestion(id, data) {
    return apiClient.patch(`/questions/${id}`, data)
  },
  
  deleteQuestion(id) {
    return apiClient.delete(`/questions/${id}`)
  }
}
```

---

### Frontend Global Styles

#### [MODIFY] [style.css](file:///c:/work/me/selective/frontend/src/style.css)
建立设计系统和全局样式。

```css
/* CSS变量 - 颜色主题 */
:root {
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-500: #3b82f6;
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-500: #6b7280;
  --gray-700: #374151;
  --gray-900: #111827;
  
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  
  /* 间距 */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* 圆角 */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

/* 全局重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: var(--gray-900);
  background-color: var(--gray-50);
  line-height: 1.5;
}

/* 工具类 */
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-lg);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-600);
  color: white;
  border: none;
}

.btn-primary:hover {
  background: var(--primary-700);
}

/* 响应式断点 */
@media (max-width: 640px) {
  .container {
    padding: 0 var(--spacing-sm);
  }
}
```

---

### Frontend Component Library

#### [NEW] [LoadingSpinner.vue](file:///c:/work/me/selective/frontend/src/components/LoadingSpinner.vue)
最简单的组件,先实现。

```vue
<script setup>
defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  text: String
})

const sizeClasses = {
  small: 'w-4 h-4',
  medium: 'w-8 h-8',
  large: 'w-12 h-12'
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-2">
    <div :class="['animate-spin rounded-full border-2 border-gray-300 border-t-primary-600', sizeClasses[size]]"></div>
    <p v-if="text" class="text-sm text-gray-600">{{ text }}</p>
  </div>
</template>
```

#### [NEW] [EmptyState.vue](file:///c:/work/me/selective/frontend/src/components/EmptyState.vue)
```vue
<script setup>
defineProps({
  icon: String,
  title: { type: String, required: true },
  description: String,
  actionText: String,
  actionTo: String
})
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div v-if="icon" class="text-6xl mb-4">{{ icon }}</div>
    <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h3>
    <p v-if="description" class="text-gray-600 mb-6 max-w-md">{{ description }}</p>
    <router-link v-if="actionText && actionTo" :to="actionTo" class="btn btn-primary">
      {{ actionText }}
    </router-link>
  </div>
</template>
```

#### [NEW] [QuestionCard.vue](file:///c:/work/me/selective/frontend/src/components/QuestionCard.vue)
```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  question: { type: Object, required: true }
})

const emit = defineEmits(['click'])

const firstImage = computed(() => {
  return props.question.images?.[0]?.url || null
})

const difficultyStars = computed(() => {
  return '⭐'.repeat(props.question.difficulty || 0)
})

const statusColors = {
  UNANSWERED: 'bg-gray-100 text-gray-700',
  ANSWERED: 'bg-blue-100 text-blue-700',
  MASTERED: 'bg-green-100 text-green-700',
  NEED_REVIEW: 'bg-yellow-100 text-yellow-700'
}
</script>

<template>
  <div class="card cursor-pointer hover:shadow-lg transition-shadow" @click="emit('click', props.question)">
    <div v-if="firstImage" class="mb-3">
      <img :src="firstImage" :alt="props.question.title || 'Question'" class="w-full h-48 object-cover rounded-md" />
    </div>
    <div class="flex items-start justify-between mb-2">
      <span class="text-sm font-medium text-primary-600">{{ props.question.subject }}</span>
      <span class="text-sm">{{ difficultyStars }}</span>
    </div>
    <h3 v-if="props.question.title" class="font-semibold mb-2">{{ props.question.title }}</h3>
    <div class="flex items-center justify-between">
      <span :class="['text-xs px-2 py-1 rounded', statusColors[props.question.status]]">
        {{ props.question.status }}
      </span>
      <span class="text-xs text-gray-500">
        {{ new Date(props.question.created_at).toLocaleDateString() }}
      </span>
    </div>
  </div>
</template>
```

#### [NEW] [QuestionFilters.vue](file:///c:/work/me/selective/frontend/src/components/QuestionFilters.vue)
```vue
<script setup>
import { ref, watch } from 'vue'
import { NSelect, NSpace } from 'naive-ui'

const props = defineProps({
  filters: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:filters'])

const localFilters = ref({ ...props.filters })

// 监听localFilters变化,emit给父组件
watch(localFilters, (newFilters) => {
  emit('update:filters', newFilters)
}, { deep: true })

// 监听props.filters变化,同步到localFilters(实现双向绑定)
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

// 使用数据库中的大写枚举值
const subjectOptions = [
  { label: 'All Subjects', value: null },
  { label: 'Reading', value: 'READING' },
  { label: 'Writing', value: 'WRITING' },
  { label: 'Maths', value: 'MATHS' },
  { label: 'Thinking Skills', value: 'THINKING_SKILLS' }
]

const difficultyOptions = [
  { label: 'All Difficulties', value: null },
  { label: '⭐ (1)', value: 1 },
  { label: '⭐⭐ (2)', value: 2 },
  { label: '⭐⭐⭐ (3)', value: 3 },
  { label: '⭐⭐⭐⭐ (4)', value: 4 },
  { label: '⭐⭐⭐⭐⭐ (5)', value: 5 }
]

const statusOptions = [
  { label: 'All Status', value: null },
  { label: 'Unanswered', value: 'UNANSWERED' },
  { label: 'Answered', value: 'ANSWERED' },
  { label: 'Mastered', value: 'MASTERED' },
  { label: 'Need Review', value: 'NEED_REVIEW' }
]

const sortOptions = [
  { label: 'Newest First', value: { sort_by: 'created_at', sort_direction: 'desc' } },
  { label: 'Oldest First', value: { sort_by: 'created_at', sort_direction: 'asc' } },
  { label: 'Difficulty: Low to High', value: { sort_by: 'difficulty', sort_direction: 'asc' } },
  { label: 'Difficulty: High to Low', value: { sort_by: 'difficulty', sort_direction: 'desc' } }
]
</script>

<template>
  <div class="card mb-4">
    <n-space vertical>
      <n-space>
        <n-select v-model:value="localFilters.subject" :options="subjectOptions" placeholder="Subject" style="width: 200px" />
        <n-select v-model:value="localFilters.difficulty" :options="difficultyOptions" placeholder="Difficulty" style="width: 200px" />
        <n-select v-model:value="localFilters.status" :options="statusOptions" placeholder="Status" style="width: 200px" />
        <n-select 
          v-model:value="localFilters.sort" 
          :options="sortOptions" 
          placeholder="Sort by" 
          style="width: 200px"
          @update:value="(val) => { localFilters.sort_by = val.sort_by; localFilters.sort_direction = val.sort_direction }"
        />
      </n-space>
    </n-space>
  </div>
</template>
```

#### [NEW] [ImageUploader.vue](file:///c:/work/me/selective/frontend/src/components/ImageUploader.vue)
Week 3创建基础UI,Week 4在此组件中集成Cloudinary上传逻辑。

```vue
<script setup>
import { ref, watch } from 'vue'
import { NUpload, NButton, useMessage } from 'naive-ui'

const props = defineProps({
  maxImages: { type: Number, default: 5 },
  maxSize: { type: Number, default: 5 * 1024 * 1024 }, // 5MB
  modelValue: { type: Array, default: () => [] }, // Week 4: {url, public_id}[]
  enableUpload: { type: Boolean, default: false }  // Week 4: true启用Cloudinary上传
})

const emit = defineEmits(['update:modelValue', 'upload-progress'])

const message = useMessage()
const fileList = ref([...props.modelValue])
const uploading = ref(false)

// 监听fileList变化,emit给父组件
watch(fileList, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

// 监听props.modelValue变化,同步到fileList(实现双向绑定)
watch(() => props.modelValue, (newValue) => {
  fileList.value = [...newValue]
}, { deep: true })

// Week 3: 简化版本,只做UI
// Week 4: 添加Cloudinary上传逻辑到此组件
function handleBeforeUpload(options) {
  const { file } = options
  
  // 基础验证
  if (file.size > props.maxSize) {
    message.error(`File size exceeds ${Math.round(props.maxSize / 1024 / 1024)}MB`)
    return false
  }
  
  // Week 4: 如果enableUpload=true,在这里上传到Cloudinary
  // 并emit 'upload-progress' 事件
  return true
}
</script>

<template>
  <div>
    <n-upload
      v-model:file-list="fileList"
      :max="maxImages"
      list-type="image-card"
      accept="image/jpeg,image/png,image/webp"
      :on-before-upload="handleBeforeUpload"
      :custom-request="() => {}"
    >
      <n-button :loading="uploading">
        {{ uploading ? 'Uploading...' : `Upload Images (Max ${maxImages})` }}
      </n-button>
    </n-upload>
    <p class="text-sm text-gray-500 mt-2">
      Accepted: JPG, PNG, WEBP. Max size: {{ Math.round(maxSize / 1024 / 1024) }}MB per image.
    </p>
  </div>
</template>
```

---

### Frontend Layouts

#### [NEW] [MainLayout.vue](file:///c:/work/me/selective/frontend/src/layouts/MainLayout.vue)
```vue
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { NLayout, NLayoutHeader, NLayoutSider, NLayoutContent, NMenu, NButton } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const collapsed = ref(false)

const menuOptions = [
  { label: 'Dashboard', key: 'dashboard', path: '/dashboard' },
  { label: 'Questions', key: 'questions', path: '/questions' },
  { label: 'Upload', key: 'upload', path: '/questions/upload' }
]

// 创建key到path的映射
const menuPathMap = Object.fromEntries(
  menuOptions.map(item => [item.key, item.path])
)

// Naive UI的menu只emit key,不是整个item对象
function handleMenuSelect(key) {
  const path = menuPathMap[key]
  if (path) {
    router.push(path)
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <n-layout has-sider class="min-h-screen">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="p-4">
        <h1 class="text-xl font-bold">Selective Prep</h1>
      </div>
      <n-menu :options="menuOptions" @update:value="handleMenuSelect" />
    </n-layout-sider>
    
    <n-layout>
      <n-layout-header bordered class="p-4 flex justify-between items-center">
        <div></div>
        <n-button @click="handleLogout">Logout</n-button>
      </n-layout-header>
      
      <n-layout-content class="p-6">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>
```

#### [NEW] [AuthLayout.vue](file:///c:/work/me/selective/frontend/src/layouts/AuthLayout.vue)
```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full">
      <router-view />
    </div>
  </div>
</template>
```

---

### Frontend Stores

#### [NEW] [analytics.js](file:///c:/work/me/selective/frontend/src/stores/analytics.js)
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyticsApi } from '../api/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  const stats = ref(null)
  const recommendations = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchStats() {
    loading.value = true
    error.value = null
    try {
      const { data } = await analyticsApi.getStats()
      stats.value = data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch stats:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchRecommendations(params = {}) {
    loading.value = true
    error.value = null
    try {
      const { data } = await analyticsApi.getRecommendations(params)
      recommendations.value = data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch recommendations:', err)
    } finally {
      loading.value = false
    }
  }

  async function refreshAll() {
    await Promise.all([fetchStats(), fetchRecommendations()])
  }

  return {
    stats,
    recommendations,
    loading,
    error,
    fetchStats,
    fetchRecommendations,
    refreshAll
  }
})
```

---

### Frontend Views (增量改进)

#### [MODIFY] [LoginView.vue](file:///c:/work/me/selective/frontend/src/views/LoginView.vue)
Week 3只做小改进:
- 添加品牌Logo区域
- 改进表单间距
- 优化错误提示显示

#### [MODIFY] [QuestionList.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionList.vue)
Week 3集成新组件:
- 使用 `QuestionCard` 组件
- 使用 `QuestionFilters` 组件
- 使用 `LoadingSpinner` 和 `EmptyState`
- 添加排序功能

---

## Verification Plan

### Backend API Tests

创建 `backend/tests/test_analytics.py`:

```python
def test_get_stats_success(client, auth_headers):
    response = client.get('/api/analytics/stats', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_questions' in data
    assert 'by_subject' in data

def test_get_recommendations_success(client, auth_headers):
    response = client.get('/api/analytics/recommendations?limit=5', headers=auth_headers)
    assert response.status_code == 200

def test_questions_sort_by_difficulty(client, auth_headers):
    response = client.get('/api/questions?sort_by=difficulty&sort_direction=asc', headers=auth_headers)
    assert response.status_code == 200
```

### Manual Verification (Week 3范围)

#### 1. 后端API测试
- [ ] 测试 `GET /api/analytics/stats`
- [ ] 测试 `GET /api/analytics/recommendations`
- [ ] 测试排序参数

#### 2. 组件库测试
- [ ] LoadingSpinner 各种尺寸
- [ ] EmptyState 显示正确
- [ ] QuestionCard 布局美观
- [ ] QuestionFilters 筛选工作

#### 3. 布局系统测试
- [ ] MainLayout 导航工作
- [ ] AuthLayout 居中显示
- [ ] 响应式适配

#### 4. 页面改进测试
- [ ] 登录页面UI改进
- [ ] 题目列表使用新组件
- [ ] 排序功能工作

---

## Success Criteria (Week 3)

完成Week 3后应达到:

1. ✅ **后端API**: 统计和推荐API可用,排序参数工作
2. ✅ **组件库**: 5个可复用组件创建并测试
3. ✅ **布局系统**: MainLayout和AuthLayout实现
4. ✅ **全局样式**: 设计系统建立
5. ✅ **增量改进**: 登录和题目列表页面使用新组件

**为Week 4准备**:
- 组件库可复用
- 设计系统确立
- 后端API就绪
- 可以获得设计反馈

---

## Notes

- Week 3专注**基础设施**,不追求完美UI
- 组件可以先实现基础功能,Week 4再完善
- ImageUploader Week 3只做UI,Week 4集成上传
- Dashboard留到Week 4,因为它最复杂
