<script setup lang="ts">
import { useAppStore } from '../stores/app'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

const appStore = useAppStore()
</script>

<template>
  <el-container class="layout-container">
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '220px'" class="layout-aside">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <Header />
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
  /* 氛围光背景：蓝色/橙色大光斑（MASTER.md「玻璃拟态」），玻璃才有折射质感 */
  background-color: var(--color-background, #f8fafc);
  background-image:
    radial-gradient(900px 620px at 10% -8%, rgba(37, 99, 235, 0.18), transparent 62%),
    radial-gradient(760px 520px at 98% 4%, rgba(249, 115, 22, 0.14), transparent 62%),
    radial-gradient(820px 640px at 85% 102%, rgba(59, 130, 246, 0.14), transparent 62%),
    radial-gradient(560px 420px at 24% 98%, rgba(249, 115, 22, 0.1), transparent 60%);
  transition: background-color 0.3s ease;
}

.layout-aside {
  background: transparent;
  border-right: none;
  transition: width 0.3s ease;
  overflow: hidden;
}

.layout-header {
  background: transparent;
  border-bottom: none;
  display: flex;
  align-items: center;
  padding: 0;
}

.layout-main {
  background: transparent;
  padding: 20px;
  overflow-y: auto;
}
</style>
