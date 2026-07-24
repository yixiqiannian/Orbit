<template>
  <div class="tasks-page">
    <!-- 热力图 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>📅 任务完成热力图</template>
      <TaskHeatmap
        :data="heatmapData?.data"
        :start-date="heatmapData?.start_date"
        :end-date="heatmapData?.end_date"
      />
    </el-card>

    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="每日任务" name="daily" />
      <el-tab-pane label="工作规划" name="plan" />
      <el-tab-pane label="目标管理" name="goal" />
    </el-tabs>

    <!-- 添加任务 -->
    <el-form :inline="true" style="margin: 20px 0;">
      <el-form-item>
        <el-input v-model="newTask.title" placeholder="任务标题" @keyup.enter="handleAdd" style="width: 240px;" />
      </el-form-item>
      <el-form-item>
        <el-select v-model="newTask.category_id" placeholder="分类" clearable style="width: 120px;">
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
          <el-option value="add_new">
            <el-button text type="primary" @click.stop="showAddCategory = true">
              <el-icon><Plus /></el-icon> 新增分类
            </el-button>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-select v-model="newTask.project_id" placeholder="项目" clearable style="width: 140px;">
          <el-option
            v-for="p in projects"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-select v-model="newTask.priority" placeholder="优先级" style="width: 100px;">
          <el-option label="低" value="low" />
          <el-option label="普通" value="normal" />
          <el-option label="高" value="high" />
          <el-option label="紧急" value="urgent" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-date-picker v-model="newTask.due_date" type="date" placeholder="截止日期" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleAdd">添加任务</el-button>
      </el-form-item>
    </el-form>

    <!-- 筛选 -->
    <el-form :inline="true" style="margin: 10px 0;">
      <el-form-item label="分类">
        <el-select v-model="filterCategory" placeholder="全部" clearable style="width: 120px;" @change="loadTasks">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="项目">
        <el-select v-model="filterProject" placeholder="全部" clearable style="width: 140px;" @change="loadTasks">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </el-form-item>
    </el-form>

    <!-- 任务卡片列表 -->
    <div v-loading="loading" class="card-grid">
      <el-card
        v-for="task in sortedTasks"
        :key="task.id"
        class="task-card"
        :class="getOverdueClass(task)"
        shadow="hover"
      >
        <div class="card-header">
          <div class="header-left">
            <el-tag
              :type="getPriorityType(task.priority)"
              size="small"
            >
              {{ getPriorityLabel(task.priority) }}
            </el-tag>
            <el-tag v-if="task.category_name" size="small" effect="plain" type="info">
              {{ task.category_name }}
            </el-tag>
            <el-tag v-if="task.project_name" size="small" effect="plain">
              {{ task.project_name }}
            </el-tag>
          </div>
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
          <div class="due-info">
            <span v-if="task.due_date" class="due-date">
              <el-icon><Calendar /></el-icon>
              {{ task.due_date }}
            </span>
            <span v-else class="due-date">无截止日期</span>
            <el-tag
              v-if="getOverdueStatus(task) === 'overdue'"
              type="danger"
              size="small"
              effect="dark"
            >已过期</el-tag>
            <el-tag
              v-else-if="getOverdueStatus(task) === 'soon'"
              type="warning"
              size="small"
              effect="dark"
            >即将过期</el-tag>
          </div>
          <div class="footer-actions">
            <el-button type="primary" size="small" text @click="openLogDialog(task)">日志</el-button>
            <el-button type="danger" size="small" text @click="handleDelete(task.id)">删除</el-button>
          </div>
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

    <!-- 日志详情弹窗 -->
    <el-dialog
      v-model="logDialogVisible"
      :title="`任务日志 - ${selectedTask?.title || ''}`"
      width="800px"
      destroy-on-close
    >
      <div class="log-dialog-content">
        <div class="log-dialog-left">
          <h4>任务信息</h4>
          <div class="task-info-item">
            <span class="label">标题：</span>
            <span>{{ selectedTask?.title }}</span>
          </div>
          <div class="task-info-item">
            <span class="label">状态：</span>
            <el-tag :type="getStatusType(selectedTask?.status)" size="small">
              {{ getStatusLabel(selectedTask?.status) }}
            </el-tag>
          </div>
          <div class="task-info-item">
            <span class="label">优先级：</span>
            <el-tag :type="getPriorityType(selectedTask?.priority)" size="small">
              {{ getPriorityLabel(selectedTask?.priority) }}
            </el-tag>
          </div>
          <div v-if="selectedTask?.category_name" class="task-info-item">
            <span class="label">分类：</span>
            <span>{{ selectedTask.category_name }}</span>
          </div>
          <div v-if="selectedTask?.project_name" class="task-info-item">
            <span class="label">项目：</span>
            <span>{{ selectedTask.project_name }}</span>
          </div>
          <div v-if="selectedTask?.due_date" class="task-info-item">
            <span class="label">截止日期：</span>
            <span>{{ selectedTask.due_date }}</span>
          </div>
        </div>
        <div class="log-dialog-right">
          <TaskLogTimeline v-if="selectedTask" :task-id="selectedTask.id" />
        </div>
      </div>
    </el-dialog>

    <!-- 新增分类弹窗 -->
    <el-dialog v-model="showAddCategory" title="新增分类" width="400px" destroy-on-close>
      <el-form :model="newCategory" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="newCategory.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="newCategory.icon" placeholder="如：📚" style="width: 80px;" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="newCategory.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCategory = false">取消</el-button>
        <el-button type="primary" @click="handleAddCategory">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { taskApi, type Task } from '../api/tasks'
