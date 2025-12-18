<template>
  <div class="h-screen w-screen overflow-hidden flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full p-4 transform -translate-y-8">
      <div class="text-center mb-4">
        <img src="/logo.png" alt="Selective Prep" class="h-14 w-auto max-w-[220px] mx-auto mb-2 object-contain" />
        <p class="text-gray-600 text-sm">Practice with Purpose. Excel with Confidence.</p>
      </div>
      <router-view />
    </div>
  </div>
</template>
