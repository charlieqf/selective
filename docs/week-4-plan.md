# Implementation Plan - Week 4: Dashboard Rebuild & Advanced Features

## Goal Description

**Week 4专注于高级功能和深度优化**,基于Week 3建立的基础设施。

### Week 4 核心目标

1. **Dashboard重构**: 使用Week 3的analytics API和组件库
2. **题目上传增强**: **扩展Week 3的ImageUploader组件**,添加Cloudinary上传
3. **高级筛选和分页**: 完善QuestionFilters和分页控件
4. **注册页面优化**: 改进角色选择和表单验证
5. **深度测试**: 跨设备/浏览器测试,性能优化

## User Review Required

> [!IMPORTANT]
> **Week 4依赖Week 3完成**:
> - ✅ 后端analytics API可用
> - ✅ 前端组件库(QuestionCard, QuestionFilters, **ImageUploader**)
> - ✅ 布局系统(MainLayout, AuthLayout)
> - ✅ analytics store
> - ✅ 全局样式系统

> [!WARNING]
> **工作量评估**:
> - Dashboard重构: 2天
> - ImageUploader扩展+题目上传: 1-2天
> - 注册页面优化: 1天
> - 深度测试和优化: 2-3天
> - **总计**: 约7天全职工作

---

## Proposed Changes

### Frontend Components (扩展Week 3组件)

#### [MODIFY] [ImageUploader.vue](file:///c:/work/me/selective/frontend/src/components/ImageUploader.vue)
**扩展Week 3的ImageUploader组件,添加Cloudinary上传能力**。

**Week 3基础** → **Week 4扩展**

```vue
<script setup>
import { ref, watch } from 'vue'
import { NUpload, NButton, useMessage } from 'naive-ui'
import uploadApi from '../api/upload'

const props = defineProps({
  maxImages: { type: Number, default: 5 },
  maxSize: { type: Number, default: 5 * 1024 * 1024 },
  modelValue: { type: Array, default: () => [] }, // {url, public_id}[]
  enableUpload: { type: Boolean, default: true }  // Week 4启用Cloudinary
})

const emit = defineEmits(['update:modelValue'])

const message = useMessage()
const fileList = ref([])
const uploading = ref(false)

// 使用WeakMap追踪File对象→已上传数据的映射(解决文件名重复问题)
const fileToUploadedMap = new WeakMap()

// 监听props.modelValue变化(用于初始化和外部重置)
let lastEmittedValue = []
watch(() => props.modelValue, async (newValue) => {
  // 避免循环:如果是我们自己emit的值,不处理
  if (newValue === lastEmittedValue) return
  
  // 外部重置为空:清理Cloudinary资源
  if (newValue.length === 0 && fileList.value.length > 0) {
    // 删除所有已上传的图片
    for (const item of fileList.value) {
      const uploadedData = fileToUploadedMap.get(item.file) || item._uploadedData
      if (uploadedData?.public_id) {
        try {
          await uploadApi.deleteImage(uploadedData.public_id)
        } catch (err) {
          console.error('Failed to cleanup image:', err)
        }
      }
    }
    fileList.value = []
    return
  }
  
  // 外部提供初始值(用于编辑场景):只在fileList为空时初始化
  if (newValue.length > 0 && fileList.value.length === 0) {
    fileList.value = newValue.map((img, index) => ({
      id: `uploaded-${index}`,
      name: img.url.split('/').pop(),
      status: 'finished',
      url: img.url,
      _uploadedData: img
    }))
  }
}, { immediate: true })

// 自定义上传请求
async function customRequest({ file, onProgress, onFinish, onError }) {
  if (!props.enableUpload) {
    onFinish()
    return
  }

  uploading.value = true

  try {
    // 上传到Cloudinary
    const { data } = await uploadApi.uploadImage(file.file)
    
    // 使用WeakMap保存File对象→上传数据的映射
    fileToUploadedMap.set(file.file, {
      url: data.url,
      public_id: data.public_id
    })
    
    // 更新modelValue
    updateModelValue()
    
    onFinish()
  } catch (err) {
    message.error(`Failed to upload ${file.name}`)
    onError()
  } finally {
    uploading.value = false
  }
}

// 文件移除时删除Cloudinary图片
async function handleRemove({ file }) {
  const uploadedData = fileToUploadedMap.get(file.file) || file._uploadedData
  
  if (uploadedData?.public_id) {
    try {
      await uploadApi.deleteImage(uploadedData.public_id)
    } catch (err) {
      console.error('Failed to delete image:', err)
    }
  }
  
  // 从fileList移除后,updateModelValue会自动触发
  updateModelValue()
  return true
}

// 更新modelValue: 转换Naive UI fileList为{url, public_id}格式
function updateModelValue() {
  const uploaded = fileList.value
    .map(item => {
      // 通过File对象引用查找上传数据(不依赖文件名)
      const data = fileToUploadedMap.get(item.file) || item._uploadedData
      if (data) {
        return { url: data.url, public_id: data.public_id }
      }
      return null
    })
    .filter(Boolean)
  
  // 记录我们emit的值,避免watch循环
  lastEmittedValue = uploaded
  emit('update:modelValue', uploaded)
}
</script>

<template>
  <div>
    <n-upload
      v-model:file-list="fileList"
      :max="maxImages"
      list-type="image-card"
      accept="image/jpeg,image/png,image/webp"
      :custom-request="customRequest"
      @remove="handleRemove"
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

### Frontend Views (使用扩展后的组件)

#### [MODIFY] [DashboardView.vue](file:///c:/work/me/selective/frontend/src/views/dashboard/DashboardView.vue)
完整重构Dashboard,使用Week 3的analytics API和组件。

```vue
<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useAnalyticsStore } from '../../stores/analytics'
import QuestionCard from '../../components/QuestionCard.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import { NGrid, NGridItem, NCard, NStatistic, NButton, NSpace } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const analyticsStore = useAnalyticsStore()

