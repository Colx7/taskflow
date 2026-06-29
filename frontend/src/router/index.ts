import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
      },
      {
        path: 'tasks',
        name: 'TaskList',
        component: () => import('@/views/TaskList.vue'),
      },
      {
        path: 'weekly-report',
        name: 'WeeklyReport',
        component: () => import('@/views/WeeklyReport.vue'),
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const isGuest = to.meta.guest === true

  if (isGuest && token) {
    // 已登录访问登录/注册页 → 跳转首页
    next({ path: '/dashboard', replace: true })
  } else if (!token && !isGuest) {
    // 未登录访问受保护页面 → 跳转登录
    next({ path: '/login', query: { redirect: to.fullPath }, replace: true })
  } else {
    next()
  }
})

export default router
