<template>
  <div class="nav-portal">
    <!-- 顶部搜索栏 -->
    <div class="portal-header">
      <div class="header-content">
        <h1 class="portal-title">🧭 导航站</h1>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索导航..."
            prefix-icon="Search"
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
    </div>

    <!-- 分类标签 -->
    <div class="category-tabs">
      <div class="tabs-container">
        <div
          class="tab-item"
          :class="{ active: selectedCategoryId === null }"
          @click="selectCategory(null)"
        >
          全部
        </div>
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="tab-item"
          :class="{ active: selectedCategoryId === cat.id }"
          @click="selectCategory(cat.id)"
        >
          {{ cat.name }}
        </div>
      </div>
    </div>

    <!-- 导航卡片网格 -->
    <div class="sites-grid">
      <div
        v-for="site in filteredSites"
        :key="site.id"
        class="site-card"
        @click="openSite(site)"
      >
        <div class="card-icon">
          <img v-if="site.icon" :src="site.icon" :alt="site.name" />
          <div v-else class="icon-placeholder">{{ site.name.charAt(0) }}</div>
        </div>
        <div class="card-info">
          <div class="card-name">{{ site.name }}</div>
          <div class="card-desc">{{ site.description || site.url }}</div>
        </div>
        <div class="card-category" v-if="site.category">
          {{ site.category.name }}
        </div>
      </div>
      <el-empty v-if="!filteredSites.length" description="暂无导航数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { navApi, type NavCategory, type NavSite } from '../api/nav'

const categories = ref<NavCategory[]>([])
const allSites = ref<NavSite[]>([])
const selectedCategoryId = ref<number | null>(null)
const searchQuery = ref('')

const filteredSites = computed(() => {
  let sites = allSites.value

  // 按分类筛选
  if (selectedCategoryId.value !== null) {
    sites = sites.filter(s => s.category_id === selectedCategoryId.value)
  }

  // 按搜索关键词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    sites = sites.filter(s =>
      s.name.toLowerCase().includes(query) ||
      (s.description && s.description.toLowerCase().includes(query)) ||
      s.url.toLowerCase().includes(query)
    )
  }

  return sites
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    const [cats, sitesRes] = await Promise.all([
      navApi.listCategories(),
      navApi.listSites()
    ])
    categories.value = cats
    const catMap = new Map(cats.map(c => [c.id, c]))
    allSites.value = (Array.isArray(sitesRes) ? sitesRes : []).map(site => ({
      ...site,
      category: catMap.get(site.category_id)
    }))
  } catch (e) {
    console.error('Failed to load nav data:', e)
  }
}

function selectCategory(catId: number | null) {
  selectedCategoryId.value = catId
}

function openSite(site: NavSite) {
  window.open(site.url, '_blank')
}
</script>

<style scoped>
.nav-portal {
  min-height: 100vh;
  background-color: #1a1a2e;
  color: #eee;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.portal-header {
  background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
  padding: 40px 20px 30px;
  text-align: center;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
}

.portal-title {
  margin: 0 0 20px;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(90deg, #e94560, #533483);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-box {
  max-width: 500px;
  margin: 0 auto;
}

.search-box :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  box-shadow: none;
}

.search-box :deep(.el-input__inner) {
  color: #fff;
}

.search-box :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

.search-box :deep(.el-input__prefix .el-icon) {
  color: rgba(255, 255, 255, 0.5);
}

.category-tabs {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}

.tabs-container {
  display: flex;
  gap: 0;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  overflow-x: auto;
}

.tab-item {
  padding: 14px 24px;
  cursor: pointer;
  white-space: nowrap;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-item:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.05);
}

.tab-item.active {
  color: #e94560;
  border-bottom-color: #e94560;
}

.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.site-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  overflow: hidden;
}

.site-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(233, 69, 96, 0.1), rgba(83, 52, 131, 0.1));
  opacity: 0;
  transition: opacity 0.3s;
}

.site-card:hover {
  transform: translateY(-4px);
  border-color: rgba(233, 69, 96, 0.4);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.site-card:hover::before {
  opacity: 1;
}

.card-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.card-icon img {
  width: 100%;
  height: 100%;
  border-radius: 10px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px;
}

.icon-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 10px;
  background: linear-gradient(135deg, #e94560, #533483);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
}

.card-info {
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-category {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 8px;
  border-radius: 10px;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .portal-header {
    padding: 30px 15px 20px;
  }

  .portal-title {
    font-size: 24px;
  }

  .sites-grid {
    grid-template-columns: 1fr;
    padding: 20px 15px;
  }

  .tab-item {
    padding: 12px 16px;
    font-size: 13px;
  }
}

/* Element Plus 暗色覆盖 */
.nav-portal :deep(.el-empty__description p) {
  color: rgba(255, 255, 255, 0.4);
}

.nav-portal :deep(.el-empty__image svg) {
  fill: rgba(255, 255, 255, 0.2);
}
</style>