onMounted(async () => {
  await analyticsStore.refreshAll()
})

function handleQuestionClick(question) {
  router.push(`/questions/${question.id}`)
}
</script>

<template>
  <div class="container">
    <!-- 欢迎信息 -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold">Welcome back, {{ authStore.user?.username }}!</h1>
      <p class="text-gray-600">Here's your learning progress</p>
    </div>

    <!-- 加载状态 -->
    <LoadingSpinner v-if="analyticsStore.loading" text="Loading dashboard..." />

    <template v-else>
      <!-- 统计卡片 -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" class="mb-6">
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Total Questions" :value="analyticsStore.stats?.total_questions || 0" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Answered" :value="analyticsStore.stats?.answered_questions || 0" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Mastered" :value="analyticsStore.stats?.mastered_questions || 0" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Need Review" :value="analyticsStore.stats?.need_review_questions || 0" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 快捷操作 -->
      <n-space class="mb-6">
        <n-button type="primary" @click="router.push('/questions/upload')">Upload New Question</n-button>
        <n-button @click="router.push('/questions')">View All Questions</n-button>
      </n-space>

      <!-- 推荐题目 -->
      <div class="mb-6">
        <h2 class="text-2xl font-bold mb-4">Recommended for You</h2>
        <div v-if="analyticsStore.recommendations.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <QuestionCard 
            v-for="question in analyticsStore.recommendations" 
            :key="question.id"
            :question="question"
            @click="handleQuestionClick"
          />
        </div>
        <EmptyState 
          v-else
          icon="📚"
          title="No recommendations yet"
          description="Upload some questions to get personalized recommendations"
          action-text="Upload Question"
          action-to="/questions/upload"
        />
      </div>

      <!-- 各科目统计 -->
      <div>
        <h2 class="text-2xl font-bold mb-4">Subject Breakdown</h2>
        <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
          <n-grid-item v-for="(stats, subject) in analyticsStore.stats?.by_subject" :key="subject" :span="4" :md-span="2" :lg-span="1">
            <n-card :title="subject">
              <n-space vertical>
                <div>Total: {{ stats.total }}</div>
                <div>Answered: {{ stats.answered }}</div>
                <div>Mastered: {{ stats.mastered }}</div>
              </n-space>
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>
    </template>
  </div>
</template>
```

#### [MODIFY] [QuestionUpload.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionUpload.vue)
**复用扩展后的ImageUploader组件**。

```vue
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NSelect, NButton, NCard, NSpace } from 'naive-ui'
import { useQuestionStore } from '../../stores/question'
import ImageUploader from '../../components/ImageUploader.vue'  // 复用Week 3组件

const router = useRouter()
const message = useMessage()
const questionStore = useQuestionStore()

const formRef = ref(null)
const loading = ref(false)

// ImageUploader会自动上传并emit {url, public_id}[]格式
const uploadedImages = ref([])

const model = ref({
  title: '',
  subject: null,
  difficulty: 3,
  content_text: ''
})

const subjectOptions = [
  { label: 'Reading', value: 'READING' },
  { label: 'Writing', value: 'WRITING' },
  { label: 'Maths', value: 'MATHS' },
  { label: 'Thinking Skills', value: 'THINKING_SKILLS' }
]

