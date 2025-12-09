<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { NSelect, NSpace, NCheckbox } from 'naive-ui'
import { useCollectionStore } from '@/stores/collections'

const props = defineProps({
  filters: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:filters'])

const filters = ref({ ...props.filters })
const collectionStore = useCollectionStore()

onMounted(() => {
  collectionStore.fetchCollections()
})

const collectionOptions = computed(() => {
  return collectionStore.activeCollections.map(c => ({
    label: c.name,
    value: c.id
  }))
})

const difficultyOptions = [
  { label: '⭐ (1)', value: 1 },
  { label: '⭐⭐ (2)', value: 2 },
  { label: '⭐⭐⭐ (3)', value: 3 },
  { label: '⭐⭐⭐⭐ (4)', value: 4 },
  { label: '⭐⭐⭐⭐⭐ (5)', value: 5 }
]

const statusOptions = [
  { label: 'Unanswered', value: 'UNANSWERED' },
  { label: 'Answered', value: 'ANSWERED' },
  { label: 'Mastered', value: 'MASTERED' }
]

function toggleNeedsReview(checked) {
  filters.value.needs_review = checked ? 'true' : undefined
  emit('update:filters', filters.value)
}
</script>

<template>
  <div class="flex gap-4 mb-4 items-center">
    <!-- Subject Filter (uses collections) -->
    <n-select
      v-model:value="filters.collection_id"
      :options="collectionOptions"
      placeholder="All Subjects"
      clearable
      data-testid="subject-filter"
      @update:value="$emit('update:filters', filters)"
    />
    
    <!-- Difficulty Filter -->
    <n-select
      v-model:value="filters.difficulty"
      :options="difficultyOptions"
      placeholder="All Difficulties"
      clearable
      data-testid="difficulty-filter"
      @update:value="$emit('update:filters', filters)"
    />
    
    <!-- Status Filter -->
    <n-select
      v-model:value="filters.status"
      :options="statusOptions"
      placeholder="All Status"
      clearable
      data-testid="status-filter"
      @update:value="$emit('update:filters', filters)"
    />
    
    <!-- Needs Review Filter -->
    <n-checkbox
      :checked="filters.needs_review === 'true'"
      @update:checked="toggleNeedsReview"
      data-testid="needs-review-filter"
    >
      Needs Review
    </n-checkbox>
  </div>
</template>

