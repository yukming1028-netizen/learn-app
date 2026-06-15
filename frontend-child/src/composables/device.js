// Generate or retrieve device UUID
export function getDeviceUUID() {
  let uuid = localStorage.getItem('deviceUUID')
  if (!uuid) {
    uuid = 'dev-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('deviceUUID', uuid)
  }
  return uuid
}

// Get current active child ID
export function getChildId() {
  return localStorage.getItem('childId')
}

// Get current active child info
export function getChildInfo() {
  return {
    id: parseInt(localStorage.getItem('childId')) || null,
    name: localStorage.getItem('childName') || '小寶貝',
    avatar: localStorage.getItem('childAvatar') || '🐻',
  }
}

// Set active child
export function setActiveChild(child) {
  localStorage.setItem('childId', child.id)
  localStorage.setItem('childName', child.name)
  localStorage.setItem('childAvatar', child.avatar || '🐻')
}

// Check if a child is selected
export function hasActiveChild() {
  return !!localStorage.getItem('childId')
}

// Clear active child selection (not unbind, just deselect)
export function clearActiveChild() {
  localStorage.removeItem('childId')
  localStorage.removeItem('childName')
  localStorage.removeItem('childAvatar')
}

// Compatibility: keep old function name
export function isBound() {
  return hasActiveChild()
}

export function clearBinding() {
  clearActiveChild()
}
