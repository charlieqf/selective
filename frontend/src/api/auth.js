import client from './client'

export const authApi = {
    register(data) {
        return client.post('/auth/register', data)
    },
    login(data) {
        return client.post('/auth/login', data)
    },
    getCurrentUser() {
        return client.get('/auth/me')
    }
}
