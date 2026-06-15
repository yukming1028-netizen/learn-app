<template>
  <div class="page">
    <button class="btn btn-outline" @click="$router.back()" style="margin-bottom: 16px;">← 返回</button>
    <h1 style="margin-bottom: 24px;">🔗 綁定子女設備</h1>

    <div class="card" style="text-align: center; padding: 32px;">
      <p style="margin-bottom: 20px; color: var(--text-light);">
        請在子女設備上打開 App，取得 QR Code 或 6 位綁定碼，然後在這裡掃描或輸入。
      </p>

      <!-- Tab switcher -->
      <div style="display: flex; gap: 8px; margin-bottom: 24px; justify-content: center;">
        <button class="tab-btn" :class="{ active: activeTab === 'scan' }" @click="activeTab = 'scan'">📷 掃碼</button>
        <button class="tab-btn" :class="{ active: activeTab === 'code' }" @click="activeTab = 'code'">⌨️ 輸入碼</button>
      </div>

      <!-- Scan tab -->
      <div v-if="activeTab === 'scan'">
        <div class="scan-area" @click="startScan" v-if="!scanning">
          <div class="scan-placeholder">
            <span style="font-size: 48px;">📷</span>
            <p>點擊開始掃描 QR Code</p>
          </div>
        </div>
        <div v-if="scanning" class="scanner-container">
          <div ref="scannerContainer" id="qr-reader"></div>
          <button class="btn btn-outline" @click="stopScan">取消掃描</button>
        </div>
      </div>

      <!-- Code input tab -->
      <div v-if="activeTab === 'code'">
        <p style="margin-bottom: 12px;">請輸入子女設備上顯示的 6 位綁定碼：</p>
        <input
          v-model="codeInput"
          class="code-input"
          placeholder="ABC123"
          maxlength="6"
          @keyup.enter="bindByCode"
          style="font-family: 'Courier New', monospace; text-transform: uppercase;"
        />
        <button class="btn btn-primary" @click="bindByCode" :disabled="!codeInput || binding" style="margin-top: 16px; width: 100%;">
          {{ binding ? '綁定中...' : '✅ 確認綁定' }}
        </button>
      </div>

      <!-- Child name input (after scan/bind code resolved, before final bind) -->
      <div v-if="pendingToken" class="bind-confirm">
        <div style="background: #e8f5e9; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
          ✅ 已驗證設備！請輸入子女姓名：
        </div>
        <input
          v-model="childName"
          class="code-input"
          placeholder="例如：小明"
          @keyup.enter="confirmBind"
        />
        <button class="btn btn-primary" @click="confirmBind" :disabled="!childName || binding" style="margin-top: 12px; width: 100%;">
          {{ binding ? '綁定中...' : '🎉 完成綁定' }}
        </button>
        <button class="btn btn-text" @click="cancelPending" style="margin-top: 8px;">取消</button>
      </div>
    </div>

    <!-- Already bound children -->
    <div class="card" style="margin-top: 20px;" v-if="children.length > 0">
      <h3 style="margin-bottom: 12px;">已綁定子女（{{ children.length }}/3）</h3>
      <div v-for="child in children" :key="child.id" class="child-item">
        <span style="font-size: 24px;">{{ child.avatar }}</span>
        <span style="flex: 1; font-weight: 600;">{{ child.name }}</span>
        <span style="font-size: 0.85rem; color: var(--text-light);">
          {{ child.total_questions }} 題
        </span>
        <button class="btn-unbind" @click="confirmUnbind(child)">解除綁定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../composables/api'
import { useToast } from '../composables/useToast'

const router = useRouter()
const toast = useToast()

const activeTab = ref('scan')
const scanning = ref(false)
const codeInput = ref('')
const binding = ref(false)
const pendingToken = ref('')
const childName = ref('')
const children = ref([])
const scannerContainer = ref(null)
let html5QrScanner = null

async function loadChildren() {
  try {
    const { data } = await api.get('/children')
    children.value = data
  } catch {
    // ignore
  }
}

