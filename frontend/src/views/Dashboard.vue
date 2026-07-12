<template>
  <div class="dashboard" v-loading="loading">
    <h2>📊 仪表盘</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>📋 任务</template>
          <div class="stat-value">{{ stats.tasks?.total || 0 }}</div>
          <div class="stat-label">
            待办 {{ stats.tasks?.pending || 0 }} |
            进行中 {{ stats.tasks?.in_progress || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>⏰ 定时任务</template>
          <div class="stat-value">{{ stats.cron?.total_jobs || 0 }}</div>
          <div class="stat-label">
            成功率 {{ stats.cron?.success_rate || 0 }}%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>📚 阅读</template>
          <div class="stat-value">{{ stats.reading?.total_books || 0 }}</div>
          <div class="stat-label">
            在读 {{ stats.reading?.reading || 0 }} |
            已读 {{ stats.reading?.finished || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>📅 今日完成</template>
          <div class="stat-value">{{ stats.tasks?.completed_today || 0 }}</div>
          <div class="stat-label">
            逾期 {{ stats.tasks?.overdue || 0 }} 项
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近任务 + 最近执行记录 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>最近任务</template>
          <el-table :data="stats.recent_tasks" stripe>
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>最近执行记录</template>
          <el-table :data="stats.recent_executions" stripe>
            <el-table-column prop="cron_job_name" label="任务" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { dashboardApi } from '../api/dashboard'

const loading = ref(false)
const stats = reactive<any>({
  tasks: {},
  cron: {},
  reading: {},
  recent_tasks: [],
  recent_executions: []
})

onMounted(async () => {
  loading.value = true
  try {
    const data = await dashboardApi.getStats()
    Object.assign(stats, data)
  } catch (e) {
    console.error('Failed to load dashboard stats:', e)
  } finally {
    loading.value = false
  }
})

function getStatusType(status: string) {
  const map: Record<string, string> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.dashboard h2 {
  margin: 0 0 20px;
  color: #303133;
}
.stat-cards {
  margin-bottom: 20px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}
.stat-label {
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
}
</style>
