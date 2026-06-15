<template>
  <div class="page">
    <button class="btn btn-outline" @click="$router.back()" style="margin-bottom: 16px;">← 返回</button>
    <h1 style="margin-bottom: 24px;">🔗 綁定子女設備</h1>

    <div class="card" style="padding: 24px;">
      <p style="margin-bottom: 16px; color: var(--text-light); text-align: center;">
        請在子女設備上打開 App，輸入綁定碼或掃描 QR Code
      </p>

      <!-- 統一輸入框：可手打碼 or 點相機掃碼 -->
      <div class="input-row">
        <button class="camera-btn" @click="toggleScan" :title="scanning ? '關閉掃描' : '掃描 QR Code'">
          {{ scanning ? '✕' : '📷' }}
        </button>
        <input
          v-model="codeInput"
          class="code-input"
          placeholder="輸入 6 位綁定碼"
          maxlength="6"
          @keyup.enter="submit"
          :disabled="scanning"
        />
      </div>

      <!-- 掃碼區域（點相機才展開） -->
      <div v-if="scanning" class="scanner-container">
        <div id="qr-reader"></div>
      </div>

      <!-- 唯一按鈕 -->
      <button class="btn btn-primary bind-btn" @click="submit" :disabled="!canSubmit || binding">
        {{ binding ? '綁定中...' : '🔗 綁定' }}
      </button>
    </div>

    <!-- 輸入姓名 + 年級 -->
    <div v-if="showNameInput" class="card" style="margin-top: 16px; padding: 24px;">
      <div style="background: #e8f5e9; padding: 12px; border-radius: 8px; margin-bottom: 16px; text-align: center;">
        ✅ 已驗證設備！請填寫子女資料：
      </div>

      <!-- 姓名 -->
      <label class="field-label">子女姓名</label>
      <input
        v-model="childName"
        class="code-input"
        placeholder="例如：小明"
        style="font-size: 18px; letter-spacing: normal; text-transform: none; margin-bottom: 16px;"
        @keyup.enter="confirmBind"
      />

      <!-- 年級 -->
      <label class="field-label">就讀年級</label>
      <div class="grade-grid">
        <button
          v-for="g in gradeOptions"
          :key="g.value"
          :class="['grade-btn', { active: selectedGrade === g.value }]"
          @click="selectedGrade = g.value"
        >{{ g.label }}</button>
      </div>

      <div style="display: flex; gap: 10px; margin-top: 16px;">
        <button class="btn btn-outline" @click="cancelNameInput" style="flex: 1;">取消</button>
        <button class="btn btn-primary" @click="confirmBind" :disabled="!childName || binding" style="flex: 2;">
          {{ binding ? '綁定中...' : '🎉 完成' }}
        </button>
      </div>
    </div>

    <!-- 已綁定子女 -->
    <div class="card" style="margin-top: 20px;" v-if="children.length > 0">
      <h3 style="margin-bottom: 12px;">已綁定子女（{{ children.length }}/3）</h3>
      <div v-for="child in children" :key="child.id" class="child-item">
        <span style="font-size: 24px;">{{ child.avatar }}</span>
        <div style="flex: 1;">
          <div style="font-weight: 600;">{{ child.name }}</div>
          <div style="font-size: 0.8rem; color: var(--text-light);">{{ gradeLabel(child.grade) }}</div>
        </div>
        <span style="font-size: 0.85rem; color: var(--text-light);">{{ child.total_questions }} 題</span>
        <button class="btn-unbind" @click="confirmUnbind(child)">解除綁定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../composables/api'
import { useToast } from '../composables/useToast'

const router = useRouter()
const toast = useToast()

const gradeOptions = [
  { value: 0, label: '學前預備' },
  { value: 1, label: '小一' },
  { value: 2, label: '小二' },
  { value: 3, label: '小三' },
  { value: 4, label: '小四' },
  { value: 5, label: '小五' },
  { value: 6, label: '小六' },
]

function gradeLabel(g) {
  const found = gradeOptions.find(o => o.value === g)
  return found ? found.label : ''
}

