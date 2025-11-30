import client from './client'

export default {
    getItems(params) {
        return client.get('/items', { params })
    },

    getItem(id) {
        return client.get(`/items/${id}`)
    },

    createItem(data) {
        return client.post('/items', data)
    },

    updateItem(id, data) {
        return client.patch(`/items/${id}`, data)
    },

    deleteItem(id) {
        return client.delete(`/items/${id}`)
    },

    submitAnswer(itemId, data) {
        return client.post(`/items/${itemId}/answers`, data)
    },

    getAnswerHistory(itemId) {
        return client.get(`/items/${itemId}/answers`)
    },

    getReviewSession(params) {
        return client.get('/items/review-session', { params })
    }
}
