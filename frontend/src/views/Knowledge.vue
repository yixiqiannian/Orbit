<template>
  <div class="knowledge-manage">
    <div class="page-header">
      <h2>🧠 知识卡片</h2>
      <el-button type="primary" @click="openCardDialog()">
        <el-icon><Plus /></el-icon>新建卡片
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
              class="category-item"
              :class="{ active: selectedCategoryId === null }"
              @click="selectCategory(null)"
            >
              <div class="category-info">
                <span>📋 全部</span>
              </div>
              <el-tag size="small" type="info">{{ totalCardCount }}</el-tag>
            </div>
            <div
              v-for="cat in categories"
              :key="cat.id"
              class="category-item"
              :class="{ active: selectedCategoryId === cat.id }"
              @click="selectCategory(cat.id)"
            >
              <div class="category-info">
                <span
                  class="category-dot"
                  :style="{ backgroundColor: cat.color || '#409eff' }"
                ></span>
                <span>{{ cat.icon || '📄' }} {{ cat.name }}</span>
              </div>
              <div class="category-actions">
                <el-tag size="small" type="info">{{ cat.card_count || 0 }}</el-tag>
                <el-button text size="small" type="danger" @click.stop="handleDeleteCategory(cat)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <el-empty v-if="!categories.length" description="暂无分类" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧卡片列表 -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>
                卡片列表
                <el-tag v-if="selectedCategoryName" type="info" size="small" style="margin-left: 8px;">
                  {{ selectedCategoryName }}
                </el-tag>
              </span>
              <el-input
                v-model="searchKeyword"
                placeholder="搜索卡片..."
                clearable
                style="width: 240px;"
                @input="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </template>

          <div v-loading="cardsLoading" class="card-grid">
            <div
              v-for="card in cards"
              :key="card.id"
              class="card-item"
              @click="openCardDetail(card)"
            >
              <div class="card-item-header">
                <span class="card-title">{{ card.title }}</span>
                <div class="card-item-actions">
                  <el-button text size="small" @click.stop="openCardDialog(card)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button text size="small" type="danger" @click.stop="handleDeleteCard(card)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="card-preview">{{ card.content?.slice(0, 120) }}{{ card.content?.length > 120 ? '...' : '' }}</div>
              <div class="card-meta">
                <el-tag v-if="card.category_name" size="small" type="info">{{ card.category_name }}</el-tag>
                <span v-if="card.tags" class="card-tags">
                  <el-tag v-for="tag in card.tags.split(',')" :key="tag" size="small" type="warning" effect="plain">
                    {{ tag.trim() }}
                  </el-tag>
                </span>
              </div>
            </div>
            <el-empty v-if="!cardsLoading && !cards.length" description="暂无卡片" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分类对话框 -->
    <el-dialog
      v-model="categoryDialogVisible"
      title="添加分类"
      width="400px"
    >
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="categoryForm.icon" placeholder="图标名称（如 📚）" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="categoryForm.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 卡片对话框 -->
    <el-dialog
      v-model="cardDialogVisible"
      :title="editingCard ? '编辑卡片' : '新建卡片'"
      width="600px"
    >
      <el-form :model="cardForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="cardForm.title" placeholder="请输入卡片标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="cardForm.category_id" placeholder="请选择分类" clearable>
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="cardForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="cardForm.content"
            type="textarea"
            :rows="10"
            placeholder="支持 Markdown 格式"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cardDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCard" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 卡片详情弹窗 -->
    <CardDetail
      v-if="detailCard"
      :card="detailCard"
      @close="detailCard = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { knowledgeApi, type KnowledgeCategory, type KnowledgeCard } from '../api/knowledge'
import CardDetail from '../components/CardDetail.vue'

const categories = ref<KnowledgeCategory[]>([])
const cards = ref<KnowledgeCard[]>([])
const selectedCategoryId = ref<number | null>(null)
const cardsLoading = ref(false)
const saving = ref(false)
const searchKeyword = ref('')
const detailCard = ref<KnowledgeCard | null>(null)

// 分类对话框
const categoryDialogVisible = ref(false)
const categoryForm = reactive({
  name: '',
  icon: '',
  color: '#409eff'
})

// 卡片对话框
const cardDialogVisible = ref(false)
const editingCard = ref<KnowledgeCard | null>(null)
const cardForm = reactive({
  title: '',
  content: '',
  category_id: undefined as number | undefined,
  tags: ''
})

