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
        <el-input v-model="newTask.title" placeholder="任务标题" @keyup.enter="handleAdd" />
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

    <!-- 任务列表 -->
    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-select v-model="row.status" @change="handleStatusChange(row)" style="width: 100px;">
            <el-option label="待办" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="优先级" width="100">
        <template #default="{ row }">
          <el-tag :type="row.priority === 2 ? 'danger' : row.priority === 1 ? 'warning' : 'info'">
            {{ row.priority === 2 ? '紧急' : row.priority === 1 ? '重要' : '普通' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="due_date" label="截止日期" width="120" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
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

async function handleStatusChange(task: any) {
  try {
    await taskApi.update(task.id, { status: task.status })
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
</script>

<style scoped>
.tasks-page {
  padding: 0;
}
</style>
