<template>
  <div class="tasks-page">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="每日任务" name="daily" />
      <el-tab-pane label="工作规划" name="plan" />
      <el-tab-pane label="目标管理" name="goal" />
    </el-tabs>

    <!-- 添加任务 -->
    <el-form :inline="true" style="margin: 20px 0;">
      <el-form-item>
        <el-input v-model="newTask.title" placeholder="任务标题" @keyup.enter="handleAdd" style="width: 300px;" />
      </el-form-item>
      <el-form-item>
        <el-select v-model="newTask.priority" placeholder="优先级" style="width: 120px;">
          <el-option label="普通" :value="0" />
          <el-option label="重要" :value="1" />
          <el-option label="紧急" :value="2" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-date-picker v-model="newTask.due_date" type="date" placeholder="截止日期" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleAdd">添加任务</el-button>
      </el-form-item>
    </el-form>

    <!-- 任务卡片列表 -->
    <div v-loading="loading" class="card-grid">
      <el-card
        v-for="task in tasks"
        :key="task.id"
        class="task-card"
        shadow="hover"
      >
        <div class="card-header">
          <el-tag
            :type="task.priority === 2 ? 'danger' : task.priority === 1 ? 'warning' : 'info'"
            size="small"
          >
            {{ task.priority === 2 ? '紧急' : task.priority === 1 ? '重要' : '普通' }}
          </el-tag>
          <el-dropdown @command="(cmd: string) => handleStatusChange(task, cmd)">
            <el-tag :type="getStatusType(task.status)" style="cursor: pointer;">
              {{ getStatusLabel(task.status) }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-tag>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pending">待办</el-dropdown-item>
                <el-dropdown-item command="in_progress">进行中</el-dropdown-item>
                <el-dropdown-item command="completed">已完成</el-dropdown-item>
                <el-dropdown-item command="cancelled">已取消</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="card-body">
          <h3 :class="{ 'completed': task.status === 'completed' }">{{ task.title }}</h3>
          <p v-if="task.description" class="desc">{{ task.description }}</p>
        </div>

        <div class="card-footer">
          <span v-if="task.due_date" class="due-date">
            <el-icon><Calendar /></el-icon>
            {{ task.due_date }}
          </span>
          <span v-else class="due-date">无截止日期</span>
          <el-button type="danger" size="small" text @click="handleDelete(task.id)">删除</el-button>
        </div>
      </el-card>

      <!-- 空状态 -->
      <el-empty v-if="!loading && tasks.length === 0" description="暂无任务" />
    </div>

    <!-- 分页 -->
    <el-pagination
      v-if="total > 20"
      v-model:current-page="page"
      :page-size="20"
      :total="total"
      layout="prev, pager, next"
      @current-change="loadTasks"
      style="margin-top: 20px; justify-content: center;"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { taskApi } from '../api/tasks'
import { ElMessage } from 'element-plus'
import { Calendar, ArrowDown } from '@element-plus/icons-vue'

const activeTab = ref('daily')
const tasks = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const newTask = ref({ title: '', type: 'daily', priority: 0, due_date: '' })

onMounted(() => loadTasks())

async function loadTasks() {
  loading.value = true
  try {
    const res = await taskApi.list({ type: activeTab.value, page: page.value })
    tasks.value = res.items
    total.value = res.total
  } catch (e) {
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  if (!newTask.value.title) return ElMessage.warning('请输入任务标题')
  try {
    await taskApi.create({ ...newTask.value, type: activeTab.value })
    ElMessage.success('添加成功')
    newTask.value.title = ''
    newTask.value.due_date = ''
    newTask.value.priority = 0
    loadTasks()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

async function handleStatusChange(task: any, status: string) {
  try {
    await taskApi.update(task.id, { status })
    task.status = status
    ElMessage.success('状态更新成功')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

async function handleDelete(id: number) {
  try {
    await taskApi.delete(id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

function handleTabClick() {
  page.value = 1
  loadTasks()
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待办',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}
</script>

<style scoped>
.tasks-page {
  padding: 0;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.task-card {
  transition: transform 0.2s;
}

.task-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-body h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #303133;
}

.card-body h3.completed {
  text-decoration: line-through;
  color: #909399;
}

.card-body .desc {
  margin: 0;
  font-size: 14px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.due-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}
</style>
