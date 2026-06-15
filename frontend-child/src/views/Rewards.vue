<template>
  <div style="padding: 20px 20px 100px;">
    <h1 style="font-size: 24px; margin-bottom: 20px;">🎁 我的獎勵</h1>

    <div class="card" style="text-align: center; margin-bottom: 16px;">
      <div style="font-size: 48px;">🏆</div>
      <h2 style="font-size: 20px; margin-top: 8px;">{{ childInfo.name }}</h2>
      <p style="color: #888; margin-top: 4px;">已收集 {{ stickerCount }} 個貼紙</p>
    </div>

    <div v-if="stickerCount === 0" class="card" style="text-align: center; padding: 40px;">
      <div style="font-size: 48px; margin-bottom: 12px;">🎈</div>
      <p style="color: #888;">還沒有貼紙呢！答對題目就能獲得貼紙哦！</p>
    </div>

    <div v-else>
      <h3 style="margin-bottom: 12px;">我的貼紙收藏</h3>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
        <div v-for="(sticker, i) in stickers" :key="i" class="card" style="text-align: center; padding: 16px 8px;">
          <div style="font-size: 36px;" class="animate-pop">{{ sticker }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../composables/api'
import { getChildInfo } from '../composables/device'

const childInfo = getChildInfo()
const stickers = ref([])
const stickerCount = computed(() => stickers.value.length)

onMounted(async () => {
  try {
    const { data } = await api.get(`/children/${childInfo.id}`)
    stickers.value = data.stickers || []
  } catch (err) {
    console.error('Failed to load', err)
  }
})
</script>
