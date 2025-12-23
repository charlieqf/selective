<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useItemStore } from '../../stores/items'
import { useAuthStore } from '../../stores/auth'
import itemsApi from '@/api/items'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import AnswerSection from '../../components/AnswerSection.vue'
import ImageLightbox from '../../components/ImageLightbox.vue'
import { NCard, NSpace, NTag, NButton, NCarousel, NEmpty, NIcon, useMessage } from 'naive-ui'
import { ArrowUndo, ArrowRedo, ArrowBack, Flag, Create, Trash, CheckmarkCircle, CloseCircle } from '@vicons/ionicons5'
import { getDisplayUrl, getRotatedUrl, getImageStyle } from '../../utils/image'

const route = useRoute()
const router = useRouter()
const itemStore = useItemStore()
const authStore = useAuthStore()
const message = useMessage()
const answerHistory = ref([])
const loadingHistory = ref(false)
const rotating = ref(false)

// Carousel and Lightbox state
const showLightbox = ref(false)
const lightboxIndex = ref(0)
const currentIndex = ref(0)


// Watch route param to reload when ID changes
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      currentIndex.value = 0 // Reset index when question changes
      await itemStore.getItem(newId)
      fetchHistory(newId)
    }
  },
  { immediate: true }
)

async function fetchHistory(id) {
  loadingHistory.value = true
  try {
    const response = await itemsApi.getAnswerHistory(id)
    answerHistory.value = response.data
  } catch (error) {
    console.error('Failed to fetch history', error)
  } finally {
    loadingHistory.value = false
  }
}

const item = computed(() => itemStore.currentItem)

const difficultyStars = computed(() => {
  if (!item.value) return ''
  return '*'.repeat(item.value.difficulty || 3)
})

const statusColor = computed(() => {
  const status = item.value?.status
  if (!status) return 'default'
  const colorMap = {
    'UNANSWERED': 'default',
    'ANSWERED': 'info',
    'MASTERED': 'success'
  }
  return colorMap[status] || 'default'
})

const statusLabel = computed(() => {
  const status = item.value?.status
  if (!status) return 'Unknown'
  const labelMap = {
    'UNANSWERED': 'Unanswered',
    'ANSWERED': 'Answered',
    'MASTERED': 'Mastered'
  }
  return labelMap[status] || status
})

const canEdit = computed(() => {
  return item.value?.author_id === authStore.user?.id
})

// Computed array of image data for lightbox (URL + Rotation)
const lightboxImages = computed(() => {
  if (!item.value?.images) return []
  return item.value.images.map(image => ({
    url: getDisplayUrl(image, item.value.updated_at),
    rotation: Number(typeof image === 'string' ? 0 : image.rotation) || 0
  }))
})

function openLightbox(index) {
  lightboxIndex.value = index
  showLightbox.value = true
}

function handleBack() {
  router.push('/questions')
}

function handleEdit() {
  router.push(`/questions/${route.params.id}/edit`)
}

async function handleDelete() {
  if (confirm('Are you sure you want to delete this question?')) {
    try {
      await itemStore.deleteItem(route.params.id)
      message.success('Question deleted successfully')
      router.push('/questions')
    } catch (error) {
      message.error('Failed to delete question')
    }
  }
}

function handleAnswerSubmitted(result) {
  // Refresh item data to update status
  itemStore.getItem(route.params.id)
  // Refresh history
  fetchHistory(route.params.id)
}


async function rotateImage(index, angle) {
  if (rotating.value) return
  
  const currentRotation = Number(item.value.images[index].rotation) || 0
  const newRotation = (currentRotation + angle + 360) % 360
  
  rotating.value = true
  try {
    await itemStore.rotateImage(item.value.id, index, newRotation)
    message.success('Image rotated')
  } catch (error) {
    console.error('Rotation failed:', error)
    message.error('Failed to save rotation')
  } finally {
    rotating.value = false
  }
}

