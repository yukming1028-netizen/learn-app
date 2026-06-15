<template>
  <div style="padding: 16px 20px 100px; position: relative; min-height: 100vh;">

    <!-- Loading -->
    <div v-if="loading" style="text-align: center; padding-top: 120px;">
      <div style="font-size: 48px;" class="animate-bounce">⏳</div>
      <p style="color: #888; margin-top: 12px;">載入題目中...</p>
    </div>

    <!-- Quiz interface -->
    <div v-else-if="currentQuestion" style="position: relative;">
      <!-- Top bar -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <button @click="exitQuiz" style="font-size: 24px; background: none; border: none; cursor: pointer;">←</button>
        <div style="font-size: 14px; color: #888;">
          第 {{ answeredCount + 1 }} 題
          <span v-if="subjectLabel" style="margin-left: 8px;">{{ subjectLabel }}</span>
        </div>
        <div style="font-size: 24px;">⭐ {{ correctCount }}</div>
      </div>

      <!-- Progress -->
      <div class="progress-bar" style="margin-bottom: 24px;">
        <div class="progress-fill" :style="`width: ${progressPercent}%`"></div>
      </div>

      <!-- Question card -->
      <div class="card" :class="{ 'animate-shake': showWrong, 'animate-pop': showCorrect }" style="margin-bottom: 20px;">
        <div style="font-size: 14px; color: #888; margin-bottom: 8px;">
          {{ difficultyStars }}
        </div>
        <h2 style="font-size: 24px; line-height: 1.6; text-align: center; padding: 16px 0;">
          {{ currentQuestion.content }}
        </h2>
      </div>

      <!-- Answer options -->
      <div v-if="currentQuestion.type === 'choice'">
        <button
          v-for="(opt, i) in currentQuestion.options"
          :key="i"
          :class="['option-btn', getOptionClass(i)]"
          :disabled="answered"
          @click="selectAnswer(opt, i)"
        >
          {{ opt }}
        </button>
      </div>

      <!-- Input answer -->
      <div v-else>
        <input
          ref="inputRef"
          class="input"
          v-model="inputAnswer"
          placeholder="輸入答案..."
          :disabled="answered"
          @keyup.enter="submitInputAnswer"
          style="margin-bottom: 12px; font-size: 24px;"
        />
        <button v-if="!answered" class="big-btn big-btn-secondary" @click="submitInputAnswer">確認答案</button>
      </div>

      <!-- Feedback -->
      <div v-if="answered && result" class="card" :style="`text-align: center; background: ${result.is_correct ? '#e8f5e9' : '#ffebee'};`">
        <div style="font-size: 40px; margin-bottom: 8px;">
          {{ result.is_correct ? '🎉' : '💪' }}
        </div>
        <div style="font-weight: 600; font-size: 18px; margin-bottom: 8px;">
          {{ result.is_correct ? '答對了！好厲害！' : '沒關係，再加油！' }}
        </div>
        <div style="font-size: 14px; color: #666; margin-bottom: 4px;">
          正確答案：<strong>{{ result.correct_answer }}</strong>
        </div>
        <div v-if="result.explanation" style="font-size: 13px; color: #888;">
          💡 {{ result.explanation }}
        </div>
        <div v-if="result.new_sticker" style="margin-top: 12px; font-size: 28px;" class="animate-pop">
          {{ result.new_sticker }} 新貼紙！
        </div>
        <button class="big-btn big-btn-primary" style="margin-top: 16px;" @click="nextQuestion">
          下一題 →
        </button>
      </div>

      <!-- Star particles -->
      <div
        v-for="star in stars"
        :key="star.id"
        class="star-particle"
        :style="`left: ${star.x}%; top: ${star.y}%; --tx: ${star.tx}px; --ty: ${star.ty}px;`"
      >
        {{ star.emoji }}
      </div>
    </div>

    <!-- No more questions -->
    <div v-else style="text-align: center; padding-top: 120px;">
      <div style="font-size: 64px;" class="animate-bounce">🏆</div>
      <h2 style="margin-top: 16px;">太棒了！</h2>
      <p style="color: #888; margin-top: 8px;">你完成了今天的練習！</p>
      <div style="margin-top: 24px;">
        <button class="big-btn big-btn-secondary" @click="$router.push('/')">回到主頁</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { childAPI } from '../composables/api'
