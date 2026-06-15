<template>
  <div class="page">
    <h1 style="margin-bottom: 24px;">📊 學習儀表板</h1>

    <div v-if="loading" style="text-align: center; padding: 40px; color: var(--text-light);">載入中...</div>

    <template v-else>
      <!-- Children cards -->
      <div v-if="children.length === 0" class="card" style="text-align: center; padding: 40px;">
        <p style="margin-bottom: 16px; color: var(--text-light);">還沒有綁定子女</p>
        <router-link to="/bind" class="btn btn-primary">📷 掃碼 / 輸入碼綁定</router-link>
      </div>

      <div v-else>
        <!-- Summary stats -->
        <div class="grid grid-3" style="margin-bottom: 24px;">
          <div class="card stat-card">
            <div class="stat-value">{{ totalChildren }}</div>
            <div class="stat-label">子女數量</div>
          </div>
          <div class="card stat-card">
            <div class="stat-value">{{ totalQuestions }}</div>
            <div class="stat-label">總答題數</div>
          </div>
          <div class="card stat-card">
            <div class="stat-value">{{ overallAccuracy }}%</div>
            <div class="stat-label">平均正確率</div>
          </div>
        </div>

        <!-- Child cards -->
        <h3 style="margin-bottom: 16px;">子女概覽</h3>
        <div class="grid grid-3">
          <div v-for="child in children" :key="child.id" class="card" style="cursor: pointer;" @click="$router.push(`/children/${child.id}`)">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
              <span style="font-size: 32px;">{{ child.avatar }}</span>
              <div>
                <div style="font-weight: 600; font-size: 16px;">{{ child.name }}</div>
                <div style="font-size: 13px; color: var(--text-light);">{{ gradeName(child.grade) }}</div>
              </div>
            </div>
            <div style="display: flex; gap: 12px; font-size: 13px;">
              <span>📚 {{ child.total_questions }} 題</span>
              <span>✅ {{ Math.round(child.accuracy * 100) }}%</span>
              <span>⏱️ {{ child.total_study_minutes }} 分鐘</span>
            </div>
            <div v-if="child.stickers && child.stickers.length" style="margin-top: 8px; font-size: 20px;">
              {{ child.stickers.join(' ') }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../composables/api'
import { useToast } from '../composables/useToast'

const toast = useToast()
const children = ref([])
const loading = ref(true)

const totalChildren = computed(() => children.value.length)
const totalQuestions = computed(() => children.value.reduce((s, c) => s + c.total_questions, 0))
const overallAccuracy = computed(() => {
  const totalQ = children.value.reduce((s, c) => s + c.total_questions, 0)
  const totalC = children.value.reduce((s, c) => s + c.total_correct, 0)
  return totalQ > 0 ? Math.round(totalC / totalQ * 100) : 0
})

function gradeName(grade) {
  const names = {1:'小一',2:'小二',3:'小三',4:'小四',5:'小五',6:'小六',7:'中一',8:'中二',9:'中三'}
  return names[grade] || `Grade ${grade}`
}

onMounted(async () => {
  try {
    const { data } = await api.get('/children')
    children.value = data
  } catch (err) {
    toast.error('載入失敗')
  } finally {
    loading.value = false
  }
})
</script>
