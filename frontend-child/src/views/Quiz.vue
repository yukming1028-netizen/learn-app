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

      <!-- Timer bar -->
      <div class="timer-bar">
        <div class="timer-track" :class="{ 'timer-urgent': timeRemaining <= 5 }">
          <div class="timer-fill" :style="`width: ${timerPercent}%; background: ${timerColor};`"></div>
        </div>
        <div class="timer-text" :class="{ 'timer-urgent-text': timeRemaining <= 5 }">
          ⏱️ {{ formatTime(timeRemaining) }}
        </div>
      </div>

      <!-- Progress -->
      <div class="progress-bar" style="margin-bottom: 24px;">
        <div class="progress-fill" :style="`width: ${progressPercent}%`"></div>
      </div>

      <!-- ─── Choice question ─── -->
      <template v-if="currentQuestion.type === 'choice'">
        <div class="card" :class="{ 'animate-shake': showWrong, 'animate-pop': showCorrect }" style="margin-bottom: 20px;">
          <div style="font-size: 14px; color: #888; margin-bottom: 8px;">
            {{ difficultyStars }}
          </div>
          <h2 style="font-size: 24px; line-height: 1.6; text-align: center; padding: 16px 0;">
            {{ currentQuestion.content }}
          </h2>
        </div>
        <div>
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
      </template>

      <!-- ─── Fill-in-the-blank question ─── -->
      <template v-else-if="currentQuestion.type === 'fill_blank'">
        <div class="card" :class="{ 'animate-shake': showWrong, 'animate-pop': showCorrect }">
          <div style="font-size: 14px; color: #888; margin-bottom: 8px;">
            {{ difficultyStars }} <span style="margin-left: 8px;">✏️ 填空題</span>
          </div>
          <!-- Render content with inline input boxes -->
          <div class="fill-blank-content">
            <template v-for="(part, i) in fillBlankParts" :key="i">
              <span style="font-size: 22px; line-height: 2.4; display: inline;">{{ part }}</span>
              <input
                v-if="i < fillBlankParts.length - 1"
                :ref="el => { if (el) fillInputs[i] = el }"
                v-model="fillBlankAnswers[i]"
                type="text"
                class="fill-blank-input"
                :class="{ 'fill-correct': answered && result?.is_correct, 'fill-wrong': answered && !result?.is_correct }"
                :placeholder="`填空 ${i + 1}`"
                :disabled="answered"
                @keyup.enter="submitFillBlank"
                :style="`width: ${Math.max(60, (correctAnswers[i] || '').length * 24 + 20)}px;`"
              />
            </template>
          </div>
        </div>
        <div style="margin-top: 20px;">
          <button v-if="!answered" class="big-btn big-btn-secondary" @click="submitFillBlank">
            確認答案
          </button>
        </div>
      </template>

      <!-- ─── Input question ─── -->
      <template v-else>
        <div class="card" :class="{ 'animate-shake': showWrong, 'animate-pop': showCorrect }" style="margin-bottom: 20px;">
          <div style="font-size: 14px; color: #888; margin-bottom: 8px;">
            {{ difficultyStars }}
          </div>
          <h2 style="font-size: 24px; line-height: 1.6; text-align: center; padding: 16px 0;">
            {{ currentQuestion.content }}
          </h2>
        </div>
        <div>
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
      </template>

      <!-- Feedback -->
      <div v-if="answered && result" class="card" :style="`text-align: center; background: ${result.is_correct ? '#e8f5e9' : '#ffebee'}; margin-top: 20px;`">
        <div style="font-size: 40px; margin-bottom: 8px;">
          {{ result.is_correct ? '🎉' : '💪' }}
        </div>
        <div style="font-weight: 600; font-size: 18px; margin-bottom: 8px;">
          {{ result._timeout ? '⏰ 時間到了！' : (result.is_correct ? '答對了！好厲害！' : '沒關係，再加油！') }}
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { childAPI } from '../composables/api'

const router = useRouter()

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

// ─── Fill-blank state ───
const fillBlankAnswers = ref([])
const fillInputs = ref([])

// ─── Timer state ───
const timeLimit = ref(30)
const timeRemaining = ref(30)
const timerPercent = ref(100)
const timerColor = ref('#4CAF50')
let timerInterval = null

