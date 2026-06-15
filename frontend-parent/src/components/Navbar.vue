<template>
  <nav class="navbar">
    <div class="navbar-brand">📚 親子學伴</div>
    <div class="navbar-links">
      <router-link to="/">儀表板</router-link>
      <router-link to="/plans">學習計劃</router-link>
      <router-link to="/bind">綁定子女</router-link>
      <a href="#" @click.prevent="logout">登出</a>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>
