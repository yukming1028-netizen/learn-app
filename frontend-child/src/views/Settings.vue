<template>
  <div class="settings">
    <h2>⚙️ 設置</h2>

    <!-- 當前子女 -->
    <div class="current-child" v-if="activeChild">
      <span class="avatar">{{ activeChild.avatar }}</span>
      <div>
        <div class="label">當前用戶</div>
        <div class="name">{{ activeChild.name }}</div>
      </div>
    </div>

    <!-- 切換子女 -->
    <div class="section" v-if="deviceChildren.length > 0">
      <h3>切換子女用戶</h3>
      <div v-for="child in deviceChildren" :key="child.id" class="child-row">
        <div class="child-info" @click="switchTo(child)">
          <span class="avatar">{{ child.avatar || '🐻' }}</span>
          <div>
            <span class="child-name">{{ child.name }}</span>
            <span class="active-badge" v-if="child.id === activeChild?.id">使用中</span>
          </div>
        </div>
        <button class="btn-unbind" @click="confirmUnbind(child)">解除綁定</button>
      </div>
      <button class="btn-refresh" @click="loadDeviceChildren">🔄 刷新列表</button>
    </div>

    <!-- 等待綁定 -->
    <div class="section" v-if="!activeChild">
      <p class="empty-hint">尚未綁定任何子女，請返回主頁生成綁定碼</p>
      <button class="btn-primary" @click="$router.push('/')">← 返回主頁</button>
    </div>

    <!-- 統計 -->
    <div class="section stats" v-if="activeChild">
      <h3>學習統計</h3>
      <div class="stat-row">
        <span>已回答題數</span>
        <span class="stat-val">{{ stats.total_questions }}</span>
      </div>
      <div class="stat-row">
        <span>答對題數</span>
        <span class="stat-val">{{ stats.total_correct }}</span>
      </div>
      <div class="stat-row">
        <span>正確率</span>
        <span class="stat-val">{{ accuracy }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDeviceUUID, getChildInfo, hasActiveChild, setActiveChild, clearActiveChild } from '../composables/device'
import { childAPI } from '../composables/api'

const deviceUuid = getDeviceUUID()
const activeChild = ref(hasActiveChild() ? getChildInfo() : null)
const deviceChildren = ref([])
const stats = ref({ total_questions: 0, total_correct: 0 })

const accuracy = computed(() => {
  if (!stats.value.total_questions) return 0
  return Math.round((stats.value.total_correct / stats.value.total_questions) * 100)
})

async function loadDeviceChildren() {
  try {
    const res = await childAPI.getDeviceChildren(deviceUuid)
    deviceChildren.value = res.data
  } catch (e) {
    // ignore
  }
}

function switchTo(child) {
  if (child.id === activeChild.value?.id) return
  setActiveChild({ id: child.id, name: child.name, avatar: child.avatar })
  activeChild.value = getChildInfo()
  loadStats()
}

async function loadStats() {
  if (!activeChild.value) return
  try {
    const res = await childAPI.getDeviceChildren(deviceUuid)
    const me = res.data.find(c => c.id === activeChild.value.id)
    if (me) {
      stats.value.total_questions = me.total_questions || 0
      stats.value.total_correct = me.total_correct || 0
    }
  } catch (e) {
    // ignore
  }
}

async function confirmUnbind(child) {
  if (!confirm(`確定要解除「${child.name}」的綁定嗎？解除後此設備將無法使用該子女帳號。`)) return
  try {
    await childAPI.unbindChild(deviceUuid, child.id)
    deviceChildren.value = deviceChildren.value.filter(c => c.id !== child.id)
    if (activeChild.value?.id === child.id) {
      clearActiveChild()
      activeChild.value = null
    }
    alert('已解除綁定')
    // Reload to update state
    if (deviceChildren.value.length > 0) {
      switchTo(deviceChildren.value[0])
    } else {
      location.reload()
    }
  } catch (e) {
    alert('解除綁定失敗')
  }
}

onMounted(() => {
  loadDeviceChildren()
  if (activeChild.value) loadStats()
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

.child-row {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border: 1px solid #e0e0e0; border-radius: 12px;
  padding: 12px 16px; margin-bottom: 8px;
}
.child-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.child-info .avatar { font-size: 1.5rem; }
.child-name { font-weight: 600; }
.active-badge {
  font-size: 0.7rem; background: #4a9eff; color: white;
  padding: 2px 8px; border-radius: 8px; margin-left: 8px;
}

.btn-unbind {
  background: #fee; color: #e74c3c; border: 1px solid #fcc;
  border-radius: 8px; padding: 6px 12px; font-size: 0.85rem; cursor: pointer;
}

.btn-refresh { background: none; border: none; color: #4a9eff; cursor: pointer; font-size: 0.85rem; }

.empty-hint { color: #999; margin-bottom: 12px; }
.btn-primary {
  background: #4a9eff; color: white; border: none; border-radius: 12px;
  padding: 10px 24px; font-size: 1rem; cursor: pointer;
}

.stats { background: #fafafa; border-radius: 12px; padding: 16px; }
.stat-row {
  display: flex; justify-content: space-between; padding: 8px 0;
  border-bottom: 1px solid #eee;
}
.stat-val { font-weight: bold; color: #4a9eff; }
</style>
