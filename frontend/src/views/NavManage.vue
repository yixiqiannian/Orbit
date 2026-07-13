<template>
  <div class="nav-manage">
    <div class="page-header">
      <h2>🧭 导航管理</h2>
      <el-button type="primary" @click="openPortal">
        <el-icon><Link /></el-icon>
        打开导航页
      </el-button>
    </div>

    <el-row :gutter="20">
      <!-- 左侧分类列表 -->
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>分类列表</span>
              <el-button type="primary" size="small" @click="openCategoryDialog()">
                <el-icon><Plus /></el-icon>添加
              </el-button>
            </div>
          </template>
          <div class="category-list">
            <div
              v-for="cat in categories"
              :key="cat.id"
              class="category-item"
              :class="{ active: selectedCategoryId === cat.id }"
              @click="selectCategory(cat)"
            >
              <div class="category-info">
                <el-icon v-if="cat.icon"><component :is="cat.icon" /></el-icon>
                <span>{{ cat.name }}</span>
              </div>
              <div class="category-actions">
                <el-button text size="small" @click.stop="openCategoryDialog(cat)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button text size="small" type="danger" @click.stop="handleDeleteCategory(cat)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <el-empty v-if="!categories.length" description="暂无分类" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧导航列表 -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>
                导航列表
                <el-tag v-if="selectedCategory" type="info" size="small" style="margin-left: 8px;">
                  {{ selectedCategory.name }}
                </el-tag>
              </span>
              <el-button type="primary" size="small" @click="openSiteDialog()">
                <el-icon><Plus /></el-icon>添加导航
              </el-button>
            </div>
          </template>

          <el-table :data="sites" v-loading="sitesLoading" stripe>
            <el-table-column prop="name" label="名称" min-width="120">
              <template #default="{ row }">
                <div class="site-name-cell">
                  <img v-if="row.icon" :src="row.icon" class="site-icon" @error="(e: any) => e.target.style.display='none'" />
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="url" label="链接" min-width="200" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
            <el-table-column prop="sort_order" label="排序" width="80" align="center" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button text size="small" @click="openSiteDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button text size="small" type="primary" @click="openSite(row)">
                  <el-icon><Link /></el-icon>
                </el-button>
                <el-button text size="small" type="danger" @click="handleDeleteSite(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分类对话框 -->
    <el-dialog
      v-model="categoryDialogVisible"
      :title="editingCategory ? '编辑分类' : '添加分类'"
      width="400px"
    >
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="categoryForm.icon" placeholder="图标名称（可选）" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导航对话框 -->
    <el-dialog
      v-model="siteDialogVisible"
      :title="editingSite ? '编辑导航' : '添加导航'"
      width="500px"
    >
      <el-form :model="siteForm" label-width="80px">
        <el-form-item label="分类" required>
          <el-select v-model="siteForm.category_id" placeholder="请选择分类">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="链接" required>
          <el-input v-model="siteForm.url" placeholder="请输入网址" @blur="fetchSiteInfo">
            <template #append>
              <el-button @click="fetchSiteInfo" :loading="fetchingInfo">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="siteForm.name" placeholder="请输入导航名称" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="siteForm.icon" placeholder="图标URL（自动识别）" />
          <div v-if="siteForm.icon" class="icon-preview">
            <img :src="siteForm.icon" @error="(e: any) => e.target.style.display='none'" />
          </div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="siteForm.description" type="textarea" placeholder="简短描述（可选）" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="siteForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="siteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveSite" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Link, Refresh } from '@element-plus/icons-vue'
import { navApi, type NavCategory, type NavSite } from '../api/nav'

const categories = ref<NavCategory[]>([])
const sites = ref<NavSite[]>([])
const selectedCategoryId = ref<number | null>(null)
const selectedCategory = ref<NavCategory | null>(null)
const sitesLoading = ref(false)
const saving = ref(false)
const fetchingInfo = ref(false)

// 分类对话框
const categoryDialogVisible = ref(false)
const editingCategory = ref<NavCategory | null>(null)
const categoryForm = reactive({
  name: '',
  icon: '',
  sort_order: 0
})

// 导航对话框
const siteDialogVisible = ref(false)
const editingSite = ref<NavSite | null>(null)
const siteForm = reactive({
  category_id: undefined as number | undefined,
  name: '',
  url: '',
  icon: '',
  description: '',
  sort_order: 0
})

onMounted(async () => {
  await loadCategories()
})

async function loadCategories() {
  try {
    categories.value = await navApi.listCategories()
    if (categories.value.length && !selectedCategoryId.value) {
      selectCategory(categories.value[0])
    }
  } catch (e) {
    console.error('Failed to load categories:', e)
    ElMessage.error('加载分类失败')
  }
}

async function selectCategory(cat: NavCategory) {
  selectedCategoryId.value = cat.id
  selectedCategory.value = cat
  await loadSites(cat.id)
}