const totalCardCount = computed(() => categories.value.reduce((sum, c) => sum + (c.card_count || 0), 0))
const selectedCategoryName = computed(() => {
  if (selectedCategoryId.value === null) return ''
  return categories.value.find(c => c.id === selectedCategoryId.value)?.name || ''
})

onMounted(async () => {
  await loadCategories()
  await loadCards()
})

async function loadCategories() {
  try {
    categories.value = await knowledgeApi.listCategories()
  } catch (e) {
    console.error('Failed to load categories:', e)
    ElMessage.error('加载分类失败')
  }
}

async function loadCards() {
  cardsLoading.value = true
  try {
    const params: any = {}
    if (selectedCategoryId.value !== null) params.category_id = selectedCategoryId.value
    if (searchKeyword.value.trim()) params.keyword = searchKeyword.value.trim()
    cards.value = await knowledgeApi.listCards(params)
  } catch (e) {
    console.error('Failed to load cards:', e)
    ElMessage.error('加载卡片失败')
  } finally {
    cardsLoading.value = false
  }
}

function selectCategory(categoryId: number | null) {
  selectedCategoryId.value = categoryId
  loadCards()
}

let searchTimer: ReturnType<typeof setTimeout> | null = null
function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadCards(), 300)
}

// 分类操作
function openCategoryDialog() {
  categoryForm.name = ''
  categoryForm.icon = ''
  categoryForm.color = '#409eff'
  categoryDialogVisible.value = true
}

async function handleSaveCategory() {
  if (!categoryForm.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  saving.value = true
  try {
    await knowledgeApi.createCategory(categoryForm)
    ElMessage.success('分类已创建')
    categoryDialogVisible.value = false
    await loadCategories()
  } catch (e: any) {
    ElMessage.error('创建分类失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

async function handleDeleteCategory(cat: KnowledgeCategory) {
  try {
    await ElMessageBox.confirm(`确定删除分类「${cat.name}」吗？`, '确认删除', { type: 'warning' })
    await knowledgeApi.deleteCategory(cat.id)
    ElMessage.success('分类已删除')
    if (selectedCategoryId.value === cat.id) {
      selectedCategoryId.value = null
    }
    await loadCategories()
    await loadCards()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除分类失败')
    }
  }
}

// 卡片操作
function openCardDialog(card?: KnowledgeCard) {
  editingCard.value = card || null
  cardForm.title = card?.title || ''
  cardForm.content = card?.content || ''
  cardForm.category_id = card?.category_id || selectedCategoryId.value || undefined
  cardForm.tags = card?.tags || ''
  cardDialogVisible.value = true
}

async function handleSaveCard() {
  if (!cardForm.title.trim()) {
    ElMessage.warning('请输入卡片标题')
    return
  }
  if (!cardForm.content.trim()) {
    ElMessage.warning('请输入卡片内容')
    return
  }
  saving.value = true
  try {
    if (editingCard.value) {
      await knowledgeApi.updateCard(editingCard.value.id, cardForm)
      ElMessage.success('卡片已更新')
    } else {
      await knowledgeApi.createCard(cardForm)
      ElMessage.success('卡片已创建')
    }
    cardDialogVisible.value = false
    await loadCards()
    await loadCategories()
  } catch (e: any) {
    ElMessage.error('保存卡片失败: ' + (e?.response?.data?.detail || e?.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

async function handleDeleteCard(card: KnowledgeCard) {
  try {
    await ElMessageBox.confirm(`确定删除卡片「${card.title}」吗？`, '确认删除', { type: 'warning' })
    await knowledgeApi.deleteCard(card.id)
    ElMessage.success('卡片已删除')
    await loadCards()
    await loadCategories()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除卡片失败')
    }
  }
}

function openCardDetail(card: KnowledgeCard) {
  detailCard.value = card
}
</script>

<style scoped>
.knowledge-manage {
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
.category-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.category-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}
.category-item:hover .category-actions {
  opacity: 1;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.card-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.card-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}
.card-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.card-title {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-item-actions {
  display: flex;
  opacity: 0;
  transition: opacity 0.2s;
}
.card-item:hover .card-item-actions {
  opacity: 1;
}
.card-preview {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
</style>
