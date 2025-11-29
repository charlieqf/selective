import apiClient from './client'

export default {
    getQuestions(params) {
        return apiClient.get('/questions', { params })
    },

    createQuestion(data) {
        return apiClient.post('/questions', data)
    },

    getQuestion(id) {
        return apiClient.get(`/questions/${id}`)
    },

    updateQuestion(id, data) {
        return apiClient.patch(`/questions/${id}`, data)
    },

    deleteQuestion(id) {
        return apiClient.delete(`/questions/${id}`)
    },

    submitAnswer(id, data) {
        return apiClient.post(`/questions/${id}/answers`, data)
    },

    getAnswerHistory(id) {
        return apiClient.get(`/questions/${id}/answers`)
    },

    getReviewSession(params) {
        return apiClient.get('/questions/review-session', { params })
    }
}
