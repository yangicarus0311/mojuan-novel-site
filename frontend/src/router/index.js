import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },
  { path: '/works/:id', component: () => import('../views/Work.vue') },
  { path: '/works/:workId/chapters/:chapterId', component: () => import('../views/Reader.vue') },
  { path: '/bookshelf', component: () => import('../views/Bookshelf.vue') },
  { path: '/search', component: () => import('../views/Search.vue') },
  { path: '/payment', component: () => import('../views/Payment.vue') },
  { path: '/notebook', component: () => import('../views/Notebook.vue') },
  { path: '/stats', component: () => import('../views/ReadingStats.vue') },
  { path: '/profile/:id', component: () => import('../views/UserProfile.vue') },
  { path: '/feed', component: () => import('../views/Feed.vue') },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    children: [
      { path: '', component: () => import('../views/admin/AdminDashboard.vue') },
      { path: 'works', component: () => import('../views/admin/AdminWorks.vue') },
      { path: 'users', component: () => import('../views/admin/AdminUsers.vue') },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(to => {
  const protectedPage = ['/bookshelf', '/payment', '/notebook', '/stats', '/feed', '/admin'].some(path => to.path.startsWith(path)) || to.path.includes('/chapters/')
  if (protectedPage && !localStorage.getItem('token')) return { path: '/login', query: { redirect: to.fullPath } }
})

export default router
