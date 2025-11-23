<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Question Bank</h1>
      <router-link
        to="/questions/upload"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Upload Question
      </router-link>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6 mb-6">
      <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <div class="sm:col-span-2">
          <label for="subject" class="block text-sm font-medium text-gray-700">Subject</label>
          <select
            id="subject"
            v-model="filters.subject"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            @change="handleFilterChange"
          >
            <option value="">All Subjects</option>
            <option value="READING">Reading</option>
            <option value="WRITING">Writing</option>
            <option value="MATHS">Maths</option>
            <option value="THINKING_SKILLS">Thinking Skills</option>
          </select>
        </div>

        <div class="sm:col-span-2">
          <label for="difficulty" class="block text-sm font-medium text-gray-700">Difficulty</label>
          <select
            id="difficulty"
            v-model="filters.difficulty"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            @change="handleFilterChange"
          >
            <option value="">All Levels</option>
            <option value="1">Level 1</option>
            <option value="2">Level 2</option>
            <option value="3">Level 3</option>
            <option value="4">Level 4</option>
            <option value="5">Level 5</option>
          </select>
        </div>
        
        <div class="sm:col-span-2">
          <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
          <select
            id="status"
            v-model="filters.status"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
            @change="handleFilterChange"
          >
            <option value="">All Statuses</option>
            <option value="UNANSWERED">Unanswered</option>
            <option value="ANSWERED">Answered</option>
            <option value="MASTERED">Mastered</option>
            <option value="NEED_REVIEW">Need Review</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="questionStore.loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent"></div>
      <p class="mt-2 text-gray-500">Loading questions...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="questionStore.error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <!-- Heroicon name: solid/exclamation -->
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ questionStore.error }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="questionStore.questions.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No questions found</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating a new question.</p>
      <div class="mt-6">
        <router-link
          to="/questions/upload"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Upload Question
        </router-link>
      </div>
    </div>

    <!-- Question Grid -->
    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="question in questionStore.questions" :key="question.id" class="bg-white overflow-hidden shadow rounded-lg flex flex-col">
        <div class="relative h-48 bg-gray-200">
          <img 
            v-if="question.images && question.images.length > 0" 
            :src="question.images[0].url" 
            :alt="question.title || 'Question Image'" 
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            No Image
          </div>
          <div class="absolute top-2 right-2">
            <span :class="[
              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
              getStatusColor(question.status)
            ]">
              {{ question.status }}
            </span>
          </div>
        </div>
        <div class="px-4 py-5 sm:p-6 flex-1">
          <div class="flex items-center justify-between mb-2">
            <span :class="[
              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
              getSubjectColor(question.subject)
            ]">
              {{ question.subject }}
            </span>
            <span class="text-sm text-gray-500">Level {{ question.difficulty }}</span>
          </div>
          <h3 class="text-lg font-medium text-gray-900 truncate" :title="question.title">
            {{ question.title || 'Untitled Question' }}
          </h3>
          <p class="mt-1 text-sm text-gray-500 line-clamp-3">
            {{ question.content_text || 'No description available.' }}
          </p>
        </div>
        <div class="bg-gray-50 px-4 py-4 sm:px-6 flex justify-between items-center">
          <div class="text-sm text-gray-500">
            {{ formatDate(question.created_at) }}
          </div>
          <div class="flex space-x-2">
             <!-- Actions could go here -->
          </div>
        </div>
      </div>
    </div>
    
    <!-- Pagination -->
    <div v-if="questionStore.pagination.pages > 1" class="mt-6 flex justify-center">
      <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
        <button
          @click="changePage(questionStore.pagination.page - 1)"
          :disabled="questionStore.pagination.page === 1"
          class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
        >
          Previous
        </button>
        <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
          Page {{ questionStore.pagination.page }} of {{ questionStore.pagination.pages }}
        </span>
        <button
          @click="changePage(questionStore.pagination.page + 1)"
          :disabled="questionStore.pagination.page === questionStore.pagination.pages"
          class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
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
import { format } from 'date-fns'

const questionStore = useQuestionStore()

const filters = reactive({
  subject: '',
  difficulty: '',
  status: ''
})

onMounted(() => {
  questionStore.fetchQuestions()
})

const handleFilterChange = () => {
  questionStore.fetchQuestions({
    page: 1,
    ...filters
  })
}

const changePage = (page) => {
  if (page >= 1 && page <= questionStore.pagination.pages) {
    questionStore.fetchQuestions({
      page,
      ...filters
    })
  }
}

const getSubjectColor = (subject) => {
  const colors = {
    'READING': 'bg-orange-100 text-orange-800',
    'WRITING': 'bg-purple-100 text-purple-800',
    'MATHS': 'bg-green-100 text-green-800',
    'THINKING_SKILLS': 'bg-indigo-100 text-indigo-800'
  }
  return colors[subject] || 'bg-gray-100 text-gray-800'
}

const getStatusColor = (status) => {
  const colors = {
    'UNANSWERED': 'bg-gray-100 text-gray-800',
    'ANSWERED': 'bg-blue-100 text-blue-800',
    'MASTERED': 'bg-green-100 text-green-800',
    'NEED_REVIEW': 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'MMM d, yyyy')
}
</script>
