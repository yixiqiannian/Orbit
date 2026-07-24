## 目标
实现任务管理模块的前端增强功能，包括项目管理、任务分类、过期提示，以及修复切换 bug。

## 前置任务
依赖 T27 完成

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 修复切换 bug (views/Tasks.vue)
问题：
- 切换每日任务/工作规划/目标管理时，内容显示异常
- 任务跑到错误的分类里

修复方案：
- 使用独立的数据源，不共享
- 切换时重新加载数据
- 添加 loading 状态

### 2. 创建项目管理组件 (components/ProjectManager.vue)
功能：
- 项目列表（卡片形式）
- 创建/编辑/删除项目
- 显示项目进度（已完成/总数）
- 项目状态：进行中/已完成/已归档

### 3. 更新任务创建弹窗
添加字段：
- 分类选择（下拉）
- 项目选择（下拉，可选）
- 截止日期（日期选择器）
- 优先级（低/普通/高/紧急）

### 4. 添加过期提示 (views/Tasks.vue)
功能：
- 已过期任务：红色背景 + 「已过期」标签
- 即将过期（3天内）：橙色背景 + 「即将过期」标签
- 过期任务置顶显示

### 5. 更新仪表盘 (views/Dashboard.vue)
添加：
- 「即将过期」卡片：显示3天内到期的任务
- 「项目进度」卡片：显示活跃项目的进度条

### 6. 创建 API (api/project.ts, api/taskCategory.ts)
```typescript
export interface Project {
  id: number
  name: string
  description: string
  status: string
  start_date?: string
  end_date?: string
  task_count: number
  completed_count: number
}

export interface TaskCategory {
  id: number
  name: string
  icon: string
  color: string
}
```

### 7. 更新侧边栏
添加菜单项：项目管理

### 8. 验收标准
- [ ] 切换 bug 已修复
- [ ] 项目 CRUD 正常
- [ ] 任务分类选择正常
- [ ] 过期提示显示正常
- [ ] 仪表盘显示即将过期任务和项目进度
