<template>
  <el-dialog
    :model-value="true"
    :title="card.title"
    width="700px"
    @close="$emit('close')"
  >
    <div class="card-detail">
      <div class="card-detail-meta">
        <el-tag v-if="card.category_name" type="info">{{ card.category_name }}</el-tag>
        <span v-if="card.tags" class="card-detail-tags">
          <el-tag v-for="tag in card.tags.split(',')" :key="tag" size="small" type="warning" effect="plain">
            {{ tag.trim() }}
          </el-tag>
        </span>
      </div>
      <div class="card-detail-content markdown-body" v-html="renderedContent"></div>
      <div class="card-detail-footer">
        <span>创建于 {{ formatDate(card.created_at) }}</span>
        <span v-if="card.updated_at !== card.created_at">更新于 {{ formatDate(card.updated_at) }}</span>
      </div>
    </div>
    <template #footer>
      <el-button @click="$emit('close')">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import type { KnowledgeCard } from '../api/knowledge'

const props = defineProps<{
  card: KnowledgeCard
}>()

defineEmits<{
  (e: 'close'): void
}>()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true
})

const renderedContent = computed(() => {
  return md.render(props.card.content || '')
})

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.card-detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.card-detail-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.card-detail-content {
  line-height: 1.7;
  color: #303133;
  min-height: 100px;
}
.card-detail-content :deep(h1),
.card-detail-content :deep(h2),
.card-detail-content :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
}
.card-detail-content :deep(p) {
  margin-bottom: 12px;
}
.card-detail-content :deep(code) {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #e6a23c;
}
.card-detail-content :deep(pre) {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 12px;
}
.card-detail-content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
}
.card-detail-content :deep(ul),
.card-detail-content :deep(ol) {
  padding-left: 24px;
  margin-bottom: 12px;
}
.card-detail-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 12px;
  margin: 12px 0;
  color: #606266;
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 0 8px 8px 0;
}
.card-detail-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 12px;
}
.card-detail-content :deep(th),
.card-detail-content :deep(td) {
  border: 1px solid #e4e7ed;
  padding: 8px 12px;
  text-align: left;
}
.card-detail-content :deep(th) {
  background-color: #f5f7fa;
  font-weight: 600;
}
.card-detail-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}
.card-detail-content :deep(a:hover) {
  text-decoration: underline;
}
.card-detail-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
  color: #909399;
  font-size: 12px;
  display: flex;
  gap: 16px;
}
</style>
