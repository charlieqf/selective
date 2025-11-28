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
