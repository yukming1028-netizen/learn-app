<template>
  <div class="home">
    <!-- Header -->
    <div class="header">
      <div class="child-info" @click="$router.push('/select')">
        <span class="avatar">{{ childInfo.avatar }}</span>
        <div>
          <div class="name">{{ childInfo.name }}</div>
          <div class="switch-hint">切換用戶 ›</div>
        </div>
      </div>
    </div>

    <!-- Progress card -->
    <div class="progress-card">
      <div class="progress-title">今日進度</div>
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill" :style="`width: ${progressPercent}%`"></div>
      </div>
      <div class="progress-stats">
        <span>{{ progress.completed_count }} / {{ progress.target_count }} 題</span>
        <span v-if="progress.accuracy_today">正確率 {{ Math.round(progress.accuracy_today * 100) }}%</span>
      </div>
    </div>

    <!-- Subject selection -->
    <div class="section">
      <h3>選擇科目</h3>
      <div class="subjects">
        <button
          v-for="subj in subjects"
          :key="subj.key"
          :class="['subject-btn', { active: selectedSubject === subj.key }]"
          @click="selectedSubject = subj.key"
        >
          <span class="subj-icon">{{ subj.icon }}</span>
          <span class="subj-name">{{ subj.name }}</span>
        </button>
      </div>
    </div>

    <!-- Start button -->
    <button class="start-btn" @click="startQuiz">
      🚀 開始答題
    </button>

    <!-- Review shortcut -->
    <button v-if="reviewCount > 0" class="review-btn" @click="$router.push('/review')">
      📖 有 {{ reviewCount }} 題錯題待複習
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getActiveChild } from '../composables/device'
import { childAPI } from '../composables/api'

const router = useRouter()
const childInfo = getActiveChild()

const progress = ref({ completed_count: 0, target_count: 5, accuracy_today: 0 })
const reviewCount = ref(0)
const selectedSubject = ref(null)

const subjects = [
  { key: 'math', icon: '🔢', name: '數學' },
  { key: 'chinese', icon: '📝', name: '語文' },
  { key: 'english', icon: '🔤', name: '英語' },
  { key: 'science', icon: '🔬', name: '科學' },
]

const progressPercent = computed(() => {
  const pct = (progress.value.completed_count / progress.value.target_count) * 100
  return Math.min(pct, 100)
})

function startQuiz() {
  if (selectedSubject.value) {
    localStorage.setItem('quizSubject', selectedSubject.value)
  } else {
    localStorage.removeItem('quizSubject')
  }
  router.push('/quiz')
}

async function loadData() {
  try {
    const [progRes, reviewRes] = await Promise.all([
      childAPI.getTodayProgress(),
      childAPI.getReviewCount(),
    ])
    progress.value = progRes.data
    reviewCount.value = reviewRes.data.due_count || 0
  } catch (err) {
    console.error('Load failed', err)
  }
}

onMounted(loadData)
</script>

<style scoped>
.home {
  padding: 16px 20px 100px;
  max-width: 480px;
  margin: 0 auto;
}

.header { margin-bottom: 20px; }
.child-info {
  display: flex; align-items: center; gap: 12px;
  cursor: pointer;
}
.avatar { font-size: 2.5rem; }
.name { font-size: 1.3rem; font-weight: bold; }
.switch-hint { font-size: 0.8rem; color: #4a9eff; }

.progress-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 16px; padding: 20px;
  color: white; margin-bottom: 24px;
}
.progress-title { font-size: 0.9rem; opacity: 0.9; margin-bottom: 12px; }
.progress-bar-wrap {
  height: 10px; background: rgba(255,255,255,0.3);
  border-radius: 5px; overflow: hidden; margin-bottom: 12px;
}
.progress-bar-fill {
  height: 100%; background: white; border-radius: 5px;
  transition: width 0.5s;
}
.progress-stats { display: flex; justify-content: space-between; font-size: 0.85rem; }

.section { margin-bottom: 24px; }
.section h3 { font-size: 1rem; margin-bottom: 12px; }
.subjects {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
}
.subject-btn {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 16px; border-radius: 14px; border: 2px solid #e0e0e0;
  background: white; cursor: pointer; transition: all 0.15s;
}
.subject-btn.active { border-color: #667eea; background: #f0f0ff; }
.subj-icon { font-size: 2rem; }
.subj-name { font-size: 0.9rem; color: #555; }

.start-btn {
  width: 100%; padding: 16px; font-size: 1.2rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white; border: none; border-radius: 14px;
  cursor: pointer; font-weight: 600;
}
.start-btn:active { transform: scale(0.98); }

.review-btn {
  width: 100%; margin-top: 12px; padding: 12px;
  background: #FFF3E0; border: 1px solid #FFE0B2;
  border-radius: 12px; cursor: pointer;
  color: #E65100; font-size: 0.95rem;
}
</style>
