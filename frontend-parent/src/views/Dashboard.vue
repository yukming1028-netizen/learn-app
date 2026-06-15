<template>
  <div class="page">
    <h1 style="margin-bottom: 24px;">📊 學習儀表板</h1>

    <div v-if="loading" style="text-align: center; padding: 40px; color: var(--text-light);">載入中...</div>

    <template v-else>
      <!-- Grade update prompts -->
      <div v-for="prompt in gradePrompts" :key="prompt.child_id" class="card" style="background: #FFF3E0; padding: 16px; margin-bottom: 12px; border-left: 4px solid #FF9800;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="font-size: 28px;">📈</span>
          <div style="flex: 1;">
            <div style="font-weight: 600;">{{ prompt.child_name }} 年級升級提醒</div>
            <div style="font-size: 0.85rem; color: #666;">
              {{ prompt.grade_label }} → {{ prompt.suggested_label }}？
            </div>
          </div>
        </div>
        <div style="display: flex; gap: 8px; margin-top: 12px;">
          <button class="btn btn-outline btn-sm" @click="dismissGrade(prompt.child_id)">下次再說</button>
          <button class="btn btn-primary btn-sm" @click="confirmGrade(prompt.child_id)">確認升級</button>
        </div>
      </div>

      <!-- Children cards -->
      <div v-if="children.length === 0" class="card" style="text-align: center; padding: 40px;">
        <p style="margin-bottom: 16px; color: var(--text-light);">還沒有子女，先新增子女吧！</p>
        <router-link to="/bind" class="btn btn-primary">前往管理</router-link>
      </div>

      <div v-else>
        <!-- Summary stats -->
        <div class="grid grid-3" style="margin-bottom: 24px;">
          <div class="card stat-card">
            <div class="stat-value">{{ children.length }}</div>
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
              <span>⏱️ {{ child.total_study_minutes }} 分</span>
            </div>
            <div v-if="child.stickers && child.stickers.length" style="margin-top: 8px; font-size: 20px;">
              {{ child.stickers.join(' ') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Devices section -->
      <div style="margin-top: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3>📱 已綁定設備（{{ devices.length }}/{{ maxDevices }}）</h3>
          <router-link to="/bind" class="btn btn-outline btn-sm">管理</router-link>
        </div>
        <div v-if="devices.length === 0" class="card" style="text-align: center; padding: 20px;">
          <p style="color: var(--text-light); font-size: 0.9rem;">尚未綁定設備</p>
        </div>
        <div v-else>
          <div v-for="dev in devices" :key="dev.id" class="card" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; margin-bottom: 8px;">
            <span style="font-size: 24px;">📱</span>
            <div style="flex: 1;">
              <div style="font-weight: 600; font-size: 14px;">{{ dev.device_uuid.substring(0, 20) }}...</div>
              <div style="font-size: 0.8rem; color: var(--text-light);">{{ formatDate(dev.bound_at) }}</div>
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
const devices = ref([])
const gradePrompts = ref([])
const loading = ref(true)
const maxDevices = 3

const totalQuestions = computed(() => children.value.reduce((s, c) => s + c.total_questions, 0))
const overallAccuracy = computed(() => {
  const totalQ = children.value.reduce((s, c) => s + c.total_questions, 0)
  const totalC = children.value.reduce((s, c) => s + c.total_correct, 0)
  return totalQ > 0 ? Math.round(totalC / totalQ * 100) : 0
})

function gradeName(grade) {
  const names = {0: '學前預備', 1: '小一', 2: '小二', 3: '小三', 4: '小四', 5: '小五', 6: '小六'}
  return names[grade] || `Grade ${grade}`
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-HK')
}

async function loadAll() {
  loading.value = true
  try {
    const [childrenRes, devicesRes] = await Promise.all([
      api.get('/children'),
      api.get('/binding/devices'),
    ])
    children.value = childrenRes.data
    devices.value = devicesRes.data

    // Check grade prompts for each child
    const prompts = []
    for (const child of children.value) {
      try {
        const { data } = await api.get(`/children/${child.id}/grade-check`)
        if (data.needs_prompt) {
          prompts.push(data)
        }
      } catch {}
    }
    gradePrompts.value = prompts
  } catch (err) {
    toast.error('載入失敗')
  } finally {
    loading.value = false
  }
}

async function confirmGrade(childId) {
  try {
    const { data } = await api.post(`/children/${childId}/grade/confirm`)
    toast.success(data.message)
    gradePrompts.value = gradePrompts.value.filter(p => p.child_id !== childId)
    await loadAll()
  } catch {
    toast.error('更新失敗')
  }
}

async function dismissGrade(childId) {
  try {
    await api.post(`/children/${childId}/grade/dismiss`)
    toast.success('下次9月1日再提醒')
    gradePrompts.value = gradePrompts.value.filter(p => p.child_id !== childId)
  } catch {
    toast.error('操作失敗')
  }
}

onMounted(loadAll)
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 0.85rem; color: var(--text-light); margin-top: 4px; }
.btn-sm { padding: 6px 12px; font-size: 0.85rem; }
</style>
