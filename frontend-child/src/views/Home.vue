<template>
  <!-- Bind flow -->
  <div v-if="!bound" style="padding: 40px 20px; text-align: center; min-height: 100vh; display: flex; flex-direction: column; justify-content: center;">
    <div style="font-size: 80px; margin-bottom: 20px;">📚</div>
    <h1 style="font-size: 28px; color: var(--primary); margin-bottom: 8px;">親子學伴</h1>
    <p style="color: #888; margin-bottom: 40px;">讓學習變得好玩！</p>

    <div v-if="!scanning" class="card" style="margin-bottom: 16px;">
      <p style="margin-bottom: 16px;">請爸爸媽媽先在家長端生成 QR Code，然後輸入綁定碼：</p>
      <input class="input" v-model="manualToken" placeholder="輸入綁定碼..." style="margin-bottom: 12px;" />
      <input class="input" v-model="childName" placeholder="你的名字（可選）" style="margin-bottom: 16px;" />
      <button class="big-btn big-btn-primary" @click="handleBind">🔗 綁定</button>
    </div>

    <div v-if="scanning" style="padding: 40px;">
      <div style="font-size: 40px;" class="animate-bounce">⏳</div>
      <p>綁定中...</p>
    </div>

    <p v-if="errorMsg" style="color: var(--danger); margin-top: 16px;">{{ errorMsg }}</p>
  </div>

  <!-- Home screen -->
  <div v-else style="padding: 20px 20px 100px;">
    <!-- Header -->
    <div style="text-align: center; margin-bottom: 30px; padding-top: 20px;">
      <div style="font-size: 56px;" class="animate-bounce">{{ childInfo.avatar }}</div>
      <h2 style="font-size: 24px; margin-top: 8px;">嗨，{{ childInfo.name }}！</h2>
    </div>

    <!-- Today's progress -->
    <div class="card" style="margin-bottom: 16px;">
      <h3 style="margin-bottom: 12px;">📋 今日任務</h3>
      <div v-if="progress" style="font-size: 16px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
          <span>完成：{{ progress.completed_count }} / {{ progress.target_count }} 題</span>
          <span v-if="progress.completion_rate >= 1" style="color: var(--success);">🎉 完成！</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="`width: ${Math.min(progress.completion_rate * 100, 100)}%`"></div>
        </div>
      </div>
    </div>

    <!-- Review reminder -->
    <div v-if="reviewCount > 0" class="card" style="margin-bottom: 16px; background: #FFF3E0; cursor: pointer;" @click="$router.push('/review')">
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 32px;">📖</span>
        <div>
          <div style="font-weight: 600;">有 {{ reviewCount }} 題需要複習</div>
          <div style="font-size: 13px; color: #888;">點擊開始複習</div>
        </div>
      </div>
    </div>

    <!-- Big start button -->
    <button class="big-btn big-btn-primary" style="margin-bottom: 16px;" @click="$router.push('/quiz')">
      🎮 開始學習！
    </button>

    <!-- Subject shortcuts -->
    <div class="grid grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
      <button class="card" style="border: none; cursor: pointer; text-align: center; font-size: 32px;" @click="startSubject('math')">
        🔢<div style="font-size: 14px; margin-top: 4px;">數學</div>
      </button>
      <button class="card" style="border: none; cursor: pointer; text-align: center; font-size: 32px;" @click="startSubject('chinese')">
        📝<div style="font-size: 14px; margin-top: 4px;">語文</div>
      </button>
      <button class="card" style="border: none; cursor: pointer; text-align: center; font-size: 32px;" @click="startSubject('english')">
        🔤<div style="font-size: 14px; margin-top: 4px;">英語</div>
      </button>
      <button class="card" style="border: none; cursor: pointer; text-align: center; font-size: 32px;" @click="startSubject('science')">
        🔬<div style="font-size: 14px; margin-top: 4px;">科學</div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { childAPI } from '../composables/api'
import { getDeviceUUID, isBound, getChildInfo } from '../composables/device'

const router = useRouter()
const bound = ref(isBound())
const scanning = ref(false)
const manualToken = ref('')
const childName = ref('')
const errorMsg = ref('')
const childInfo = ref(getChildInfo())
const progress = ref(null)
const reviewCount = ref(0)

async function handleBind() {
  if (!manualToken.value.trim()) {
    errorMsg.value = '請輸入綁定碼'
    return
  }
  scanning.value = true
  errorMsg.value = ''
  try {
    const { data } = await childAPI.bind(
      manualToken.value.trim(),
      getDeviceUUID(),
      childName.value || '小寶貝'
    )
    if (data.success) {
      localStorage.setItem('childId', data.child_id)
      localStorage.setItem('childName', data.child_name)
      bound.value = true
      childInfo.value = getChildInfo()
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '綁定失敗，請重試'
  } finally {
    scanning.value = false
  }
}

function startSubject(subject) {
  localStorage.setItem('quizSubject', subject)
  router.push('/quiz')
}

async function loadHomeData() {
  if (!bound.value) return
  try {
    const [progressRes, reviewRes] = await Promise.all([
      childAPI.getTodayProgress(childInfo.value.id),
      childAPI.getReviewCount(childInfo.value.id),
    ])
    progress.value = progressRes.data
    reviewCount.value = reviewRes.data.due_count
  } catch (err) {
    console.error('Load failed', err)
  }
}

onMounted(() => {
  if (bound.value) loadHomeData()
})
</script>