const scanning = ref(false)
const codeInput = ref('')
const binding = ref(false)
const resolvedToken = ref('')
const childName = ref('')
const selectedGrade = ref(0)
const children = ref([])
let html5QrScanner = null

const canSubmit = computed(() => codeInput.value.trim().length > 0)
const showNameInput = computed(() => !!resolvedToken.value)

async function loadChildren() {
  try {
    const { data } = await api.get('/children')
    children.value = data
  } catch {}
}

// ─── 唯一提交按鈕 ───
function submit() {
  if (!canSubmit.value) return
  resolvedToken.value = codeInput.value.toUpperCase().trim()
  codeInput.value = ''
}

// ─── 確認綁定 ───
async function confirmBind() {
  if (!resolvedToken.value || !childName.value) return
  binding.value = true
  try {
    const payload = {
      child_name: childName.value,
      grade: selectedGrade.value,
    }
    if (resolvedToken.value.length === 6 && /^[A-Z0-9]+$/.test(resolvedToken.value)) {
      payload.bind_code = resolvedToken.value
    } else {
      payload.qr_token = resolvedToken.value
    }
    const { data } = await api.post('/binding/device/verify', payload)
    toast.success(data.welcome_message || '綁定成功！')
    // 清空表單，留在綁定頁
    resolvedToken.value = ''
    childName.value = ''
    selectedGrade.value = 0
    await loadChildren()
  } catch (err) {
    toast.error(err.response?.data?.detail || '綁定失敗，碼可能已過期')
    resolvedToken.value = ''
    childName.value = ''
  } finally {
    binding.value = false
  }
}

function cancelNameInput() {
  resolvedToken.value = ''
  childName.value = ''
  selectedGrade.value = 0
}

// ─── 掃碼 ───
async function toggleScan() {
  if (scanning.value) { stopScan(); return }
  scanning.value = true
  try {
    const { Html5Qrcode } = await import('html5-qrcode')
    html5QrScanner = new Html5Qrcode('qr-reader')
    await html5QrScanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 200, height: 200 } },
      (decodedText) => {
        stopScan()
        let token = decodedText
        try { const p = JSON.parse(decodedText); if (p.token) token = p.token } catch {}
        resolvedToken.value = token
        toast.success('已掃描成功！')
      },
      () => {}
    )
  } catch {
    toast.error('無法啟動相機')
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

// ─── 解綁 ───
async function confirmUnbind(child) {
  if (!confirm(`確定要解除「${child.name}」的綁定嗎？`)) return
  try {
    await api.delete(`/binding/unbind/${child.id}`)
    toast.success(`已解除 ${child.name} 的綁定`)
    await loadChildren()
  } catch {
    toast.error('解除失敗')
  }
}

onMounted(() => { loadChildren() })
onUnmounted(() => { stopScan() })
</script>

<style scoped>
.input-row { display: flex; gap: 8px; margin-bottom: 12px; }
.camera-btn {
  flex-shrink: 0; width: 52px; border: 2px solid #e0e0e0; background: #f8f8f8;
  border-radius: 12px; font-size: 22px; cursor: pointer; transition: all 0.2s;
}
.camera-btn:hover { border-color: var(--primary); background: #f0f7ff; }
.code-input {
  flex: 1; font-size: 22px; font-weight: 700; letter-spacing: 6px; text-align: center;
  border: 2px solid #e0e0e0; border-radius: 12px; padding: 14px; outline: none;
  box-sizing: border-box; width: 100%;
}
.code-input:focus { border-color: var(--primary); }
.code-input:disabled { background: #f5f5f5; }

.bind-btn { width: 100%; font-size: 1.1rem; padding: 14px; }

.scanner-container { margin-bottom: 12px; }
#qr-reader { border-radius: 12px; overflow: hidden; }

.field-label {
  display: block; font-size: 0.9rem; font-weight: 700; color: #666; margin-bottom: 6px;
}

.grade-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
}
.grade-btn {
  padding: 10px 4px; border: 2px solid #e0e0e0; background: white;
  border-radius: 10px; cursor: pointer; font-size: 0.85rem; font-weight: 600;
  transition: all 0.15s; color: #666;
}
.grade-btn.active {
  border-color: var(--primary); background: var(--primary); color: white;
}

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
