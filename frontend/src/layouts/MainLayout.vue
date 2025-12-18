<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { NLayout, NLayoutHeader, NLayoutSider, NLayoutContent, NMenu, NButton, NIcon } from 'naive-ui'
import { useDevice } from '../composables/useDevice'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { isMobile } = useDevice()

const collapsed = ref(false)

const menuOptions = [
  { label: 'Dashboard', key: 'dashboard', path: '/dashboard' },
  { label: 'Questions', key: 'questions', path: '/questions' },
  { label: 'Upload', key: 'upload', path: '/questions/upload' }
]

// 创建key到path的映射
const menuPathMap = Object.fromEntries(
  menuOptions.map(item => [item.key, item.path])
)

// 根据当前路由获取active key
const activeKey = computed(() => {
  const path = route.path
  if (path.startsWith('/questions/upload')) return 'upload'
  if (path.startsWith('/questions')) return 'questions'
  if (path.startsWith('/dashboard')) return 'dashboard'
  return 'dashboard'
})

function handleMenuSelect(key) {
  const path = menuPathMap[key]
  if (path) {
    router.push(path)
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <n-layout has-sider class="min-h-screen">
    <!-- 侧边栏 - PC显示,移动端隐藏 -->
    <n-layout-sider
      v-if="!isMobile"
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="p-4">
        <router-link v-if="!collapsed" to="/dashboard" class="no-underline flex items-center gap-2 hover:opacity-80 transition-opacity">
          <img src="/logo.png" alt="Selective Prep" class="h-10 w-auto max-w-[160px] object-contain" />
        </router-link>
        <router-link v-else to="/dashboard" class="block text-center">
          <span class="text-xl font-bold text-primary">S</span>
        </router-link>
      </div>
      <n-menu 
        :value="activeKey"
        :options="menuOptions" 
        @update:value="handleMenuSelect" 
      />
    </n-layout-sider>
    
    <n-layout>
      <!-- 顶部导航栏 -->
      <n-layout-header bordered class="p-4 flex justify-between items-center">
        <div>
          <!-- 移动端显示 Logo -->
          <router-link v-if="isMobile" to="/dashboard" class="no-underline flex items-center hover:opacity-80 transition-opacity">
            <img src="/logo.png" alt="Selective Prep" class="h-8 w-auto max-w-[140px] object-contain" />
          </router-link>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">{{ authStore.user?.username }}</span>
          <n-button @click="handleLogout" secondary>Logout</n-button>
        </div>
      </n-layout-header>
      
      <!-- 主内容区 -->
      <n-layout-content class="p-6">
        <router-view />
      </n-layout-content>

      <!-- 移动端底部导航 -->
      <n-layout-footer v-if="isMobile" bordered class="p-2">
        <div class="flex justify-around">
          <n-button 
            v-for="item in menuOptions" 
            :key="item.key"
            :type="activeKey === item.key ? 'primary' : 'default'"
            text
            @click="handleMenuSelect(item.key)"
          >
            {{ item.label }}
          </n-button>
        </div>
      </n-layout-footer>
    </n-layout>
  </n-layout>
</template>
