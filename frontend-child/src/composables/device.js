// Device management — UUID, device_token, active child

// ─── Device UUID (persists per physical device) ───
export function getDeviceUUID() {
  let uuid = localStorage.getItem('deviceUUID')
  if (!uuid) {
    uuid = 'dev-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('deviceUUID', uuid)
  }
  return uuid
}

// ─── Device Token (32-char hex, from server after parent binds) ───
export function getDeviceToken() {
  return localStorage.getItem('deviceToken')
}
export function setDeviceToken(token) {
  localStorage.setItem('deviceToken', token)
}
export function clearDeviceToken() {
  localStorage.removeItem('deviceToken')
}

// ─── Active Child (selected on UserSelect page) ───
export function getActiveChildId() {
  const id = localStorage.getItem('activeChildId')
  return id ? parseInt(id) : null
}

export function getActiveChild() {
  const id = getActiveChildId()
  if (!id) return null
  return {
    id,
    name: localStorage.getItem('activeChildName') || '小寶貝',
    avatar: localStorage.getItem('activeChildAvatar') || '🐻',
  }
}

export function setActiveChild(child) {
  localStorage.setItem('activeChildId', child.id)
  localStorage.setItem('activeChildName', child.name)
  localStorage.setItem('activeChildAvatar', child.avatar || '🐻')
}

export function clearActiveChild() {
  localStorage.removeItem('activeChildId')
  localStorage.removeItem('activeChildName')
  localStorage.removeItem('activeChildAvatar')
}

// ─── Full reset (device unbound) ───
export function clearAll() {
  clearDeviceToken()
  clearActiveChild()
}

// ─── State checks ───
export function hasDeviceToken() {
  return !!getDeviceToken()
}
export function hasActiveChild() {
  return !!getActiveChildId()
}
