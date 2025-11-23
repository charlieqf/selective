import { defineStore } from 'pinia'
import questionsApi from '@/api/questions'

export const useQuestionStore = defineStore('question', {
    state: () => ({
        questions: [],
        currentQuestion: null,
        loading: false,
        error: null,
        pagination: {
            page: 1,
            per_page: 10,
            total: 0,
            pages: 0
        }
    }),

    actions: {
        async fetchQuestions(params = {}) {
            this.loading = true
            this.error = null
            try {
                const response = await questionsApi.getQuestions({
                    page: this.pagination.page,
                    per_page: this.pagination.per_page,
                    ...params
                })

                this.questions = response.data.questions
                this.pagination = {
                    page: response.data.current_page,
                    per_page: 10, // Default or from response if API returned it
                    total: response.data.total,
                    pages: response.data.pages
                }
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to fetch questions'
                console.error('Fetch questions error:', error)
            } finally {
                this.loading = false
            }
        },

        async createQuestion(data) {
            this.loading = true
            this.error = null
            try {
                const response = await questionsApi.createQuestion(data)
                return response.data
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to create question'
                throw error
            } finally {
                this.loading = false
            }
        },

        async getQuestion(id) {
            this.loading = true
            this.error = null
            try {
                const response = await questionsApi.getQuestion(id)
                this.currentQuestion = response.data
                return response.data
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to fetch question'
                console.error('Get question error:', error)
            } finally {
                this.loading = false
            }
        },

        async updateQuestion(id, data) {
            this.loading = true
            this.error = null
            try {
                const response = await questionsApi.updateQuestion(id, data)
                this.currentQuestion = response.data
                return response.data
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to update question'
                throw error
            } finally {
                this.loading = false
            }
        },

        async deleteQuestion(id) {
            this.loading = true
            this.error = null
            try {
                await questionsApi.deleteQuestion(id)
                // Remove from list if present
                this.questions = this.questions.filter(q => q.id !== id)
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to delete question'
                throw error
            } finally {
                this.loading = false
            }
        }
    }
})
