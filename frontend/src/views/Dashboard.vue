<template>
  <div class="dashboard" v-loading="loading">
    <h2>仪表盘</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="4" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><Tickets /></el-icon>
              <span>任务</span>
            </div>
          </template>
          <div class="stat-value">{{ stats.tasks?.total || 0 }}</div>
          <div class="stat-label">
            待办 {{ stats.tasks?.pending || 0 }} |
            进行中 {{ stats.tasks?.in_progress || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="4" class="fade-in-up" style="animation-delay: 50ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><Clock /></el-icon>
              <span>定时任务</span>
            </div>
          </template>
          <div class="stat-value">{{ stats.cron?.total_jobs || 0 }}</div>
          <div class="stat-label">
            成功率 {{ stats.cron?.success_rate || 0 }}%
          </div>
        </el-card>
      </el-col>
      <el-col :span="4" class="fade-in-up" style="animation-delay: 100ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><Reading /></el-icon>
              <span>阅读</span>
            </div>
          </template>
          <div class="stat-value">{{ stats.reading?.total_books || 0 }}</div>
          <div class="stat-label">
            在读 {{ stats.reading?.reading || 0 }} |
            已读 {{ stats.reading?.finished || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="4" class="fade-in-up" style="animation-delay: 150ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><Compass /></el-icon>
              <span>导航</span>
            </div>
          </template>
          <div class="stat-value">{{ navStats.total_sites || 0 }}</div>
          <div class="stat-label">
            {{ navStats.total_categories || 0 }} 个分类
          </div>
        </el-card>
      </el-col>
      <el-col :span="4" class="fade-in-up" style="animation-delay: 200ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><Box /></el-icon>
              <span>上月归档</span>
            </div>
          </template>
          <div class="stat-value">{{ stats.archive?.last_month_archived || 0 }}</div>
          <div class="stat-label">
            总归档 {{ stats.archive?.total_archived || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="4" class="fade-in-up" style="animation-delay: 250ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><CircleCheckFilled /></el-icon>
              <span>本月已完成</span>
            </div>
          </template>
          <div class="stat-value">{{ stats.archive?.this_month_completed || 0 }}</div>
          <div class="stat-label">
            待归档
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 即将过期 + 项目进度 -->
    <el-row :gutter="20">
      <el-col :span="12" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><AlarmClock /></el-icon>
              <span>即将过期任务</span>
            </div>
          </template>
          <div v-if="upcomingTasks.length" class="upcoming-tasks-list">
            <div
              v-for="task in upcomingTasks"
              :key="task.id"
              class="upcoming-task-item"
              :class="{ 'is-overdue': isOverdue(task.due_date) }"
            >
              <div class="upcoming-task-info">
                <span class="upcoming-task-title">{{ task.title }}</span>
                <el-tag v-if="isOverdue(task.due_date)" type="danger" size="small" effect="dark">已过期</el-tag>
                <el-tag v-else type="warning" size="small" effect="dark">即将过期</el-tag>
              </div>
              <div class="upcoming-task-due">
                <el-icon><Calendar /></el-icon>
                {{ task.due_date }}
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无即将过期任务" :image-size="60" />
        </el-card>
      </el-col>
      <el-col :span="12" class="fade-in-up" style="animation-delay: 60ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><Folder /></el-icon>
              <span>项目进度</span>
            </div>
          </template>
          <div v-if="projectList.length" class="project-progress-list">
            <div v-for="p in projectList" :key="p.id" class="project-progress-item">
              <div class="project-progress-header">
                <span class="project-progress-name">{{ p.name }}</span>
                <span class="project-progress-count">{{ p.completed_count }}/{{ p.task_count }}</span>
              </div>
              <el-progress
                :percentage="p.task_count > 0 ? Math.round(p.completed_count / p.task_count * 100) : 0"
                :stroke-width="12"
                :status="p.task_count > 0 && p.completed_count >= p.task_count ? 'success' : ''"
              />
            </div>
          </div>
          <el-empty v-else description="暂无活跃项目" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 每日一记 + 知识统计 -->
    <el-row :gutter="20">
      <el-col :span="16" class="fade-in-up" style="animation-delay: 0ms">
        <el-card class="daily-card">
          <template #header>
            <div class="card-header-with-action">
              <div class="card-header">
                <el-icon class="card-header-icon"><Memo /></el-icon>
                <span>每日一记</span>
              </div>
              <el-button text size="small" @click="loadRandomCard">
                <el-icon><Refresh /></el-icon>换一张
              </el-button>
            </div>
          </template>
          <div v-if="randomCard" class="daily-card-content" @click="goToKnowledge">
            <div class="daily-card-title">{{ randomCard.title }}</div>
            <div class="daily-card-meta">
              <el-tag v-if="randomCard.category_name" size="small" type="info">{{ randomCard.category_name }}</el-tag>
              <span v-if="randomCard.tags" class="daily-tags">
                <el-tag v-for="tag in randomCard.tags.split(',')" :key="tag" size="small" type="warning" effect="plain">
                  {{ tag.trim() }}
                </el-tag>
              </span>
            </div>
            <div class="daily-card-preview markdown-body" v-html="renderMarkdown(randomCard.content?.slice(0, 500))"></div>
          </div>
          <el-empty v-else description="暂无知识卡片" :image-size="80">
            <el-button type="primary" size="small" @click="goToKnowledge">去创建</el-button>
          </el-empty>
        </el-card>
      </el-col>
      <el-col :span="8" class="fade-in-up" style="animation-delay: 60ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><DataAnalysis /></el-icon>
              <span>知识统计</span>
            </div>
          </template>
          <div v-if="knowledgeStats" class="knowledge-stats">
            <div class="stat-item">
              <div class="stat-value">{{ knowledgeStats.total_cards || 0 }}</div>
              <div class="stat-label">卡片总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ knowledgeStats.total_categories || 0 }}</div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 热力图 -->
    <el-row :gutter="20">
      <el-col :span="24" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon class="card-header-icon"><Calendar /></el-icon>
              <span>任务完成热力图</span>
            </div>
          </template>
          <TaskHeatmap
            :data="heatmapData?.data"
            :start-date="heatmapData?.start_date"
            :end-date="heatmapData?.end_date"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <!-- 任务状态饼图 -->
      <el-col :span="8" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>任务状态分布</template>
          <div ref="taskChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <!-- 阅读进度环形图 -->
      <el-col :span="8" class="fade-in-up" style="animation-delay: 60ms">
        <el-card>
          <template #header>阅读进度</template>
          <div ref="readingChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <!-- 定时任务执行状态 -->
      <el-col :span="8" class="fade-in-up" style="animation-delay: 120ms">
        <el-card>
          <template #header>定时任务执行状态</template>
          <div ref="cronChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 阅读书籍进度 -->
    <el-row :gutter="20">
      <el-col :span="24" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>在读书籍进度</template>
          <div class="book-progress-list">
            <div v-for="book in stats.reading_books" :key="book.id" class="book-progress-item">
              <div class="book-info">
                <span class="book-title">{{ book.title }}</span>
                <span class="book-author">{{ book.author }}</span>
              </div>
              <el-progress
                :percentage="book.progress || 0"
                :stroke-width="20"
                :text-inside="true"
                :status="book.progress >= 100 ? 'success' : ''"
              />
            </div>
            <el-empty v-if="!stats.reading_books?.length" description="暂无在读书籍" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近任务 + 最近执行记录 -->
    <el-row :gutter="20">
      <el-col :span="12" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>最近任务</template>
          <el-table :data="stats.recent_tasks" stripe>
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12" class="fade-in-up" style="animation-delay: 60ms">
        <el-card>
          <template #header>邮箱未读</template>
          <el-table :data="stats.email_unread" stripe>
            <el-table-column prop="subject" label="主题" />
            <el-table-column prop="sender" label="发件人" width="180" />
            <el-table-column prop="received_at" label="时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.received_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近学习日志 -->
    <el-row :gutter="20">
      <el-col :span="24" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>
            <div class="card-header-with-action">
              <div class="card-header">
                <el-icon class="card-header-icon"><EditPen /></el-icon>
                <span>最近学习日志</span>
              </div>
              <el-button text size="small" @click="router.push('/tasks')">查看全部</el-button>
            </div>
          </template>
          <div v-if="stats.recent_logs?.length" class="recent-logs-list">
            <div
              v-for="log in stats.recent_logs"
              :key="log.id"
              class="recent-log-item"
              @click="router.push('/tasks')"
            >
              <div class="recent-log-header">
                <el-tag :type="getLogTypeTag(log.log_type)" size="small">
                  {{ getLogTypeLabel(log.log_type) }}
                </el-tag>
                <span class="recent-log-task">{{ log.task_title }}</span>
                <span class="recent-log-time">{{ formatDate(log.created_at) }}</span>
              </div>
              <div class="recent-log-preview">{{ log.content?.slice(0, 100) }}{{ log.content?.length > 100 ? '...' : '' }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无日志" :image-size="60">
            <el-button type="primary" size="small" @click="router.push('/tasks')">去记录</el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近日志 -->
    <el-row :gutter="20">
      <el-col :span="24" class="fade-in-up" style="animation-delay: 0ms">
        <el-card>
          <template #header>
            <div class="card-header-with-action">
              <div class="card-header">
                <el-icon class="card-header-icon"><Notebook /></el-icon>
                <span>最近日志</span>
              </div>
              <el-button text size="small" @click="router.push('/daily-logs')">查看全部</el-button>
            </div>
          </template>
          <div v-if="recentDailyLogs.length" class="recent-daily-logs-list">
            <div
              v-for="log in recentDailyLogs"
              :key="log.id"
              class="recent-daily-log-item"
              @click="router.push('/daily-logs')"
            >
              <div class="recent-daily-log-header">
                <span class="recent-daily-log-date">{{ formatDailyDate(log.date) }}</span>
                <el-icon class="recent-daily-log-mood" :class="'mood-' + (log.mood || 'normal')">
                  <component :is="getDailyMoodIcon(log.mood)" />
                </el-icon>
                <span class="recent-daily-log-title">{{ log.title }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无日志" :image-size="60">
            <el-button type="primary" size="small" @click="router.push('/daily-logs')">去写日志</el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '../stores/theme'
import { dashboardApi, type HeatmapData } from '../api/dashboard'
import { navApi, type NavStats } from '../api/nav'
import { knowledgeApi, type KnowledgeCard } from '../api/knowledge'
import { dailyLogApi, type DailyLog } from '../api/dailyLog'
import { projectApi, type Project } from '../api/project'
import {
  Refresh,
  Calendar,
  Tickets,
  Clock,
  Reading,
  Compass,
  Box,
  CircleCheckFilled,
  AlarmClock,
  Folder,
  Memo,
  DataAnalysis,
  EditPen,
  Notebook,
  Sunny,
  PartlyCloudy,
  Cloudy
} from '@element-plus/icons-vue'
import TaskHeatmap from '../components/TaskHeatmap.vue'
import * as echarts from 'echarts'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
function renderMarkdown(text: string) {
  if (!text) return ''
  return md.render(text)
}

const router = useRouter()
const themeStore = useThemeStore()
const loading = ref(false)
const taskChartRef = ref<HTMLElement>()
const readingChartRef = ref<HTMLElement>()
const cronChartRef = ref<HTMLElement>()

const chartInstances: echarts.ECharts[] = []

const stats = reactive<any>({
  tasks: {},
  cron: {},
  reading: {},
  email: {},
  recent_tasks: [],
  recent_executions: [],
  reading_books: [],
  email_unread: []
})

const navStats = reactive<NavStats>({
  total_categories: 0,
  total_sites: 0
})

const randomCard = ref<KnowledgeCard | null>(null)
const knowledgeStats = ref<{ total_categories: number; total_cards: number } | null>(null)
const heatmapData = ref<HeatmapData | null>(null)
const upcomingTasks = ref<any[]>([])
const projectList = ref<Project[]>([])
const recentDailyLogs = ref<DailyLog[]>([])

function isOverdue(dueDate?: string): boolean {
  if (!dueDate) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const due = new Date(dueDate)
  due.setHours(0, 0, 0, 0)
  return due.getTime() < today.getTime()
}

onMounted(async () => {
  loading.value = true
  try {
    const [dashboardData, navData, kStats, kCard, heatmap, upcoming, projs, dailyLogs] = await Promise.all([
      dashboardApi.getStats(),
      navApi.getStats().catch(() => ({ total_categories: 0, total_sites: 0 })),
      knowledgeApi.getStats().catch(() => null),
      knowledgeApi.randomCard().catch(() => null),
      dashboardApi.getHeatmap(365).catch(() => null),
      dashboardApi.getUpcomingTasks().catch(() => []),
      projectApi.list({ status: 'active' }).catch(() => ({ items: [] })),
      dailyLogApi.recent(5).catch(() => [])
    ])
    Object.assign(stats, dashboardData)
    Object.assign(navStats, navData)
    knowledgeStats.value = kStats
    randomCard.value = kCard
    heatmapData.value = heatmap
    upcomingTasks.value = upcoming || []
    projectList.value = (projs as any)?.items || projs || []
    recentDailyLogs.value = dailyLogs || []
    await nextTick()
    initCharts()
  } catch (e) {
    console.error('Failed to load dashboard stats:', e)
  } finally {
    loading.value = false
  }
})

// 主题切换时重绘图表（深浅色适配）
watch(
  () => themeStore.theme,
  () => nextTick(initCharts)
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

async function loadRandomCard() {
  try {
    randomCard.value = await knowledgeApi.randomCard()
  } catch (e) {
    console.error('Failed to load random card:', e)
  }
}

function goToKnowledge() {
  router.push('/knowledge')
}

function disposeCharts() {
  chartInstances.forEach((c) => c.dispose())
  chartInstances.length = 0
}

function handleResize() {
  chartInstances.forEach((c) => c.resize())
}

function initCharts() {
  disposeCharts()
  initTaskChart()
  initReadingChart()
  initCronChart()
}

/** ECharts 深浅色适配调色板（跟随 data-theme） */
function chartPalette() {
  const dark = document.documentElement.dataset.theme === 'dark'
  return {
    dark,
    text: dark ? '#f1f5f9' : '#0f172a',
    subText: dark ? '#94a3b8' : '#64748b',
    axisLine: dark ? 'rgba(241,245,249,0.22)' : 'rgba(15,23,42,0.2)',
    splitLine: dark ? 'rgba(241,245,249,0.08)' : 'rgba(15,23,42,0.06)',
    borderColor: dark ? '#111827' : '#ffffff',
    tooltipBg: dark ? 'rgba(30,41,59,0.92)' : 'rgba(255,255,255,0.95)',
    tooltipBorder: dark ? 'rgba(255,255,255,0.1)' : 'rgba(15,23,42,0.08)',
    tooltipText: dark ? '#f1f5f9' : '#0f172a'
  }
}

function initTaskChart() {
  if (!taskChartRef.value) return
  const c = chartPalette()
  const chart = echarts.init(taskChartRef.value)
  chartInstances.push(chart)
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: c.tooltipBg,
      borderColor: c.tooltipBorder,
      textStyle: { color: c.tooltipText }
    },
    legend: { bottom: '5%', left: 'center', textStyle: { color: c.text } },
    series: [{
      name: '任务状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: c.borderColor, borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 20, fontWeight: 'bold', color: c.text }
      },
      labelLine: { show: false },
      data: [
        { value: stats.tasks?.pending || 0, name: '待办', itemStyle: { color: '#909399' } },
        { value: stats.tasks?.in_progress || 0, name: '进行中', itemStyle: { color: '#E6A23C' } },
        { value: stats.tasks?.completed || 0, name: '已完成', itemStyle: { color: '#67C23A' } },
        { value: stats.tasks?.overdue || 0, name: '逾期', itemStyle: { color: '#F56C6C' } }
      ]
    }]
  }
  chart.setOption(option)
}

function initReadingChart() {
  if (!readingChartRef.value) return
  const c = chartPalette()
  const chart = echarts.init(readingChartRef.value)
  chartInstances.push(chart)
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: c.tooltipBg,
      borderColor: c.tooltipBorder,
      textStyle: { color: c.tooltipText }
    },
    legend: { bottom: '5%', left: 'center', textStyle: { color: c.text } },
    series: [{
      name: '阅读状态',
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: c.borderColor, borderWidth: 2 },
      label: { show: true, position: 'outside', formatter: '{b}: {c}本', color: c.text },
      data: [
        { value: stats.reading?.want_to_read || 0, name: '想读', itemStyle: { color: '#409EFF' } },
        { value: stats.reading?.reading || 0, name: '在读', itemStyle: { color: '#E6A23C' } },
        { value: stats.reading?.finished || 0, name: '已读', itemStyle: { color: '#67C23A' } }
      ]
    }]
  }
  chart.setOption(option)
}

function initCronChart() {
  if (!cronChartRef.value) return
  const c = chartPalette()
  const chart = echarts.init(cronChartRef.value)
  chartInstances.push(chart)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: c.tooltipBg,
      borderColor: c.tooltipBorder,
      textStyle: { color: c.tooltipText }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['成功', '失败', '运行中'],
      axisLabel: { color: c.text },
      axisLine: { lineStyle: { color: c.axisLine } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: c.subText },
      splitLine: { lineStyle: { color: c.splitLine } }
    },
    series: [{
      name: '执行次数',
      type: 'bar',
      barWidth: '60%',
      itemStyle: { borderRadius: [8, 8, 0, 0] },
      data: [
        { value: stats.cron?.success_count || 0, itemStyle: { color: '#67C23A' } },
        { value: stats.cron?.failed_count || 0, itemStyle: { color: '#F56C6C' } },
        { value: stats.cron?.running_count || 0, itemStyle: { color: '#409EFF' } }
      ]
    }]
  }
  chart.setOption(option)
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

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getLogTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
    note: 'info',
    problem: 'danger',
    knowledge: 'success',
    progress: 'warning'
  }
  return map[type] || 'info'
}

