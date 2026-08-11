<template>
  <div class="daily-logs" v-loading="loading">
    <div class="page-header">
      <h2>每日日志</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          :shortcuts="dateShortcuts"
          @change="loadLogs"
          style="margin-right: 12px;"
        />
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon> 新增日志
        </el-button>
      </div>
    </div>

    <!-- 日志列表 -->
    <div v-if="logs.length" class="logs-list">
      <div
        v-for="log in logs"
        :key="log.id"
        class="log-card"
      >
        <div class="log-header">
          <div class="log-date-mood">
            <span class="log-date">{{ formatDate(log.date) }}</span>
            <span class="log-mood">{{ getMoodEmoji(log.mood) }}</span>
          </div>
          <div class="log-actions">
            <el-button text size="small" @click="openDialog(log)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button text size="small" type="danger" @click="handleDelete(log.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="log-title">{{ log.title }}</div>
        <div class="log-content markdown-body" v-html="renderMarkdown(log.content)"></div>
        <div v-if="log.tags" class="log-tags">
          <el-tag
            v-for="tag in log.tags.split(',')"
            :key="tag"
            size="small"
            type="info"
            effect="plain"
          >{{ tag.trim() }}</el-tag>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无日志" :image-size="120">
      <el-button type="primary" @click="openDialog()">写第一篇日志</el-button>
    </el-empty>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑日志' : '新增日志'"
      width="640px"
      destroy-on-close
    >
      <el-form :model="form" label-width="70px">
        <el-form-item label="日期">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="日志标题" />
        </el-form-item>
        <el-form-item label="心情">
          <el-radio-group v-model="form.mood">
            <el-radio-button v-for="m in moods" :key="m.value" :value="m.value">
              {{ m.emoji }} {{ m.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="支持 Markdown 格式..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { dailyLogApi, type DailyLog } from '../api/dailyLog'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

function renderMarkdown(text: string) {
  if (!text) return ''
  return md.render(text)
}

const moods = [
  { value: 'good', emoji: '😊', label: '好' },
  { value: 'normal', emoji: '😐', label: '一般' },
  { value: 'bad', emoji: '😢', label: '差' }
]

const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 3600 * 1000)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 3600 * 1000)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 90 * 24 * 3600 * 1000)
      return [start, end]
    }
  }
]

const loading = ref(false)
const saving = ref(false)
const logs = ref<DailyLog[]>([])
const dateRange = ref<[string, string] | null>(null)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  date: new Date().toISOString().slice(0, 10),
  title: '',
  content: '',
  mood: 'good',
  tags: ''
})

function getMoodEmoji(mood: string) {
  const m = moods.find(m => m.value === mood)
  return m ? m.emoji : '😐'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short' })
}

async function loadLogs() {
  loading.value = true
  try {
    const params: any = {}
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    logs.value = await dailyLogApi.list(params)
  } catch (e) {
    console.error('Failed to load daily logs:', e)
    logs.value = []
  } finally {
    loading.value = false
  }
}

function openDialog(log?: DailyLog) {
  if (log) {
    isEdit.value = true
    editingId.value = log.id
    form.date = log.date
    form.title = log.title
    form.content = log.content
    form.mood = log.mood || 'good'
    form.tags = log.tags || ''
  } else {
    isEdit.value = false
    editingId.value = null
    form.date = new Date().toISOString().slice(0, 10)
    form.title = ''
    form.content = ''
    form.mood = 'good'
    form.tags = ''
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入日志标题')
    return
  }
  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      await dailyLogApi.update(editingId.value, { ...form })
      ElMessage.success('日志已更新')
    } else {
      await dailyLogApi.create({ ...form })
      ElMessage.success('日志已创建')
    }
    dialogVisible.value = false
    await loadLogs()
  } catch (e) {
    ElMessage.error('操作失败')
    console.error(e)
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除这篇日志吗？', '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await dailyLogApi.delete(id)
    ElMessage.success('已删除')
    await loadLogs()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(e)
    }
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.daily-logs {
  padding: 20px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--el-text-color-primary);
}
.header-actions {
  display: flex;
  align-items: center;
}
.logs-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.log-card {
  background: var(--surface);
  backdrop-filter: var(--glass-filter);
  -webkit-backdrop-filter: var(--glass-filter);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius);
  box-shadow: var(--shadow-glass);
  padding: 16px 20px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}
.log-card:hover {
  transform: translateY(-2px);
  background: var(--glass-bg-strong);
  box-shadow: var(--shadow-glow);
}
.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.log-date-mood {
  display: flex;
  align-items: center;
  gap: 8px;
}
.log-date {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.log-mood {
  font-size: 18px;
}
.log-actions {
  display: flex;
  gap: 4px;
}
.log-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}
.log-content {
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.7;
  max-height: 300px;
  overflow: hidden;
  position: relative;
}
.log-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 12px;
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin: 12px 0 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.markdown-body p {
  margin: 6px 0;
}
.markdown-body code {
  background: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: var(--el-color-warning);
}
.markdown-body pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}
.markdown-body pre code {
  background: none;
  color: inherit;
  padding: 0;
}
.markdown-body ul, .markdown-body ol {
  padding-left: 20px;
  margin: 6px 0;
}
.markdown-body li {
  margin: 3px 0;
}
.markdown-body blockquote {
  border-left: 4px solid var(--el-color-primary);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--el-text-color-secondary);
}
.markdown-body a {
  color: var(--el-color-primary);
  text-decoration: none;
}
</style>
