<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { taskApi, type Task } from '../api/tasks'
import { taskCategoryApi, type TaskCategory } from '../api/taskCategory'
import { projectApi, type Project } from '../api/project'

interface ArchiveFolder {
  month: string
  total: number
  completed: number
  tasks: Task[]
}

const loading = ref(false)
const allTasks = ref<Task[]>([])
const categories = ref<TaskCategory[]>([])
const projects = ref<Project[]>([])
const filterCategory = ref<number | undefined>(undefined)
const filterProject = ref<number | undefined>(undefined)
const dialogVisible = ref(false)
const selectedFolder = ref<ArchiveFolder | null>(null)

const folders = computed<ArchiveFolder[]>(() => {
  const map: Record<string, ArchiveFolder> = {}
  for (const task of allTasks.value) {
    const month = task.archived_month || task.updated_at?.slice(0, 7) || 'unknown'
    if (!map[month]) {
      map[month] = { month, total: 0, completed: 0, tasks: [] }
    }
    map[month].total++
    if (task.status === 'completed') map[month].completed++
    map[month].tasks.push(task)
  }
  return Object.values(map).sort((a, b) => b.month.localeCompare(a.month))
})

const folderTasks = computed(() => selectedFolder.value?.tasks || [])

async function loadArchives() {
  loading.value = true
  try {
    const params: any = { archived: true, size: 100 }
    if (filterCategory.value) params.category_id = filterCategory.value
    if (filterProject.value) params.project_id = filterProject.value
    const res = await taskApi.list(params)
    allTasks.value = res.items || []
  } catch (e) {
    console.error('Failed to load archives:', e)
  } finally {
    loading.value = false
  }
}

async function loadFilters() {
  try {
    const [catRes, projRes] = await Promise.all([
      taskCategoryApi.list(),
      projectApi.getAll()
    ])
    categories.value = catRes || []
    projects.value = projRes || []
  } catch (e) {
    console.error('Failed to load filters:', e)
  }
}

function openFolder(folder: ArchiveFolder) {
  selectedFolder.value = folder
  dialogVisible.value = true
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    completed: 'success',
    in_progress: 'warning',
    cancelled: 'info'
  }
  return map[status] || ''
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    completed: '已完成',
    in_progress: '进行中',
    cancelled: '已取消',
    todo: '待办'
  }
  return map[status] || status
}

function getPriorityType(priority: string) {
  const map: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[priority] || ''
}

function getPriorityLabel(priority: string) {
  const map: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[priority] || priority
}

function formatDate(date?: string) {
  if (!date) return '-'
  return date.slice(0, 10)
}

onMounted(() => {
  loadFilters()
  loadArchives()
})
</script>

<template>
  <div class="archives-page">
    <h1>📁 任务归档</h1>

    <!-- 搜索筛选 -->
    <el-form :inline="true" style="margin: 20px 0;">
      <el-form-item label="分类">
        <el-select v-model="filterCategory" clearable placeholder="全部分类" @change="loadArchives">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="项目">
        <el-select v-model="filterProject" clearable placeholder="全部项目" @change="loadArchives">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </el-form-item>
    </el-form>

    <!-- 加载状态 -->
    <div v-if="loading" v-loading="loading" style="min-height: 200px;"></div>

    <!-- 空状态 -->
    <el-empty v-else-if="folders.length === 0" description="暂无归档任务" />

    <!-- 文件夹网格 -->
    <div v-else class="folder-grid">
      <div
        v-for="folder in folders"
        :key="folder.month"
        class="folder-card"
        @click="openFolder(folder)"
      >
        <div class="folder-icon">📁</div>
        <div class="folder-name">{{ folder.month }}</div>
        <div class="folder-stats">
          {{ folder.completed }}/{{ folder.total }} 完成
        </div>
        <el-progress
          :percentage="folder.total > 0 ? Math.round(folder.completed / folder.total * 100) : 0"
          :stroke-width="4"
          :show-text="false"
          style="margin-top: 8px;"
        />
      </div>
    </div>

    <!-- 文件夹详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="`📁 ${selectedFolder?.month} 归档任务`"
      width="900px"
      destroy-on-close
    >
      <el-table :data="folderTasks" style="width: 100%" stripe>
        <el-table-column prop="title" label="任务标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="project_name" label="项目" width="120" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="完成日期" width="120" align="center">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<style scoped>
.archives-page {
  padding: 20px;
}

.archives-page h1 {
  margin: 0 0 10px;
  font-size: 24px;
  color: #303133;
}

.folder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.folder-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  border: 1px solid #ebeef5;
}

.folder-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.folder-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.folder-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.folder-stats {
  font-size: 14px;
  color: #909399;
}
</style>
