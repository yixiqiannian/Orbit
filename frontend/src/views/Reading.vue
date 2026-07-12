<template>
  <div class="reading-page">
    <el-row :gutter="20">
      <!-- 左侧书架 -->
      <el-col :span="18">
        <el-tabs v-model="activeTab" @tab-click="loadBooks">
          <el-tab-pane label="全部" name="all" />
          <el-tab-pane label="想读" name="want_to_read" />
          <el-tab-pane label="在读" name="reading" />
          <el-tab-pane label="已读" name="finished" />
        </el-tabs>

        <!-- 添加书籍 -->
        <el-form :inline="true" style="margin: 20px 0;">
          <el-form-item>
            <el-input v-model="newBook.title" placeholder="书名" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="newBook.author" placeholder="作者" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleAdd">添加书籍</el-button>
          </el-form-item>
          <el-form-item>
            <el-button @click="handleSync" :loading="syncing">同步微信读书</el-button>
          </el-form-item>
        </el-form>

        <!-- 书籍列表 -->
        <el-table :data="books" stripe v-loading="loading">
          <el-table-column prop="title" label="书名" />
          <el-table-column prop="author" label="作者" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-select v-model="row.status" @change="handleStatusChange(row)">
                <el-option label="想读" value="want_to_read" />
                <el-option label="在读" value="reading" />
                <el-option label="已读" value="finished" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="进度" width="200">
            <template #default="{ row }">
              <el-progress :percentage="row.progress || 0" :stroke-width="10" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" @click="updateProgress(row)">更新进度</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-col>

      <!-- 右侧统计 -->
      <el-col :span="6">
        <el-card>
          <template #header>阅读统计</template>
          <div class="stat-item">
            <span>总书籍</span>
            <span class="stat-value">{{ stats.total_books || 0 }}</span>
          </div>
          <div class="stat-item">
            <span>在读</span>
            <span class="stat-value">{{ stats.reading || 0 }}</span>
          </div>
          <div class="stat-item">
            <span>已读</span>
            <span class="stat-value">{{ stats.finished || 0 }}</span>
          </div>
          <div class="stat-item">
            <span>平均进度</span>
            <span class="stat-value">{{ stats.avg_progress || 0 }}%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

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
const currentBook = ref<Book | null>(null)
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
    // stats load silently
  }
}

async function handleAdd() {
  if (!newBook.value.title) return ElMessage.warning('请输入书名')
  try {
    await readingApi.createBook(newBook.value)
    ElMessage.success('添加成功')
    newBook.value = { title: '', author: '' }
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
    ElMessage.error('状态更新失败')
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
</script>

<style scoped>
.reading-page {
  padding: 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.stat-value {
  font-weight: bold;
  color: #409eff;
}
</style>