async function toggleNeedReview() {
  const newNeedsReview = !item.value.needs_review
  
  try {
    const response = await itemsApi.toggleReview(item.value.id, newNeedsReview)
    itemStore.currentItem = { 
      ...item.value, 
      needs_review: response.data.needs_review,
      status: response.data.status 
    }
    message.success(newNeedsReview ? 'Marked for review' : 'Review mark removed')
  } catch (error) {
    message.error('Operation failed')
  }
}
</script>

<template>
  <div class="container max-w-4xl mx-auto py-6">
    <!-- Loading State -->
    <LoadingSpinner v-if="itemStore.loading && !item" text="Loading question..." class="my-12" />

    <!-- Error State -->
    <div v-else-if="itemStore.error" class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
      <p class="text-sm text-red-700">{{ itemStore.error }}</p>
      <n-button @click="handleBack" class="mt-4">Back to Questions</n-button>
    </div>

    <!-- Question Content -->
    <template v-else-if="item">
      <!-- Header -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <n-button @click="handleBack" data-testid="back-button" aria-label="Back to Questions">
            <template #icon>
              <n-icon><ArrowBack /></n-icon>
            </template>
            <span class="hidden md:inline">Back to Questions</span>
          </n-button>
          
          <n-space v-if="canEdit" class="flex-nowrap">
            <n-button 
              :type="item.needs_review ? 'warning' : 'default'"
              @click="toggleNeedReview"
              data-testid="toggle-review-btn"
              :title="item.needs_review ? 'Remove Review Mark' : 'Mark for Review'"
            >
              <template #icon>
                <n-icon><Flag /></n-icon>
              </template>
              <span class="hidden md:inline">{{ item.needs_review ? 'Remove Review Mark' : 'Mark for Review' }}</span>
            </n-button>
            <n-button @click="handleEdit" title="Edit">
              <template #icon>
                <n-icon><Create /></n-icon>
              </template>
              <span class="hidden md:inline">Edit</span>
            </n-button>
            <n-button type="error" @click="handleDelete" title="Delete">
              <template #icon>
                <n-icon><Trash /></n-icon>
              </template>
              <span class="hidden md:inline">Delete</span>
            </n-button>
          </n-space>
        </div>
        
        <h1 class="text-3xl font-bold mb-2" data-testid="question-title">
          {{ item.title || `Question #${item.id}` }}
        </h1>
        
        <n-space>
          <n-tag :type="statusColor" data-testid="status-tag">{{ statusLabel }}</n-tag>
          <n-tag data-testid="subject-tag">{{ item.subject }}</n-tag>
          <n-tag data-testid="difficulty-tag">{{ difficultyStars }}</n-tag>
        </n-space>
      </div>

      <!-- Images -->
      <n-card title="Question Images" class="mb-6">
        <div v-if="item.images && item.images.length > 0" class="flex flex-col items-center">
          <n-carousel
            v-model:current-index="currentIndex"
            show-arrow
            draggable
            :loop="false"
            :arrow-style="{ color: '#0f172a', backgroundColor: '#e2e8f0', boxShadow: '0 0 0 1px #94a3b8', opacity: 1 }"
            arrow-placement="outer"
            class="bg-gray-50 rounded-lg"
          >
            <div
              v-for="(image, index) in item.images"
              :key="index"
              class="relative flex flex-col items-center justify-center p-4"
            >
              <img
                :key="`${image.public_id || index}-${image.rotation || 0}`"
                :src="getDisplayUrl(image, item.updated_at)"
                :style="getImageStyle(image)"
                class="w-full h-auto object-contain max-h-96 cursor-pointer hover:opacity-90"
                :alt="`Question image ${index + 1}`"
                @click="openLightbox(index)"
                data-testid="question-image"
              />
              <div class="mt-2 text-sm text-gray-600" data-testid="image-counter">
                Image {{ index + 1 }} of {{ item.images.length }}
              </div>
            </div>
          </n-carousel>

          <!-- Rotation Controls (Outside Carousel for stability) -->
          <div v-if="canEdit" class="mt-4 flex flex-col items-center gap-2">
            <div class="flex gap-4">
              <n-button 
                secondary 
                round
                @click="rotateImage(currentIndex, -90)" 
                :disabled="rotating" 
                data-testid="rotate-left-btn"
              >
                <template #icon><n-icon><ArrowUndo /></n-icon></template>
                Rotate Left
              </n-button>
              <n-button 
                secondary 
                round
                @click="rotateImage(currentIndex, 90)" 
                :disabled="rotating" 
                data-testid="rotate-right-btn"
              >
                <template #icon><n-icon><ArrowRedo /></n-icon></template>
                Rotate Right
              </n-button>
            </div>
            <div class="text-xs text-gray-400">
              Current Rotation: {{ item.images[currentIndex]?.rotation || 0 }}°
            </div>
          </div>
        </div>
        <n-empty v-else description="No images available" />
      </n-card>

      <!-- Description -->
      <n-card v-if="item.content_text" title="Description" class="mb-6">
        <p class="whitespace-pre-wrap">{{ item.content_text }}</p>
      </n-card>

      <!-- Metadata -->
      <n-card title="Question Information" class="mb-6">
        <div class="space-y-2">
          <div><strong>Subject:</strong> {{ item.subject }}</div>
          <div><strong>Difficulty:</strong> {{ difficultyStars }} ({{ item.difficulty }}/5)</div>
          <div><strong>Status:</strong> {{ statusLabel }}</div>
          <div><strong>Created:</strong> {{ new Date(item.created_at).toLocaleDateString() }}</div>
          <div v-if="item.updated_at !== item.created_at">
            <strong>Updated:</strong> {{ new Date(item.updated_at).toLocaleDateString() }}
          </div>
        </div>
      </n-card>

      <!-- Answer Section -->
      <AnswerSection 
        v-if="item.status !== 'MASTERED'"
        :key="item.id"
        :item-id="item.id"
        @answer-submitted="handleAnswerSubmitted"
      />

      <!-- Answer History -->
      <n-card title="Answer History">
        <div v-if="loadingHistory" class="py-4 text-center text-gray-500">Loading history...</div>
        <div v-else-if="answerHistory.length > 0" class="space-y-4">
          <div 
            v-for="answer in answerHistory" 
            :key="answer.id"
            class="flex items-center justify-between p-3 rounded bg-gray-50 border border-gray-100"
          >
            <div class="flex items-center space-x-3">
              <span class="text-2xl">
                <n-icon v-if="answer.is_correct" color="#10b981"><CheckmarkCircle /></n-icon>
                <n-icon v-else color="#ef4444"><CloseCircle /></n-icon>
              </span>
              <div>
                <div class="font-medium">{{ answer.is_correct ? 'Correct' : 'Incorrect' }}</div>
                <div class="text-xs text-gray-500">{{ new Date(answer.created_at).toLocaleString() }}</div>
              </div>
            </div>
            <div class="text-sm text-gray-600">
              Duration: {{ Math.floor(answer.duration_seconds / 60) }}:{{ (answer.duration_seconds % 60).toString().padStart(2, '0') }}
            </div>
          </div>
        </div>
        <n-empty v-else description="No attempts yet" />
      </n-card>
    </template>
  </div>

  <!-- Image Lightbox for fullscreen viewing -->
  <ImageLightbox
    :images="lightboxImages"
    :initial-index="lightboxIndex"
    :show="showLightbox"
    @close="showLightbox = false"
  />
</template>

<style scoped>
  /* Make carousel arrows high-contrast and always visible */
  :deep(.n-carousel__arrow) {
    opacity: 1;
    background-color: #e2e8f0;
    color: #0f172a;
    box-shadow: 0 0 0 1px #94a3b8;
  }
  /* Increase arrow icon size */
  :deep(.n-carousel__arrow .n-icon) {
    font-size: 20px;
  }
  /* Ensure outer placement arrows sit away from content */
  :deep(.n-carousel__arrow--left) {
    left: -36px;
  }
  :deep(.n-carousel__arrow--right) {
    right: -36px;
  }
</style>

<style scoped>
.container {
  max-width: 1024px;
}
</style>
