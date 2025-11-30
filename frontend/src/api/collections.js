import client from './client'

export default {
    getCollections() {
        return client.get('/collections')
    },

    createCollection(data) {
        return client.post('/collections', data)
    },

    updateCollection(id, data) {
        return client.patch(`/collections/${id}`, data)
    },

    deleteCollection(id) {
        return client.delete(`/collections/${id}`)
    },

    restoreCollection(id) {
        return client.post(`/collections/${id}/restore`)
    }
}
