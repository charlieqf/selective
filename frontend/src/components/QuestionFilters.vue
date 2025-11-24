<script setup>
import { ref, watch } from 'vue'
import { NSelect, NSpace } from 'naive-ui'

const props = defineProps({
  filters: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:filters'])

const localFilters = ref({ ...props.filters })

// 监听localFilters变化,emit给父组件
watch(localFilters, (newFilters) => {
  emit('update:filters', newFilters)
}, { deep: true })

// 监听props.filters变化,同步到localFilters(实现双向绑定)
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

// 使用数据库中的大写枚举值
const subjectOptions = [
  { label: 'All Subjects', value: null },
  { label: 'Reading', value: 'READING' },
  { label: 'Writing', value: 'WRITING' },
  { label: 'Maths', value: 'MATHS' },
  { label: 'Thinking Skills', value: 'THINKING_SKILLS' }
]

const difficultyOptions = [
  { label: 'All Difficulties', value: null },
  { label: '⭐ (1)', value: 1 },
  { label: '⭐⭐ (2)', value: 2 },
  { label: '⭐⭐⭐ (3)', value: 3 },
  { label: '⭐⭐⭐⭐ (4)', value: 4 },
  { label: '⭐⭐⭐⭐⭐ (5)', value: 5 }
]

const statusOptions = [
  { label: 'All Status', value: null },
  { label: 'Unanswered', value: 'UNANSWERED' },
  { label: 'Answered', value: 'ANSWERED' },
  { label: 'Mastered', value: 'MASTERED' },
  { label: 'Need Review', value: 'NEED_REVIEW' }
]

const sortOptions = [
  { label: 'Newest First', value: { sort_by: 'created_at', sort_direction: 'desc' } },
  { label: 'Oldest First', value: { sort_by: 'created_at', sort_direction: 'asc' } },
  { label: 'Difficulty: Low to High', value: { sort_by: 'difficulty', sort_direction: 'asc' } },
  { label: 'Difficulty: High to Low', value: { sort_by: 'difficulty', sort_direction: 'desc' } }
]
</script>

<template>
  <div class="card mb-4">
    <n-space vertical>
      <n-space>
        <n-select v-model:value="localFilters.subject" :options="subjectOptions" placeholder="Subject" style="width: 200px" />
        <n-select v-model:value="localFilters.difficulty" :options="difficultyOptions" placeholder="Difficulty" style="width: 200px" />
        <n-select v-model:value="localFilters.status" :options="statusOptions" placeholder="Status" style="width: 200px" />
        <n-select 
          v-model:value="localFilters.sort" 
          :options="sortOptions" 
          placeholder="Sort by" 
          style="width: 200px"
          @update:value="(val) => { localFilters.sort_by = val.sort_by; localFilters.sort_direction = val.sort_direction }"
        />
      </n-space>
    </n-space>
  </div>
</template>