import { getChildInfo } from '../composables/device'

const router = useRouter()
const childInfo = getChildInfo()

const loading = ref(true)
const currentQuestion = ref(null)
const answered = ref(false)
const selectedOptIndex = ref(-1)
const result = ref(null)
const inputAnswer = ref('')
const inputRef = ref(null)
const answeredCount = ref(0)
const correctCount = ref(0)
const showCorrect = ref(false)
const showWrong = ref(false)
const stars = ref([])
let startTime = 0
let starId = 0

const subjectLabels = { math: '🔢 數學', chinese: '📝 語文', english: '🔤 英語', science: '🔬 科學' }
const subjectLabel = computed(() => subjectLabels[currentQuestion.value?.subject] || '')
const difficultyStars = computed(() => '⭐'.repeat(currentQuestion.value?.difficulty || 1))
const progressPercent = computed(() => {
  const target = 5
  return Math.min((answeredCount.value / target) * 100, 100)
})

async function loadQuestion() {
  loading.value = true
  answered.value = false
  selectedOptIndex.value = -1
  inputAnswer.value = ''
  result.value = null

  const subject = localStorage.getItem('quizSubject') || null
  try {
    const { data } = await childAPI.getNextQuestion(childInfo.id, subject)
    currentQuestion.value = data
    if (!data) return
    startTime = Date.now()
    if (data.type === 'input') {
      await nextTick()
      inputRef.value?.focus()
    }
  } catch (err) {
    console.error('Failed to load question', err)
  } finally {
    loading.value = false
  }
}

function getOptionClass(index) {
  if (!answered.value || !result.value) return ''
  if (index === selectedOptIndex.value) {
    return result.value.is_correct ? 'correct' : 'wrong'
  }
  // Highlight the correct option
  if (currentQuestion.value.options[index] === result.value.correct_answer) {
    return 'correct'
  }
  return ''
}

async function selectAnswer(option, index) {
  if (answered.value) return
  selectedOptIndex.value = index
  await submitAnswer(option)
}

async function submitInputAnswer() {
  if (answered.value || !inputAnswer.value.trim()) return
  await submitAnswer(inputAnswer.value.trim())
}

async function submitAnswer(selectedAnswer) {
  const timeTaken = (Date.now() - startTime) / 1000
  answered.value = true
  answeredCount.value++

  try {
    const { data } = await childAPI.submitAnswer(
      childInfo.id,
      currentQuestion.value.id,
      selectedAnswer,
      timeTaken,
    )
    result.value = data

    if (data.is_correct) {
      correctCount.value++
      showCorrect.value = true
      triggerStars()
      setTimeout(() => showCorrect.value = false, 600)
    } else {
      showWrong.value = true
      setTimeout(() => showWrong.value = false, 400)
    }
  } catch (err) {
    console.error('Submit failed', err)
    result.value = {
      is_correct: false,
      correct_answer: '?',
      explanation: '',
      reward: '提交失敗，請重試',
    }
  }
}

function triggerStars() {
  const emojis = ['⭐', '🌟', '✨', '🎉', '💫']
  for (let i = 0; i < 8; i++) {
    const star = {
      id: starId++,
      x: 45 + Math.random() * 10,
      y: 30 + Math.random() * 10,
      tx: (Math.random() - 0.5) * 300,
      ty: -100 - Math.random() * 200,
      emoji: emojis[Math.floor(Math.random() * emojis.length)],
    }
    stars.value.push(star)
    setTimeout(() => {
      stars.value = stars.value.filter(s => s.id !== star.id)
    }, 800)
  }
}

function nextQuestion() {
  if (answeredCount.value >= 5) {
    currentQuestion.value = null
    return
  }
  loadQuestion()
}

function exitQuiz() {
  if (confirm('確定要離開嗎？')) {
    router.push('/')
  }
}

onMounted(loadQuestion)
</script>
