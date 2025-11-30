<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useItemStore } from '../../stores/items'
import { useAuthStore } from '../../stores/auth'
import itemsApi from '@/api/items'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import AnswerSection from '../../components/AnswerSection.vue'
import { NCard, NSpace, NTag, NButton, NCarousel, NEmpty, useMessage } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const itemStore = useItemStore()
const authStore = useAuthStore()
const message = useMessage()
const answerHistory = ref([])
const loadingHistory = ref(false)

// Watch route param to reload when ID changes
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
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
  return '⭐'.repeat(item.value.difficulty || 3)
})

const statusColor = computed(() => {
  const status = item.value?.status
  if (!status) return 'default'
  const colorMap = {
    'UNANSWERED': 'default',
    'ANSWERED': 'info',
    'NEED_REVIEW': 'warning',
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
    'NEED_REVIEW': 'Need Review',
    'MASTERED': 'Mastered'
  }
  return labelMap[status] || status
})

const canEdit = computed(() => {
  return item.value?.author_id === authStore.user?.id
})

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
          <n-button @click="handleBack" data-testid="back-button">← Back to Questions</n-button>
          <n-space v-if="canEdit">
            <n-button @click="handleEdit">Edit</n-button>
            <n-button type="error" @click="handleDelete">Delete</n-button>
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
        <n-carousel
          v-if="item.images && item.images.length > 0"
          show-arrow
          draggable
        >
          <img
            v-for="(image, index) in item.images"
            :key="index"
            :src="image.url"
            class="w-full h-auto object-contain max-h-96"
            :alt="`Question image ${index + 1}`"
          />
        </n-carousel>
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
              <span class="text-2xl">{{ answer.is_correct ? '✅' : '❌' }}</span>
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
</template>

<style scoped>
.container {
  max-width: 1024px;
}
</style>
