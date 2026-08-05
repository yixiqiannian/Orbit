## 目标
实现任务归档的前端功能，包括归档筛选、归档月份查看。

## 前置任务
依赖 T31 完成

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 更新任务 API (api/tasks.ts)
添加归档相关参数：
```typescript
export interface TaskQuery {
  type?: string
  status?: string
  page?: number
  size?: number
  category_id?: number
  project_id?: number
  archived?: boolean
  archived_month?: string
}

export const taskApi = {
  ...
  archive: (month?: string) => api.post('/api/tasks/archive', null, { params: { month } }),
}
```

### 2. 更新任务管理页面 (views/Tasks.vue)
添加功能：
- 筛选区域添加「归档状态」下拉：全部 / 未归档 / 已归档
- 归档月份筛选（当选择已归档时显示）
- 归档按钮（手动触发归档）
- 归档任务显示样式（灰色背景或角标）

### 3. 添加归档月份选择器
当选择「已归档」时，显示月份选择器：
```vue
<el-form-item v-if="filterArchived === true" label="归档月份">
  <el-date-picker
    v-model="filterArchivedMonth"
    type="month"
    placeholder="选择月份"
    value-format="YYYY-MM"
    @change="loadTasks"
  />
</el-form-item>
```

### 4. 归档任务样式
已归档任务显示：
- 灰色背景或半透明
- 角标显示「已归档」
- 显示归档月份

### 5. 归档操作按钮
在任务列表顶部添加「归档上月」按钮：
```vue
<el-button @click="handleArchive" :loading="archiving">
  <el-icon><Archive /></el-icon> 归档上月已完成任务
</el-button>
```

### 6. 更新仪表盘 (views/Dashboard.vue)
添加归档统计：
- 「上月归档」卡片：显示上月归档任务数量
- 「本月已完成」卡片：显示本月已完成任务数量

### 7. 验收标准
- [ ] 归档筛选正常
- [ ] 归档月份选择正常
- [ ] 归档任务样式显示正常
- [ ] 归档按钮正常工作
- [ ] 仪表盘显示归档统计
