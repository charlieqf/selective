<script setup>
import { ref, watch, computed } from 'vue'
import { NUpload, NButton, NIcon, useMessage, NModal, NSpace, NCard } from 'naive-ui'
import { Add, Camera, Image as ImageIcon, Refresh, ArrowUndo, ArrowRedo } from '@vicons/ionicons5'
import uploadApi from '../api/upload'
import imageCompression from 'browser-image-compression'

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
const cameraInput = ref(null)
const showPreview = ref(false)
const previewUrl = ref('')
const previewFile = ref(null)
const previewRotation = ref(0)

// 使用WeakMap追踪File对象→已上传数据的映射(解决文件名重复问题)
const fileToUploadedMap = new WeakMap()

const isMobile = computed(() => {
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
})

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
  return validateFile(file)
}

function validateFile(file) {
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    message.error(`Invalid file type. Only JPG, PNG, and WEBP are allowed.`)
    return false
  }
  
  // Check file size (pre-compression check)
  // We allow slightly larger files if we are going to compress them, but strict check for now
  if (file.size > props.maxSize * 2) { // Allow 2x size before compression
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
    // Compress image
    const compressedFile = await compressImage(file.file)
    
    // 上传到Cloudinary
    const { data } = await uploadApi.uploadImage(compressedFile)
    
    // 使用WeakMap保存File对象→上传数据的映射
        // Track uploaded data
    fileToUploadedMap.set(file.file, {
      url: data.url,
      public_id: data.public_id
    })
    // Sync Naive UI entry so new uploads append instead of overwrite
    const idx = fileList.value.findIndex(f => f.id === file.id)
    if (idx !== -1) {
      fileList.value[idx] = {
        ...fileList.value[idx],
        status: 'finished',
        url: data.url
      }
    }
    
    // Emit updated modelValue
    updateModelValue()
    
    onFinish()
  } catch (err) {
    console.error('Upload error:', err)
    message.error(`Failed to upload ${file.name}`)
    onError()
  } finally {
    uploading.value = false
  }
}

async function compressImage(file) {
  const options = {
    maxSizeMB: 1, // Compress to 1MB
    maxWidthOrHeight: 1920,
    useWebWorker: false, // Disable WebWorker for better compatibility with Playwright
    fileType: file.type
  }
  
  try {
    // Add timeout to prevent hanging
    const compressionPromise = imageCompression(file, options)
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Compression timeout')), 10000)
    )
    
    return await Promise.race([compressionPromise, timeoutPromise])
  } catch (error) {
    console.warn('Compression failed, using original:', error)
    return file
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
        // Preserve all original fields (like rotation) + url/public_id
        return { ...data, url: data.url, public_id: data.public_id }
      }
      return null
    })
    .filter(Boolean)
  
  // 记录我们emit的值,避免watch循环
  lastEmittedValue = uploaded
  emit('update:modelValue', uploaded)
}

// Camera Handling
function handleCameraClick() {
  cameraInput.value.click()
}

async function handleCameraCapture(event) {
  const file = event.target.files[0]
  if (!file) return
  
  if (!validateFile(file)) {
    event.target.value = '' // Reset input
    return
  }
  
  // Show preview
  previewFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  previewRotation.value = 0
  showPreview.value = true
  
  // Reset input so same file can be selected again if needed
  event.target.value = ''
}

function rotatePreview(angle) {
  previewRotation.value = (previewRotation.value + angle + 360) % 360
}