function getLogTypeLabel(type: string) {
  const map: Record<string, string> = {
    note: '笔记',
    problem: '问题',
    knowledge: '知识点',
    progress: '进度'
  }
  return map[type] || type
}

function formatDailyDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', weekday: 'short' })
}

function getDailyMoodIcon(mood: string) {
  const map: Record<string, any> = { good: Sunny, normal: PartlyCloudy, bad: Cloudy }
  return map[mood] || PartlyCloudy
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.dashboard h2 {
  margin: 0 0 20px;
  color: var(--color-foreground);
  font-family: var(--font-heading);
  font-weight: 600;
}

/* ================= 玻璃卡片统一范式（MASTER.md .glass-card） ================= */
.dashboard .el-row + .el-row {
  margin-top: 20px;
}
.dashboard .el-card {
  --el-card-bg-color: var(--surface);
  --el-card-border-color: var(--glass-border);
  background: var(--surface);
  backdrop-filter: var(--glass-filter);
  -webkit-backdrop-filter: var(--glass-filter);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius);
  box-shadow: var(--glass-shadow);
  transition: transform 0.25s ease, box-shadow 0.25s ease, background-color 0.25s ease,
    border-color 0.25s ease;
}
/* hover：蓝色光晕 + 上浮 2px（MASTER.md 动画范式） */
.dashboard .el-card:hover {
  transform: translateY(-2px);
  background: var(--glass-bg-strong);
  box-shadow: var(--shadow-glow);
  border-color: rgba(37, 99, 235, 0.45);
}
.dashboard .el-card :deep(.el-card__header) {
  border-bottom: 1px solid var(--glass-border);
  padding: 16px 20px;
}
.dashboard .el-card :deep(.el-card__body) {
  padding: 20px;
}

