<template>
  <div class="project-manager">
    <!-- 项目列表 -->
    <div class="project-grid">
      <el-card
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        shadow="hover"
      >
        <div class="project-header">
          <div class="project-title-row">
            <h3>{{ project.name }}</h3>
            <el-tag :type="getStatusType(project.status)" size="small">
              {{ getStatusLabel(project.status) }}
            </el-tag>
          </div>
          <p v-if="project.description" class="project-desc">{{ project.description }}</p>
        </div>

        <div class="project-progress">
          <div class="progress-info">
            <span>进度</span>
            <span>{{ project.completed_count }}/{{ project.task_count }}</span>
          </div>
          <el-progress
            :percentage="project.task_count > 0 ? Math.round(project.completed_count / project.task_count * 100) : 0"
            :stroke-width="8"
          />
        </div>

        <div class="project-meta">
          <span v-if="project.start_date" class="meta-item">
            <el-icon><Calendar /></el-icon>
            {{ project.start_date }} ~ {{ project.end_date || '无截止' }}
          </span>
        </div>

        <div class="project-actions">
          <el-button type="primary" size="small" text @click="openEdit(project)">编辑</el-button>
          <el-button type="danger" size="small" text @click="handleDelete(project.id)">删除</el-button>
        </div>
      </el-card>

      <!-- 添加项目卡片 -->
      <el-card class="project-card add-card" shadow="hover" @click="openCreate">
        <div class="add-card-content">
          <el-icon :size="32"><Plus /></el-icon>
          <span>新建项目</span>
        </div>
      </el-card>

      <el-empty v-if="!loading && projects.length === 0" description="暂无项目" />
    </div>

    <!-- 创建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑项目' : '新建项目'"
      width="500px"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="项目描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%;">
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="起止日期">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { projectApi, type Project } from '../api/project'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Calendar, Plus } from '@element-plus/icons-vue'

const projects = ref<Project[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const submitting = ref(false)

const form = ref({
  name: '',
  description: '',
  status: 'active',
  dateRange: null as [string, string] | null
})

onMounted(() => {
  loadProjects()
})

async function loadProjects() {
  loading.value = true
  try {
    const res = await projectApi.list()
    projects.value = res.items || res as any
  } catch (e: any) {
    ElMessage.error('加载项目失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = { name: '', description: '', status: 'active', dateRange: null }
  dialogVisible.value = true
}

function openEdit(project: Project) {
  isEdit.value = true
  editId.value = project.id
  form.value = {
    name: project.name,
    description: project.description || '',
    status: project.status,
    dateRange: project.start_date && project.end_date
      ? [project.start_date, project.end_date]
      : null
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name) return ElMessage.warning('请输入项目名称')
  submitting.value = true
  try {
    const data: any = {
      name: form.value.name,
      description: form.value.description,
      status: form.value.status
    }
    if (form.value.dateRange) {
      data.start_date = form.value.dateRange[0]
      data.end_date = form.value.dateRange[1]
    }
    if (isEdit.value && editId.value) {
      await projectApi.update(editId.value, data)
      ElMessage.success('更新成功')
    } else {
      await projectApi.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadProjects()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除此项目吗？', '确认删除', { type: 'warning' })
    await projectApi.delete(id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
    }
  }
}

function getStatusType(status: string) {
  const map: Record<string, string> = { active: '', completed: 'success', archived: 'info' }
  return map[status] || ''
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = { active: '进行中', completed: '已完成', archived: '已归档' }
  return map[status] || status
}

defineExpose({ loadProjects })
</script>

<style scoped>
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.project-card {
  transition: transform 0.2s;
}

.project-card:hover {
  transform: translateY(-2px);
}

.project-header {
  margin-bottom: 12px;
}

.project-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.project-title-row h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.project-desc {
  margin: 0;
  font-size: 13px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-progress {
  margin: 12px 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.project-meta {
  margin: 8px 0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.project-actions {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.add-card {
  cursor: pointer;
  border: 2px dashed #dcdfe6;
  background: #fafafa;
}

.add-card:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.add-card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 160px;
  gap: 8px;
  color: #909399;
}

.add-card:hover .add-card-content {
  color: #409eff;
}
</style>
