<template>
  <div class="app-container">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- Bottom nav (only when a child is active) -->
    <div v-if="showNav" class="bottom-nav">
      <button :class="['nav-item', { active: $route.name === 'Home' }]" @click="$router.push('/')">
        <span class="nav-icon">🏠</span> 主頁
      </button>
      <button :class="['nav-item', { active: $route.name === 'Review' }]" @click="$router.push('/review')">
        <span class="nav-icon">📖</span> 錯題本
      </button>
      <button :class="['nav-item', { active: $route.name === 'Rewards' }]" @click="$router.push('/rewards')">
        <span class="nav-icon">🎁</span> 我的獎勵
      </button>
      <button :class="['nav-item', { active: $route.name === 'Settings' }]" @click="$router.push('/settings')">
        <span class="nav-icon">⚙️</span> 設置
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { hasActiveChild } from './composables/device'

const route = useRoute()
const isQuizPage = computed(() => route.name === 'Quiz')
// Reactive: check on each route change
const childActive = computed(() => hasActiveChild())
const showNav = computed(() => childActive.value && !isQuizPage.value)
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
