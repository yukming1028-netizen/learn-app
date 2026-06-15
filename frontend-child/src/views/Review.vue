<template>
  <div style="padding: 20px 20px 100px;">
    <h1 style="font-size: 24px; margin-bottom: 20px;">📖 錯題複習</h1>

    <div v-if="loading" style="text-align: center; padding: 40px;">
      <div style="font-size: 40px;" class="animate-bounce">⏳</div>
      <p>載入中...</p>
    </div>

    <div v-else-if="reviews.length === 0" class="card" style="text-align: center; padding: 40px;">
      <div style="font-size: 48px; margin-bottom: 12px;">🌟</div>
      <p style="color: #888;">太棒了！沒有需要複習的錯題！</p>
    </div>

    <div v-else>
      <div class="card" style="margin-bottom: 16px; background: #FFF3E0;">
        <p>📝 有 <strong>{{ reviews.length }}</strong> 題需要複習，一起加油吧！</p>
      </div>

      <div v-for="(q, i) in reviews" :key="q.id" class="card" style="margin-bottom: 12px;">
        <div style="font-size: 12px; color: #888; margin-bottom: 4px;">{{ subjectLabel(q.subject) }} · 難度 {{ '⭐'.repeat(q.difficulty) }}</div>
        <div style="font-size: 16px; margin-bottom: 8px;">{{ q.content }}</div>
        <div v-if="q.options" style="display: flex; flex-wrap: wrap; gap: 6px;">
          <span v-for="opt in q.options" :key="opt" style="padding: 4px 10px; background: #f0f0f0; border-radius: 6px; font-size: 13px;">{{ opt }}</span>
        </div>
      </div>

      <button class="big-btn big-btn-primary" @click="$router.push('/quiz')">開始練習</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { childAPI } from '../composables/api'
import { getChildInfo } from '../composables/device'

const childInfo = getChildInfo()
const reviews = ref([])
const loading = ref(true)

const subjectLabels = { math: '數學', chinese: '語文', english: '英語', science: '科學' }
function subjectLabel(s) { return subjectLabels[s] || s }

onMounted(async () => {
  try {
    const { data } = await childAPI.getReviewList(childInfo.id)
    reviews.value = data
  } catch (err) {
    console.error('Failed', err)
  } finally {
    loading.value = false
  }
})
</script>