async function loadSites(categoryId?: number) {
  sitesLoading.value = true
  try {
    sites.value = await navApi.listSites(categoryId)
  } catch (e) {
    console.error('Failed to load sites:', e)
    ElMessage.error('加载导航失败')
  } finally {
    sitesLoading.value = false
  }
}

function openCategoryDialog(cat?: NavCategory) {
  editingCategory.value = cat || null
  categoryForm.name = cat?.name || ''
  categoryForm.icon = cat?.icon || ''
  categoryForm.sort_order = cat?.sort_order || 0
  categoryDialogVisible.value = true
}

async function handleSaveCategory() {
  if (!categoryForm.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  saving.value = true
  try {
    if (editingCategory.value) {
      await navApi.updateCategory(editingCategory.value.id, categoryForm)
      ElMessage.success('分类已更新')
    } else {
      await navApi.createCategory(categoryForm)
      ElMessage.success('分类已创建')
    }
    categoryDialogVisible.value = false
    await loadCategories()
  } catch (e) {
    console.error('Failed to save category:', e)
    ElMessage.error('保存分类失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteCategory(cat: NavCategory) {
  try {
    await ElMessageBox.confirm(`确定删除分类「${cat.name}」吗？`, '确认删除', {
      type: 'warning'
    })
    await navApi.deleteCategory(cat.id)
    ElMessage.success('分类已删除')
    if (selectedCategoryId.value === cat.id) {
      selectedCategoryId.value = null
      selectedCategory.value = null
      sites.value = []
    }
    await loadCategories()
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('Failed to delete category:', e)
      ElMessage.error(e.response?.data?.detail || '删除分类失败')
    }
  }
}

function openSiteDialog(site?: NavSite) {
  editingSite.value = site || null
  siteForm.category_id = site?.category_id || selectedCategoryId.value || undefined
  siteForm.name = site?.name || ''
  siteForm.url = site?.url || ''
  siteForm.icon = site?.icon || ''
  siteForm.description = site?.description || ''
  siteForm.sort_order = site?.sort_order || 0
  siteDialogVisible.value = true
}

async function fetchSiteInfo() {
  if (!siteForm.url.trim()) return
  
  // 确保URL有协议
  let url = siteForm.url.trim()
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url
    siteForm.url = url
  }
  
  fetchingInfo.value = true
  try {
    const info = await navApi.fetchSiteInfo(url)
    if (info.title && !siteForm.name) {
      siteForm.name = info.title
    }
    if (info.icon) {
      siteForm.icon = info.icon
    }
    ElMessage.success('已识别网站信息')
  } catch (e) {
    console.error('Failed to fetch site info:', e)
  } finally {
    fetchingInfo.value = false
  }
}

async function handleSaveSite() {
  if (!siteForm.url.trim()) {
    ElMessage.warning('请输入网址')
    return
  }
  if (!siteForm.category_id) {
    ElMessage.warning('请选择分类')
    return
  }
  
  // 如果没有名称，使用域名
  if (!siteForm.name.trim()) {
    try {
      const url = new URL(siteForm.url)
      siteForm.name = url.hostname
    } catch {
      siteForm.name = siteForm.url
    }
  }
  
  saving.value = true
  try {
    if (editingSite.value) {
      await navApi.updateSite(editingSite.value.id, siteForm)
      ElMessage.success('导航已更新')
    } else {
      await navApi.createSite(siteForm as any)
      ElMessage.success('导航已创建')
    }
    siteDialogVisible.value = false
    await loadSites(selectedCategoryId.value!)
  } catch (e) {
    console.error('Failed to save site:', e)
    ElMessage.error('保存导航失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteSite(site: NavSite) {
  try {
    await ElMessageBox.confirm(`确定删除导航「${site.name}」吗？`, '确认删除', {
      type: 'warning'
    })
    await navApi.deleteSite(site.id)
    ElMessage.success('导航已删除')
    await loadSites(selectedCategoryId.value!)
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('Failed to delete site:', e)
      ElMessage.error('删除导航失败')
    }
  }
}

function openSite(site: NavSite) {
  window.open(site.url, '_blank')
}

function openPortal() {
  window.open('/portal', '_blank')
}
</script>

<style scoped>
.nav-manage {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
  color: #303133;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.category-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.category-item:hover {
  background-color: #f5f7fa;
}
.category-item.active {
  background-color: #ecf5ff;
  color: #409eff;
}
.category-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.category-actions {
  display: flex;
  gap: 0;
  opacity: 0;
  transition: opacity 0.2s;
}
.category-item:hover .category-actions {
  opacity: 1;
}
.site-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.site-icon {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  object-fit: contain;
}
.icon-preview {
  margin-top: 8px;
}
.icon-preview img {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  object-fit: contain;
}
</style>
