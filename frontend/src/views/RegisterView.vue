<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NButton, NCard, NRadioGroup, NRadioButton, NProgress, NSpace } from 'naive-ui'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const model = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'student'
})

const rules = {
  username: {
    required: true,
    message: 'Please enter your username',
    trigger: ['input', 'blur'],
    min: 3,
    max: 64
  },
  email: {
    required: true,
    message: 'Please enter your email',
    trigger: ['input', 'blur'],
    type: 'email'
  },
  password: {
    required: true,
    message: 'Please enter your password',
    trigger: ['input', 'blur'],
    min: 6
  },
  confirmPassword: {
    required: true,
    message: 'Please confirm your password',
    trigger: ['input', 'blur'],
    validator: (rule, value) => {
      return value === model.value.password || new Error('Passwords do not match')
    }
  },
  role: {
    required: true,
    message: 'Please select a role',
    trigger: 'change'
  }
}

const passwordStrength = computed(() => {
  const pwd = model.value.password
  if (!pwd) return 0
  let score = 0
  if (pwd.length >= 8) score += 25
  if (/[A-Z]/.test(pwd)) score += 25
  if (/[a-z]/.test(pwd)) score += 25
  if (/[0-9!@#$%^&*]/.test(pwd)) score += 25
  return score
})

const passwordStrengthColor = computed(() => {
  const score = passwordStrength.value
  if (score <= 25) return '#d03050'
  if (score <= 50) return '#f0a020'
  if (score <= 75) return '#18a058'
  return '#2080f0'
})

async function handleRegister(e) {
  e.preventDefault()
  
  try {
    await formRef.value?.validate()
    loading.value = true
    
    const { data } = await authApi.register({
      username: model.value.username,
      email: model.value.email,
      password: model.value.password,
      role: model.value.role
    })
    
    authStore.login(data.user, data.token)
    message.success('Registration successful')
    router.push('/dashboard')
    
  } catch (error) {
    if (error.response) {
      message.error(error.response.data.error || 'Registration failed')
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
      <div class="text-center mb-2">
        <h2 class="text-xl font-extrabold text-gray-900">
          Create account
        </h2>
          <p class="mt-1 text-xs text-gray-600">
            Join Selective to start your learning journey
          </p>
        </div>
        
        <n-form ref="formRef" :model="model" :rules="rules" size="medium">
          <!-- Role Selection -->
          <n-form-item path="role" label="I am a...">
            <n-radio-group v-model:value="model.role" name="role-group" class="w-full">
              <div class="grid grid-cols-3 gap-4 w-full">
                <n-radio-button value="student" label="Student" class="text-center" />
                <n-radio-button value="parent" label="Parent" class="text-center" />
                <n-radio-button value="tutor" label="Tutor" class="text-center" />
              </div>
            </n-radio-group>
          </n-form-item>

          <n-form-item path="username" label="Username">
            <n-input v-model:value="model.username" placeholder="Username" />
          </n-form-item>
          
          <n-form-item path="email" label="Email" class="-mt-4">
            <n-input v-model:value="model.email" placeholder="Email" />
          </n-form-item>
          
          <n-form-item path="password" label="Password" class="-mt-4">
            <n-space vertical class="w-full">
              <n-input
                v-model:value="model.password"
                type="password"
                show-password-on="click"
                placeholder="Password"
              />
              <n-progress
                type="line"
                :percentage="passwordStrength"
                :color="passwordStrengthColor"
                :show-indicator="false"
                height="4"
                v-if="model.password"
              />
            </n-space>
          </n-form-item>
          
          <n-form-item path="confirmPassword" label="Confirm Password">
            <n-input
              v-model:value="model.confirmPassword"
              type="password"
              show-password-on="click"
              placeholder="Confirm Password"
            />
          </n-form-item>
          
          <div class="flex justify-center mt-6">
            <n-button type="primary" :loading="loading" @click="handleRegister" class="w-full" size="large">
              Register
            </n-button>
          </div>
        </n-form>
        
        <div class="text-center mt-6">
          <p class="text-sm text-gray-600">
            Already have an account?
            <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">
              Sign in
            </router-link>
          </p>
        </div>
      </n-card>
    </div>
</template>
