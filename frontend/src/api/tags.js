import client from './client'

export default {
    getTags(params) {
        return client.get('/tags', { params })
    }
}