import { taskCategoryApi, type TaskCategory } from '../api/taskCategory'
import { projectApi, type Project } from '../api/project'
import { dashboardApi, type HeatmapData } from '../api/dashboard'
import { ElMessage } from 'element-plus'
import { Calendar, ArrowDown } from '@element-plus/icons-vue'
import TaskLogTimeline from '../components/TaskLogTimeline.vue'
import TaskHeatmap from '../components/TaskHeatmap.vue'

const activeTab = ref('daily')
const tasks = ref<Task[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const categories = ref<TaskCategory[]>([])
const projects = ref<Project[]>([])
const newTask = ref({
  title: '',
  type: 'daily',
  priority: 'normal',
  due_date: '',
  category_id: undefined as number | undefined,
  project_id: undefined as number | undefined
})
const heatmapData = ref<HeatmapData | null>(null)

// 筛选
const filterCategory = ref<number | undefined>(undefined)
const filterProject = ref<number | undefined>(undefined)

// 日志弹窗
const logDialogVisible = ref(false)
const selectedTask = ref<Task | null>(null)

// 分类弹窗
const showAddCategory = ref(false)
const newCategory = ref({
  name: '',
  icon: '📚',
  color: '#409EFF'
})

// 过期任务排序：过期的置顶
const sortedTasks = computed(() => {
  const list = [...tasks.value]
  return list.sort((a, b) => {
    const aOverdue = getOverdueSortKey(a)
    const bOverdue = getOverdueSortKey(b)
    if (aOverdue !== bOverdue) return aOverdue - bOverdue
    return 0
  })
})

function getOverdueSortKey(task: Task): number {
  if (!task.due_date || task.status === 'completed' || task.status === 'cancelled') return 2
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const due = new Date(task.due_date)
  due.setHours(0, 0, 0, 0)
  const diff = (due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
  if (diff < 0) return 0 // overdue - top
  if (diff <= 3) return 1 // soon
  return 2 // normal
}

function getOverdueStatus(task: Task): 'overdue' | 'soon' | 'normal' {
  if (!task.due_date || task.status === 'completed' || task.status === 'cancelled') return 'normal'
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const due = new Date(task.due_date)
  due.setHours(0, 0, 0, 0)
  const diff = (due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
  if (diff < 0) return 'overdue'
  if (diff <= 3) return 'soon'
  return 'normal'
}

function getOverdueClass(task: Task): string {
  const status = getOverdueStatus(task)
  if (status === 'overdue') return 'overdue-card'
  if (status === 'soon') return 'soon-card'
  return ''
}

onMounted(() => {
  loadTasks()
  loadHeatmap()
  loadCategories()
  loadProjects()
})

// 切换 tab 时重新加载数据（修复切换 bug）
function handleTabClick() {
  page.value = 1
  tasks.value = []
  loadTasks()
}

async function loadHeatmap() {
  try {
    heatmapData.value = await dashboardApi.getHeatmap(365)
  } catch (e) {
    console.error('Failed to load heatmap:', e)
  }
}

async function loadCategories() {
  try {
    categories.value = await taskCategoryApi.list()
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
}

async function loadProjects() {
  try {
    const res = await projectApi.list()
    projects.value = res.items || res as any
  } catch (e) {
    console.error('Failed to load projects:', e)
  }
}

async function loadTasks() {
  loading.value = true
  try {
    const res = await taskApi.list({
      type: activeTab.value,
      page: page.value,
      category_id: filterCategory.value,
      project_id: filterProject.value
    })
    tasks.value = res.items
    total.value = res.total
  } catch (e: any) {
    ElMessage.error('加载任务失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  if (!newTask.value.title) return ElMessage.warning('请输入任务标题')
  try {
    await taskApi.create({
      title: newTask.value.title,
      type: activeTab.value,
      priority: newTask.value.priority,
      due_date: newTask.value.due_date || undefined,
      category_id: newTask.value.category_id || undefined,
      project_id: newTask.value.project_id || undefined
    })
    ElMessage.success('添加成功')
    newTask.value.title = ''
    newTask.value.due_date = ''
    newTask.value.priority = 'normal'
    newTask.value.category_id = undefined
    newTask.value.project_id = undefined
    loadTasks()
  } catch (e: any) {
    ElMessage.error('添加失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  }
}

async function handleStatusChange(task: Task, status: string) {
  try {
    await taskApi.update(task.id, { status })
    task.status = status
    ElMessage.success('状态更新成功')
  } catch (e: any) {
    ElMessage.error('更新失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  }
}

async function handleDelete(id: number) {
  try {
    await taskApi.delete(id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (e: any) {
    ElMessage.error('删除失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  }
}

async function handleAddCategory() {
  if (!newCategory.value.name) return ElMessage.warning('请输入分类名称')
  try {
    await taskCategoryApi.create(newCategory.value)
    ElMessage.success('分类创建成功')
    showAddCategory.value = false
    newCategory.value = { name: '', icon: '📚', color: '#409EFF' }
    loadCategories()
  } catch (e: any) {
    ElMessage.error('创建失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  }
}

function openLogDialog(task: Task) {
  selectedTask.value = task
  logDialogVisible.value = true
}

function getStatusType(status?: string) {
  const map: Record<string, string> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status || ''] || 'info'
}

function getStatusLabel(status?: string) {
  const map: Record<string, string> = {
    pending: '待办',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status || ''] || status || ''
}

function getPriorityType(priority?: string) {
  const map: Record<string, string> = {
    low: 'info',
    normal: '',
    high: 'warning',
    urgent: 'danger'
  }
  return map[priority || ''] || ''
}

function getPriorityLabel(priority?: string) {
  const map: Record<string, string> = {
    low: '低',
    normal: '普通',
    high: '高',
    urgent: '紧急'
  }
  return map[priority || ''] || priority || '普通'
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

/* 过期任务样式 */
.overdue-card {
  background: #fef0f0;
  border-left: 3px solid #f56c6c;
}

.soon-card {
  background: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 8px;
}

.header-left {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
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

.due-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.due-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.footer-actions {
  display: flex;
  gap: 4px;
}

/* 日志弹窗布局 */
.log-dialog-content {
  display: flex;
  gap: 20px;
  min-height: 400px;
}

.log-dialog-left {
  width: 200px;
  flex-shrink: 0;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.log-dialog-left h4 {
  margin: 0 0 16px;
  font-size: 15px;
  color: #303133;
}

.task-info-item {
  margin-bottom: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-info-item .label {
  color: #909399;
  flex-shrink: 0;
}

.log-dialog-right {
  flex: 1;
  overflow-y: auto;
  max-height: 500px;
}
</style>
