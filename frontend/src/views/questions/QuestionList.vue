<template>
  <div class="container py-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <h1 class="text-3xl font-bold text-gray-900">Question Bank</h1>
      <n-space>
        <n-button @click="handleRefresh" :loading="questionStore.loading">
          <template #icon>
            <n-icon><RefreshIcon /></n-icon>
          </template>
          Refresh
        </n-button>
        <n-button type="primary" @click="router.push('/questions/upload')">
          Upload Question
        </n-button>
      </n-space>
    </div>

    <!-- Filters -->
    <QuestionFilters 
      v-model:filters="filters" 
      @update:filters="handleFilterChange" 
    />

    <!-- Loading State -->
    <LoadingSpinner 
      v-if="questionStore.loading && !questionStore.questions.length" 
      text="Loading questions..." 
      class="my-12"
    />

    <!-- Error State -->
    <div v-else-if="questionStore.error" class="bg-red-50 border-l-4 border-error p-4 mb-6">
      <p class="text-sm text-error">{{ questionStore.error }}</p>
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else-if="questionStore.questions.length === 0"
      icon="📚"
      title="No questions found"
      description="Get started by uploading your first question."
      action-text="Upload Question"
      action-to="/questions/upload"
    />

    <!-- Question Grid -->
    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <QuestionCard
          v-for="question in questionStore.questions"
          :key="question.id"
          :question="question"
          @click="handleQuestionClick"
        />
      </div>
      
      <!-- Pagination -->
      <div class="flex justify-center">
        <n-pagination
          v-model:page="questionStore.pagination.page"
          :page-count="questionStore.pagination.pages"
          @update:page="changePage"
          size="large"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuestionStore } from '../../stores/question'
import { NButton, NSpace, NIcon, NPagination } from 'naive-ui'
import { RefreshOutline as RefreshIcon } from '@vicons/ionicons5'
import QuestionFilters from '../../components/QuestionFilters.vue'
import QuestionCard from '../../components/QuestionCard.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'

const router = useRouter()
const questionStore = useQuestionStore()

const filters = ref({
  subject: null,
  difficulty: null,
  status: null,
  sort_by: 'created_at',
  sort_direction: 'desc'
})

onMounted(() => {
  // Initial fetch
  handleRefresh()
})

const handleRefresh = () => {
  questionStore.fetchQuestions({
    page: 1,
    ...filters.value
  })
}

const handleFilterChange = () => {
  questionStore.fetchQuestions({
    page: 1,
    ...filters.value
  })
}

const changePage = (page) => {
  questionStore.fetchQuestions({
    page,
    ...filters.value
  })
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleQuestionClick = (question) => {
  router.push(`/questions/${question.id}`)
}
</script>
