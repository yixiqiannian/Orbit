<script setup lang="ts">
// 占位页：T5 将替换为本模块完整页面（日期选择 + 数据源 tab + 热榜列表）
</script>

<template>
  <div class="hotlist-page">
    <el-card class="glass-card">
      <template #header>
        <span class="card-title">热榜</span>
      </template>
      <el-empty description="热榜页面建设中（T5）" />
    </el-card>
  </div>
</template>

<style scoped>
.hotlist-page {
  padding: 20px;
}

.glass-card {
  background: var(--glass-bg, rgba(255, 255, 255, 0.55));
  backdrop-filter: blur(var(--glass-blur, 20px));
  -webkit-backdrop-filter: blur(var(--glass-blur, 20px));
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.6));
  border-radius: var(--glass-radius, 16px);
  box-shadow: var(--glass-shadow, 0 8px 32px rgba(37, 99, 235, 0.14));
}

.card-title {
  font-family: var(--font-display, 'Fredoka', 'Fira Sans', sans-serif);
  font-size: 18px;
  font-weight: 700;
  color: var(--color-foreground, #0f172a);
}
</style>
