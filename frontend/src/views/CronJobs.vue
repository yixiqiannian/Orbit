<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { cronApi, type CronJob, type CronExecution } from '../api/cron'
import { ElMessage } from 'element-plus'

const jobs = ref<CronJob[]>([])
const executions = ref<CronExecution[]>([])
const showHistory = ref(false)
const runningId = ref<string>('')
const loading = ref(false)

onMounted(() => loadJobs())

async function loadJobs() {
  loading.value = true
  try {
    jobs.value = await cronApi.listJobs()
  } catch (e) {
    ElMessage.error('加载定时任务失败')
  } finally {
    loading.value = false
  }
}

async function handleRun(jobId: string) {
  runningId.value = jobId
  try {
    const res = await cronApi.runJob(jobId)
    ElMessage.success(res.message || '任务已触发')
    loadJobs()
  } catch (error) {
    ElMessage.error('执行失败')
  } finally {
    runningId.value = ''
  }
}

async function handlePause(jobId: string) {
  try {
    await cronApi.pauseJob(jobId)
    ElMessage.success('已暂停')
    loadJobs()
  } catch (e) {
    ElMessage.error('暂停失败')
  }
}

async function handleResume(jobId: string) {
  try {
    await cronApi.resumeJob(jobId)
    ElMessage.success('已恢复')
    loadJobs()
  } catch (e) {
    ElMessage.error('恢复失败')
  }
}

async function viewHistory(jobId: string) {
  try {
    executions.value = await cronApi.listExecutions(jobId)
    showHistory.value = true
  } catch (e) {
    ElMessage.error('加载执行记录失败')
  }
}
</script>

<template>
  <div class="cron-page">
    <div class="page-header">
      <h2>⏰ 定时任务</h2>
    </div>

    <!-- 任务列表 -->
    <el-table :data="jobs" v-loading="loading" stripe>
      <el-table-column prop="name" label="任务名称" min-width="150" />
      <el-table-column prop="schedule" label="调度规则" width="150" />
      <el-table-column prop="enabled" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">
            {{ row.enabled ? '运行中' : '已暂停' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_run" label="上次执行" width="180">
        <template #default="{ row }">
          {{ row.last_run || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="last_status" label="执行结果" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.last_status" :type="row.last_status === 'success' ? 'success' : 'danger'">
            {{ row.last_status }}
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="handleRun(row.id)"
            :loading="runningId === row.id"
          >
            立即执行
          </el-button>
          <el-button
            v-if="row.enabled"
            type="warning"
            size="small"
            @click="handlePause(row.id)"
          >
            暂停
          </el-button>
          <el-button
            v-else
            type="success"
            size="small"
            @click="handleResume(row.id)"
          >
            恢复
          </el-button>
          <el-button
            size="small"
            @click="viewHistory(row.id)"
          >
            历史
          </el-button>
        </template>
      </el-table-column>
    </el-table>

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
        <el-table-column prop="result" label="结果" show-overflow-tooltip />
        <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}
</style>
