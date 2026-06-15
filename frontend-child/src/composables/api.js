import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use(config => {
  const childId = localStorage.getItem('childId')
  if (childId) {
    config.headers['X-Child-Id'] = childId
  }
  return config
})

export default api

// Child device API functions
export const childAPI = {
  // Device generates QR/bind code for parent to scan
  generateBindCode: (deviceUuid) =>
    api.post('/binding/device/generate', { device_uuid: deviceUuid }),

  // List all children bound to this device
  getDeviceChildren: (deviceUuid) =>
    api.get(`/binding/device/${deviceUuid}/children`),

  // Device unbinds a child profile
  unbindChild: (deviceUuid, childId) =>
    api.post('/binding/device/unbind', { device_uuid: deviceUuid, child_id: childId }),

  // Quiz / questions
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
