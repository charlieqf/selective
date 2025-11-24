import client from './client'

export const analyticsApi = {
    getStats: () => client.get('/analytics/stats'),
    getRecommendations: (params) => client.get('/analytics/recommendations', { params })
}
