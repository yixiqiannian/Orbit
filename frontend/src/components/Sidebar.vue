<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import {
  Odometer,
  List,
  Timer,
  Reading,
  Message,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const menuItems = [
  { path: '/', name: 'Dashboard', icon: Odometer, title: '仪表盘' },
  { path: '/tasks', name: 'Tasks', icon: List, title: '任务管理' },
  { path: '/cron', name: 'CronJobs', icon: Timer, title: '定时任务' },
  { path: '/reading', name: 'Reading', icon: Reading, title: '阅读规划' },
  { path: '/email', name: 'Email', icon: Message, title: '邮箱' }
]

function handleMenuClick(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h2 v-show="!appStore.sidebarCollapsed" class="logo">Orbit</h2>
      <el-icon class="collapse-btn" @click="appStore.toggleSidebar">
        <Fold v-if="!appStore.sidebarCollapsed" />
        <Expand v-else />
      </el-icon>
    </div>
    <el-menu
      :default-active="route.path"
      :collapse="appStore.sidebarCollapsed"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409eff"
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
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  color: #fff;
}

.logo {
  margin: 0;
  font-size: 20px;
  white-space: nowrap;
}

.collapse-btn {
  cursor: pointer;
  font-size: 18px;
  color: #bfcbd9;
}

.collapse-btn:hover {
  color: #409eff;
}

.el-menu {
  border-right: none;
}
</style>
