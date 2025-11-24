<template>
  <div class="container py-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Question Bank</h1>
      <router-link to="/questions/upload" class="btn btn-primary">
        Upload Question
      </router-link>
    </div>

    <!-- Filters - 使用QuestionFilters组件 -->
    <QuestionFilters 
      v-model:filters="filters" 
      @update:filters="handleFilterChange" 
    />

    <!-- Loading State - 使用LoadingSpinner -->
    <LoadingSpinner 
      v-if="questionStore.loading" 
      text="Loading questions..." 
      class="my-12"
    />

    <!-- Error State -->
    <div v-else-if="questionStore.error" class="card bg-red-50 border-l-4 border-error mb-6">
      <p class="text-sm text-error">{{ questionStore.error }}</p>
    </div>

    <!-- Empty State - 使用EmptyState -->
    <EmptyState
      v-else-if="questionStore.questions.length === 0"
      icon="📚"
      title="No questions found"
      description="Get started by uploading your first question."
      action-text="Upload Question"
      action-to="/questions/upload"
    />


    <!-- Question Grid - 响应式网格 -->
    <div v-else class="question-grid">
      <QuestionCard
        v-for="question in questionStore.questions"
        :key="question.id"
        :question="question"
        @click="() => {/* TODO: Week 4添加详情页导航 */}"
      />
    </div>
    
    <!-- Pagination -->
    <div v-if="questionStore.pagination.pages > 1" class="mt-6 flex justify-center">
      <nav class="flex gap-2" aria-label="Pagination">
        <button
          @click="changePage(questionStore.pagination.page - 1)"
          :disabled="questionStore.pagination.page === 1"
          class="btn btn-secondary"
          :class="{ 'opacity-50 cursor-not-allowed': questionStore.pagination.page === 1 }"
        >
          Previous
        </button>
        <span class="flex items-center px-4 text-sm text-gray-700">
          Page {{ questionStore.pagination.page }} of {{ questionStore.pagination.pages }}
        </span>
        <button
          @click="changePage(questionStore.pagination.page + 1)"
          :disabled="questionStore.pagination.page === questionStore.pagination.pages"
          class="btn btn-secondary"
          :class="{ 'opacity-50 cursor-not-allowed': questionStore.pagination.page === questionStore.pagination.pages }"
        >
          Next
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useQuestionStore } from '@/stores/question'
import QuestionFilters from '@/components/QuestionFilters.vue'
import QuestionCard from '@/components/QuestionCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'

const questionStore = useQuestionStore()

const filters = ref({
  subject: null,
  difficulty: null,
  status: null,
  sort_by: 'created_at',
  sort_direction: 'desc'
})

onMounted(() => {
  questionStore.fetchQuestions()
})

const handleFilterChange = () => {
  questionStore.fetchQuestions({
    page: 1,
    ...filters.value
  })
}

const changePage = (page) => {
  if (page >= 1 && page <= questionStore.pagination.pages) {
    questionStore.fetchQuestions({
      page,
      ...filters.value
    })
  }
}
</script>
