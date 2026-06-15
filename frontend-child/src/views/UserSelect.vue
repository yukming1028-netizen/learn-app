<template>
  <div class="user-select">
    <div class="header">
      <h1>誰在使用？</h1>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner">⏳</div>
      <p>載入中...</p>
    </div>

    <!-- Bound: show children grid + "+" -->
    <div v-else-if="bound" class="children-grid">
      <div
        v-for="child in children"
        :key="child.id"
        class="child-card"
        @click="selectChild(child)"
      >
        <div class="child-avatar">{{ child.avatar || '🐻' }}</div>
        <div class="child-name">{{ child.name }}</div>
        <div class="child-grade">{{ child.grade_label }}</div>
      </div>

      <!-- "+" Add new user -->
      <div class="child-card add-card" @click="showAddModal = true">
        <div class="add-icon">＋</div>
        <div class="add-text">新增用戶</div>
      </div>
    </div>

    <!-- Not bound: show bind prompt -->
    <div v-else class="not-bound">
      <div class="empty-icon">📱</div>
      <p class="empty-title">設備尚未綁定</p>
      <p class="empty-hint">請聯繫家長掃描綁定碼</p>
      <button class="btn-generate" @click="showBindModal = true">
        ＋ 生成綁定碼
      </button>
    </div>

    <!-- Bind code modal -->
    <div v-if="showBindModal" class="modal-overlay" @click.self="showBindModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showBindModal = false">✕</button>

        <div v-if="generating" class="modal-loading">
          <div class="spinner">⏳</div>
          <p>生成中...</p>
        </div>

        <div v-else-if="bindData">
          <h3>家長請掃描或輸入綁定碼</h3>

          <!-- Bind Code -->
          <div class="code-section">
            <p class="code-label">或輸入綁定碼</p>
            <div class="code-display">
              <span v-for="(ch, i) in bindData.bind_code" :key="i" class="code-char">{{ ch }}</span>
            </div>
            <button class="btn-copy" @click="copyCode">📋 複製綁定碼</button>
          </div>

          <div class="expire-hint">
            ⏰ 綁定碼 {{ expireCountdown }} 秒後過期
          </div>

          <!-- Waiting status -->
          <div v-if="!bound" class="waiting-status">
            <p class="waiting-text">⏳ 等待家長綁定中...</p>
            <button class="btn-check" @click="checkStatus">🔄 檢查狀態</button>
          </div>
          <div v-else class="bound-status">
            <p class="bound-text">✅ 綁定成功！</p>
            <button class="btn-done" @click="onBoundSuccess">繼續 →</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add child modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showAddModal = false">✕</button>
        <h3>新增用戶</h3>

        <div class="add-form">
          <div class="form-row">
            <label>頭像</label>
            <div class="avatar-picker">
              <button
                v-for="a in avatars"
                :key="a"
                :class="['avatar-btn', { selected: newChild.avatar === a }]"
                @click="newChild.avatar = a"
              >{{ a }}</button>
            </div>
          </div>

          <div class="form-row">
            <label>名稱</label>
            <input v-model="newChild.name" type="text" placeholder="輸入名稱" maxlength="20" class="form-input" />
          </div>

          <div class="form-row">
            <label>年級</label>
            <select v-model="newChild.grade" class="form-input">
              <option :value="0">學前預備</option>
              <option :value="1">小一</option>
              <option :value="2">小二</option>
              <option :value="3">小三</option>
              <option :value="4">小四</option>
              <option :value="5">小五</option>
              <option :value="6">小六</option>
            </select>
          </div>

          <button
            class="btn-submit"
            :disabled="!newChild.name.trim() || creating"
            @click="createChild"
          >{{ creating ? '建立中...' : '建立' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getDeviceUUID, setDeviceToken, setActiveChild, hasDeviceToken } from '../composables/device'
import { childAPI } from '../composables/api'

const router = useRouter()
const deviceUuid = getDeviceUUID()

const loading = ref(true)
const bound = ref(false)
const children = ref([])
const showBindModal = ref(false)
const showAddModal = ref(false)
const generating = ref(false)
const bindData = ref(null)
const expireCountdown = ref(300)
let pollTimer = null
let countdownTimer = null

// Add child form
const avatars = ['🐻', '🐰', '🐱', '🐶', '🦊', '🐼', '🐨', '🦁']
const newChild = reactive({ name: '', grade: 1, avatar: '🐻' })
const creating = ref(false)

async function checkBindingStatus() {
  try {
    const { data } = await childAPI.getDeviceStatus(deviceUuid)
    bound.value = data.bound

    if (data.bound) {
      if (data.device_token) {
        setDeviceToken(data.device_token)
      }
      const { data: childList } = await childAPI.getDeviceChildren(deviceUuid)
      children.value = childList
    }
  } catch (err) {
    console.error('Status check failed', err)
  } finally {
    loading.value = false
  }
}

async function checkStatus() {
  await checkBindingStatus()
  if (bound.value) {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
    if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null }
  }
}

function selectChild(child) {
  setActiveChild({ id: child.id, name: child.name, avatar: child.avatar })
  router.push('/')
}

async function createChild() {
  if (!newChild.name.trim()) return
  creating.value = true
  try {
    const { data } = await childAPI.deviceCreateChild(deviceUuid, {
      name: newChild.name.trim(),
      grade: newChild.grade,
      avatar: newChild.avatar,
    })
    // Add to local list
    children.value.push(data)
    // Auto-select the new child
    selectChild(data)
  } catch (err) {
    console.error('Create child failed', err)
    const msg = err.response?.data?.detail || '建立失敗'
    alert(msg)
  } finally {
    creating.value = false
  }
}