const rules = {
  subject: {
    required: true,
    message: 'Please select a subject',
    trigger: 'change'
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    
    if (uploadedImages.value.length === 0) {
      message.warning('Please upload at least one image')
      return
   }
    
    loading.value = true
    
    // uploadedImages已经是{url, public_id}格式,直接使用
    const questionData = {
      ...model.value,
      images: uploadedImages.value
    }
    
    await questionStore.createQuestion(questionData)
    message.success('Question uploaded successfully')
    router.push('/questions')
    
  } catch (error) {
    message.error(error.message || 'Failed to upload question')
    // ImageUploader组件内部已处理Cloudinary清理
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  // 清空uploadedImages会触发ImageUploader的watch
  // watch检测到空数组后会自动删除Cloudinary图片
  uploadedImages.value = []
  router.push('/questions')
}
</script>

<template>
  <div class="container max-w-4xl mx-auto">
    <div class="mb-6">
      <h1 class="text-3xl font-bold">Upload New Question</h1>
      <p class="text-gray-600">Add a question from your practice materials</p>
    </div>

    <n-card>
      <n-form ref="formRef" :model="model" :rules="rules">
        <!-- 图片上传 - 复用ImageUploader组件 -->
        <n-form-item label="Question Images" required>
          <ImageUploader 
            v-model="uploadedImages"
            :enable-upload="true"
            :max-images="5"
          />
        </n-form-item>

        <!-- 标题 -->
        <n-form-item label="Title (Optional)">
          <n-input v-model:value="model.title" placeholder="e.g., Year 2023 Question 15" />
        </n-form-item>

        <!-- 科目 -->
        <n-form-item label="Subject" path="subject">
          <n-select v-model:value="model.subject" :options="subjectOptions" placeholder="Select subject" />
        </n-form-item>

        <!-- 难度 -->
        <n-form-item label="Difficulty">
          <n-select 
            v-model:value="model.difficulty" 
            :options="[
              { label: '⭐ Very Easy', value: 1 },
              { label: '⭐⭐ Easy', value: 2 },
              { label: '⭐⭐⭐ Medium', value: 3 },
              { label: '⭐⭐⭐⭐ Hard', value: 4 },
              { label: '⭐⭐⭐⭐⭐ Very Hard', value: 5 }
            ]"
            placeholder="Select difficulty"
          />
        </n-form-item>

        <!-- 描述/OCR文本 -->
        <n-form-item label="Description (Optional)">
          <n-input 
            v-model:value="model.content_text" 
            type="textarea" 
            :rows="4"
            placeholder="Add notes or paste OCR text..."
          />
        </n-form-item>

        <!-- 操作按钮 -->
        <n-space justify="end">
          <n-button @click="handleCancel">Cancel</n-button>
          <n-button type="primary" :loading="loading" @click="handleSubmit">
            Upload Question
          </n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>
```

#### [MODIFY] [RegisterView.vue](file:///c:/work/me/selective/frontend/src/views/RegisterView.vue)
优化注册页面。

**改进**:
1. 卡片式角色选择
2. 密码强度指示器
3. 实时表单验证
4. 注册成功后自动登录

#### [MODIFY] [QuestionList.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionList.vue)
完善分页和筛选。

**改进**:
1. 添加分页控件
2. 优化筛选器布局(移动端折叠)
3. 添加"刷新"按钮
4. 网格布局优化

---

### Frontend Router

#### [MODIFY] [router/index.js](file:///c:/work/me/selective/frontend/src/router/index.js)
应用布局系统。

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      component: AuthLayout,
      children: [
        {
          path: '',
          name: 'Login',
          component: () => import('../views/LoginView.vue')
        }
      ]
    },
    {
      path: '/register',
      component: AuthLayout,
      children: [
        {
          path: '',
          name: 'Register',
          component: () => import('../views/RegisterView.vue')
        }
      ]
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/dashboard/DashboardView.vue')
        },
        {
          path: 'questions',
          name: 'QuestionList',
          component: () => import('../views/questions/QuestionList.vue')
        },
        {
          path: 'questions/upload',
          name: 'QuestionUpload',
          component: () => import('../views/questions/QuestionUpload.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
```

---

## Verification Plan

### Manual Verification

#### 1. Dashboard完整测试
- [ ] 统计卡片显示正确数据
- [ ] 推荐题目显示(优先NEED_REVIEW)
- [ ] 空状态显示正确
- [ ] 科目统计显示
- [ ] 快捷操作按钮工作
- [ ] 响应式布局(手机/平板/桌面)

#### 2. 题目上传完整测试 (**ImageUploader组件**)
- [ ] 图片上传到Cloudinary(通过File对象追踪)
- [ ] 多图上传(最多5张)
- [ ] 文件名重复处理正确(IMG_0001.jpg多次上传)
- [ ] 文件类型验证
- [ ] 文件大小验证
- [ ] 上传进度显示
- [ ] 移除时删除Cloudinary图片
- [ ] 取消时清理所有已上传图片
- [ ] 表单验证工作
- [ ] 提交成功跳转

#### 3-9. (其他测试项目同原计划)

---

## Success Criteria (Week 4)

1. ✅ **Dashboard**: 功能完整,数据准确,UI美观
2. ✅ **ImageUploader扩展**: Cloudinary集成,WeakMap追踪,组件复用
3. ✅ **题目上传**: 使用ImageUploader组件,体验流畅
4. ✅ **注册优化**: UI改进,自动登录
5. ✅ **题目列表**: 分页和筛选完善
6. ✅ **布局系统**: 应用到所有页面

**关键改进**:
- **组件复用**: QuestionUpload复用ImageUploader,避免重复逻辑
- **文件追踪**: 使用WeakMap追踪File对象引用,解决文件名重复问题
- **责任分离**: Cloudinary逻辑集中在ImageUploader组件

---

## Notes

- Week 4**扩展Week 3组件**而非重新实现
- ImageUploader是可复用组件,Week 5可继续使用
- WeakMap确保了垃圾回收,不会内存泄漏
- 如果Week 3延期,Week 4可以相应调整
