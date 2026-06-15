<template>
  <div class="page">
    <button class="btn btn-outline" @click="$router.back()" style="margin-bottom: 16px;">← 返回</button>
    <h1 style="margin-bottom: 24px;">🔗 綁定子女</h1>

    <div class="card" style="text-align: center; padding: 40px;">
      <div v-if="!qrToken">
        <p style="margin-bottom: 20px; color: var(--text-light);">
          點擊下方按鈕生成 QR Code，讓孩子用 App 掃描即可綁定。
        </p>
        <button class="btn btn-primary" @click="generateQR" :disabled="loading">
          {{ loading ? '生成中...' : '📱 生成綁定 QR Code' }}
        </button>
      </div>

      <div v-else>
        <p style="margin-bottom: 16px;">請讓孩子掃描以下 QR Code：</p>

        <!-- QR Code displayed as text token (child app will scan it) -->
        <div style="display: inline-block; background: white; padding: 20px; border-radius: 12px; border: 2px solid var(--primary); margin-bottom: 16px;">
          <div ref="qrContainer"></div>
        </div>

        <div style="background: #fff3e0; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
          ⏰ QR Code 將在 5 分鐘後失效
        </div>

        <button class="btn btn-outline" @click="qrToken = null">重新生成</button>
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
const loading = ref(false)
const qrContainer = ref(null)

async function generateQR() {
  loading.value = true
  try {
    const { data } = await api.post('/binding/qr/generate')
    qrToken.value = data.qr_token

    await nextTick()

    // Generate QR code image
    const canvas = document.createElement('canvas')
    await QRCode.toCanvas(canvas, data.qr_token, { width: 250, margin: 2 })
    if (qrContainer.value) {
      qrContainer.value.innerHTML = ''
      qrContainer.value.appendChild(canvas)
    }

    toast.success('QR Code 已生成！')
  } catch (err) {
    toast.error('生成失敗')
  } finally {
    loading.value = false
  }
}
</script>