async function generateCode() {
  generating.value = true
  try {
    const { data } = await childAPI.generateBindCode(deviceUuid)
    bindData.value = data
    expireCountdown.value = 300

    if (countdownTimer) clearInterval(countdownTimer)
    countdownTimer = setInterval(() => {
      expireCountdown.value--
      if (expireCountdown.value <= 0) {
        clearInterval(countdownTimer)
        countdownTimer = null
        bindData.value = null
      }
    }, 1000)

    if (pollTimer) clearInterval(pollTimer)
    pollTimer = setInterval(async () => {
      await checkBindingStatus()
      if (bound.value) {
        clearInterval(pollTimer)
        pollTimer = null
      }
    }, 3000)
  } catch (err) {
    console.error('Generate failed', err)
    alert('生成失敗，請重試')
  } finally {
    generating.value = false
  }
}

function copyCode() {
  const code = bindData.value?.bind_code
  if (!code) return
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(code)
  } else {
    const ta = document.createElement('textarea')
    ta.value = code
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
  alert('已複製：' + code)
}

function onBoundSuccess() {
  showBindModal.value = false
  if (children.value.length === 1) {
    selectChild(children.value[0])
  }
}

watch(showBindModal, (val) => {
  if (val && !bindData.value && !bound.value) {
    generateCode()
  }
})

watch(showAddModal, (val) => {
  if (val) {
    newChild.name = ''
    newChild.grade = 1
    newChild.avatar = '🐻'
  }
})

onMounted(async () => {
  await checkBindingStatus()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style scoped>
.user-select {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.header { text-align: center; margin-bottom: 32px; }
.header h1 { color: white; font-size: 28px; margin: 0; }

.loading-state, .not-bound {
  text-align: center;
  padding-top: 80px;
  color: white;
}
.spinner { font-size: 48px; animation: bounce 1s infinite; }
@keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

.empty-icon { font-size: 72px; margin-bottom: 16px; }
.empty-title { font-size: 20px; font-weight: 600; color: white; }
.empty-hint { color: rgba(255,255,255,0.7); margin-top: 4px; margin-bottom: 24px; }

.btn-generate {
  background: white; color: #667eea; border: none; border-radius: 16px;
  padding: 14px 32px; font-size: 18px; font-weight: 600; cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.btn-generate:active { transform: scale(0.97); }

.children-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  max-width: 420px;
  margin: 0 auto;
}

.child-card {
  background: white; border-radius: 20px; padding: 20px 12px;
  text-align: center; cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.child-card:active { transform: scale(0.95); }
.child-avatar { font-size: 48px; margin-bottom: 8px; }
.child-name { font-size: 16px; font-weight: 600; color: #333; }
.child-grade { font-size: 12px; color: #888; margin-top: 4px; }

.add-card {
  background: rgba(255,255,255,0.2); border: 2px dashed rgba(255,255,255,0.6);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 120px;
}
.add-icon { font-size: 40px; color: white; font-weight: 300; }
.add-text { font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 8px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 20px;
}
.modal-content {
  background: white; border-radius: 20px; padding: 28px 24px;
  max-width: 360px; width: 100%; position: relative;
}
.modal-close {
  position: absolute; top: 12px; right: 12px;
  background: none; border: none; font-size: 20px; cursor: pointer;
  color: #999;
}
.modal-content h3 { font-size: 18px; text-align: center; margin-bottom: 20px; }
.modal-loading { text-align: center; padding: 40px 0; }
.modal-loading .spinner { font-size: 36px; }

.code-section { margin-bottom: 20px; }
.code-label { font-size: 12px; color: #888; margin-bottom: 8px; }
.code-display {
  display: flex; justify-content: center; gap: 8px; margin-bottom: 12px;
}
.code-char {
  width: 36px; height: 44px; display: flex; align-items: center; justify-content: center;
  background: #667eea; color: white; border-radius: 8px;
  font-size: 22px; font-weight: 700;
}
.btn-copy {
  width: 100%; background: #f0f0f0; border: none; border-radius: 10px;
  padding: 10px; font-size: 14px; cursor: pointer;
}
.expire-hint { text-align: center; color: #e74c3c; font-size: 13px; margin-bottom: 16px; }
.waiting-status, .bound-status { text-align: center; padding-top: 12px; }
.waiting-text { color: #888; margin-bottom: 12px; }
.btn-check {
  background: #667eea; color: white; border: none; border-radius: 10px;
  padding: 10px 24px; cursor: pointer;
}
.bound-text { color: #27ae60; font-size: 18px; margin-bottom: 12px; }
.btn-done {
  background: #27ae60; color: white; border: none; border-radius: 10px;
  padding: 10px 32px; font-size: 16px; cursor: pointer;
}

/* Add child form */
.add-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: flex; flex-direction: column; gap: 8px; }
.form-row label { font-size: 14px; font-weight: 600; color: #555; }
.form-input {
  padding: 10px 12px; border: 2px solid #e0e0e0; border-radius: 10px;
  font-size: 16px; outline: none;
}
.form-input:focus { border-color: #667eea; }
.avatar-picker { display: flex; flex-wrap: wrap; gap: 8px; }
.avatar-btn {
  width: 44px; height: 44px; border-radius: 10px; border: 2px solid #e0e0e0;
  background: white; font-size: 24px; cursor: pointer;
}
.avatar-btn.selected { border-color: #667eea; background: #f0f0ff; }
.btn-submit {
  width: 100%; padding: 14px; font-size: 16px; font-weight: 600;
  background: #667eea; color: white; border: none; border-radius: 12px;
  cursor: pointer; margin-top: 8px;
}
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-submit:active:not(:disabled) { transform: scale(0.98); }
</style>
