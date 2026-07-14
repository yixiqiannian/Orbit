<template>
  <div class="dashboard" v-loading="loading">
    <h2>📊 仪表盘</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>📋 任务</template>
          <div class="stat-value">{{ stats.tasks?.total || 0 }}</div>
          <div class="stat-label">
            待办 {{ stats.tasks?.pending || 0 }} |
            进行中 {{ stats.tasks?.in_progress || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>⏰ 定时任务</template>
          <div class="stat-value">{{ stats.cron?.total_jobs || 0 }}</div>
          <div class="stat-label">
            成功率 {{ stats.cron?.success_rate || 0 }}%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>📚 阅读</template>
          <div class="stat-value">{{ stats.reading?.total_books || 0 }}</div>
          <div class="stat-label">
            在读 {{ stats.reading?.reading || 0 }} |
            已读 {{ stats.reading?.finished || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>🧭 导航</template>
          <div class="stat-value">{{ navStats.total_sites || 0 }}</div>
          <div class="stat-label">
            {{ navStats.total_categories || 0 }} 个分类
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 每日一记 + 知识统计 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="daily-card">
          <template #header>
            <div class="card-header-with-action">
              <span>🧠 每日一记</span>
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
            <div class="daily-card-preview">{{ randomCard.content?.slice(0, 200) }}{{ randomCard.content?.length > 200 ? '...' : '' }}</div>
          </div>
          <el-empty v-else description="暂无知识卡片" :image-size="80">
            <el-button type="primary" size="small" @click="goToKnowledge">去创建</el-button>
          </el-empty>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>📊 知识统计</template>
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

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 任务状态饼图 -->
      <el-col :span="8">
        <el-card>
          <template #header>任务状态分布</template>
          <div ref="taskChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <!-- 阅读进度环形图 -->
      <el-col :span="8">
        <el-card>
          <template #header>阅读进度</template>
          <div ref="readingChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <!-- 定时任务执行状态 -->
      <el-col :span="8">
        <el-card>
          <template #header>定时任务执行状态</template>
          <div ref="cronChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 阅读书籍进度 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
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
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
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
      <el-col :span="12">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardApi } from '../api/dashboard'
import { navApi, type NavStats } from '../api/nav'
import { knowledgeApi, type KnowledgeCard } from '../api/knowledge'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const loading = ref(false)
const taskChartRef = ref<HTMLElement>()
const readingChartRef = ref<HTMLElement>()
const cronChartRef = ref<HTMLElement>()

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

onMounted(async () => {
  loading.value = true
  try {
    const [dashboardData, navData, kStats, kCard] = await Promise.all([
      dashboardApi.getStats(),
      navApi.getStats().catch(() => ({ total_categories: 0, total_sites: 0 })),
      knowledgeApi.getStats().catch(() => null),
      knowledgeApi.randomCard().catch(() => null)
    ])
    Object.assign(stats, dashboardData)
    Object.assign(navStats, navData)
    knowledgeStats.value = kStats
    randomCard.value = kCard
    await nextTick()
    initCharts()
  } catch (e) {
    console.error('Failed to load dashboard stats:', e)
  } finally {
    loading.value = false
  }
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

function initCharts() {
  initTaskChart()
  initReadingChart()
  initCronChart()
}

function initTaskChart() {
  if (!taskChartRef.value) return
  const chart = echarts.init(taskChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%', left: 'center' },
    series: [{
      name: '任务状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 20, fontWeight: 'bold' }
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
  window.addEventListener('resize', () => chart.resize())
}

function initReadingChart() {
  if (!readingChartRef.value) return
  const chart = echarts.init(readingChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%', left: 'center' },
    series: [{
      name: '阅读状态',
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, position: 'outside', formatter: '{b}: {c}本' },
      data: [
        { value: stats.reading?.want_to_read || 0, name: '想读', itemStyle: { color: '#409EFF' } },
        { value: stats.reading?.reading || 0, name: '在读', itemStyle: { color: '#E6A23C' } },
        { value: stats.reading?.finished || 0, name: '已读', itemStyle: { color: '#67C23A' } }
      ]
    }]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

function initCronChart() {
  if (!cronChartRef.value) return
  const chart = echarts.init(cronChartRef.value)
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['成功', '失败', '运行中'] },
    yAxis: { type: 'value' },
    series: [{
      name: '执行次数',
      type: 'bar',
      barWidth: '60%',
      data: [
        { value: stats.cron?.success_count || 0, itemStyle: { color: '#67C23A' } },
        { value: stats.cron?.failed_count || 0, itemStyle: { color: '#F56C6C' } },
        { value: stats.cron?.running_count || 0, itemStyle: { color: '#409EFF' } }
      ]
    }]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
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
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.dashboard h2 {
  margin: 0 0 20px;
  color: #303133;
}
.stat-cards {
  margin-bottom: 20px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}
.stat-label {
  color: #909399;
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
  color: #303133;
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
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
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
  color: #303133;
}
.book-author {
  font-size: 12px;
  color: #909399;
}
.book-progress-item .el-progress {
  flex: 1;
}
</style>
