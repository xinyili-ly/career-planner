const STACK_KEY = '__dcp_nav_stack__'
const SKIP_KEY = '__dcp_nav_skip__'

function safeSession() {
  try {
    if (typeof window === 'undefined') return null
    if (!window.sessionStorage) return null
    return window.sessionStorage
  } catch {
    return null
  }
}

function loadStack() {
  const s = safeSession()
  if (!s) return []
  try {
    const raw = s.getItem(STACK_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter((x) => typeof x === 'string')
  } catch {
    return []
  }
}

function saveStack(stack) {
  const s = safeSession()
  if (!s) return
  try {
    s.setItem(STACK_KEY, JSON.stringify(stack))
  } catch {
    // ignore
  }
}

export function recordFromRoute(fromFullPath, toFullPath) {
  if (!fromFullPath || !toFullPath) return
  if (fromFullPath === toFullPath) return

  const stack = loadStack()
  if (stack.length && stack[stack.length - 1] === fromFullPath) return

  stack.push(fromFullPath)

  const MAX = 50
  if (stack.length > MAX) stack.splice(0, stack.length - MAX)

  saveStack(stack)
}

export function popBackTarget() {
  const stack = loadStack()
  if (!stack.length) return null
  const target = stack.pop()
  saveStack(stack)
  return target || null
}

export function setSkipNextRecord() {
  const s = safeSession()
  if (!s) return
  try {
    s.setItem(SKIP_KEY, '1')
  } catch {
    // ignore
  }
}

export function consumeSkipNextRecord() {
  const s = safeSession()
  if (!s) return false
  try {
    const v = s.getItem(SKIP_KEY)
    if (v === '1') {
      s.removeItem(SKIP_KEY)
      return true
    }
  } catch {
    // ignore
  }
  return false
}

