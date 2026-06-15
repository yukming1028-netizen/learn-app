import { createRouter, createWebHistory } from 'vue-router'
import { hasDeviceToken, hasActiveChild } from '../composables/device'

const routes = [
  {
    path: '/select',
    name: 'UserSelect',
    component: () => import('../views/UserSelect.vue'),
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresChild: true },
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: () => import('../views/Quiz.vue'),
    meta: { requiresChild: true },
  },
  {
    path: '/rewards',
    name: 'Rewards',
    component: () => import('../views/Rewards.vue'),
    meta: { requiresChild: true },
  },
  {
    path: '/review',
    name: 'Review',
    component: () => import('../views/Review.vue'),
    meta: { requiresChild: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresChild: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Global guard: redirect to /select if no active child
router.beforeEach((to, from, next) => {
  if (to.meta.requiresChild && !hasActiveChild()) {
    next('/select')
  } else if (to.name === 'UserSelect' && hasActiveChild() && hasDeviceToken()) {
    // Already selected, allow staying on /select to switch
    next()
  } else {
    next()
  }
})

export default router
