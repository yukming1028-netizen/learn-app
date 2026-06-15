<template>
  <div class="page">
    <button class="btn btn-outline" @click="$router.back()" style="margin-bottom: 16px;">← 返回</button>
    <h1 style="margin-bottom: 24px;">🔗 綁定子女</h1>

    <div class="card" style="text-align: center; padding: 40px;">
      <div v-if="!qrToken">
        <p style="margin-bottom: 20px; color: var(--text-light);">
          點擊下方按鈕生成 QR Code，讓孩子掃描或直接輸入綁定碼即可綁定。
        </p>
        <button class="btn btn-primary" @click="generateQR" :disabled="loading">
          {{ loading ? '生成中...' : '📱 生成綁定碼' }}
        </button>
      </div>

      <div v-else>
        <!-- Tab switcher -->
        <div style="display: flex; gap: 8px; margin-bottom: 20px; justify-content: center;">
          <button class="tab-btn" :class="{ active: activeTab === 'qr' }" @click="activeTab = 'qr'">📱 掃碼</button>
          <button class="tab-btn" :class="{ active: activeTab === 'code' }" @click="activeTab = 'code'">🔑 綁定碼</button>
        </div>

        <!-- QR Code tab -->
        <div v-if="activeTab === 'qr'">
          <p style="margin-bottom: 16px;">請讓孩子掃描以下 QR Code：</p>
          <div style="display: inline-block; background: white; padding: 20px; border-radius: 12px; border: 2px solid var(--primary); margin-bottom: 16px;">
            <div ref="qrContainer"></div>
          </div>
        </div>

        <!-- Bind code tab -->
        <div v-if="activeTab === 'code'">
          <p style="margin-bottom: 16px;">讓孩子輸入以下 6 位綁定碼：</p>
          <div style="display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); padding: 24px 40px; border-radius: 16px; margin-bottom: 16px;">
            <div style="font-size: 36px; font-weight: 800; letter-spacing: 12px; color: white; font-family: 'Courier New', monospace;">
              {{ bindCode }}
            </div>
          </div>
        </div>

        <!-- Shared: copy button + expiry -->
        <div style="display: flex; gap: 12px; justify-content: center; margin-bottom: 16px;">
          <button class="btn btn-primary" @click="copyCode" style="min-width: 160px;">
            {{ copied ? '✅ 已複製' : '📋 一鍵複製綁定碼' }}
          </button>
        </div>

        <div style="background: #fff3e0; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
          ⏰ 綁定碼將在 5 分鐘後失效
        </div>

        <button class="btn btn-outline" @click="resetQR">重新生成</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import api from '../composables/api'
import { useToast } from '../composables/useToast'
import QRCode from 'qrcode'

const toast = useToast()
const qrToken = ref('')
const bindCode = ref('')
const loading = ref(false)
const qrContainer = ref(null)
const activeTab = ref('qr')
const copied = ref(false)

async function generateQR() {
  loading.value = true
  try {
    const { data } = await api.post('/binding/qr/generate')
    qrToken.value = data.qr_token
    bindCode.value = data.bind_code

    await nextTick()

    // Generate QR code image
    const canvas = document.createElement('canvas')
    await QRCode.toCanvas(canvas, data.qr_token, { width: 250, margin: 2 })
    if (qrContainer.value) {
      qrContainer.value.innerHTML = ''
      qrContainer.value.appendChild(canvas)
    }

    toast.success('綁定碼已生成！')
  } catch (err) {
    toast.error('生成失敗')
  } finally {
    loading.value = false
  }
}

async function copyCode() {
  try {
    await navigator.clipboard.writeText(bindCode.value)
    copied.value = true
    toast.success(`綁定碼 ${bindCode.value} 已複製`)
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback
    const input = document.createElement('input')
    input.value = bindCode.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

function resetQR() {
  qrToken.value = ''
  bindCode.value = ''
  activeTab.value = 'qr'
}
</script>

<style scoped>
.tab-btn {
  padding: 8px 20px;
  border: 2px solid #e0e0e0;
  background: transparent;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  color: #666;
}
.tab-btn.active {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}
</style>