async function confirmUpload() {
  if (!previewFile.value) return
  
  showPreview.value = false
  uploading.value = true
  
  try {
    let fileToUpload = previewFile.value
    
    // If rotated, apply rotation to file (using canvas)
    if (previewRotation.value !== 0) {
      fileToUpload = await applyRotation(fileToUpload, previewRotation.value)
    }
    
    // Compress
    const compressedFile = await compressImage(fileToUpload)
    
    // Create a mock UploadFile object for Naive UI
    const naiveFile = {
      id: `camera-${Date.now()}`,
      name: `capture-${Date.now()}.jpg`,
      status: 'uploading',
      file: compressedFile
    }
    
    fileList.value.push(naiveFile)
    
    // Upload
    const { data } = await uploadApi.uploadImage(compressedFile)
    
    // Update Naive UI file status
    const index = fileList.value.findIndex(f => f.id === naiveFile.id)
    if (index !== -1) {
      fileList.value[index].status = 'finished'
      fileList.value[index].url = data.url
    }
    
    // Map data
    fileToUploadedMap.set(compressedFile, {
      url: data.url,
      public_id: data.public_id
    })
    
    updateModelValue()
    
  } catch (err) {
    console.error('Camera upload failed:', err)
    message.error('Failed to upload captured image')
    // Remove from list if failed
    fileList.value = fileList.value.filter(f => f.file !== previewFile.value)
  } finally {
    uploading.value = false
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
    previewFile.value = null
  }
}

async function applyRotation(file, degrees) {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      if (degrees === 90 || degrees === 270) {
        canvas.width = img.height
        canvas.height = img.width
      } else {
        canvas.width = img.width
        canvas.height = img.height
      }
      
      ctx.translate(canvas.width / 2, canvas.height / 2)
      ctx.rotate(degrees * Math.PI / 180)
      ctx.drawImage(img, -img.width / 2, -img.height / 2)
      
      canvas.toBlob((blob) => {
        resolve(new File([blob], file.name, { type: file.type }))
      }, file.type)
    }
    img.src = URL.createObjectURL(file)
  })
}
</script>

<template>
  <div>
    <!-- Hidden Camera Input -->
    <input 
      type="file" 
      accept="image/*" 
      capture="environment"
      ref="cameraInput"
      style="display: none"
      @change="handleCameraCapture"
    />

    <!-- Preview Modal -->
    <n-modal v-model:show="showPreview" :mask-closable="false">
      <n-card style="width: 90vw; max-width: 600px;" title="Preview & Rotate" :bordered="false" size="huge" role="dialog" aria-modal="true">
        <div class="flex flex-col items-center gap-4">
          <div class="relative w-full h-64 bg-black flex items-center justify-center overflow-hidden rounded">
            <img 
              :src="previewUrl" 
              :style="{ transform: `rotate(${previewRotation}deg)`, transition: 'transform 0.3s' }"
              class="max-w-full max-h-full object-contain" 
            />
          </div>
          
          <n-space justify="center">
            <n-button circle @click="rotatePreview(-90)">
              <template #icon><n-icon><ArrowUndo /></n-icon></template>
            </n-button>
            <n-button circle @click="rotatePreview(90)">
              <template #icon><n-icon><ArrowRedo /></n-icon></template>
            </n-button>
          </n-space>
          
          <n-space justify="end" class="w-full mt-4">
            <n-button @click="showPreview = false">Cancel</n-button>
            <n-button type="primary" @click="confirmUpload" :loading="uploading">Upload</n-button>
          </n-space>
        </div>
      </n-card>
    </n-modal>

    <!-- Upload Area -->
    <div class="flex flex-col gap-4">
      <div v-if="isMobile" class="flex gap-2">
        <n-button type="primary" class="flex-1" @click="handleCameraClick" :disabled="fileList.length >= maxImages">
          <template #icon><n-icon><Camera /></n-icon></template>
          Take Photo
        </n-button>
      </div>

      <n-upload
        v-model:file-list="fileList"
        :max="maxImages"
        list-type="image-card"
        accept="image/jpeg,image/png,image/webp"
        :custom-request="customRequest"
        :before-upload="beforeUpload"
        @remove="handleRemove"
      >
        <div class="flex flex-col justify-center items-center w-full h-full bg-gray-50 border border-dashed border-gray-300 rounded hover:bg-gray-100 transition-colors">
          <n-icon size="24" class="text-gray-400">
            <Add />
          </n-icon>
          <span class="text-xs text-gray-500 mt-1">Select File</span>
        </div>
      </n-upload>
    </div>
    
    <p class="text-sm text-gray-500 mt-2">
      Accepted: JPG, PNG, WEBP. Max size: {{ Math.round(maxSize / 1024 / 1024) }}MB per image.
    </p>
  </div>
</template>