/* 表格在玻璃卡片上透明化 */
.dashboard .el-card :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
  --el-table-border-color: var(--glass-border);
  --el-table-row-hover-bg-color: var(--glass-hover);
  --el-table-striped-row-bg-color: var(--glass-hover);
}

/* ================= 卡片 stagger 入场（fadeInUp 0.4s，逐个延迟） ================= */
.fade-in-up {
  animation: fadeInUp 0.4s ease both;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: none; }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-header-icon {
  font-size: 16px;
  color: var(--color-primary);
}
/* 统计数值：Fredoka 大号数字 + 双蓝渐变文字 */
.stat-value {
  font-family: var(--font-display);
  font-size: 40px;
  font-weight: 600;
  line-height: 1.2;
  background: var(--gradient-brand-blue);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
.stat-label {
  color: var(--color-text-muted);
  font-size: 14px;
  margin-top: 8px;
}
.card-header-with-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.daily-card-content {
  cursor: pointer;
  padding: 4px 0;
}
.daily-card-content:hover {
  opacity: 0.85;
}
.daily-card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: 10px;
}
.daily-card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.daily-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.daily-card-preview {
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin: 12px 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-foreground);
}
.markdown-body h1 { font-size: 18px; }
.markdown-body h2 { font-size: 16px; }
.markdown-body p {
  margin: 8px 0;
}
.markdown-body code {
  background: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #e6a23c;
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
  margin: 8px 0;
}
.markdown-body li {
  margin: 4px 0;
}
.markdown-body blockquote {
  border-left: 4px solid var(--color-primary);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--color-text-muted);
}
.markdown-body strong {
  color: var(--color-foreground);
}
.markdown-body a {
  color: var(--color-primary);
  text-decoration: none;
}
.knowledge-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}
.knowledge-stats .stat-item {
  text-align: center;
}
.book-progress-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.book-progress-item {
  display: flex;
  align-items: center;
  gap: 20px;
}
.book-info {
  min-width: 200px;
  display: flex;
  flex-direction: column;
}
.book-title {
  font-weight: 500;
  color: var(--color-foreground);
}
.book-author {
  font-size: 12px;
  color: var(--color-text-muted);
}
.book-progress-item .el-progress {
  flex: 1;
}
.recent-logs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.recent-log-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius-sm);
  cursor: pointer;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
}
.recent-log-item:hover {
  background: var(--glass-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow);
}
.recent-log-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.recent-log-task {
  font-weight: 500;
  color: var(--color-foreground);
  font-size: 14px;
}
.recent-log-time {
  margin-left: auto;
  font-size: 12px;
  color: var(--color-text-muted);
}
.recent-log-preview {
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.upcoming-tasks-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}
.upcoming-task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius-sm);
  border-left: 3px solid #e6a23c;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
}
.upcoming-task-item:hover {
  background: var(--glass-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow);
}
.upcoming-task-item.is-overdue {
  background: rgba(251, 44, 54, 0.08);
  border-left-color: var(--color-destructive);
}
.upcoming-task-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.upcoming-task-title {
  font-size: 14px;
  color: var(--color-foreground);
  font-weight: 500;
}
.upcoming-task-due {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-muted);
}
.project-progress-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 300px;
  overflow-y: auto;
}
.project-progress-item {
  padding: 0 4px;
}
.project-progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.project-progress-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-foreground);
}
.project-progress-count {
  font-size: 13px;
  color: var(--color-text-muted);
}
.recent-daily-logs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.recent-daily-log-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius-sm);
  cursor: pointer;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
}
.recent-daily-log-item:hover {
  background: var(--glass-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow);
}
.recent-daily-log-header {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.recent-daily-log-date {
  font-size: 13px;
  color: var(--color-text-muted);
  min-width: 80px;
}
.recent-daily-log-mood {
  font-size: 16px;
}
.recent-daily-log-mood.mood-good {
  color: #67c23a;
}
.recent-daily-log-mood.mood-normal {
  color: var(--color-text-muted);
}
.recent-daily-log-mood.mood-bad {
  color: #f56c6c;
}
.recent-daily-log-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-foreground);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

<!-- 深色模式微调：scoped :global() 复合选择器编译异常，改走非 scoped 块 -->
<style>
html[data-theme='dark'] .stat-value {
  background: linear-gradient(90deg, #60a5fa, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
html[data-theme='dark'] .recent-log-item,
html[data-theme='dark'] .upcoming-task-item,
html[data-theme='dark'] .recent-daily-log-item {
  background: rgba(30, 41, 59, 0.6);
}
</style>
