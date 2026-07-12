<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { SwitchButton, User } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

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
    <div class="header-right">
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
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.page-title {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #606266;
}

.user-info:hover {
  color: #409eff;
}
</style>
