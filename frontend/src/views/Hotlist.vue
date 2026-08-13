<template>
  <div class="hotlist-page">
    <!-- 页头：标题 + 数据源标签 + 日期选择 + 抓取 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">热榜</h2>
        <div class="source-tags">
          <a
            v-for="s in sources"
            :key="s.key"
            :class="['source-tag', { active: s.key === activeSource }]"
            :href="s.url"
            target="_blank"
            rel="noopener noreferrer"
            @click.prevent="switchSource(s.key)"
          >
            {{ s.name }}
          </a>
        </div>
      </div>
      <div class="header-actions">
        <el-date-picker
          v-model="hotDate"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          :clearable="false"
          :disabled-date="disableFuture"
          style="margin-right: 12px"
          @change="loadList"
        />
        <el-button type="primary" :loading="fetching" @click="handleFetch">
          <el-icon style="margin-right: 4px"><Refresh /></el-icon>
          立即抓取
        </el-button>
      </div>
    </div>

    <!-- 热榜列表 -->
    <div v-loading="loading" class="hotlist-body">
      <transition-group v-if="items.length" name="fade-up" tag="div" class="hotlist-list">
        <div
          v-for="item in items"
          :key="item.id"
          class="hotlist-card glass-card-hover"
        >
          <div class="card-rank" :class="rankClass(item.rank)">
            {{ item.rank }}
          </div>

          <div class="card-main">
            <div class="card-title-row">
              <a
                class="repo-link"
                :href="item.url"
                target="_blank"
                rel="noopener noreferrer"
                :title="item.title"
              >
                {{ item.title }}
              </a>
              <el-tag
                v-if="item.language"
                size="small"
                effect="plain"
                class="lang-tag"
              >
                {{ item.language }}
              </el-tag>
            </div>

            <p v-if="item.description" class="repo-desc">{{ item.description }}</p>

            <div class="repo-stats">
              <span class="stat">
                <el-icon class="stat-icon today"><Star /></el-icon>
                <span class="stat-num">{{ formatNum(item.stars_today) }}</span>
                <span class="stat-label">今日</span>
              </span>
              <span class="stat">
                <el-icon class="stat-icon total"><StarFilled /></el-icon>
                <span class="stat-num">{{ formatNum(item.stars_total) }}</span>
                <span class="stat-label">Star</span>
              </span>
              <span class="stat">
                <el-icon class="stat-icon fork"><Share /></el-icon>
                <span class="stat-num">{{ formatNum(item.forks) }}</span>
                <span class="stat-label">Fork</span>
              </span>
            </div>
          </div>
        </div>
      </transition-group>

      <!-- 空状态 -->
      <el-empty
        v-else-if="!loading"
        description="当天暂无热榜数据，点击立即抓取获取"
        :image-size="120"
      >
        <el-button type="primary" :loading="fetching" @click="handleFetch">
          立即抓取
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, StarFilled, Refresh, Share } from '@element-plus/icons-vue'
import { hotlistApi, type HotlistItem } from '../api/hotlist'

const sources = ref<{ key: string; name: string; url: string }[]>([])
const activeSource = ref('github')
const hotDate = ref('')
const items = ref<HotlistItem[]>([])
const loading = ref(false)
const fetching = ref(false)

const FALLBACK_SOURCES = [
  { key: 'github', name: 'GitHub Trending', url: 'https://github.com/trending' }
]

