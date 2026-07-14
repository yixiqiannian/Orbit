import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/portal',
    name: 'NavPortal',
    component: () => import('../views/NavPortal.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: '/tasks',
        name: 'Tasks',
        component: () => import('../views/Tasks.vue')
      },
      {
        path: '/cron',
        name: 'CronJobs',
        component: () => import('../views/CronJobs.vue')
      },
      {
        path: '/reading',
        name: 'Reading',
        component: () => import('../views/Reading.vue')
      },
      {
        path: '/email',
        name: 'Email',
        component: () => import('../views/Email.vue')
      },
      {
        path: '/nav',
        name: 'NavManage',
        component: () => import('../views/NavManage.vue')
      },
      {
        path: '/knowledge',
        name: 'Knowledge',
        component: () => import('../views/Knowledge.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
