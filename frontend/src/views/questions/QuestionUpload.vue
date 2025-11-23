<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="md:flex md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          Upload New Question
        </h2>
      </div>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Image Upload -->
          <div>
            <label class="block text-sm font-medium text-gray-700">Question Images</label>
            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md"
                 :class="{'border-red-300': errors.images}">
              <div class="space-y-1 text-center">
                <div v-if="uploadedImages.length === 0">
                  <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  <div class="flex text-sm text-gray-600 justify-center">
                    <label for="file-upload" class="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                      <span>Upload a file</span>
                      <input id="file-upload" name="file-upload" type="file" class="sr-only" @change="handleFileUpload" accept="image/png, image/jpeg, image/webp" :disabled="uploading">
                    </label>
                    <p class="pl-1">or drag and drop</p>
                  </div>
                  <p class="text-xs text-gray-500">PNG, JPG, WEBP up to 5MB</p>
                </div>
                
                <!-- Image Preview List -->
                <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3">
                  <div v-for="(img, index) in uploadedImages" :key="img.public_id" class="relative group">
                    <img :src="img.url" class="h-24 w-full object-cover rounded-md" />
                    <button 
                      type="button"
                      @click="removeImage(index)"
                      class="absolute top-0 right-0 -mt-2 -mr-2 bg-red-500 text-white rounded-full p-1 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  
                  <!-- Add more button -->
                  <div v-if="uploadedImages.length < 5" class="flex items-center justify-center h-24 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400">
                    <label for="file-upload-more" class="cursor-pointer w-full h-full flex items-center justify-center">
                      <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                      <input id="file-upload-more" type="file" class="sr-only" @change="handleFileUpload" accept="image/png, image/jpeg, image/webp" :disabled="uploading">
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <p v-if="uploading" class="mt-2 text-sm text-gray-500">Uploading...</p>
            <p v-if="errors.images" class="mt-2 text-sm text-red-600">{{ errors.images }}</p>
          </div>

          <!-- Subject -->
          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700">Subject</label>
            <select
              id="subject"
              v-model="form.subject"
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
              :class="{'border-red-300': errors.subject}"
            >
              <option value="" disabled>Select a subject</option>
              <option value="READING">Reading</option>
              <option value="WRITING">Writing</option>
              <option value="MATHS">Maths</option>
              <option value="THINKING_SKILLS">Thinking Skills</option>
            </select>
            <p v-if="errors.subject" class="mt-2 text-sm text-red-600">{{ errors.subject }}</p>
          </div>

          <!-- Difficulty -->
          <div>
            <label class="block text-sm font-medium text-gray-700">Difficulty (1-5)</label>
            <div class="mt-1 flex items-center space-x-4">
              <div v-for="level in 5" :key="level" class="flex items-center">
                <input
                  :id="`difficulty-${level}`"
                  name="difficulty"
                  type="radio"
                  :value="level"
                  v-model="form.difficulty"
                  class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300"
                >
                <label :for="`difficulty-${level}`" class="ml-2 block text-sm text-gray-700">
                  {{ level }}
                </label>
              </div>
            </div>
          </div>

          <!-- Title (Optional) -->
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700">Title (Optional)</label>
            <input
              type="text"
              id="title"
              v-model="form.title"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              placeholder="e.g. 2023 Practice Test Q5"
            >
          </div>

          <!-- Content Text (Optional) -->
          <div>
            <label for="content" class="block text-sm font-medium text-gray-700">Description / Notes</label>
            <textarea
              id="content"
              v-model="form.content_text"
              rows="3"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            ></textarea>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="handleCancel"
              class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="submitting || uploading"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {{ submitting ? 'Saving...' : 'Save Question' }}
            </button>
          </div>
          
          <div v-if="submitError" class="rounded-md bg-red-50 p-4 mt-4">
            <div class="flex">
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Submission failed</h3>
                <div class="mt-2 text-sm text-red-700">
                  <p>{{ submitError }}</p>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onBeforeUnmount } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { useQuestionStore } from '@/stores/question'
import uploadApi from '@/api/upload'

const router = useRouter()
const questionStore = useQuestionStore()

const form = reactive({
  subject: '',
  difficulty: 3,
  title: '',
  content_text: ''
})

const uploadedImages = ref([]) // Array of { url, public_id }
const uploading = ref(false)
const submitting = ref(false)
const submitError = ref(null)
const errors = reactive({})
const questionSaved = ref(false) // Track if question was successfully saved

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Basic validation
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    alert('Only JPG, PNG and WEBP images are allowed.')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    alert('File size must be less than 5MB.')
    return
  }
  
  if (uploadedImages.value.length >= 5) {
    alert('Maximum 5 images allowed.')
    return
  }
  
  uploading.value = true
  try {
    const response = await uploadApi.uploadImage(file)
    uploadedImages.value.push({
      url: response.data.url,
      public_id: response.data.public_id
    })
    // Clear error if any
    if (errors.images) delete errors.images
  } catch (error) {
    console.error('Upload failed:', error)
    alert('Failed to upload image. Please try again.')
  } finally {
    uploading.value = false
    // Reset input
    event.target.value = ''
  }
}

const removeImage = async (index) => {
  const image = uploadedImages.value[index]
  if (!image) return
  
  if (confirm('Are you sure you want to remove this image?')) {
    try {
      await uploadApi.deleteImage(image.public_id)
      uploadedImages.value.splice(index, 1)
    } catch (error) {
      console.error('Delete failed:', error)
      alert('Failed to delete image from server.')
    }
  }
}

const validate = () => {
  const newErrors = {}
  
  if (!form.subject) {
    newErrors.subject = 'Subject is required'
  }
  
  if (uploadedImages.value.length === 0 && !form.content_text) {
    newErrors.images = 'Please upload at least one image or provide a description'
  }
  
  Object.keys(errors).forEach(key => delete errors[key])
  Object.assign(errors, newErrors)
  
  return Object.keys(errors).length === 0
}

const cleanupImages = async () => {
  for (const img of uploadedImages.value) {
    try {
      await uploadApi.deleteImage(img.public_id)
    } catch (e) {
      console.error('Cleanup failed for image:', img.public_id, e)
    }
  }
}

const handleSubmit = async () => {
  if (!validate()) return
  
  submitting.value = true
  submitError.value = null
  
  try {
    await questionStore.createQuestion({
      ...form,
      images: uploadedImages.value
    })
    questionSaved.value = true
    router.push('/questions')
  } catch (error) {
    submitError.value = error.response?.data?.error || 'Failed to create question'
    // Cleanup images on submission failure
    await cleanupImages()
    uploadedImages.value = []
  } finally {
    submitting.value = false
  }
}

const handleCancel = async () => {
  if (uploadedImages.value.length > 0) {
    if (confirm('Discard unsaved changes? Uploaded images will be deleted.')) {
      await cleanupImages()
      router.back()
    }
  } else {
    router.back()
  }
}

// Cleanup on navigation away without saving
onBeforeRouteLeave((to, from, next) => {
  if (!questionSaved.value && uploadedImages.value.length > 0) {
    if (confirm('You have unsaved images. Discard them?')) {
      cleanupImages().then(() => next())
    } else {
      next(false)
    }
  } else {
    next()
  }
})

// Cleanup on component unmount (e.g., browser close)
onBeforeUnmount(() => {
  if (!questionSaved.value && uploadedImages.value.length > 0) {
    cleanupImages()
  }
})
</script>
