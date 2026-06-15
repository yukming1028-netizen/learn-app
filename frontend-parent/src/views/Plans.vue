<template>
  <div class="page">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <h1>📋 學習計劃</h1>
      <button class="btn btn-primary" @click="showForm = !showForm">{{ showForm ? '取消' : '新增計劃' }}</button>
    </div>

    <!-- New plan form -->
    <div v-if="showForm" class="card" style="margin-bottom: 16px;">
      <h3 style="margin-bottom: 16px;">新增學習計劃</h3>
      <div class="grid grid-2">
        <div>
          <label style="display:block; margin-bottom: 6px; font-size: 14px;">計劃名稱</label>
          <input class="input" v-model="form.title" placeholder="例如：數學強化訓練" />
        </div>
        <div>
          <label style="display:block; margin-bottom: 6px; font-size: 14px;">適用子女</label>
          <select class="input" v-model="form.child_id">
            <option :value="null">所有子女</option>
            <option v-for="c in children" :key="c.id" :value="c.id">{{ c.name }} ({{ gradeName(c.grade) }})</option>
          </select>
        </div>
        <div>
          <label style="display:block; margin-bottom: 6px; font-size: 14px;">每日學習分鐘</label>
          <input class="input" type="number" v-model.number="form.daily_minutes" />
        </div>
        <div>
          <label style="display:block; margin-bottom: 6px; font-size: 14px;">每日題數</label>
          <input class="input" type="number" v-model.number="form.daily_task_count" />
        </div>
      </div>
      <div style="margin-top: 12px;">
        <label style="display:block; margin-bottom: 6px; font-size: 14px;">學科（可多選）</label>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <label v-for="s in subjects" :key="s.key" style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
            <input type="checkbox" :value="s.key" v-model="form.subjects" />
            {{ s.label }}
          </label>
        </div>
      </div>
      <div style="margin-top: 16px;">
        <button class="btn btn-primary" @click="createPlan">建立計劃</button>
      </div>
    </div>

    <!-- Plans list -->
    <div v-if="loading" style="text-align: center; padding: 40px;">載入中...</div>
    <div v-else-if="plans.length === 0" class="card" style="text-align: center; padding: 40px; color: var(--text-light);">
      暫無學習計劃，點擊「新增計劃」建立
    </div>
    <div v-else class="grid grid-2">
      <div v-for="plan in plans" :key="plan.id" class="card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
          <h3>{{ plan.title }}</h3>
          <span :class="['badge', plan.is_active ? 'badge-success' : 'badge-warning']">
            {{ plan.is_active ? '✅ 啟用' : '⏸️ 暫停' }}
          </span>
        </div>
        <div style="font-size: 13px; color: var(--text-light); margin-bottom: 12px;">
          <div>📚 {{ plan.subjects.map(s => subjectLabels[s] || s).join('、') }}</div>
          <div>⏱️ 每日 {{ plan.daily_minutes }} 分鐘 / {{ plan.daily_task_count }} 題</div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-outline" @click="togglePlan(plan)">{{ plan.is_active ? '暫停' : '啟用' }}</button>
          <button class="btn btn-danger" @click="deletePlan(plan.id)">刪除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../composables/api'
import { useToast } from '../composables/useToast'

const toast = useToast()
const plans = ref([])
const children = ref([])
const loading = ref(true)
const showForm = ref(false)

const subjects = [
  { key: 'math', label: '數學' },
  { key: 'chinese', label: '語文' },
  { key: 'english', label: '英語' },
  { key: 'science', label: '科學' },
]
const subjectLabels = Object.fromEntries(subjects.map(s => [s.key, s.label]))

const form = ref({
  title: '',
  child_id: null,
  subjects: ['math'],
  daily_minutes: 20,
  daily_task_count: 5,
})

function gradeName(grade) {
  const names = {1:'小一',2:'小二',3:'小三',4:'小四',5:'小五',6:'小六',7:'中一',8:'中二',9:'中三'}
  return names[grade] || `Grade ${grade}`
}

async function loadPlans() {
  loading.value = true
  try {
    const [planRes, childRes] = await Promise.all([api.get('/plans'), api.get('/children')])
    plans.value = planRes.data
    children.value = childRes.data
  } catch (err) {
    toast.error('載入失敗')
  } finally {
    loading.value = false
  }
}

async function createPlan() {
  if (!form.value.title) {
    toast.error('請輸入計劃名稱')
    return
  }
  try {
    await api.post('/plans', form.value)
    toast.success('計劃建立成功！')
    showForm.value = false
    form.value = { title: '', child_id: null, subjects: ['math'], daily_minutes: 20, daily_task_count: 5 }
    await loadPlans()
  } catch (err) {
    toast.error('建立失敗')
  }
}

async function togglePlan(plan) {
  try {
    await api.patch(`/plans/${plan.id}/toggle`)
    await loadPlans()
  } catch (err) {
    toast.error('操作失敗')
  }
}

async function deletePlan(id) {
  if (!confirm('確定刪除此計劃？')) return
  try {
    await api.delete(`/plans/${id}`)
    toast.success('已刪除')
    await loadPlans()
  } catch (err) {
    toast.error('刪除失敗')
  }
}

onMounted(loadPlans)
</script>
