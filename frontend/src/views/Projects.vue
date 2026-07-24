<template>
  <div class="projects-page">
    <h2>📁 项目管理</h2>
    <ProjectManager />
  </div>
</template>

<script setup lang="ts">
import ProjectManager from '../components/ProjectManager.vue'
</script>

<style scoped>
.projects-page {
  padding: 0;
}
.projects-page h2 {
  margin: 0 0 20px;
  color: #303133;
}
</style>
