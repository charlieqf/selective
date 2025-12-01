<template>
  <div class="container py-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <h1 class="text-3xl font-bold text-gray-900">Question Bank</h1>
      <n-space>
        <n-button @click="handleRefresh" :loading="itemStore.loading">
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

    <!-- Active Tag Filters -->
    <div v-if="activeTags.length > 0" class="flex flex-wrap gap-2 mb-4">
      <span class="text-sm font-medium text-gray-700">Active Tags:</span>
      <span 
        v-for="(tag, index) in activeTags" 
        :key="index"
        class="inline-flex items-center gap-1 text-sm px-3 py-1 bg-primary-100 text-primary-800 rounded-full"
      >
        #{{ tag }}
        <button @click="removeTag(tag)" class="hover:text-primary-900">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>
      <button @click="clearTags" class="text-sm text-primary-600 hover:text-primary-800 underline">
        Clear All
      </button>
    </div>

    <!-- Loading State -->
    <LoadingSpinner 
      v-if="itemStore.loading && !itemStore.items.length" 
      text="Loading questions..." 
      class="my-12"
    />

    <!-- Error State -->
    <div v-else-if="itemStore.error" class="bg-red-50 border-l-4 border-error p-4 mb-6">
      <p class="text-sm text-error">{{ itemStore.error }}</p>
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else-if="itemStore.items.length === 0"
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
          v-for="item in itemStore.items"
          :key="item.id"
          :item="item"
          @click="handleItemClick"
          @tag-click="handleTagClick"
        />
      </div>
      
      <!-- Pagination -->
      <div class="flex justify-center">
        <n-pagination
          v-model:page="itemStore.pagination.page"
          :page-count="itemStore.pagination.pages"
          @update:page="changePage"
          size="large"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useItemStore } from '../../stores/items'
import { NButton, NSpace, NIcon, NPagination } from 'naive-ui'
import { RefreshOutline as RefreshIcon } from '@vicons/ionicons5'
import QuestionFilters from '../../components/QuestionFilters.vue'
import QuestionCard from '../../components/QuestionCard.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'

const router = useRouter()
const route = useRoute()
const itemStore = useItemStore()

const filters = ref({
  collection_id: null,
  subject: null,
  difficulty: null,
  status: null,
  sort_by: 'created_at',
  sort_direction: 'desc'
})

const activeTags = ref([])

// Initialize from URL query
onMounted(() => {
  const tagParam = route.query.tag
  if (tagParam) {
    activeTags.value = Array.isArray(tagParam) ? tagParam : [tagParam]
  }
  handleRefresh()
})

// Watch for route query changes
watch(() => route.query.tag, (newTag) => {
  if (newTag) {
    activeTags.value = Array.isArray(newTag) ? newTag : [newTag]
  } else {
    activeTags.value = []
  }
  handleRefresh()
})

const handleRefresh = () => {
  itemStore.fetchItems({
    page: 1,
    ...filters.value,
    tag: activeTags.value.length > 0 ? activeTags.value : undefined
  })
}

const handleFilterChange = () => {
  itemStore.fetchItems({
    page: 1,
    ...filters.value,
    tag: activeTags.value.length > 0 ? activeTags.value : undefined
  })
}

const changePage = (page) => {
  itemStore.fetchItems({
    page,
    ...filters.value,
    tag: activeTags.value.length > 0 ? activeTags.value : undefined
  })
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleItemClick = (item) => {
  router.push(`/questions/${item.id}`)
}

const handleTagClick = (tagName) => {
  if (!activeTags.value.includes(tagName)) {
    activeTags.value.push(tagName)
    updateRouteQuery()
    handleRefresh()
  }
}

const removeTag = (tagName) => {
  activeTags.value = activeTags.value.filter(t => t !== tagName)
  updateRouteQuery()
  handleRefresh()
}

const clearTags = () => {
  activeTags.value = []
  updateRouteQuery()
  handleRefresh()
}

const updateRouteQuery = () => {
  const query = { ...route.query }
  
  if (activeTags.value.length > 0) {
    query.tag = activeTags.value
  } else {
    delete query.tag
  }
  
  router.replace({ query })
}
</script>
