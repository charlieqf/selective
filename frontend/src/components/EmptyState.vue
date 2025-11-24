<script setup>
defineProps({
  icon: String,
  title: { type: String, required: true },
  description: String,
  actionText: String,
  actionTo: String
})
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div v-if="icon" class="text-6xl mb-4">{{ icon }}</div>
    <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h3>
    <p v-if="description" class="text-gray-600 mb-6 max-w-md">{{ description }}</p>
    <router-link v-if="actionText && actionTo" :to="actionTo" class="btn btn-primary">
      {{ actionText }}
    </router-link>
  </div>
</template>
