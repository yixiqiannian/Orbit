<template>
  <div class="reading-page">
    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-number">{{ stats.total_books || 0 }}</div>
          <div class="stat-label">总书籍</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card reading">
          <div class="stat-number">{{ stats.reading || 0 }}</div>
          <div class="stat-label">在读</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card finished">
          <div class="stat-number">{{ stats.finished || 0 }}</div>
          <div class="stat-label">已读</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card progress">
          <div class="stat-number">{{ stats.avg_progress || 0 }}%</div>
          <div class="stat-label">平均进度</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-tabs v-model="activeTab" @tab-click="loadBooks">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="想读" name="want_to_read" />
        <el-tab-pane label="在读" name="reading" />
        <el-tab-pane label="已读" name="finished" />
      </el-tabs>
      <div class="actions">
        <el-button type="primary" @click="showAddDialog = true">添加书籍</el-button>
        <el-button @click="handleSync" :loading="syncing">同步微信读书</el-button>
      </div>
    </div>

    <!-- 书籍卡片列表 -->
    <div v-loading="loading" class="card-grid">
      <el-card
        v-for="book in books"
        :key="book.id"
        class="book-card"
        shadow="hover"
      >
        <div class="book-cover">
          <img v-if="book.cover_url" :src="book.cover_url" :alt="book.title" />
          <div v-else class="no-cover">📚</div>
        </div>

        <div class="book-info">
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-author">{{ book.author || '未知作者' }}</p>

          <div class="book-status">
            <el-select v-model="book.status" @change="handleStatusChange(book)" size="small" style="width: 100px;">
              <el-option label="想读" value="want_to_read" />
              <el-option label="在读" value="reading" />
              <el-option label="已读" value="finished" />
            </el-select>
          </div>

          <div class="book-progress">
            <el-progress :percentage="book.progress || 0" :stroke-width="8" />
            <span v-if="book.last_read_at" class="last-read">
              {{ formatDate(book.last_read_at) }}
            </span>
          </div>

          <div class="book-actions">
            <el-button
              v-if="book.weread_id"
              size="small"
              type="success"
              @click="syncProgress(book)"
              :loading="syncingId === book.id"
            >
              同步进度
            </el-button>
            <el-button size="small" @click="updateProgress(book)">手动更新</el-button>
            <el-button type="danger" size="small" text @click="handleDelete(book.id)">删除</el-button>
          </div>
        </div>
      </el-card>

      <!-- 空状态 -->
      <el-empty v-if="!loading && books.length === 0" description="暂无书籍">
        <el-button type="primary" @click="handleSync">同步微信读书</el-button>
      </el-empty>
    </div>

    <!-- 添加书籍对话框 -->
    <el-dialog v-model="showAddDialog" title="添加书籍" width="400px">
      <el-form>
        <el-form-item label="书名" required>
          <el-input v-model="newBook.title" placeholder="请输入书名" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="newBook.author" placeholder="请输入作者" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>

    <!-- 进度更新对话框 -->
    <el-dialog v-model="showProgress" title="更新进度" width="400px">
      <el-form>
        <el-form-item label="当前章节">
          <el-input-number v-model="progressForm.current_chapter" :min="0" :max="progressForm.total_chapters || 999" />
        </el-form-item>
        <el-form-item label="总章节">
          <el-input-number v-model="progressForm.total_chapters" :min="0" />
        </el-form-item>
        <el-form-item label="进度百分比">
          <el-slider v-model="progressForm.progress" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProgress = false">取消</el-button>
        <el-button type="primary" @click="saveProgress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { readingApi, type Book, type ReadingStats } from '../api/reading'
import { ElMessage } from 'element-plus'

const activeTab = ref('all')
const books = ref<Book[]>([])
const stats = ref<ReadingStats>({ total_books: 0, reading: 0, finished: 0, avg_progress: 0 })
const syncing = ref(false)
const loading = ref(false)
const showProgress = ref(false)
const showAddDialog = ref(false)
const currentBook = ref<Book | null>(null)
const syncingId = ref<number | null>(null)
const newBook = ref({ title: '', author: '' })
const progressForm = ref({ current_chapter: 0, total_chapters: 0, progress: 0 })

onMounted(() => {
  loadBooks()
  loadStats()
})

async function loadBooks() {
  loading.value = true
  try {
    const status = activeTab.value === 'all' ? undefined : activeTab.value
    const res = await readingApi.listBooks({ status })
    books.value = res.items
  } catch (e) {
    ElMessage.error('加载书籍失败')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    stats.value = await readingApi.getStats()
  } catch (e) {
    // silent
  }
}

async function handleAdd() {
  if (!newBook.value.title) return ElMessage.warning('请输入书名')
  try {
    await readingApi.createBook(newBook.value)
    ElMessage.success('添加成功')
    newBook.value = { title: '', author: '' }
    showAddDialog.value = false
    loadBooks()
    loadStats()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

async function handleStatusChange(book: Book) {
  try {
    await readingApi.updateBook(book.id, { status: book.status })
    ElMessage.success('状态更新成功')
    loadStats()
  } catch (e) {
    ElMessage.error('更新失败')
    loadBooks()
  }
}

async function handleDelete(id: number) {
  try {
    await readingApi.deleteBook(id)
    ElMessage.success('删除成功')
    loadBooks()
    loadStats()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

function updateProgress(book: Book) {
  currentBook.value = book
  progressForm.value = {
    current_chapter: book.current_chapter || 0,
    total_chapters: book.total_chapters || 0,
    progress: book.progress || 0
  }
  showProgress.value = true
}

async function saveProgress() {
  if (!currentBook.value) return
  try {
    await readingApi.updateBook(currentBook.value.id, progressForm.value)
    ElMessage.success('进度更新成功')
    showProgress.value = false
    loadBooks()
    loadStats()
  } catch (e) {
    ElMessage.error('进度更新失败')
  }
}

async function syncProgress(book: Book) {
  syncingId.value = book.id
  try {
    const updated = await readingApi.syncBookProgress(book.id)
    book.progress = updated.progress
    book.status = updated.status
    book.last_read_at = updated.last_read_at
    ElMessage.success('进度同步成功')
    loadStats()
  } catch (e) {
    ElMessage.error('同步失败')
  } finally {
    syncingId.value = null
  }
}

async function handleSync() {
  syncing.value = true
  try {
    await readingApi.syncWeread()
    ElMessage.success('同步成功')
    loadBooks()
    loadStats()
  } catch (error) {
    ElMessage.error('同步失败')
  } finally {
    syncing.value = false
  }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.reading-page {
  padding: 0;
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.stat-card.reading .stat-number { color: #e6a23c; }
.stat-card.finished .stat-number { color: #67c23a; }
.stat-card.progress .stat-number { color: #909399; }

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 10px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.book-card {
  transition: transform 0.2s;
}

.book-card:hover {
  transform: translateY(-2px);
}

.book-card :deep(.el-card__body) {
  display: flex;
  gap: 16px;
}

.book-cover {
  flex-shrink: 0;
  width: 80px;
  height: 110px;
  overflow: hidden;
  border-radius: 4px;
  background: #f5f7fa;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.book-info {
  flex: 1;
  min-width: 0;
}

.book-title {
  margin: 0 0 4px;
  font-size: 15px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  margin: 0 0 8px;
  font-size: 13px;
  color: #909399;
}

.book-status {
  margin-bottom: 8px;
}

.book-progress {
  margin-bottom: 8px;
}

.last-read {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.book-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
