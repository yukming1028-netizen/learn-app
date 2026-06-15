<template>
  <div class="home">
    <!-- 已有綁定的子女 → 顯示主頁 -->
    <div v-if="activeChild" class="welcome-screen">
      <div class="child-header">
        <span class="avatar">{{ activeChild.avatar }}</span>
        <span class="name">{{ activeChild.name }}</span>
      </div>
      <h2>歡迎返嚟學習！</h2>
      <p class="today-info" v-if="todayQuestions > 0">今日已完成 {{ todayQuestions }} 題</p>
      <p class="today-info" v-else>今日仲未開始答題呀～</p>

      <div class="subject-grid">
        <button v-for="s in subjects" :key="s.key" class="subject-card" @click="startQuiz(s.key)">
          <span class="subject-icon">{{ s.icon }}</span>
          <span class="subject-name">{{ s.name }}</span>
        </button>
      </div>

      <button class="btn-secondary" @click="$router.push('/settings')">⚙️ 切換 / 管理</button>
    </div>

    <!-- 未綁定 → 顯示 QR / 綁定碼等家長掃 -->
    <div v-else class="bind-screen">
      <h2>📱 等待家長綁定</h2>
      <p class="hint">請家長打開家長端 App，掃描下面嘅 QR Code 或者輸入綁定碼</p>

      <!-- 綁定碼 -->
      <div class="bind-code-box" v-if="bindCode">
        <div class="bind-code">{{ bindCode }}</div>
        <button class="btn-copy" @click="copyCode">📋 複製</button>
        <p class="expire-text" v-if="expiresIn > 0">{{ expiresIn }} 秒後過期</p>
      </div>

      <!-- QR Code (text placeholder) -->
      <div class="qr-box" v-if="qrToken">
        <img v-if="qrImageUrl" :src="qrImageUrl" alt="QR Code" class="qr-img" />
      </div>

      <button class="btn-primary" @click="generateCode" :disabled="loading">
        {{ loading ? '生成中...' : '🔄 重新生成綁定碼' }}
      </button>

      <!-- 已綁定的子女列表（切換） -->
      <div v-if="deviceChildren.length > 0" class="switch-section">
        <h3>已綁定的子女</h3>
        <div v-for="child in deviceChildren" :key="child.id" class="child-card" @click="selectChild(child)">
          <span class="avatar">{{ child.avatar || '🐻' }}</span>
          <div class="child-info">
            <span class="child-name">{{ child.name }}</span>
            <span class="child-parent">{{ child.parent_email }}</span>
          </div>
          <span class="arrow">→</span>
        </div>
      </div>

      <button class="btn-text" @click="refreshDeviceChildren" v-if="deviceChildren.length > 0">🔄 刷新</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDeviceUUID, hasActiveChild, getChildInfo, setActiveChild } from '../composables/device'
import { childAPI } from '../composables/api'

const router = useRouter()
const deviceUuid = getDeviceUUID()

const loading = ref(false)
const bindCode = ref('')
const qrToken = ref('')
const qrImageUrl = ref('')
const expiresIn = ref(0)
const todayQuestions = ref(0)
const deviceChildren = ref([])

let timer = null

const activeChild = computed(() => hasActiveChild() ? getChildInfo() : null)

const subjects = [
  { key: 'math', icon: '🔢', name: '數學' },
  { key: 'chinese', icon: '📝', name: '中文' },
  { key: 'english', icon: '🔤', name: '英文' },
  { key: 'science', icon: '🔬', name: '常識' },
]

