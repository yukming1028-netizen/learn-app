import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

export function useToast() {
  function add(message, type = 'info', duration = 3000) {
    const id = nextId++
    toasts.value.push({ id, message, type })
    if (duration > 0) setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, duration)
  }
  return {
    toasts,
    success: (msg) => add(msg, 'success'),
    error: (msg) => add(msg, 'error'),
    info: (msg) => add(msg, 'info'),
    remove: (id) => { toasts.value = toasts.value.filter(t => t.id !== id) },
  }
}
