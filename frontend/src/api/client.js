import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json'
    },
    paramsSerializer: {
        serialize: (params) => {
            const searchParams = new URLSearchParams();
            for (const key in params) {
                const value = params[key];
                if (Array.isArray(value)) {
                    value.forEach(val => searchParams.append(key, val));
                } else if (value !== null && value !== undefined) {
                    searchParams.append(key, value);
                }
            }
            return searchParams.toString();
        }
    }
})

// 请求拦截器：注入Token
client.interceptors.request.use(config => {
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
