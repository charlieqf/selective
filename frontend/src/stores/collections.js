import { defineStore } from 'pinia'
import collectionsApi from '@/api/collections'

export const useCollectionStore = defineStore('collections', {
    state: () => ({
        collections: [],
        loading: false,
        error: null
    }),

    getters: {
        getCollectionById: (state) => (id) => {
            return state.collections.find(c => c.id === id)
        },
        activeCollections: (state) => {
            return state.collections.filter(c => !c.is_deleted)
        }
    },

    actions: {
        async fetchCollections() {
            this.loading = true
            this.error = null
            try {
                const response = await collectionsApi.getCollections()
                this.collections = response.data
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to fetch collections'
                console.error('Error fetching collections:', err)
            } finally {
                this.loading = false
            }
        },

        async createCollection(data) {
            this.loading = true
            this.error = null
            try {
                const response = await collectionsApi.createCollection(data)
                this.collections.push(response.data)
                return response.data
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to create collection'
                throw err
            } finally {
                this.loading = false
            }
        },

        async updateCollection(id, data) {
            this.loading = true
            this.error = null
            try {
                const response = await collectionsApi.updateCollection(id, data)
                const index = this.collections.findIndex(c => c.id === id)
                if (index !== -1) {
                    this.collections[index] = response.data
                }
                return response.data
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to update collection'
                throw err
            } finally {
                this.loading = false
            }
        },

        async deleteCollection(id) {
            this.loading = true
            this.error = null
            try {
                await collectionsApi.deleteCollection(id)
                const index = this.collections.findIndex(c => c.id === id)
                if (index !== -1) {
                    // Optimistic update or refetch? 
                    // Since it's soft delete, we might want to just update the status or remove it from active list.
                    // The API returns success message.
                    // Let's remove it from the list for now or refetch.
                    this.collections = this.collections.filter(c => c.id !== id)
                }
            } catch (err) {
                this.error = err.response?.data?.error || 'Failed to delete collection'
                throw err
            } finally {
                this.loading = false
            }
        }
    }
})
