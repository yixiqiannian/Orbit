<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import {
  Odometer,
  List,
  Timer,
  Reading,
  Message,
  Location,
  Notebook,
  Folder,
  Fold,
  Expand,
  Calendar,
  Box
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const menuItems = [
  { path: '/', name: 'Dashboard', icon: Odometer, title: '仪表盘' },
  { path: '/tasks', name: 'Tasks', icon: List, title: '任务管理' },
  { path: '/projects', name: 'Projects', icon: Folder, title: '项目管理' },
  { path: '/cron', name: 'CronJobs', icon: Timer, title: '定时任务' },
  { path: '/reading', name: 'Reading', icon: Reading, title: '阅读规划' },
  { path: '/email', name: 'Email', icon: Message, title: '邮箱' },
  { path: '/nav', name: 'NavManage', icon: Location, title: '导航管理' },
  { path: '/knowledge', name: 'Knowledge', icon: Notebook, title: '知识卡片' },
  { path: '/daily-logs', name: 'DailyLogs', icon: Calendar, title: '每日日志' },
  { path: '/archives', name: 'Archives', icon: Box, title: '任务归档' }
]

function handleMenuClick(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-header" :class="{ collapsed: appStore.sidebarCollapsed }">
      <h2 v-show="!appStore.sidebarCollapsed" class="logo">Orbit</h2>
      <el-icon class="collapse-btn" @click="appStore.toggleSidebar">
        <Fold v-if="!appStore.sidebarCollapsed" />
        <Expand v-else />
      </el-icon>
    </div>
    <el-menu
      :default-active="route.path"
      :collapse="appStore.sidebarCollapsed"
      class="sidebar-menu"
      @select="(index: string) => handleMenuClick(index)"
    >
      <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
        <el-icon><component :is="item.icon" /></el-icon>
        <template #title>{{ item.title }}</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<style scoped>
/* 玻璃面板：半透明背景 + blur(20px) + 圆角 16px + 1px 半透明描边 + 蓝色光晕阴影 */
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: 12px;
  background: var(--glass-bg, rgba(255, 255, 255, 0.55));
  backdrop-filter: blur(var(--glass-blur, 20px));
  -webkit-backdrop-filter: blur(var(--glass-blur, 20px));
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.6));
  border-radius: var(--glass-radius, 16px);
  box-shadow: var(--glass-shadow, 0 8px 32px rgba(37, 99, 235, 0.14));
  overflow: hidden;
  transition: background-color 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  color: var(--color-foreground, #0f172a);
  transition: color 0.25s ease;
}

.sidebar-header.collapsed {
  justify-content: center;
  padding: 16px 0;
}

/* Logo：Fredoka 加粗 + 品牌渐变文字（#2563EB → #3B82F6 → #F97316） */
.logo {
  margin: 0;
  font-family: var(--font-display, 'Fredoka', 'Fira Sans', sans-serif);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
  white-space: nowrap;
  background: var(--gradient-brand, linear-gradient(90deg, #2563eb, #3b82f6, #f97316));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}

.collapse-btn {
  cursor: pointer;
  font-size: 18px;
  color: var(--color-foreground, #0f172a);
  transition: color 0.2s ease, transform 0.25s ease;
}

.collapse-btn:hover {
  color: var(--color-primary, #2563eb);
  transform: scale(1.12);
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 4px 8px 12px;
  overflow-y: auto;
}

/* 菜单项：圆角 8px，hover 用主色浅变体，active 用 #2563EB 渐变高亮 */
:deep(.el-menu-item) {
  height: 42px;
  line-height: 42px;
  margin-bottom: 4px;
  border-radius: var(--glass-radius-sm, 8px);
  color: var(--color-foreground, #0f172a);
  transition: background-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

:deep(.el-menu-item .el-icon) {
  color: inherit;
}

:deep(.el-menu-item:hover) {
  background-color: var(--glass-hover, rgba(37, 99, 235, 0.08));
  color: var(--color-primary, #2563eb);
}

:deep(.el-menu-item.is-active) {
  background: var(--gradient-active, linear-gradient(90deg, #2563eb, #3b82f6));
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #ffffff;
}

/* 折叠态：菜单宽度铺满玻璃面板，图标居中 */
:deep(.el-menu--collapse) {
  width: 100%;
}

:deep(.el-menu--collapse .el-menu-item) {
  width: 100%;
  padding: 0;
  justify-content: center;
}

/* 折叠时弹出层（tooltip）文字保持浅色可读 */
:deep(.el-menu--collapse .el-tooltip__trigger) {
  color: var(--color-foreground, #0f172a);
}

/* 细滚动条（菜单过长时） */
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.35);
  border-radius: 4px;
}
</style>
