<script setup>
import { computed } from 'vue'
import { getDisplayUrl, getImageStyle } from '../utils/image'

const props = defineProps({
  item: { type: Object, required: true }
})

const emit = defineEmits(['click', 'tag-click'])

const visibleImages = computed(() => {
  return props.item.images?.slice(0, 4) || []
})

const difficultyStars = computed(() => {
  return '⭐'.repeat(props.item.difficulty || 0)
})

const statusColors = {
  UNANSWERED: 'bg-gray-100 text-gray-700',
  ANSWERED: 'bg-blue-100 text-blue-700',
  MASTERED: 'bg-green-100 text-green-700'
}
</script>

<template>
  <div class="card cursor-pointer hover:shadow-lg transition-shadow" data-testid="question-card" @click="emit('click', props.item)">
    <!-- Image Grid (up to 4 images) -->
    <div 
      v-if="visibleImages.length > 0" 
      class="mb-3 overflow-hidden rounded-md h-40 bg-gray-50 grid gap-1"
      :class="{
        'grid-cols-1': visibleImages.length === 1,
        'grid-cols-2': visibleImages.length >= 2,
        'grid-rows-2': visibleImages.length >= 3
      }"
    >
      <div 
        v-for="(image, index) in visibleImages" 
        :key="index"
        class="relative overflow-hidden flex items-center justify-center bg-gray-100"
      >
        <img 
          :src="getDisplayUrl(image, props.item.updated_at)" 
          :style="getImageStyle(image)"
          class="max-w-full max-h-full object-contain" 
        />
        <!-- More images indicator -->
        <div 
          v-if="index === 3 && props.item.images.length > 4" 
          class="absolute inset-0 bg-black/40 flex items-center justify-center text-white text-xs font-bold"
        >
          +{{ props.item.images.length - 4 }}
        </div>
      </div>
    </div>
    <div class="flex items-start justify-between mb-2">
      <span class="text-sm font-medium text-primary-600" data-testid="card-subject">{{ props.item.subject }}</span>
      <span class="text-sm">{{ difficultyStars }}</span>
    </div>
    <h3 v-if="props.item.title" class="font-semibold mb-2" data-testid="card-title">{{ props.item.title }}</h3>
    <!-- Tags -->
    <div v-if="props.item.tags && props.item.tags.length > 0" class="flex flex-wrap gap-2 mb-2">
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
