import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/dashboard'
        },
        {
            path: '/login',
            name: 'Login',
            component: () => import('../views/LoginView.vue')
        },
        {
            path: '/register',
            name: 'Register',
            component: () => import('../views/RegisterView.vue')
        },
        {
            path: '/dashboard',
            name: 'Dashboard',
            component: () => import('../views/dashboard/DashboardView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/questions',
            name: 'QuestionList',
            component: () => import('../views/questions/QuestionList.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/questions/upload',
            name: 'QuestionUpload',
            component: () => import('../views/questions/QuestionUpload.vue'),
            meta: { requiresAuth: true }
        }
    ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token')
    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else {
        next()
    }
})

export default router
