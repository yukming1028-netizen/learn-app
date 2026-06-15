<template>
  <div class="page">
    <button class="btn btn-outline" @click="$router.back()" style="margin-bottom: 16px;">← 返回</button>

    <div v-if="loading" style="text-align: center; padding: 40px;">載入中...</div>

    <template v-else-if="child">
      <!-- Child header -->
      <div class="card" style="margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-size: 48px;">{{ child.avatar }}</span>
            <div>
              <h2>{{ child.name }}</h2>
              <p style="color: var(--text-light); font-size: 14px;">{{ gradeName(child.grade) }}</p>
            </div>
          </div>
          <button class="btn btn-secondary" @click="downloadReport">📄 下載報告</button>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-3" style="margin-bottom: 16px;">
        <div class="card stat-card">
          <div class="stat-value">{{ child.total_questions }}</div>
          <div class="stat-label">總答題數</div>
        </div>
        <div class="card stat-card">
          <div class="stat-value">{{ Math.round(child.accuracy * 100) }}%</div>
          <div class="stat-label">正確率</div>
        </div>
        <div class="card stat-card">
          <div class="stat-value">{{ child.total_study_minutes }}</div>
          <div class="stat-label">學習分鐘</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-2" style="margin-bottom: 16px;">
        <div class="card">
          <h3 style="margin-bottom: 12px;">📈 近7日趨勢</h3>
          <canvas ref="dailyChartRef"></canvas>
        </div>
        <div class="card">
          <h3 style="margin-bottom: 12px;">📚 學科分布</h3>
          <canvas ref="subjectChartRef"></canvas>
        </div>
      </div>

      <!-- Today progress -->
      <div class="card" v-if="todayProgress">
        <h3 style="margin-bottom: 12px;">📋 今日進度</h3>
        <div style="display: flex; gap: 24px;">
          <span>完成: {{ todayProgress.completed_count }} / {{ todayProgress.target_count }} 題</span>
          <span>正確率: {{ Math.round(todayProgress.accuracy_today * 100) }}%</span>
          <span>用時: {{ todayProgress.minutes_today }} 分鐘</span>
        </div>
        <div style="margin-top: 12px; background: var(--bg); border-radius: 8px; height: 12px; overflow: hidden;">
          <div :style="`width: ${Math.min(todayProgress.completion_rate * 100, 100)}%; height: 100%; background: var(--primary); transition: width 0.3s;`"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '../composables/api'
import { useToast } from '../composables/useToast'
import Chart from 'chart.js/auto'

const route = useRoute()
const toast = useToast()
const child = ref(null)
const stats = ref(null)
const todayProgress = ref(null)
const loading = ref(true)
const dailyChartRef = ref(null)
const subjectChartRef = ref(null)
let charts = []

function gradeName(grade) {
  const names = {1:'小一',2:'小二',3:'小三',4:'小四',5:'小五',6:'小六',7:'中一',8:'中二',9:'中三'}
  return names[grade] || `Grade ${grade}`
}

async function downloadReport() {
  try {
    const response = await api.get(`/reports/${route.params.id}/pdf?period_days=30`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `${child.value.name}_report.pdf`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('報告下載成功！')
  } catch (err) {
    toast.error('下載失敗')
  }
}

function renderCharts() {
  charts.forEach(c => c.destroy())
  charts = []

  if (dailyChartRef.value && stats.value) {
    charts.push(new Chart(dailyChartRef.value, {
      type: 'line',
      data: {
        labels: stats.value.daily_trend.map(d => d.date.slice(5)),
        datasets: [
          { label: '答題數', data: stats.value.daily_trend.map(d => d.total), borderColor: '#FF6B35', backgroundColor: 'rgba(255,107,53,0.1)', tension: 0.3 },
          { label: '答對數', data: stats.value.daily_trend.map(d => d.correct), borderColor: '#4A90E2', backgroundColor: 'rgba(74,144,226,0.1)', tension: 0.3 },
        ]
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    }))
  }

  if (subjectChartRef.value && stats.value) {
    const subjects = stats.value.subject_breakdown
    const subjectNames = { math: '數學', chinese: '語文', english: '英語', science: '科學' }
    charts.push(new Chart(subjectChartRef.value, {
      type: 'doughnut',
      data: {
        labels: Object.keys(subjects).map(s => subjectNames[s] || s),
        datasets: [{
          data: Object.values(subjects).map(s => s.total),
          backgroundColor: ['#FF6B35', '#4A90E2', '#4CAF50', '#FF9800'],
        }]
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    }))
  }
}

onMounted(async () => {
  try {
    const [childRes, statsRes, progressRes] = await Promise.all([
      api.get(`/children/${route.params.id}`),
      api.get(`/children/${route.params.id}/stats`),
      api.get(`/progress/today/${route.params.id}`),
    ])
    child.value = childRes.data
    stats.value = statsRes.data
    todayProgress.value = progressRes.data
    await nextTick()
    renderCharts()
  } catch (err) {
    toast.error('載入失敗')
  } finally {
    loading.value = false
  }
})
</script>
