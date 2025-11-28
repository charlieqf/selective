import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(null)

    // 初始化时安全地读取localStorage
    if (typeof window !== 'undefined') {
        token.value = localStorage.getItem('access_token')
        const storedUser = localStorage.getItem('user')
        if (storedUser) {
            try {
                user.value = JSON.parse(storedUser)
            } catch (e) {
                console.error('Failed to parse stored user:', e)
                localStorage.removeItem('user')
            }
        }
    }

    const isAuthenticated = computed(() => !!token.value)

    function login(userData, authToken) {
        user.value = userData
        token.value = authToken
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', authToken)
            localStorage.setItem('user', JSON.stringify(userData))
        }
    }

    function logout() {
        user.value = null
        token.value = null
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token')
            localStorage.removeItem('user')
        }
    }

    // Refresh user data from server
    async function refreshUser() {
        if (!token.value) return

        try {
            const response = await axios.get('/api/auth/me', {
                headers: { Authorization: `Bearer ${token.value}` }
            })
            user.value = response.data
            if (typeof window !== 'undefined') {
                localStorage.setItem('user', JSON.stringify(response.data))
            }
        } catch (error) {
            console.error('Failed to refresh user:', error)
            // If token is invalid, logout
            if (error.response?.status === 401) {
                logout()
            }
        }
    }

    return {
        user,
        token,
        isAuthenticated,
        login,
        logout,
        refreshUser
    }
})