// ─── Scan ───
async function startScan() {
  scanning.value = true
  try {
    const { Html5Qrcode } = await import('html5-qrcode')
    html5QrScanner = new Html5Qrcode('qr-reader')
    await html5QrScanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 200, height: 200 } },
      (decodedText) => {
        stopScan()
        try {
          const payload = JSON.parse(decodedText)
          if (payload.token && payload.type === 'device_bind') {
            pendingToken.value = payload.token
            toast.success('已掃描成功！')
          } else {
            // Try using raw text as token
            pendingToken.value = decodedText
            toast.success('已掃描成功！')
          }
        } catch {
          pendingToken.value = decodedText
          toast.success('已掃描成功！')
        }
      },
      () => {}
    )
  } catch (err) {
    toast.error('無法啟動相機，請改用輸入碼')
    activeTab.value = 'code'
    scanning.value = false
  }
}

function stopScan() {
  scanning.value = false
  if (html5QrScanner) {
    html5QrScanner.stop().then(() => html5QrScanner.clear()).catch(() => {})
    html5QrScanner = null
  }
}

// ─── Code ───
async function bindByCode() {
  if (!codeInput.value) return
  binding.value = true
  try {
    // Use the bind code as token reference — backend resolves code → token
    pendingToken.value = codeInput.value.toUpperCase()
    codeInput.value = ''
    toast.success('綁定碼已驗證！')
  } catch (err) {
    toast.error('綁定碼無效或已過期')
  } finally {
    binding.value = false
  }
}

// ─── Confirm bind ───
async function confirmBind() {
  if (!pendingToken.value || !childName.value) return
  binding.value = true
  try {
    const payload = {
      child_name: childName.value,
    }
    // If pendingToken looks like a 6-char code, send as bind_code, else qr_token
    if (pendingToken.value.length === 6 && /^[A-Z0-9]+$/.test(pendingToken.value)) {
      payload.bind_code = pendingToken.value
    } else {
      payload.qr_token = pendingToken.value
    }
    const { data } = await api.post('/binding/device/verify', payload)
    toast.success(data.welcome_message || '綁定成功！')
    pendingToken.value = ''
    childName.value = ''
    await loadChildren()
    router.push('/dashboard')
  } catch (err) {
    toast.error(err.response?.data?.detail || '綁定失敗')
  } finally {
    binding.value = false
  }
}

function cancelPending() {
  pendingToken.value = ''
  childName.value = ''
}

// ─── Unbind ───
async function confirmUnbind(child) {
  if (!confirm(`確定要解除「${child.name}」的綁定嗎？`)) return
  try {
    await api.delete(`/binding/unbind/${child.id}`)
    toast.success(`已解除 ${child.name} 的綁定`)
    await loadChildren()
  } catch (err) {
    toast.error('解除失敗')
  }
}

onMounted(() => {
  loadChildren()
})

onUnmounted(() => {
  stopScan()
})
</script>

<style scoped>
.tab-btn {
  padding: 8px 24px; border: 2px solid #e0e0e0; background: transparent;
  border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 600;
  transition: all 0.2s; color: #666;
}
.tab-btn.active {
  border-color: var(--primary); background: var(--primary); color: white;
}

.scan-area {
  border: 3px dashed #ccc; border-radius: 16px; padding: 40px; cursor: pointer;
  transition: all 0.2s;
}
.scan-area:hover { border-color: var(--primary); background: #f8faff; }
.scan-placeholder { color: #999; }
.scan-placeholder p { margin-top: 12px; }

.scanner-container { margin-top: 16px; }
#qr-reader { border-radius: 12px; overflow: hidden; margin-bottom: 12px; }

.code-input {
  font-size: 24px; font-weight: 700; letter-spacing: 6px; text-align: center;
  border: 2px solid #e0e0e0; border-radius: 12px; padding: 16px; width: 100%;
  box-sizing: border-box; outline: none;
}
.code-input:focus { border-color: var(--primary); }

.bind-confirm { margin-top: 20px; }

.child-item {
  display: flex; align-items: center; gap: 12px; padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}
.child-item:last-child { border-bottom: none; }

.btn-unbind {
  background: #fee; color: #e74c3c; border: 1px solid #fcc;
  border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; cursor: pointer;
  white-space: nowrap;
}

.btn-text {
  background: none; border: none; color: #999; cursor: pointer;
  font-size: 0.9rem; text-decoration: underline;
}
</style>
