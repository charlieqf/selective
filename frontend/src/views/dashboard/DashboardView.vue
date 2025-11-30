<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useAnalyticsStore } from '../../stores/analytics'
import QuestionCard from '../../components/QuestionCard.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import { NGrid, NGridItem, NCard, NStatistic, NButton, NSpace } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const analyticsStore = useAnalyticsStore()

onMounted(async () => {
  await analyticsStore.refreshAll()
})

function handleItemClick(item) {
  router.push(`/questions/${item.id}`)
}
</script>

<template>
  <div class="container">
    <!-- 欢迎信息 -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold">Welcome back, {{ authStore.user?.username }}!</h1>
      <p class="text-gray-600">Here's your learning progress</p>
    </div>

    <!-- 加载状态 -->
    <LoadingSpinner v-if="analyticsStore.loading" text="Loading dashboard..." />

    <template v-else>
      <!-- 统计卡片 -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" class="mb-6">
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Total Questions" :value="analyticsStore.stats?.total_questions || 0" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Answered" :value="analyticsStore.stats?.answered_questions || 0" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Mastered" :value="analyticsStore.stats?.mastered_questions || 0" />
          </n-card>
        </n-grid-item>
        <n-grid-item :span="4" :md-span="2" :lg-span="1">
          <n-card>
            <n-statistic label="Need Review" :value="analyticsStore.stats?.need_review_questions || 0" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 快捷操作 -->
      <n-space class="mb-6">
        <n-button type="primary" @click="router.push('/questions/upload')">Upload New Question</n-button>
        <n-button @click="router.push('/questions')">View All Questions</n-button>
      </n-space>

      <div class="mb-6">
        <h2 class="text-2xl font-bold mb-4">Recommended for You</h2>
        <div v-if="analyticsStore.recommendations.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <QuestionCard 
            v-for="item in analyticsStore.recommendations" 
            :key="item.id"
            :item="item"
            @click="handleItemClick"
          />
        </div>
        <EmptyState 
          v-else
          icon="📚"
          title="No recommendations yet"
          description="Upload some questions to get personalized recommendations"
          action-text="Upload Question"
          action-to="/questions/upload"
        />
      </div>

      <!-- 各科目统计 -->
      <div>
        <h2 class="text-2xl font-bold mb-4">Subject Breakdown</h2>
        <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
          <n-grid-item v-for="(stats, subject) in analyticsStore.stats?.by_subject" :key="subject" :span="4" :md-span="2" :lg-span="1">
            <n-card :title="subject">
              <n-space vertical>
                <div>Total: {{ stats.total }}</div>
                <div>Answered: {{ stats.answered }}</div>
                <div>Mastered: {{ stats.mastered }}</div>
              </n-space>
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>
    </template>
  </div>
</template>
