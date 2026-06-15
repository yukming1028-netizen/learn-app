<template>
  <div class="settings">
    <h2>⚙️ 設置</h2>

    <!-- Current child -->
    <div class="current-child" v-if="childInfo">
      <span class="avatar">{{ childInfo.avatar }}</span>
      <div>
        <div class="label">當前用戶</div>
        <div class="name">{{ childInfo.name }}</div>
      </div>
    </div>

    <!-- Switch user -->
    <div class="section">
      <button class="btn-primary full" @click="$router.push('/select')">
        👥 切換用戶
      </button>
    </div>

    <!-- Stats -->
    <div class="section stats" v-if="childInfo">
      <h3>學習統計</h3>
      <div class="stat-row">
        <span>已回答題數</span>
        <span class="stat-val">{{ info.total_questions || 0 }}</span>
      </div>
      <div class="stat-row">
        <span>答對題數</span>
        <span class="stat-val">{{ info.total_correct || 0 }}</span>
      </div>
      <div class="stat-row">
        <span>正確率</span>
        <span class="stat-val">{{ accuracy }}%</span>
      </div>
    </div>

    <!-- Unbind device -->
    <div class="section danger">
      <h3>設備管理</h3>
      <p class="danger-hint">解除綁定後此設備將無法使用，需要重新綁定。</p>
      <button class="btn-danger" @click="confirmUnbind">解除設備綁定</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getActiveChild, clearAll, getDeviceUUID } from '../composables/device'
import { childAPI } from '../composables/api'

const router = useRouter()
const childInfo = getActiveChild()
const info = ref({})
const deviceUuid = getDeviceUUID()

const accuracy = computed(() => {
  if (!info.value.total_questions) return 0
  return Math.round((info.value.total_correct / info.value.total_questions) * 100)
})

async function confirmUnbind() {
  if (!confirm('確定要解除設備綁定嗎？此操作不可撤銷。')) return
  try {
    await childAPI.deviceUnbind(deviceUuid)
    clearAll()
    router.push('/select')
    location.reload()
  } catch (err) {
    alert('解除失敗，請重試')
  }
}

onMounted(async () => {
  try {
    const { data } = await childAPI.getMyInfo()
    info.value = data
  } catch (err) {
    console.error('Load failed', err)
  }
})
</script>

<style scoped>
.settings { padding: 20px; max-width: 480px; margin: 0 auto; }
.settings h2 { margin-bottom: 20px; }

.current-child {
  display: flex; align-items: center; gap: 12px;
  background: #f0f7ff; border-radius: 12px; padding: 16px; margin-bottom: 20px;
}
.current-child .avatar { font-size: 2rem; }
.current-child .label { font-size: 0.8rem; color: #666; }
.current-child .name { font-size: 1.2rem; font-weight: bold; }

.section { margin-bottom: 24px; }
.section h3 { font-size: 1rem; margin-bottom: 12px; color: #333; }

.btn-primary {
  background: #4a9eff; color: white; border: none; border-radius: 12px;
  padding: 12px 24px; font-size: 1rem; cursor: pointer;
}
.btn-primary.full { width: 100%; }

.stats { background: #fafafa; border-radius: 12px; padding: 16px; }
.stat-row {
  display: flex; justify-content: space-between; padding: 8px 0;
  border-bottom: 1px solid #eee;
}
.stat-val { font-weight: bold; color: #4a9eff; }

.danger-hint { font-size: 0.85rem; color: #999; margin-bottom: 12px; }
.btn-danger {
  background: #fee; color: #e74c3c; border: 1px solid #fcc;
  border-radius: 10px; padding: 10px 24px; cursor: pointer;
  width: 100%; font-size: 0.95rem;
}
</style>
