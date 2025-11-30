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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useItemStore } from '../../stores/items'
import { NButton, NSpace, NIcon, NPagination } from 'naive-ui'
import { RefreshOutline as RefreshIcon } from '@vicons/ionicons5'
import QuestionFilters from '../../components/QuestionFilters.vue'
import QuestionCard from '../../components/QuestionCard.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'

const router = useRouter()
const itemStore = useItemStore()

const filters = ref({
  collection_id: null,
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
  itemStore.fetchItems({
    page: 1,
    ...filters.value
  })
}

const handleFilterChange = () => {
  itemStore.fetchItems({
    page: 1,
    ...filters.value
  })
}

const changePage = (page) => {
  itemStore.fetchItems({
    page,
    ...filters.value
  })
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleItemClick = (item) => {
  router.push(`/questions/${item.id}`)
}
</script>
