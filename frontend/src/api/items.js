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

    rotateImage(id, imageIndex, rotation) {
        return client.patch(`/items/${id}/rotate`, { image_index: imageIndex, rotation })
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
    },

    updateStatus(id, status) {
        return client.patch(`/items/${id}/status`, { status })
    },

    toggleReview(id, needsReview) {
        // Toggle or set the needs_review flag
        return client.patch(`/items/${id}/review`, { needs_review: needsReview })
    }
}
