import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analyticsApi } from '../api/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
    const stats = ref(null)
    const recommendations = ref([])
    const loadingCounter = ref(0)
    const error = ref(null)

    const loading = computed(() => loadingCounter.value > 0)

    async function fetchStats() {
        loadingCounter.value++
        error.value = null
        try {
            const { data } = await analyticsApi.getStats()
            stats.value = data
        } catch (err) {
            error.value = err.message
            console.error('Failed to fetch stats:', err)
        } finally {
            loadingCounter.value--
        }
    }

    async function fetchRecommendations(params = {}) {
        loadingCounter.value++
        error.value = null
        try {
            const { data } = await analyticsApi.getRecommendations(params)
            recommendations.value = data
        } catch (err) {
            error.value = err.message
            console.error('Failed to fetch recommendations:', err)
        } finally {
            loadingCounter.value--
        }
    }

    async function refreshAll() {
        await Promise.all([fetchStats(), fetchRecommendations()])
    }

    return {
        stats,
        recommendations,
        loading,
        error,
        fetchStats,
        fetchRecommendations,
        refreshAll
    }
})
