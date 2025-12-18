<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useAnalyticsStore } from '../../stores/analytics'
import { useCollectionStore } from '../../stores/collections'
import QuestionCard from '../../components/QuestionCard.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import EmptyState from '../../components/EmptyState.vue'
import { NGrid, NGridItem, NCard, NStatistic, NButton, NSpace } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const analyticsStore = useAnalyticsStore()
const collectionStore = useCollectionStore()

onMounted(async () => {
  await Promise.all([
    analyticsStore.refreshAll(),
    collectionStore.fetchCollections()
  ])
})

function handleItemClick(item) {
  router.push(`/questions/${item.id}`)
}

function goToReview(collectionId) {
  router.push({
    path: '/questions',
    query: { collection_id: collectionId, needs_review: 'true' }
  })
}

function goToCollection(collectionId) {
  router.push({
    path: '/questions',
    query: { collection_id: collectionId }
  })
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
      <!-- 统计卡片 - 2x2 Grid -->
      <div class="stats-grid mb-6">
        <!-- Total Questions -->
        <div class="stat-card stat-card--total">
          <div class="stat-card__icon">📚</div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ analyticsStore.stats?.total_questions || 0 }}</div>
            <div class="stat-card__label">Total Questions</div>
          </div>
        </div>
        
        <!-- Answered -->
        <div class="stat-card stat-card--answered">
          <div class="stat-card__icon">✅</div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ analyticsStore.stats?.answered_questions || 0 }}</div>
            <div class="stat-card__label">Answered</div>
          </div>
        </div>
        
        <!-- Mastered -->
        <div class="stat-card stat-card--mastered">
          <div class="stat-card__icon">🏆</div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ analyticsStore.stats?.mastered_questions || 0 }}</div>
            <div class="stat-card__label">Mastered</div>
          </div>
        </div>
        
        <!-- Need Review -->
        <div class="stat-card stat-card--review">
          <div class="stat-card__icon">🔄</div>
          <div class="stat-card__content">
            <div class="stat-card__value">{{ analyticsStore.stats?.need_review_questions || 0 }}</div>
            <div class="stat-card__label">Need Review</div>
          </div>
        </div>
      </div>

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

      <!-- Collections -->
      <div>
        <h2 class="text-2xl font-bold mb-4">Collections</h2>
        <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
          <n-grid-item v-for="collection in collectionStore.activeCollections" :key="collection.id" :span="4" :md-span="2" :lg-span="1">
            <n-card>
              <template #header>
                <router-link 
                  :to="{ path: '/questions', query: { collection_id: collection.id } }"
                  class="collection-title"
                >
                  {{ collection.name }}
                </router-link>
              </template>
              <n-space vertical>
                <div>Total: {{ collection.total_count || 0 }}</div>
                <div>Need Review: {{ collection.need_review_count || 0 }}</div>
              </n-space>
              <template #action>
                <n-button 
                  v-if="collection.need_review_count > 0"
                  size="small" 
                  type="warning"
                  @click="goToReview(collection.id)"
                >
                  Review ({{ collection.need_review_count }})
                </n-button>
              </template>
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* 2x2 Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

/* Stat Card Base Styles */
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.stat-card__icon {
  font-size: 2.5rem;
  line-height: 1;
}

.stat-card__content {
  flex: 1;
}

.stat-card__value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
}

.stat-card__label {
  font-size: 0.875rem;
  opacity: 0.9;
  margin-top: 4px;
}

/* Card Color Variants - Clean & Professional */
.stat-card--total {
  background: linear-gradient(135deg, #4a5568 0%, #718096 100%);
}

.stat-card--answered {
  background: linear-gradient(135deg, #3182ce 0%, #63b3ed 100%);
}

.stat-card--mastered {
  background: linear-gradient(135deg, #38a169 0%, #68d391 100%);
}

.stat-card--review {
  background: linear-gradient(135deg, #dd6b20 0%, #ed8936 100%);
}

/* Collection Title Link */
.collection-title {
  color: #18a058;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
}

.collection-title:hover {
  color: #0c7a43;
  text-decoration: underline;
}

/* Responsive: Stack to 1 column on very small screens */
@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-card__icon {
    font-size: 2rem;
  }
  
  .stat-card__value {
    font-size: 1.5rem;
  }
}
</style>
