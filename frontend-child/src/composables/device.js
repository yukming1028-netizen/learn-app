// Generate or retrieve device UUID
export function getDeviceUUID() {
  let uuid = localStorage.getItem('deviceUUID')
  if (!uuid) {
    uuid = 'dev-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('deviceUUID', uuid)
  }
  return uuid
}

// Check if child is bound
export function isBound() {
  return !!localStorage.getItem('childId')
}

// Get bound child info
export function getChildInfo() {
  return {
    id: localStorage.getItem('childId'),
    name: localStorage.getItem('childName') || '小寶貝',
    avatar: localStorage.getItem('childAvatar') || '🐻',
  }
}

// Clear binding (logout)
export function clearBinding() {
  localStorage.removeItem('childId')
  localStorage.removeItem('childName')
  localStorage.removeItem('childAvatar')
}
