import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(null)

    // 初始化时安全地读取localStorage
    if (typeof window !== 'undefined') {
        token.value = localStorage.getItem('token')
    }

    const isAuthenticated = computed(() => !!token.value)

    function login(userData, authToken) {
        user.value = userData
        token.value = authToken
        if (typeof window !== 'undefined') {
            localStorage.setItem('token', authToken)
        }
    }

    function logout() {
        user.value = null
        token.value = null
        if (typeof window !== 'undefined') {
            localStorage.removeItem('token')
        }
    }

    return {
        user,
        token,
        isAuthenticated,
        login,
        logout
    }
})