function todayStr() {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

function disableFuture(date: Date) {
  return date.getTime() > Date.now()
}

function formatNum(n?: number) {
  if (n === null || n === undefined) return '—'
  return n.toLocaleString('en-US')
}

function rankClass(rank: number) {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return 'rank-normal'
}

function errMsg(e: any) {
  return e?.response?.data?.detail || e?.message || '未知错误'
}

async function loadSources() {
  try {
    const res = await hotlistApi.sources()
    if (res.sources?.length) {
      sources.value = res.sources
      if (!res.sources.some((s) => s.key === activeSource.value)) {
        activeSource.value = res.sources[0].key
      }
      return
    }
  } catch (e) {
    // 接口不可用时回退默认源，页面仍可正常展示
  }
  sources.value = FALLBACK_SOURCES
}

async function loadList() {
  if (!hotDate.value) return
  loading.value = true
  try {
    const res = await hotlistApi.list({ source: activeSource.value, hot_date: hotDate.value })
    items.value = res.items
  } catch (e) {
    ElMessage.error('加载热榜失败: ' + errMsg(e))
  } finally {
    loading.value = false
  }
}

async function handleFetch() {
  fetching.value = true
  try {
    const res = await hotlistApi.fetch(activeSource.value)
    ElMessage.success(res.message || `抓取完成，新增 ${res.count} 条`)
    await loadList()
  } catch (e) {
    ElMessage.error('抓取失败: ' + errMsg(e))
  } finally {
    fetching.value = false
  }
}

function switchSource(key: string) {
  if (key === activeSource.value) return
  activeSource.value = key
  loadList()
}

onMounted(() => {
  hotDate.value = todayStr()
  loadSources()
  loadList()
})
</script>

<style scoped>
.hotlist-page {
  padding: 0;
}

/* ---------- 页头 ---------- */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.page-title {
  margin: 0;
  font-family: var(--font-heading);
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.source-tags {
  display: flex;
  gap: 8px;
}

.source-tag {
  display: inline-block;
  padding: 4px 12px;
  font-size: 13px;
  border-radius: 999px;
  border: 1px solid var(--glass-border);
  background: var(--surface);
  color: var(--el-text-color-secondary);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
  backdrop-filter: var(--glass-filter);
  -webkit-backdrop-filter: var(--glass-filter);
}

.source-tag:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.source-tag.active {
  color: var(--color-on-primary);
  background: var(--gradient-brand-blue);
  border-color: transparent;
  box-shadow: var(--shadow-glow);
}

.header-actions {
  display: flex;
  align-items: center;
}

/* ---------- 列表 ---------- */
.hotlist-body {
  min-height: 240px;
}

.hotlist-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hotlist-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  background: var(--surface);
  backdrop-filter: var(--glass-filter);
  -webkit-backdrop-filter: var(--glass-filter);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius);
  box-shadow: var(--shadow-glass);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.hotlist-card:hover {
  transform: translateY(-2px);
  background: var(--glass-bg-strong);
  box-shadow: var(--shadow-glow);
}

/* ---------- 排名徽章 ---------- */
.card-rank {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-code);
  font-size: 15px;
  font-weight: 700;
  border-radius: var(--radius-sm);
  background: var(--glass-hover);
  border: 1px solid var(--glass-border);
  color: var(--el-text-color-secondary);
}

.rank-gold {
  background: linear-gradient(135deg, #fbbf24, #f97316);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35);
}

.rank-silver {
  background: linear-gradient(135deg, #e2e8f0, #94a3b8);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(148, 163, 184, 0.35);
}

.rank-bronze {
  background: linear-gradient(135deg, #fcd9b6, #c9835f);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(201, 131, 95, 0.35);
}

/* ---------- 卡片内容 ---------- */
.card-main {
  flex: 1;
  min-width: 0;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.repo-link {
  font-family: var(--font-code);
  font-size: 15px;
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.repo-link:hover {
  color: var(--color-secondary);
  text-decoration: underline;
}

.lang-tag {
  --el-tag-bg-color: var(--glass-hover);
  --el-tag-border-color: var(--glass-border);
  color: var(--el-text-color-regular);
}

.repo-desc {
  margin: 0 0 10px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.repo-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.stat-icon {
  font-size: 15px;
}

.stat-icon.today { color: var(--color-accent); }
.stat-icon.total { color: #fbbf24; }
.stat-icon.fork { color: var(--color-secondary); }

.stat-num {
  font-family: var(--font-code);
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* ---------- 入场动画 ---------- */
.fade-up-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.fade-up-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-date-picker {
    margin-right: 0;
    flex: 1;
    min-width: 160px;
  }

  .hotlist-card {
    gap: 12px;
    padding: 14px 16px;
  }

  .repo-stats {
    gap: 14px;
  }
}
</style>