async function generateCode() {
  loading.value = true
  try {
    const res = await childAPI.generateBindCode(deviceUuid)
    bindCode.value = res.data.bind_code
    qrToken.value = res.data.qr_token
    // Generate QR image via public API
    const qrPayload = JSON.stringify({ token: res.data.qr_token, type: 'device_bind' })
    qrImageUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrPayload)}`
    // Countdown
    const expires = new Date(res.data.expires_at).getTime()
    updateCountdown(expires)
    timer = setInterval(() => updateCountdown(expires), 1000)
  } catch (e) {
    alert('生成失敗，請重試')
  } finally {
    loading.value = false
  }
}

function updateCountdown(expiresTs) {
  const diff = Math.floor((expiresTs - Date.now()) / 1000)
  expiresIn.value = Math.max(0, diff)
  if (diff <= 0 && timer) {
    clearInterval(timer)
    bindCode.value = ''
    qrToken.value = ''
  }
}

function copyCode() {
  navigator.clipboard.writeText(bindCode.value)
  alert('已複製：' + bindCode.value)
}

async function refreshDeviceChildren() {
  try {
    const res = await childAPI.getDeviceChildren(deviceUuid)
    deviceChildren.value = res.data
  } catch (e) {
    // ignore
  }
}

function selectChild(child) {
  setActiveChild({ id: child.id, name: child.name, avatar: child.avatar })
  location.reload()
}

function startQuiz(subject) {
  router.push({ path: '/quiz', query: { subject } })
}

onMounted(() => {
  if (hasActiveChild()) {
    const child = getChildInfo()
    childAPI.getTodayProgress(child.id).then(res => {
      todayQuestions.value = res.data.total_questions || 0
    }).catch(() => {})
  } else {
    generateCode()
    refreshDeviceChildren()
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.home { padding: 20px; max-width: 480px; margin: 0 auto; }

.welcome-screen { text-align: center; }
.child-header { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 16px; }
.avatar { font-size: 2.5rem; }
.name { font-size: 1.5rem; font-weight: bold; }

.subject-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 24px 0; }
.subject-card {
  background: #fff; border: 2px solid #e0e0e0; border-radius: 16px;
  padding: 24px; cursor: pointer; transition: all 0.2s; text-align: center;
}
.subject-card:active { transform: scale(0.95); }
.subject-icon { display: block; font-size: 2rem; margin-bottom: 8px; }
.subject-name { font-size: 1.1rem; font-weight: 600; }

.bind-screen { text-align: center; padding-top: 20px; }
.hint { color: #666; font-size: 0.9rem; margin-bottom: 20px; }

.bind-code-box { margin: 16px 0; }
.bind-code {
  font-size: 2rem; font-weight: bold; letter-spacing: 8px;
  background: #f0f7ff; border: 2px dashed #4a9eff; border-radius: 12px;
  padding: 16px 24px; display: inline-block;
}
.btn-copy { margin-top: 8px; background: none; border: none; color: #4a9eff; cursor: pointer; font-size: 0.9rem; }
.expire-text { color: #999; font-size: 0.8rem; margin-top: 4px; }

.qr-box { margin: 16px auto; }
.qr-img { border-radius: 12px; border: 1px solid #e0e0e0; }

.btn-primary {
  background: #4a9eff; color: white; border: none; border-radius: 12px;
  padding: 12px 32px; font-size: 1rem; cursor: pointer; margin-top: 12px;
}
.btn-primary:disabled { opacity: 0.5; }

.btn-secondary {
  background: #f0f0f0; border: none; border-radius: 12px;
  padding: 10px 24px; font-size: 0.9rem; cursor: pointer; margin-top: 16px;
}

.switch-section { margin-top: 32px; text-align: left; }
.switch-section h3 { font-size: 1rem; margin-bottom: 12px; }
.child-card {
  display: flex; align-items: center; gap: 12px; background: #fff;
  border: 1px solid #e0e0e0; border-radius: 12px; padding: 12px 16px;
  margin-bottom: 8px; cursor: pointer; transition: all 0.2s;
}
.child-card:active { background: #f0f7ff; }
.child-info { flex: 1; display: flex; flex-direction: column; }
.child-name { font-weight: 600; }
.child-parent { font-size: 0.8rem; color: #999; }
.arrow { color: #ccc; }

.btn-text { background: none; border: none; color: #4a9eff; cursor: pointer; font-size: 0.85rem; margin-top: 8px; }
</style>
