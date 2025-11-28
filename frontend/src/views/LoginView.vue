<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NButton, NCard } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const model = ref({
  username: '',
  password: ''
})

const rules = {
  username: {
    required: true,
    message: 'Please enter your username',
    trigger: ['input', 'blur']
  },
  password: {
    required: true,
    message: 'Please enter your password',
    trigger: ['input', 'blur']
  }
}

async function handleLogin(e) {
  e.preventDefault()
  
  try {
    await formRef.value?.validate()
    loading.value = true
    
    const { data } = await authApi.login(model.value)
    authStore.login(data.user, data.token)
    message.success('Login successful')
    router.push('/dashboard')
    
  } catch (error) {
    if (error.response) {
      message.error(error.response.data.error || 'Login failed')
    } else if (error.message) {
      // Validation error or other
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <n-card>
        <div class="text-center mb-6">
          <h2 class="text-3xl font-extrabold text-gray-900">
            Sign in
          </h2>
        </div>
        
        <n-form ref="formRef" :model="model" :rules="rules">
          <n-form-item path="username" label="Username">
            <n-input v-model:value="model.username" placeholder="Username" @keydown.enter.prevent />
          </n-form-item>
          <n-form-item path="password" label="Password">
            <n-input
              v-model:value="model.password"
              type="password"
              show-password-on="click"
              placeholder="Password"
              @keydown.enter.prevent
            />
          </n-form-item>
          <div class="flex justify-center">
            <n-button type="primary" :loading="loading" @click="handleLogin" class="w-full">
              Sign in
            </n-button>
          </div>
        </n-form>
        
        <div class="text-center mt-4">
          <router-link to="/" class="text-primary-600 hover:text-primary-500 mr-4">Home</router-link>
          <router-link to="/register" class="text-primary-600 hover:text-primary-500">Create account</router-link>
        </div>
      </n-card>
    </div>
  </div>
</template>
