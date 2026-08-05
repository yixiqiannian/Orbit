## 目标
实现任务归档页面，以文件夹形式展示归档任务。

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 创建归档页面 (views/Archives.vue)
功能要求：
- 显示归档月份文件夹列表
- 每个文件夹显示：月份名称、任务数量、完成任务数
- 点击文件夹展开，显示该月所有归档任务
- 支持按分类、项目搜索
- 任务显示：标题、状态、优先级、分类、项目、完成日期

### 2. 文件夹样式
```vue
<template>
  <div class="archives-page">
    <h1>📁 任务归档</h1>
    
    <!-- 搜索 -->
    <el-form :inline="true" style="margin: 20px 0;">
      <el-form-item label="分类">
        <el-select v-model="filterCategory" clearable @change="loadArchives">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="项目">
        <el-select v-model="filterProject" clearable @change="loadArchives">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </el-form-item>
    </el-form>
    
    <!-- 文件夹列表 -->
    <div class="folder-grid">
      <div
        v-for="folder in folders"
        :key="folder.month"
        class="folder-card"
        @click="openFolder(folder)"
      >
        <div class="folder-icon">📁</div>
        <div class="folder-name">{{ folder.month }}</div>
        <div class="folder-stats">
          {{ folder.completed }}/{{ folder.total }} 完成
        </div>
      </div>
    </div>
    
    <!-- 文件夹详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="`📁 ${selectedFolder?.month} 归档任务`"
      width="800px"
    >
      <el-table :data="folderTasks" style="width: 100%">
        <el-table-column prop="title" label="任务标题" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="project_name" label="项目" width="120" />
        <el-table-column prop="updated_at" label="完成日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>
```

### 3. 文件夹数据结构
```typescript
interface ArchiveFolder {
  month: string  // 2026-07
  total: number  // 总任务数
  completed: number  // 完成任务数
  tasks: Task[]  // 任务列表
}
```

### 4. API 调用
```typescript
// 获取归档月份列表
const months = await taskApi.list({ archived: true })

// 按月份分组
const folders = months.reduce((acc, task) => {
  const month = task.archived_month
  if (!acc[month]) {
    acc[month] = { month, total: 0, completed: 0, tasks: [] }
  }
  acc[month].total++
  if (task.status === 'completed') acc[month].completed++
  acc[month].tasks.push(task)
  return acc
}, {})
```

### 5. 更新侧边栏
添加菜单项：
```vue
<el-menu-item index="/archives">
  <el-icon><Box /></el-icon>
  <span>任务归档</span>
</el-menu-item>
```

### 6. 更新路由
```typescript
{
  path: '/archives',
  name: 'Archives',
  component: () => import('../views/Archives.vue'),
  meta: { requiresAuth: true }
}
```

### 7. 样式要求
- 文件夹卡片：圆角、阴影、悬停效果
- 文件夹图标：📁 或 📂
- 文件夹名称：年月格式（2026-07）
- 统计信息：完成数/总数

### 8. 验收标准
- [ ] 归档页面显示正常
- [ ] 文件夹列表显示正常
- [ ] 点击文件夹显示任务列表
- [ ] 支持分类、项目搜索
- [ ] 侧边栏菜单正常
