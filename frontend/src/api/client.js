import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const client = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器：注入Token
client.interceptors.request.use(config => {
    // 在拦截器内部调用 useAuthStore，此时 Pinia 已经激活
    const authStore = useAuthStore()
    if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
})

// 响应拦截器：处理401错误
client.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            const authStore = useAuthStore()
            authStore.logout()
        }
        return Promise.reject(error)
    }
)

export default client
