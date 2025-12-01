<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true }
})

const emit = defineEmits(['click', 'tag-click'])

const firstImage = computed(() => {
  return props.item.images?.[0]?.url || null
})

const difficultyStars = computed(() => {
  return '⭐'.repeat(props.item.difficulty || 0)
})

const statusColors = {
  UNANSWERED: 'bg-gray-100 text-gray-700',
  ANSWERED: 'bg-blue-100 text-blue-700',
  MASTERED: 'bg-green-100 text-green-700',
  NEED_REVIEW: 'bg-yellow-100 text-yellow-700'
}
</script>

<template>
  <div class="card cursor-pointer hover:shadow-lg transition-shadow" data-testid="question-card" @click="emit('click', props.item)">
    <div v-if="firstImage" class="mb-3">
      <img :src="firstImage" :alt="props.item.title || 'Question'" class="w-full h-48 object-cover rounded-md" />
    </div>
    <div class="flex items-start justify-between mb-2">
      <span class="text-sm font-medium text-primary-600" data-testid="card-subject">{{ props.item.subject }}</span>
      <span class="text-sm">{{ difficultyStars }}</span>
    </div>
    <h3 v-if="props.item.title" class="font-semibold mb-2" data-testid="card-title">{{ props.item.title }}</h3>
    <!-- Tags -->
    <div v-if="props.item.tags && props.item.tags.length > 0" class="flex flex-wrap gap-1 mb-2">
      <span 
        v-for="tag in props.item.tags" 
        :key="tag.id || tag.name"
        @click.stop="emit('tag-click', tag.name)"
        class="text-xs px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full cursor-pointer hover:bg-primary-100 transition-colors"
        data-testid="card-tag"
      >
        #{{ tag.name }}
      </span>
    </div>
    <div class="flex items-center justify-between">
      <span :class="['text-xs px-2 py-1 rounded', statusColors[props.item.status]]">
        {{ props.item.status }}
      </span>
      <span class="text-xs text-gray-500">
        {{ new Date(props.item.created_at).toLocaleDateString() }}
      </span>
    </div>
  </div>
</template>
