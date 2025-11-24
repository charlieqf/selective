<script setup>
defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  text: String
})

const sizeClasses = {
  small: 'w-4 h-4',
  medium: 'w-8 h-8',
  large: 'w-12 h-12'
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-2">
    <div :class="['animate-spin rounded-full border-2 border-gray-300 border-t-primary-600', sizeClasses[size]]"></div>
    <p v-if="text" class="text-sm text-gray-600">{{ text }}</p>
  </div>
</template>
