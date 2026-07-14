<template>
  <div class="task-log-timeline">
    <!-- 添加日志按钮 -->
    <div class="timeline-header">
      <el-button type="primary" size="small" @click="openAddDialog">
        <el-icon><Plus /></el-icon>新增日志
      </el-button>
    </div>

    <!-- 时间线 -->
    <el-timeline v-if="logs.length > 0">
      <el-timeline-item
        v-for="log in logs"
        :key="log.id"
        :timestamp="formatDate(log.created_at)"
        placement="top"
        :color="getTypeColor(log.log_type)"
      >
        <el-card shadow="never" class="log-card">
          <div class="log-header">
            <el-tag :type="getTypeTag(log.log_type)" size="small">
              {{ getTypeLabel(log.log_type) }}
            </el-tag>
            <div class="log-actions">
              <el-button text size="small" @click="openEditDialog(log)">编辑</el-button>
              <el-button text size="small" type="danger" @click="handleDelete(log.id)">删除</el-button>
            </div>
          </div>
          <div class="log-content markdown-body" v-html="renderMarkdown(log.content)"></div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-else description="暂无日志" :image-size="80" />

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑日志' : '新增日志'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="formData" label-width="80px">
        <el-form-item label="类型">
          <el-select v-model="formData.log_type" style="width: 100%;">
            <el-option label="笔记" value="note" />
            <el-option label="问题" value="problem" />
            <el-option label="知识点" value="knowledge" />
            <el-option label="进度" value="progress" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="8"
            placeholder="支持 Markdown 格式"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { taskLogApi, type TaskLog } from '../api/taskLog'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  taskId: number
}>()

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

const logs = ref<TaskLog[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)

const formData = ref({
  log_type: 'note',
  content: ''
})

function renderMarkdown(text: string) {
  if (!text) return ''
  return md.render(text)
}

async function loadLogs() {
  loading.value = true
  try {
    logs.value = await taskLogApi.list({ task_id: props.taskId })
  } catch (e: any) {
    ElMessage.error('加载日志失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

function openAddDialog() {
  isEdit.value = false
  editingId.value = null
  formData.value = { log_type: 'note', content: '' }
  dialogVisible.value = true
}

function openEditDialog(log: TaskLog) {
  isEdit.value = true
  editingId.value = log.id
  formData.value = { log_type: log.log_type, content: log.content }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formData.value.content.trim()) {
    return ElMessage.warning('请输入日志内容')
  }
  submitting.value = true
  try {
    if (isEdit.value && editingId.value) {
      await taskLogApi.update(editingId.value, formData.value)
      ElMessage.success('更新成功')
    } else {
      await taskLogApi.create({ ...formData.value, task_id: props.taskId })
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadLogs()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除这条日志吗？', '确认删除', { type: 'warning' })
    await taskLogApi.delete(id)
    ElMessage.success('删除成功')
    loadLogs()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
    }
  }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getTypeColor(type: string) {
  const map: Record<string, string> = {
    note: '#409EFF',
    problem: '#F56C6C',
    knowledge: '#67C23A',
    progress: '#E6A23C'
  }
  return map[type] || '#909399'
}

function getTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
    note: 'info',
    problem: 'danger',
    knowledge: 'success',
    progress: 'warning'
  }
  return map[type] || 'info'
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = {
    note: '笔记',
    problem: '问题',
    knowledge: '知识点',
    progress: '进度'
  }
  return map[type] || type
}

watch(() => props.taskId, (id) => {
  if (id) loadLogs()
}, { immediate: true })
</script>

<style scoped>
.timeline-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.log-card {
  margin-bottom: 0;
}

.log-card :deep(.el-card__body) {
  padding: 12px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-actions {
  display: flex;
  gap: 4px;
}

.log-content {
  font-size: 14px;
  line-height: 1.7;
  color: #303133;
}

.log-content :deep(h1),
.log-content :deep(h2),
.log-content :deep(h3) {
  margin-top: 12px;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 15px;
}

.log-content :deep(p) {
  margin-bottom: 8px;
}

.log-content :deep(code) {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #e6a23c;
}

.log-content :deep(pre) {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.log-content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
}

.log-content :deep(ul),
.log-content :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}

.log-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 12px;
  margin: 8px 0;
  color: #909399;
}
</style>
