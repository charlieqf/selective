<script setup>
import { ref, watch } from 'vue'
import uploadApi from '@/api/upload'

const props = defineProps({
  maxImages: { type: Number, default: 5 },
  maxSize: { type: Number, default: 5 * 1024 * 1024 }, // 5MB
  modelValue: { type: Array, default: () => [] }, // Array of { url, public_id }
})

const emit = defineEmits(['update:modelValue', 'error', 'update:uploading'])

const uploading = ref(false)
const dragActive = ref(false)

// Handle file selection
const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  await processFile(file)
  // Reset input
  event.target.value = ''
}

// Handle drag and drop
const handleDrop = async (event) => {
  event.preventDefault()
  dragActive.value = false
  
  const file = event.dataTransfer.files[0]
  if (!file) return
  await processFile(file)
}

const processFile = async (file) => {
  // Validation
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    emit('error', 'Only JPG, PNG and WEBP images are allowed.')
    return
  }
  
  if (file.size > props.maxSize) {
    emit('error', `File size must be less than ${Math.round(props.maxSize / 1024 / 1024)}MB.`)
    return
  }
  
  if (props.modelValue.length >= props.maxImages) {
    emit('error', `Maximum ${props.maxImages} images allowed.`)
    return
  }
  
  // Defensive copy
  const currentImages = [...props.modelValue]
  
  // Upload
  uploading.value = true
  emit('update:uploading', true)
  try {
    const response = await uploadApi.uploadImage(file)
    const newImages = [...currentImages, {
      url: response.data.url,
      public_id: response.data.public_id
    }]
    emit('update:modelValue', newImages)
  } catch (error) {
    console.error('Upload failed:', error)
    emit('error', 'Failed to upload image. Please try again.')
  } finally {
    uploading.value = false
    emit('update:uploading', false)
  }
}

const removeImage = async (index) => {
  const image = props.modelValue[index]
  if (!image) return
  
  if (confirm('Are you sure you want to remove this image?')) {
    try {
      await uploadApi.deleteImage(image.public_id)
      const newImages = [...props.modelValue]
      newImages.splice(index, 1)
      emit('update:modelValue', newImages)
    } catch (error) {
      console.error('Delete failed:', error)
      emit('error', 'Failed to delete image from server.')
    }
  }
}
</script>

<template>
  <div>
    <label class="block text-sm font-medium text-gray-700">Question Images</label>
    
    <div 
      class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-md transition-colors"
      :class="[
        dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300',
        uploading ? 'opacity-50 cursor-wait' : ''
      ]"
      @dragenter.prevent="dragActive = true"
      @dragleave.prevent="dragActive = false"
      @dragover.prevent
      @drop="handleDrop"
    >
      <div class="space-y-1 text-center w-full">
        <!-- Empty State -->
        <div v-if="modelValue.length === 0">
          <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div class="flex text-sm text-gray-600 justify-center">
            <label class="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
              <span>Upload a file</span>
              <input type="file" class="sr-only" @change="handleFileUpload" accept="image/png, image/jpeg, image/webp" :disabled="uploading">
            </label>
            <p class="pl-1">or drag and drop</p>
          </div>
          <p class="text-xs text-gray-500">PNG, JPG, WEBP up to {{ Math.round(maxSize / 1024 / 1024) }}MB</p>
        </div>
        
        <!-- Image Preview Grid -->
        <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <div v-for="(img, index) in modelValue" :key="img.public_id" class="relative group">
            <img :src="img.url" class="h-24 w-full object-cover rounded-md shadow-sm" />
            <button 
              type="button"
              @click="removeImage(index)"
              class="absolute top-0 right-0 -mt-2 -mr-2 bg-red-500 text-white rounded-full p-1 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 focus:outline-none"
              :disabled="uploading"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- Add More Button -->
          <div v-if="modelValue.length < maxImages" class="flex items-center justify-center h-24 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
            <label class="cursor-pointer w-full h-full flex items-center justify-center">
              <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <input type="file" class="sr-only" @change="handleFileUpload" accept="image/png, image/jpeg, image/webp" :disabled="uploading">
            </label>
          </div>
        </div>
      </div>
    </div>
    
    <p v-if="uploading" class="mt-2 text-sm text-primary-600 animate-pulse">Uploading...</p>
  </div>
</template>
