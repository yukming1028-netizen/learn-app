import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: API_BASE })

// ─── Request interceptor: attach device_token + child_id headers ───
api.interceptors.request.use(config => {
  const token = localStorage.getItem('deviceToken')
  const childId = localStorage.getItem('activeChildId')
  if (token) config.headers['X-Device-Token'] = token
  if (childId) config.headers['X-Child-Id'] = childId
  return config
})

// ─── Response interceptor: 401 → token invalid → back to user select ───
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      // Only redirect for auth-protected endpoints, not binding/status endpoints
      const isBindingEndpoint = url.includes('/binding/device/') && url.includes('/status')
                               || url.includes('/binding/device/') && url.includes('/children')
                               || url.includes('/binding/device/generate')
      if (!isBindingEndpoint) {
        // Device token invalid or expired
        localStorage.removeItem('deviceToken')
        localStorage.removeItem('activeChildId')
        localStorage.removeItem('activeChildName')
        localStorage.removeItem('activeChildAvatar')
        if (window.location.pathname !== '/select') {
          window.location.href = '/select'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ─── Child device API ───
export const childAPI = {
  // Binding: generate QR / bind code (no auth needed)
  generateBindCode: (deviceUuid) =>
    api.post('/binding/device/generate', { device_uuid: deviceUuid }),

  // Check device binding status (returns device_token if bound)
  getDeviceStatus: (deviceUuid) =>
    api.get(`/binding/device/${deviceUuid}/status`),

  // List children visible on this device (no auth, uses device_uuid in URL)
  getDeviceChildren: (deviceUuid) =>
    api.get(`/binding/device/${deviceUuid}/children`),

  // Device self-unbind
  deviceUnbind: (deviceUuid) =>
    api.post('/binding/device/unbind', { device_uuid: deviceUuid }),

  // Device create a new child (user) for bound parent
  deviceCreateChild: (deviceUuid, data) =>
    api.post(`/binding/device/${deviceUuid}/children`, data),

  // Questions (auth: device_token + child_id via headers)
  getNextQuestion: (subject) =>
    api.post('/questions/next', { subject }),

  submitAnswer: (questionId, selectedAnswer, timeTakenSec) =>
    api.post('/questions/answer', {
      question_id: questionId,
      selected_answer: selectedAnswer,
      time_taken_sec: timeTakenSec,
    }),

  // Review
  getReviewList: () => api.get('/review'),
  getReviewCount: () => api.get('/review/count'),

  // Progress + profile (auth via headers)
  getTodayProgress: () => api.get('/progress/today'),
  getMyInfo: () => api.get('/progress/me'),
}
