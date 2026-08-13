<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { SwitchButton, User, Sunny, Moon } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { getDailyQuote } from '../data/quotes'

const userStore = useUserStore()
const themeStore = useThemeStore()
const router = useRouter()

const isDark = computed(() => themeStore.theme === 'dark')
const dailyQuote = computed(() => getDailyQuote())

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.logout()
    router.push('/login')
  } catch {
    // cancelled
  }
}
</script>

<template>
  <div class="header">
    <div class="header-left">
      <h3 class="page-title">Orbit 管理系统</h3>
    </div>
    <div class="header-center" :title="`${dailyQuote.text} —— ${dailyQuote.from}`">
      <span class="quote-mark">「</span>
      <span class="quote-text">{{ dailyQuote.text }}</span>
      <span class="quote-from">—— {{ dailyQuote.from }}</span>
      <span class="quote-mark">」</span>
    </div>
    <div class="header-right">
      <el-tooltip :content="isDark ? '切换到浅色模式' : '切换到深色模式'" placement="bottom">
        <button
          class="theme-toggle"
          type="button"
          :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'"
          @click="themeStore.toggleTheme()"
        >
          <el-icon class="theme-icon" :class="{ 'is-dark': isDark }">
            <Sunny v-if="isDark" />
            <Moon v-else />
          </el-icon>
        </button>
      </el-tooltip>
      <el-dropdown>
        <span class="user-info">
          <el-icon><User /></el-icon>
          <span>{{ userStore.userInfo?.username || '用户' }}</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style scoped>
/* 玻璃条：半透明白 + blur(20px) + 底部 1px 半透明边框（MASTER.md 玻璃范式） */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  width: 100%;
  height: 100%;
  padding: 0 20px;
  background: var(--glass-bg, rgba(255, 255, 255, 0.55));
  backdrop-filter: blur(var(--glass-blur, 20px));
  -webkit-backdrop-filter: blur(var(--glass-blur, 20px));
  border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.6));
  box-shadow: 0 1px 12px rgba(37, 99, 235, 0.06);
  transition: background-color 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.page-title {
  margin: 0;
  font-family: var(--font-display, 'Fredoka', 'Fira Sans', sans-serif);
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--color-foreground, #0f172a);
  white-space: nowrap;
  transition: color 0.25s ease;
}

/* 每日一言：绝对居中，不挤压左右两端的标题和操作区 */
.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 4px;
  max-width: 55%;
  font-size: 13px;
  color: var(--color-foreground, #0f172a);
  opacity: 0.72;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.25s ease, opacity 0.25s ease;
  cursor: default;
}

.header-center:hover {
  opacity: 1;
  color: var(--color-primary, #2563eb);
}

.quote-mark {
  font-family: var(--font-display, 'Fredoka', 'Fira Sans', sans-serif);
  color: var(--color-primary, #2563eb);
  opacity: 0.8;
}

.quote-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quote-from {
  color: var(--color-foreground, #0f172a);
  opacity: 0.55;
  font-size: 12px;
  flex-shrink: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.6));
  border-radius: 10px;
  background: transparent;
  color: var(--color-foreground, #0f172a);
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease, background-color 0.2s ease,
    box-shadow 0.2s ease, transform 0.3s ease;
}

.theme-toggle:hover {
  color: var(--color-primary, #2563eb);
  border-color: var(--color-primary, #2563eb);
  background-color: var(--glass-hover, rgba(37, 99, 235, 0.08));
  box-shadow: 0 0 16px rgba(37, 99, 235, 0.18);
}

.theme-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.theme-icon.is-dark {
  transform: rotate(180deg);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  color: var(--color-foreground, #0f172a);
  transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

.user-info:hover {
  color: var(--color-primary, #2563eb);
  background-color: var(--glass-hover, rgba(37, 99, 235, 0.08));
  border-color: var(--glass-border, rgba(255, 255, 255, 0.6));
}
</style>
