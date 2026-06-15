<template>
  <div class="page">
    <button class="btn btn-outline" @click="$router.back()" style="margin-bottom: 16px;">← 返回</button>
    <h1 style="margin-bottom: 24px;">🔗 綁定設備</h1>

    <!-- Bind input -->
    <div class="card" style="padding: 24px;">
      <p style="margin-bottom: 16px; color: var(--text-light); text-align: center;">
        請在子女設備上生成綁定碼，然後在此輸入或掃描
      </p>

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

      <div v-if="scanning" class="scanner-container">
        <div id="qr-reader"></div>
      </div>

      <button class="btn btn-primary bind-btn" @click="submit" :disabled="!canSubmit || binding">
        {{ binding ? '綁定中...' : '🔗 綁定設備' }}
      </button>
    </div>

    <!-- Bind result -->
    <div v-if="bindResult" class="card" style="margin-top: 16px; padding: 16px; background: #e8f5e9;">
      <div style="text-align: center;">
        <div style="font-size: 40px;">✅</div>
        <p style="font-weight: 600; margin-top: 8px;">{{ bindResult.message }}</p>
        <p v-if="bindResult.children_count !== undefined" style="color: #666; font-size: 0.9rem;">
          目前有 {{ bindResult.children_count }} 名子女
        </p>
        <div style="margin-top: 12px; display: flex; gap: 8px; justify-content: center;">
          <button class="btn btn-outline" @click="bindResult = null">繼續綁定</button>
          <button class="btn btn-primary" @click="$router.push('/')">查看儀表板</button>
        </div>
      </div>
    </div>

    <!-- Devices list -->
    <div class="card" style="margin-top: 20px;" v-if="devices.length > 0">
      <h3 style="margin-bottom: 12px;">已綁定設備（{{ devices.length }}/{{ maxDevices }}）</h3>
      <div v-for="dev in devices" :key="dev.id" class="device-item">
        <div>
          <div style="font-weight: 600;">📱 {{ dev.device_uuid.substring(0, 16) }}...</div>
          <div style="font-size: 0.8rem; color: var(--text-light);">
            綁定時間：{{ formatDate(dev.bound_at) }}
          </div>
        </div>
        <button class="btn-unbind" @click="confirmUnbindDevice(dev)">解除綁定</button>
      </div>
    </div>

    <!-- Children management -->
    <div class="card" style="margin-top: 20px;" v-if="children.length > 0 || showAddChild">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h3>子女管理（{{ children.length }}/3）</h3>
        <button v-if="!showAddChild && children.length < 3" class="btn btn-outline btn-sm" @click="showAddChild = true">+ 新增</button>
      </div>

      <!-- Add child form -->
      <div v-if="showAddChild" style="background: #f8f9fa; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
        <label class="field-label">姓名</label>
        <input v-model="newChild.name" class="form-input" placeholder="例如：小明" style="margin-bottom: 12px;" />

        <label class="field-label">年級</label>
        <div class="grade-grid" style="margin-bottom: 12px;">
          <button
            v-for="g in gradeOptions"
            :key="g.value"
            :class="['grade-btn', { active: newChild.grade === g.value }]"
            @click="newChild.grade = g.value"
          >{{ g.label }}</button>
        </div>

        <div style="display: flex; gap: 8px;">
          <button class="btn btn-outline" @click="cancelAddChild" style="flex: 1;">取消</button>
          <button class="btn btn-primary" @click="createChild" :disabled="!newChild.name || creatingChild" style="flex: 2;">
            {{ creatingChild ? '建立中...' : '✅ 建立' }}
          </button>
        </div>
      </div>

      <!-- Children list -->
      <div v-for="child in children" :key="child.id" class="child-item">
        <span style="font-size: 24px;">{{ child.avatar }}</span>
        <div style="flex: 1;">
          <div style="font-weight: 600;">{{ child.name }}</div>
          <div style="font-size: 0.8rem; color: var(--text-light);">{{ gradeLabel(child.grade) }}</div>
        </div>
        <span style="font-size: 0.85rem; color: var(--text-light);">{{ child.total_questions }} 題</span>
        <button class="btn-unbind" @click="confirmDeleteChild(child)">刪除</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../composables/api'
import { useToast } from '../composables/useToast'

const toast = useToast()

