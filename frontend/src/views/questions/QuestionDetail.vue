<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuestionStore } from '../../stores/question'
import { useAuthStore } from '../../stores/auth'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import { NCard, NSpace, NTag, NButton, NCarousel, NEmpty, useMessage } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const questionStore = useQuestionStore()
const authStore = useAuthStore()
const message = useMessage()

// Watch route param to reload when ID changes
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      await questionStore.getQuestion(newId)
    }
  },
  { immediate: true }
)

const question = computed(() => questionStore.currentQuestion)

const difficultyStars = computed(() => {
  if (!question.value) return ''
  return '⭐'.repeat(question.value.difficulty || 3)
})

const statusColor = computed(() => {
  const status = question.value?.status
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
  const status = question.value?.status
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
  return question.value?.author_id === authStore.user?.id
})

function handleBack() {
  router.push('/questions')
}

function handleEdit() {
  message.info('Edit functionality coming in Week 5')
  // router.push(`/questions/${questionId}/edit`)
}

async function handleDelete() {
  if (confirm('Are you sure you want to delete this question?')) {
    try {
      await questionStore.deleteQuestion(route.params.id)
      message.success('Question deleted successfully')
      router.push('/questions')
    } catch (error) {
      message.error('Failed to delete question')
    }
  }
}
</script>

<template>
  <div class="container max-w-4xl mx-auto py-6">
    <!-- Loading State -->
    <LoadingSpinner v-if="questionStore.loading && !question" text="Loading question..." class="my-12" />

    <!-- Error State -->
    <div v-else-if="questionStore.error" class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
      <p class="text-sm text-red-700">{{ questionStore.error }}</p>
      <n-button @click="handleBack" class="mt-4">Back to Questions</n-button>
    </div>

    <!-- Question Content -->
    <template v-else-if="question">
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
          {{ question.title || `Question #${question.id}` }}
        </h1>
        
        <n-space>
          <n-tag :type="statusColor" data-testid="status-tag">{{ statusLabel }}</n-tag>
          <n-tag data-testid="subject-tag">{{ question.subject }}</n-tag>
          <n-tag data-testid="difficulty-tag">{{ difficultyStars }}</n-tag>
        </n-space>
      </div>

      <!-- Images -->
      <n-card title="Question Images" class="mb-6">
        <n-carousel
          v-if="question.images && question.images.length > 0"
          show-arrow
          draggable
        >
          <img
            v-for="(image, index) in question.images"
            :key="index"
            :src="image.url"
            class="w-full h-auto object-contain max-h-96"
            :alt="`Question image ${index + 1}`"
          />
        </n-carousel>
        <n-empty v-else description="No images available" />
      </n-card>

      <!-- Description -->
      <n-card v-if="question.content_text" title="Description" class="mb-6">
        <p class="whitespace-pre-wrap">{{ question.content_text }}</p>
      </n-card>

      <!-- Metadata -->
      <n-card title="Question Information" class="mb-6">
        <div class="space-y-2">
          <div><strong>Subject:</strong> {{ question.subject }}</div>
          <div><strong>Difficulty:</strong> {{ difficultyStars }} ({{ question.difficulty }}/5)</div>
          <div><strong>Status:</strong> {{ statusLabel }}</div>
          <div><strong>Created:</strong> {{ new Date(question.created_at).toLocaleDateString() }}</div>
          <div v-if="question.updated_at !== question.created_at">
            <strong>Updated:</strong> {{ new Date(question.updated_at).toLocaleDateString() }}
          </div>
        </div>
      </n-card>

      <!-- Answer History Placeholder -->
      <n-card title="Answer History">
        <n-empty description="Answer tracking coming in Week 5" />
      </n-card>
    </template>
  </div>
</template>

<style scoped>
.container {
  max-width: 1024px;
}
</style>
