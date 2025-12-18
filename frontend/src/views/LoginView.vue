<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NButton, NCard } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const googleLoaded = ref(false)
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

// Google Sign-In initialization
// Google Sign-In initialization
onMounted(() => {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (!clientId) {
    // Rely on the initialize function to show the warning, don't poll
    initializeGoogleSignIn()
    return
  }

  const checkGoogle = setInterval(() => {
    if (window.google?.accounts?.id) {
      clearInterval(checkGoogle)
      initializeGoogleSignIn()
    }
  }, 100)
  
  // Timeout after 5 seconds
  setTimeout(() => {
    clearInterval(checkGoogle)
    if (!googleLoaded.value && clientId) {
      console.warn('Google Sign-In SDK failed to load')
    }
  }, 5000)
})

function initializeGoogleSignIn() {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (!clientId) {
    console.warn('VITE_GOOGLE_CLIENT_ID not configured')
    return
  }
  
  // Mark as loaded first so the container div is rendered
  googleLoaded.value = true
  
  // Wait for next tick to ensure DOM is ready
  setTimeout(() => {
    const buttonContainer = document.getElementById('google-signin-btn')
    if (!buttonContainer) {
      console.warn('Google button container not found')
      return
    }
    
    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleGoogleLogin,
        auto_select: false,
        cancel_on_tap_outside: true
      })
      
      window.google.accounts.id.renderButton(
        buttonContainer,
        { 
          theme: 'outline', 
          size: 'large', 
          text: 'signin_with',
          width: 300 
        }
      )
    } catch (error) {
      console.error('Failed to initialize Google Sign-In:', error)
    }
  }, 100)
}

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

async function handleGoogleLogin(response) {
  try {
    loading.value = true
    
    // Get CSRF token from cookie (set by Google SDK)
    const gCsrfToken = getCookie('g_csrf_token')
    
    const { data } = await authApi.googleLogin({
      credential: response.credential,
      g_csrf_token: gCsrfToken
    })
    
    authStore.login(data.user, data.token)
    message.success('Login successful')
    router.push('/dashboard')
  } catch (error) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('Google login failed. Please try again.')
    }
  } finally {
    loading.value = false
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
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto" style="max-width: 400px;">
    <n-card>
      <div class="text-center mb-4">
        <h2 class="text-2xl font-extrabold text-gray-900">
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
        
        <!-- Divider -->
        <div class="flex items-center my-4">
          <div class="flex-1 border-t border-gray-300"></div>
          <span class="px-4 text-gray-500 text-sm">OR</span>
          <div class="flex-1 border-t border-gray-300"></div>
        </div>
        
        <!-- Google Sign-In Button -->
        <div class="flex justify-center">
          <div v-if="googleLoaded" id="google-signin-btn"></div>
          <div v-else id="google-signin-btn" class="text-center text-gray-500 text-sm py-2">
            Loading Google Sign-In...
          </div>
        </div>
        
        <div class="text-center mt-4">
          <span class="text-gray-600">Don't have an account? </span>
          <router-link to="/register" class="text-primary-600 hover:text-primary-500 font-medium">Create account</router-link>
        </div>
      </n-card>
    </div>
  </div>
</template>
