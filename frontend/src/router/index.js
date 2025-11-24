import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/dashboard'
        },
        // 认证路由 - 使用AuthLayout
        {
            path: '/login',
            component: AuthLayout,
            children: [
                {
                    path: '',
                    name: 'Login',
                    component: () => import('../views/LoginView.vue')
                }
            ]
        },
        {
            path: '/register',
            component: AuthLayout,
            children: [
                {
                    path: '',
                    name: 'Register',
                    component: () => import('../views/RegisterView.vue')
                }
            ]
        },
        // 主应用路由 - 使用MainLayout
        {
            path: '/',
            component: MainLayout,
            meta: { requiresAuth: true },
            children: [
                {
                    path: 'dashboard',
                    name: 'Dashboard',
                    component: () => import('../views/dashboard/DashboardView.vue')
                },
                {
                    path: 'questions',
                    name: 'QuestionList',
                    component: () => import('../views/questions/QuestionList.vue')
                },
                {
                    path: 'questions/upload',
                    name: 'QuestionUpload',
                    component: () => import('../views/questions/QuestionUpload.vue')
                }
            ]
        }
    ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token')

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if ((to.path === '/login' || to.path === '/register') && token) {
        next('/dashboard')
    } else {
        next()
    }
})

export default router
