<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { NSelect, NCheckbox } from 'naive-ui'
import { useCollectionStore } from '@/stores/collections'

const props = defineProps({
  filters: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:filters'])

const filters = ref({ ...props.filters })
const collectionStore = useCollectionStore()

// Sync filters from props if they change externally
watch(() => props.filters, (newVal) => {
  if (newVal) {
    filters.value = { ...newVal }
  }
}, { deep: true })

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
  { label: '1 Star', value: 1 },
  { label: '2 Stars', value: 2 },
  { label: '3 Stars', value: 3 },
  { label: '4 Stars', value: 4 },
  { label: '5 Stars', value: 5 }
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
  <div class="flex flex-row md:items-center gap-4 mb-4">
    <!-- Dropdowns: Stack on mobile, Row on desktop -->
    <div class="flex flex-col md:flex-row gap-4 flex-1 min-w-0">
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
    </div>

    <!-- Needs Review Filter -->
    <div class="flex-none pt-2 md:pt-0">
      <n-checkbox
        :checked="filters.needs_review === 'true'"
        @update:checked="toggleNeedsReview"
        data-testid="needs-review-filter"
        class="items-start md:items-center"
      >
        <span class="writing-mode-vertical md:writing-mode-horizontal text-xs md:text-sm leading-tight md:leading-normal block h-24 md:h-auto">
          Needs Review
        </span>
      </n-checkbox>
    </div>
  </div>
</template>

<style scoped>
.writing-mode-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
}
.writing-mode-horizontal {
  writing-mode: horizontal-tb;
  transform: none;
}
</style>

