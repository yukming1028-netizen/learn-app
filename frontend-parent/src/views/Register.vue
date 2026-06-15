<template>
  <div class="page" style="max-width: 400px; margin-top: 80px;">
    <div class="card">
      <h2 style="text-align: center; color: var(--primary); margin-bottom: 24px;">家長註冊</h2>
      <form @submit.prevent="handleRegister">
        <div style="margin-bottom: 16px;">
          <label style="display:block; margin-bottom: 6px; font-size: 14px;">郵箱</label>
          <input class="input" v-model="email" type="email" placeholder="your@email.com" required />
        </div>
        <div style="margin-bottom: 24px;">
          <label style="display:block; margin-bottom: 6px; font-size: 14px;">密碼</label>
          <input class="input" v-model="password" type="password" placeholder="至少6個字符" required />
        </div>
        <button class="btn btn-primary" style="width: 100%;" type="submit" :disabled="loading">
          {{ loading ? '註冊中...' : '註冊' }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 16px; font-size: 14px; color: var(--text-light);">
        已有帳號？<router-link to="/login" style="color: var(--secondary);">立即登入</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../composables/api'
import { useToast } from '../composables/useToast'

const router = useRouter()
const toast = useToast()
const email = ref('')
const password = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  try {
    const { data } = await api.post('/auth/register', { email: email.value, password: password.value })
    localStorage.setItem('token', data.access_token)
    toast.success('註冊成功！歡迎加入！')
    router.push('/')
  } catch (err) {
    toast.error(err.response?.data?.detail || '註冊失敗')
  } finally {
    loading.value = false
  }
}
</script>
