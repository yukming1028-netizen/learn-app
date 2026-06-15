<template>
  <div>
    <Navbar v-if="isLoggedIn" />
    <router-view />
    <div class="toast-container">
      <div v-for="t in toasts" :key="t.id" :class="['toast', `toast-${t.type}`]" @click="remove(t.id)">
        {{ t.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useToast } from './composables/useToast'
import Navbar from './components/Navbar.vue'

const { toasts, remove } = useToast()
const isLoggedIn = computed(() => !!localStorage.getItem('token'))
</script>
