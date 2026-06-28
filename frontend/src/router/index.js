import { createRouter, createWebHistory } from 'vue-router'

const routes = [
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
    component: () => import('@/components/Layout.vue'),
    redirect: '/projects',
    children: [
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/ProjectList.vue'),
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/ProjectDetail.vue'),
        redirect: (to) => ({ name: 'TaskKanban', params: { id: to.params.id } }),
        children: [
          {
            path: 'kanban',
            name: 'TaskKanban',
            component: () => import('@/views/TaskKanban.vue'),
          },
          {
            path: 'list',
            name: 'TaskList',
            component: () => import('@/views/TaskList.vue'),
          },
          {
            path: 'gantt',
            name: 'TaskGantt',
            component: () => import('@/views/TaskGantt.vue'),
          },
          {
            path: 'docs',
            name: 'DocumentList',
            component: () => import('@/views/DocumentList.vue'),
          },
        ],
      },
      {
        path: 'projects/:id/docs/:docId',
        name: 'DocumentEditor',
        component: () => import('@/views/DocumentEditor.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.guest) {
    next()
  } else if (!token) {
    next('/login')
  } else {
    next()
  }
})

export default router
