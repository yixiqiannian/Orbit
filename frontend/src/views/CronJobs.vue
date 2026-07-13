<template>
  <div class="cron-page">
    <div class="page-header">
      <h2>⏰ 定时任务</h2>
      <el-button @click="loadJobs" :loading="loading">刷新</el-button>
    </div>

    <!-- 任务卡片列表 -->
    <div v-loading="loading" class="card-grid">
      <el-card
        v-for="job in jobs"
        :key="job.id"
        class="job-card"
        shadow="hover"
      >
        <div class="card-header">
          <div class="job-name">
            <el-tag :type="job.enabled ? 'success' : 'info'" size="small">
              {{ job.enabled ? '运行中' : '已暂停' }}
            </el-tag>
            <span>{{ job.name }}</span>
          </div>
          <el-button
            type="primary"
            size="small"
            @click="runJob(job.id)"
            :loading="runningId === job.id"
          >
            立即执行
          </el-button>
          <el-button
            type="info"
            size="small"
            @click="viewHistory(job.id)"
          >
            查看历史
          </el-button>
        </div>

        <div class="card-body">
          <div class="info-item">
            <span class="label">调度规则：</span>
            <el-tag type="warning" size="small">{{ job.schedule }}</el-tag>
          </div>
          <div class="info-item">
            <span class="label">上次执行：</span>
            <span>{{ job.last_run || '未执行' }}</span>
          </div>
          <div class="info-item" v-if="job.status">
            <span class="label">执行状态：</span>
            <el-tag :type="job.status === 'ok' ? 'success' : 'danger'" size="small">
              {{ job.status === 'ok' ? '成功' : '失败' }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <el-empty v-if="!loading && jobs.length === 0" description="暂无定时任务" />
    </div>

    <!-- 执行记录对话框 -->
    <el-dialog v-model="showHistory" title="执行记录" width="800px">
      <el-table :data="executions" stripe>
        <el-table-column prop="executed_at" label="执行时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" />
        <el-table-column prop="error_message" label="错误信息" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { cronApi, type CronJob, type CronExecution } from '../api/cron'
import { ElMessage } from 'element-plus'

const jobs = ref<CronJob[]>([])
const executions = ref<CronExecution[]>([])
const showHistory = ref(false)
const loading = ref(false)
const runningId = ref<string | null>(null)

onMounted(() => loadJobs())

async function loadJobs() {
  loading.value = true
  try {
    jobs.value = await cronApi.listJobs()
  } catch (e) {
    ElMessage.error('加载任务失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

async function runJob(jobId: string) {
  runningId.value = jobId
  try {
    const res = await cronApi.runJob(jobId)
    if (res.success) {
      ElMessage.success(res.message)
    } else {
      ElMessage.warning(res.message)
    }
    loadJobs()
  } catch (e) {
    ElMessage.error('执行失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    runningId.value = null
  }
}

async function viewHistory(jobId: string) {
  try {
    executions.value = await cronApi.listExecutions(jobId)
    showHistory.value = true
  } catch (e) {
    ElMessage.error('加载执行记录失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  }
}
</script>

<style scoped>
.cron-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.job-card {
  transition: transform 0.2s;
}

.job-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.job-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.info-item .label {
  color: #909399;
  min-width: 80px;
}
</style>
