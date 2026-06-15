<template>
  <div style="padding: 20px 20px 100px;">
    <h1 style="font-size: 24px; margin-bottom: 20px;">⚙️ 設置</h1>

    <div class="card" style="margin-bottom: 16px;">
      <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
        <span style="font-size: 48px;">{{ childInfo.avatar }}</span>
        <div>
          <div style="font-weight: 600; font-size: 18px;">{{ childInfo.name }}</div>
          <div style="color: #888; font-size: 13px;">設備：{{ deviceId }}</div>
        </div>
      </div>
    </div>

    <div class="card" style="margin-bottom: 16px;">
      <h3 style="margin-bottom: 8px;">🔔 提醒</h3>
      <p style="font-size: 13px; color: #888;">每日學習20分鐘，進步看得見！</p>
    </div>

    <div class="card" style="margin-bottom: 16px;">
      <h3 style="margin-bottom: 8px;">📱 關於</h3>
      <p style="font-size: 13px; color: #888;">親子學伴 v2.0.0</p>
      <p style="font-size: 13px; color: #888; margin-top: 4px;">讓學習，成為親子間最自然的對話。</p>
    </div>

    <button class="big-btn" style="background: #ffebee; color: var(--danger);" @click="handleUnbind">
      解除綁定
    </button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { getChildInfo, clearBinding, getDeviceUUID } from '../composables/device'

const router = useRouter()
const childInfo = getChildInfo()
const deviceId = getDeviceUUID().substring(0, 12)

function handleUnbind() {
  if (confirm('確定解除綁定嗎？所有本地資料將被清除。')) {
    clearBinding()
    window.location.reload()
  }
}
</script>