const gradeOptions = [
  { value: 0, label: '學前' },
  { value: 1, label: '小一' },
  { value: 2, label: '小二' },
  { value: 3, label: '小三' },
  { value: 4, label: '小四' },
  { value: 5, label: '小五' },
  { value: 6, label: '小六' },
]
const maxDevices = 3

function gradeLabel(g) {
  const found = gradeOptions.find(o => o.value === g)
  return found ? found.label : ''
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-HK')
}

// ─── Device binding ───
const scanning = ref(false)
const codeInput = ref('')
const binding = ref(false)
const bindResult = ref(null)
const devices = ref([])
let html5QrScanner = null

const canSubmit = computed(() => codeInput.value.trim().length > 0)

async function loadDevices() {
  try {
    const { data } = await api.get('/binding/devices')
    devices.value = data
  } catch {}
}

async function submit() {
  if (!canSubmit.value) return
  binding.value = true
  const code = codeInput.value.toUpperCase().trim()
  codeInput.value = ''
  try {
    const payload = {}
    if (code.length === 6 && /^[A-Z0-9]+$/.test(code)) {
      payload.bind_code = code
    } else {
      payload.qr_token = code
    }
    const { data } = await api.post('/binding/device/verify', payload)
    bindResult.value = data
    toast.success('設備綁定成功！')
    await loadDevices()
  } catch (err) {
    toast.error(err.response?.data?.detail || '綁定失敗，碼可能已過期')
  } finally {
    binding.value = false
  }
}

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
        codeInput.value = decodedText.length <= 6 ? decodedText : ''
        submitQR(decodedText)
      },
      () => {}
    )
  } catch {
    toast.error('無法啟動相機')
    scanning.value = false
  }
}

async function submitQR(qrToken) {
  binding.value = true
  try {
    const { data } = await api.post('/binding/device/verify', { qr_token: qrToken })
    bindResult.value = data
    toast.success('設備綁定成功！')
    await loadDevices()
  } catch (err) {
    toast.error(err.response?.data?.detail || '綁定失敗')
  } finally {
    binding.value = false
  }
}

function stopScan() {
  scanning.value = false
  if (html5QrScanner) {
    html5QrScanner.stop().then(() => html5QrScanner.clear()).catch(() => {})
    html5QrScanner = null
  }
}

async function confirmUnbindDevice(dev) {
  if (!confirm('確定要解除此設備的綁定嗎？設備上的子女將無法繼續使用。')) return
  try {
    await api.delete(`/binding/device/${dev.device_uuid}`)
    toast.success('已解除設備綁定')
    await loadDevices()
  } catch {
    toast.error('解除失敗')
  }
}

// ─── Children management ───
const children = ref([])
const showAddChild = ref(false)
const creatingChild = ref(false)
const newChild = ref({ name: '', grade: 0 })

async function loadChildren() {
  try {
    const { data } = await api.get('/children')
    children.value = data
  } catch {}
}

function cancelAddChild() {
  showAddChild.value = false
  newChild.value = { name: '', grade: 0 }
}

async function createChild() {
  if (!newChild.value.name) return
  creatingChild.value = true
  try {
    await api.post('/children', {
      name: newChild.value.name,
      grade: newChild.value.grade,
    })
    toast.success('子女建立成功！')
    cancelAddChild()
    await loadChildren()
  } catch (err) {
    toast.error(err.response?.data?.detail || '建立失敗')
  } finally {
    creatingChild.value = false
  }
}

async function confirmDeleteChild(child) {
  if (!confirm(`確定要刪除「${child.name}」嗎？所有學習記錄將被刪除。`)) return
  try {
    await api.delete(`/children/${child.id}`)
    toast.success(`已刪除 ${child.name}`)
    await loadChildren()
  } catch {
    toast.error('刪除失敗')
  }
}

onMounted(() => {
  loadDevices()
  loadChildren()
})
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

.device-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 0; border-bottom: 1px solid #f0f0f0;
}
.device-item:last-child { border-bottom: none; }

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

.btn-sm { padding: 6px 12px; font-size: 0.85rem; }

.field-label {
  display: block; font-size: 0.9rem; font-weight: 700; color: #666; margin-bottom: 6px;
}

.form-input {
  width: 100%; font-size: 16px; border: 2px solid #e0e0e0;
  border-radius: 10px; padding: 10px 14px; outline: none;
  box-sizing: border-box;
}
.form-input:focus { border-color: var(--primary); }

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
</style>
