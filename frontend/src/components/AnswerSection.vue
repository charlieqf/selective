<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { NCard, NButton, NSpace, NTag, NAlert } from 'naive-ui'
import { useMessage } from 'naive-ui'
import questionsApi from '@/api/questions'

const props = defineProps({
  questionId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['answer-submitted'])

const message = useMessage()
const showAnswer = ref(false)
const submitting = ref(false)
const isSubmitted = ref(false)
const startTime = ref(Date.now())
const timer = ref(0)
const timerInterval = ref(null)

function reset() {
  showAnswer.value = false
  isSubmitted.value = false
  timer.value = 0
  stopTimer() // Clear existing interval
  startTimer()
}

// Timer logic
function startTimer() {
  startTime.value = Date.now()
  timerInterval.value = setInterval(() => {
    timer.value = Math.floor((Date.now() - startTime.value) / 1000)
  }, 1000)
}

function stopTimer() {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

// Format seconds to MM:SS
const formattedTime = computed(() => {
  const m = Math.floor(timer.value / 60).toString().padStart(2, '0')
  const s = (timer.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

// Start timer on mount
startTimer()

onUnmounted(() => {
  stopTimer()
})

function handleShowAnswer() {
  showAnswer.value = true
  stopTimer()
}

async function handleSubmit(isCorrect) {
  submitting.value = true
  try {
    const data = {
      is_correct: isCorrect,
      duration_seconds: timer.value
    }
    
    const response = await questionsApi.submitAnswer(props.questionId, data)
    
    if (isCorrect) {
      message.success('Great job! Marked as Mastered.')
    } else {
      message.info('Keep practicing! Marked for Review.')
    }
    
    emit('answer-submitted', response.data)
    isSubmitted.value = true
    
  } catch (error) {
    message.error('Failed to submit answer')
    console.error(error)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <n-card title="Practice Area" class="mb-6 bg-gray-50">
    <div class="flex flex-col items-center justify-center space-y-6 py-4">
      
      <!-- Timer -->
      <div class="text-4xl font-mono text-gray-700 font-bold">
        {{ formattedTime }}
      </div>
      
      <!-- Step 1: Show Answer -->
      <div v-if="!showAnswer">
        <n-button type="primary" size="large" @click="handleShowAnswer">
          Show Answer
        </n-button>
        <p class="text-gray-500 text-sm mt-2">Click when you are ready to check your answer</p>
      </div>
      
      <!-- Step 2: Self Marking -->
      <div v-else-if="!isSubmitted" class="text-center w-full max-w-md animate-fade-in">
        <n-alert type="info" class="mb-6" title="Self Marking">
          Did you get the answer correct?
        </n-alert>
        
        <div class="grid grid-cols-2 gap-4">
          <button 
            class="p-4 rounded-lg border-2 border-red-200 bg-red-50 hover:bg-red-100 transition-colors flex flex-col items-center group"
            :disabled="submitting"
            @click="handleSubmit(false)"
          >
            <span class="text-2xl mb-2 group-hover:scale-110 transition-transform">❌</span>
            <span class="font-bold text-red-700">I got it Wrong</span>
          </button>
          
          <button 
            class="p-4 rounded-lg border-2 border-green-200 bg-green-50 hover:bg-green-100 transition-colors flex flex-col items-center group"
            :disabled="submitting"
            @click="handleSubmit(true)"
          >
            <span class="text-2xl mb-2 group-hover:scale-110 transition-transform">✅</span>
            <span class="font-bold text-green-700">I got it Right</span>
          </button>
        </div>
      </div>

      <!-- Step 3: Result & Try Again -->
      <div v-else class="text-center animate-fade-in">
        <n-button type="default" size="large" @click="reset">
          Try Again
        </n-button>
        <p class="text-gray-500 text-sm mt-2">Practice makes perfect!</p>
      </div>
      
    </div>
  </n-card>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
