<template>
  <div class="page">
    <button class="btn btn-outline" @click="$router.back()" style="margin-bottom: 16px;">← 返回</button>
    <h1 style="margin-bottom: 24px;">🔗 綁定子女設備</h1>

    <div class="card" style="padding: 24px;">
      <p style="margin-bottom: 20px; color: var(--text-light); text-align: center;">
        請在子女設備上打開 App，取得 6 位綁定碼或 QR Code
      </p>

      <!-- 輸入綁定碼 (預設顯示，主要方式) -->
      <div class="section-title">⌨️ 輸入綁定碼</div>
      <div style="display: flex; gap: 10px;">
        <input
          v-model="codeInput"
          class="code-input"
          placeholder="輸入 6 位碼"
          maxlength="6"
          @keyup.enter="bindByCode"
          style="font-family: 'Courier New', monospace; text-transform: uppercase;"
        />
        <button class="btn btn-primary" @click="bindByCode" :disabled="!codeInput || binding" style="white-space: nowrap;">
          {{ binding ? '...' : '確認' }}
        </button>
      </div>

      <!-- 分隔線 -->
      <div class="divider">
        <span>或者</span>
      </div>

      <!-- 掃碼 (次要方式) -->
      <div class="section-title">📷 掃描 QR Code</div>
      <div v-if="!scanning" class="scan-btn" @click="startScan">
        <span style="font-size: 32px;">📷</span>
        <p>點擊掃描</p>
      </div>
      <div v-if="scanning" class="scanner-container">
        <div id="qr-reader"></div>
        <button class="btn btn-outline" @click="stopScan" style="width: 100%; margin-top: 8px;">取消掃描</button>
      </div>
    </div>

    <!-- 確認綁定 (輸入子女姓名) -->
    <div v-if="pendingToken" class="card" style="margin-top: 16px; padding: 24px;">
      <div style="background: #e8f5e9; padding: 12px; border-radius: 8px; margin-bottom: 16px; text-align: center;">
        ✅ 已驗證設備！請輸入子女姓名：
      </div>
      <input
        v-model="childName"
        class="code-input"
        placeholder="例如：小明"
        style="font-size: 18px; letter-spacing: normal; text-transform: none;"
        @keyup.enter="confirmBind"
      />
      <div style="display: flex; gap: 10px; margin-top: 12px;">
        <button class="btn btn-outline" @click="cancelPending" style="flex: 1;">取消</button>
        <button class="btn btn-primary" @click="confirmBind" :disabled="!childName || binding" style="flex: 2;">
          {{ binding ? '綁定中...' : '🎉 完成綁定' }}
        </button>
      </div>
    </div>

    <!-- 已綁定子女 -->
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

const scanning = ref(false)
const codeInput = ref('')
const binding = ref(false)
const pendingToken = ref('')
const childName = ref('')
const children = ref([])
let html5QrScanner = null

async function loadChildren() {
  try {
    const { data } = await api.get('/children')
    children.value = data
  } catch {
    // ignore
  }
}

// ─── 掃碼 ───
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
          pendingToken.value = (payload.token && payload.type === 'device_bind') ? payload.token : decodedText
        } catch {
          pendingToken.value = decodedText
        }
        toast.success('已掃描成功！')
      },
      () => {}
    )
  } catch (err) {
    toast.error('無法啟動相機，請改用輸入碼')
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

// ─── 輸入碼 ───
function bindByCode() {
  if (!codeInput.value) return
  pendingToken.value = codeInput.value.toUpperCase().trim()
  codeInput.value = ''
  toast.success('碼已輸入，請填寫子女姓名')
}

// ─── 確認綁定 ───
async function confirmBind() {
  if (!pendingToken.value || !childName.value) return
  binding.value = true
  try {
    const payload = { child_name: childName.value }
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
    toast.error(err.response?.data?.detail || '綁定失敗，碼可能已過期')
    pendingToken.value = ''
    childName.value = ''
  } finally {
    binding.value = false
  }
}

function cancelPending() {
  pendingToken.value = ''
  childName.value = ''
}

// ─── 解綁 ───
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

onMounted(() => { loadChildren() })
onUnmounted(() => { stopScan() })
</script>

<style scoped>
.section-title {
  font-size: 0.9rem; font-weight: 700; color: #666; margin-bottom: 8px;
}

.code-input {
  flex: 1; font-size: 24px; font-weight: 700; letter-spacing: 6px; text-align: center;
  border: 2px solid #e0e0e0; border-radius: 12px; padding: 14px; outline: none;
  box-sizing: border-box;
}
.code-input:focus { border-color: var(--primary); }

.divider {
  display: flex; align-items: center; text-align: center; margin: 20px 0;
  color: #ccc; font-size: 0.85rem;
}
.divider::before, .divider::after {
  content: ''; flex: 1; border-bottom: 1px solid #e8e8e8;
}
.divider span { padding: 0 12px; }

.scan-btn {
  border: 2px dashed #ccc; border-radius: 12px; padding: 24px; text-align: center;
  cursor: pointer; transition: all 0.2s;
}
.scan-btn:hover { border-color: var(--primary); background: #f8faff; }
.scan-btn p { margin-top: 8px; color: #999; font-size: 0.9rem; }

.scanner-container { margin-top: 8px; }
#qr-reader { border-radius: 12px; overflow: hidden; }

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
</style>
