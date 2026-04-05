import { ref, readonly } from 'vue'

const STORAGE_KEY = 'career-planner-theme'

function getStored() {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    if (v === 'light' || v === 'dark') return v
  } catch (_) {}
  return 'light'
}

const theme = ref(getStored())

export function useTheme() {
  const setTheme = (value) => {
    if (value !== 'light' && value !== 'dark') return
    theme.value = value
    try {
      localStorage.setItem(STORAGE_KEY, value)
    } catch (_) {}
  }
  return { theme: readonly(theme), setTheme }
}