const subjectLabels = { math: '🔢 數學', chinese: '📝 語文', english: '🔤 英語', science: '🔬 科學' }
const subjectLabel = computed(() => subjectLabels[currentQuestion.value?.subject] || '')
const difficultyStars = computed(() => '⭐'.repeat(currentQuestion.value?.difficulty || 1))
const progressPercent = computed(() => {
  const target = 5
  return Math.min((answeredCount.value / target) * 100, 100)
})

// ─── Fill-blank: split content by ___ into parts ───
const fillBlankParts = computed(() => {
  if (!currentQuestion.value || currentQuestion.value.type !== 'fill_blank') return []
  return currentQuestion.value.content.split('___')
})

// ─── Fill-blank: correct answers split by | ───
const correctAnswers = computed(() => {
  if (!result.value) return []
  return result.value.correct_answer.split('|')
})

async function loadQuestion() {
  loading.value = true
  answered.value = false
  selectedOptIndex.value = -1
  inputAnswer.value = ''
  result.value = null
  fillBlankAnswers.value = []
  fillInputs.value = []
  stopTimer()

  const subject = localStorage.getItem('quizSubject') || null
  try {
    const { data } = await childAPI.getNextQuestion(subject)
    currentQuestion.value = data
    if (!data) return

    // Set time limit
    const avg = data.avg_time_sec || 30
    timeLimit.value = Math.max(10, Math.ceil(avg * 1.5))
    timeRemaining.value = timeLimit.value

    startTime = Date.now()
    startTimer()

    if (data.type === 'fill_blank') {
      const blankCount = data.content.split('___').length - 1
      fillBlankAnswers.value = new Array(blankCount).fill('')
      await nextTick()
      fillInputs.value[0]?.focus()
    } else if (data.type === 'input') {
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

async function submitFillBlank() {
  if (answered.value) return
  const allFilled = fillBlankAnswers.value.every(a => a.trim() !== '')
  if (!allFilled) {
    showWrong.value = true
    setTimeout(() => showWrong.value = false, 300)
    return
  }
  // Join answers with | to match backend format
  const joined = fillBlankAnswers.value.map(a => a.trim()).join('|')
  await submitAnswer(joined)
}

async function submitAnswer(selectedAnswer) {
  if (answered.value) return
  stopTimer()
  const timeTaken = (Date.now() - startTime) / 1000
  answered.value = true
  answeredCount.value++

  try {
    const { data } = await childAPI.submitAnswer(
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
    stopTimer()
    router.push('/')
  }
}

// ─── Timer functions ───
function startTimer() {
  timerPercent.value = 100
  updateTimerColor()
  timerInterval = setInterval(() => {
    timeRemaining.value -= 1
    timerPercent.value = (timeRemaining.value / timeLimit.value) * 100
    updateTimerColor()
    if (timeRemaining.value <= 0) {
      stopTimer()
      if (!answered.value && currentQuestion.value) {
        autoTimeoutSubmit()
      }
    }
  }, 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function updateTimerColor() {
  const ratio = timeRemaining.value / timeLimit.value
  if (ratio > 0.5) {
    timerColor.value = '#4CAF50'
  } else if (ratio > 0.25) {
    timerColor.value = '#FF9800'
  } else {
    timerColor.value = '#F44336'
  }
}

function formatTime(sec) {
  const s = Math.max(0, Math.ceil(sec))
  const m = Math.floor(s / 60)
  const r = s % 60
  return `${m}:${r.toString().padStart(2, '0')}`
}

async function autoTimeoutSubmit() {
  answered.value = true
  answeredCount.value++
  const timeTaken = timeLimit.value
  // For fill_blank, submit empty blanks
  let answerStr = '__TIMEOUT__'
  if (currentQuestion.value.type === 'fill_blank') {
    const blankCount = currentQuestion.value.content.split('___').length - 1
    answerStr = new Array(blankCount).fill('').join('|')
  }
  try {
    const { data } = await childAPI.submitAnswer(
      currentQuestion.value.id,
      answerStr,
      timeTaken,
    )
    result.value = { ...data, _timeout: true }
    showWrong.value = true
    setTimeout(() => showWrong.value = false, 400)
  } catch (err) {
    result.value = {
      is_correct: false,
      correct_answer: '?',
      explanation: '',
      reward: '時間到了！下次加油！',
      _timeout: true,
    }
  }
}

onMounted(loadQuestion)
onUnmounted(stopTimer)
</script>
