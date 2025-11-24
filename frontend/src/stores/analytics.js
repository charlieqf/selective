import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyticsApi } from '../api/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
    const stats = ref(null)
    const recommendations = ref([])
    const loading = ref(false)
    const error = ref(null)

    async function fetchStats() {
        loading.value = true
        error.value = null
        try {
            const { data } = await analyticsApi.getStats()
            stats.value = data
        } catch (err) {
            error.value = err.message
            console.error('Failed to fetch stats:', err)
        } finally {
            loading.value = false
        }
    }

    async function fetchRecommendations(params = {}) {
        loading.value = true
        error.value = null
        try {
            const { data } = await analyticsApi.getRecommendations(params)
            recommendations.value = data
        } catch (err) {
            error.value = err.message
            console.error('Failed to fetch recommendations:', err)
        } finally {
            loading.value = false
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
