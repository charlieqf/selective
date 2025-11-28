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

// Validate before upload
function beforeUpload(data) {
  const file = data.file.file
  
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    message.error(`Invalid file type. Only JPG, PNG, and WEBP are allowed.`)
    return false
  }
  
  // Check file size
  if (file.size > props.maxSize) {
    message.error(`File too large. Maximum size is ${Math.round(props.maxSize / 1024 / 1024)}MB.`)
    return false
  }
  
  return true
}

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
      :before-upload="beforeUpload"
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
