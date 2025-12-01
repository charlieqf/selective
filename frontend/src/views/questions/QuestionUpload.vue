<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NSelect, NButton, NCard, NSpace } from 'naive-ui'
import { useItemStore } from '../../stores/items'
import { useCollectionStore } from '../../stores/collections'
import ImageUploader from '../../components/ImageUploader.vue'
import uploadApi from '../../api/upload'
import client from '../../api/client'
import tagsApi from '../../api/tags'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const itemStore = useItemStore()
const collectionStore = useCollectionStore()

const formRef = ref(null)
const loading = ref(false)
const isEditMode = ref(false)
const itemId = ref(null)

// ImageUploader会自动上传并emit {url, public_id}[]格式
const uploadedImages = ref([])
const initialImages = ref([]) // Track original state for cleanup

const model = ref({
  title: '',
  collection_id: null,
  difficulty: 3,
  content_text: '',
  tags: []
})

const tagOptions = ref([])
const loadingTags = ref(false)

const collectionOptions = computed(() => {
  return collectionStore.activeCollections.map(c => ({
    label: c.name,
    value: c.id
  }))
})

const rules = {
  collection_id: {
    type: 'number',
    required: true,
    message: 'Please select a subject',
    trigger: 'change'
  }
}

onMounted(async () => {
  // Fetch collections and tags
  await collectionStore.fetchCollections()
  await fetchTags()

  if (route.params.id) {
    isEditMode.value = true
    itemId.value = route.params.id
    loading.value = true
    try {
      const item = await itemStore.getItem(itemId.value)
      model.value = {
        title: item.title,
        collection_id: item.collection_id,
        difficulty: item.difficulty,
        content_text: item.content_text,
        tags: item.tags ? item.tags.map(t => t.name) : []
      }
      // Transform images for uploader
      uploadedImages.value = item.images || []
      initialImages.value = JSON.parse(JSON.stringify(uploadedImages.value))
    } catch (error) {
      message.error('Failed to load question')
      router.push('/questions')
    } finally {
      loading.value = false
    }
  }
})

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    
    if (uploadedImages.value.length === 0) {
      message.warning('Please upload at least one image')
      return
    }
    
    loading.value = true
    
    // uploadedImages已经是{url, public_id}格式,直接使用
    const itemData = {
      ...model.value,
      images: uploadedImages.value
    }
    
    if (isEditMode.value) {
      await itemStore.updateItem(itemId.value, itemData)
      message.success('Question updated successfully')
      router.push(`/questions/${itemId.value}`)
    } else {
      await itemStore.createItem(itemData)
      message.success('Question uploaded successfully')
      router.push('/questions')
    }
    
  } catch (error) {
    message.error(error.message || 'Failed to upload question')
    // ImageUploader组件内部已处理Cloudinary清理
  } finally {
    loading.value = false
  }
}

async function handleCancel() {
  const currentImages = uploadedImages.value
  const initial = initialImages.value
  
  let imagesToDelete = []

  if (isEditMode.value) {
    // Edit Mode: Only delete NEW images that weren't there initially
    // We keep images that were in initial (even if removed from UI, because we are cancelling the removal)
    imagesToDelete = currentImages.filter(img => 
      !initial.some(init => init.public_id === img.public_id)
    )
  } else {
    // Create Mode: All images are new and unsaved, so delete them all
    imagesToDelete = currentImages
  }
  
  // Delete from Cloudinary
  if (imagesToDelete.length > 0) {
    loading.value = true
    try {
      await Promise.all(imagesToDelete.map(img => uploadApi.deleteImage(img.public_id)))
      message.info('Cleaned up unsaved uploads')
    } catch (error) {
      console.error('Failed to cleanup uploads:', error)
    } finally {
      loading.value = false
    }
  }

  router.push('/questions')
}

async function fetchTags() {
  loadingTags.value = true
  try {
    const response = await tagsApi.getTags()
    tagOptions.value = response.data.map(tag => ({
      label: tag.name,
      value: tag.name
    }))
  } catch (error) {
    console.error('Failed to fetch tags:', error)
  } finally {
    loadingTags.value = false
  }
}
</script>

<template>
  <div class="container max-w-4xl mx-auto">
    <div class="mb-6">
      <h1 class="text-3xl font-bold">{{ isEditMode ? 'Edit Question' : 'Upload New Question' }}</h1>
      <p class="text-gray-600">{{ isEditMode ? 'Update question details' : 'Add a question from your practice materials' }}</p>
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

        <!-- Subject (Collection) -->
        <n-form-item label="Subject" path="collection_id">
          <n-select v-model:value="model.collection_id" :options="collectionOptions" placeholder="Select subject" />
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

        <!-- Tags -->
        <n-form-item label="Tags (Optional)">
          <n-select
            v-model:value="model.tags"
            :options="tagOptions"
            filterable
            tag
            multiple
            :loading="loadingTags"
            placeholder="Add tags like 'fractions', 'patterns'..."
            :max-tag-count="5"
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
            {{ isEditMode ? 'Update Question' : 'Upload Question' }}
          </n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>
