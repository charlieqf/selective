import { defineStore } from 'pinia'
import itemsApi from '@/api/items'

export const useItemStore = defineStore('items', {
    state: () => ({
        items: [],
        currentItem: null,
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
        async fetchItems(params = {}) {
            this.loading = true
            this.error = null
            try {
                const response = await itemsApi.getItems({
                    page: this.pagination.page,
                    per_page: this.pagination.per_page,
                    ...params
                })

                this.items = response.data.items
                this.pagination = {
                    page: response.data.current_page,
                    per_page: 10, // Default or from response if API returned it
                    total: response.data.total,
                    pages: response.data.pages
                }
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to fetch items'
                console.error('Fetch items error:', error)
            } finally {
                this.loading = false
            }
        },

        async createItem(data) {
            this.loading = true
            this.error = null
            try {
                const response = await itemsApi.createItem(data)
                return response.data
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to create item'
                throw error
            } finally {
                this.loading = false
            }
        },

        async getItem(id) {
            this.loading = true
            this.error = null
            try {
                const response = await itemsApi.getItem(id)
                this.currentItem = response.data
                return response.data
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to fetch item'
                console.error('Get item error:', error)
            } finally {
                this.loading = false
            }
        },

        async updateItem(id, data) {
            this.loading = true
            this.error = null
            try {
                const response = await itemsApi.updateItem(id, data)
                this.currentItem = response.data
                return response.data
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to update item'
                throw error
            } finally {
                this.loading = false
            }
        },

        async deleteItem(id) {
            this.loading = true
            this.error = null
            try {
                await itemsApi.deleteItem(id)
                // Remove from list if present
                this.items = this.items.filter(q => q.id !== id)
            } catch (error) {
                this.error = error.response?.data?.error || 'Failed to delete item'
                throw error
            } finally {
                this.loading = false
            }
        },

        async rotateImage(id, index, rotation) {
            if (!this.currentItem) return

            // Store current images for potential revert
            const originalImages = JSON.parse(JSON.stringify(this.currentItem.images))

            // Optimistic update
            const updatedImages = [...this.currentItem.images]
            updatedImages[index] = { ...updatedImages[index], rotation }
            this.currentItem = { ...this.currentItem, images: updatedImages }

            try {
                const response = await itemsApi.rotateImage(id, index, rotation)
                // Update with server values (updated_at)
                this.currentItem = {
                    ...this.currentItem,
                    updated_at: response.data.updated_at
                }
                return response.data
            } catch (error) {
                // Revert on failure
                this.currentItem = { ...this.currentItem, images: originalImages }
                throw error
            }
        }
    }
})
