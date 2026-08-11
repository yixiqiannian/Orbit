import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ThemeMode = 'light' | 'dark'

const THEME_KEY = 'orbit-theme'

function readStoredTheme(): ThemeMode {
  try {
    return localStorage.getItem(THEME_KEY) === 'dark' ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

function applyTheme(theme: ThemeMode) {
  document.documentElement.dataset.theme = theme
  try {
    localStorage.setItem(THEME_KEY, theme)
  } catch {
    // localStorage 不可用（隐私模式等）时仅本次会话生效
  }
}

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<ThemeMode>(readStoredTheme())

  /** 启动兜底：与 index.html 预置脚本保持一致，确保 data-theme 已生效 */
  function applyStoredTheme() {
    theme.value = readStoredTheme()
    document.documentElement.dataset.theme = theme.value
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    applyTheme(theme.value)
  }

  function setTheme(mode: ThemeMode) {
    theme.value = mode
    applyTheme(mode)
  }

  return {
    theme,
    applyStoredTheme,
    toggleTheme,
    setTheme
  }
})
