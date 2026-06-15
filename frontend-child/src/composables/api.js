import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use(config => {
  // Child app uses device UUID + child_id for auth (no password)
  const childId = localStorage.getItem('childId')
  if (childId) {
    config.headers['X-Child-Id'] = childId
  }
  return config
})

export default api

// Child-specific API functions (no JWT, uses device binding)
export const childAPI = {
  bind: (qrToken, deviceUuid, childName) =>
    api.post('/binding/qr/verify', { qr_token: qrToken, device_uuid: deviceUuid, child_name: childName }),

  bindByCode: (bindCode, deviceUuid, childName) =>
    api.post('/binding/code/verify', { bind_code: bindCode, device_uuid: deviceUuid, child_name: childName }),

  getQuestions: (params) =>
    api.get('/questions', { params }),

  getNextQuestion: (childId, subject) =>
    api.post('/questions/next', { child_id: childId, subject }),

  submitAnswer: (childId, questionId, selectedAnswer, timeTakenSec) =>
    api.post('/questions/answer', { child_id: childId, question_id: questionId, selected_answer: selectedAnswer, time_taken_sec: timeTakenSec }),

  getReviewList: (childId) =>
    api.get(`/review/${childId}`),

  getReviewCount: (childId) =>
    api.get(`/review/${childId}/count`),

  getTodayProgress: (childId) =>
    api.get(`/progress/today/${childId}`),
}
