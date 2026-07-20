## 目标
实现 GitHub 风格的热力图组件，显示每天已完成任务数量。

## 前置任务
依赖 T25 完成

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 创建热力图组件 (components/TaskHeatmap.vue)
功能要求：
- GitHub 风格的热力图（52列 x 7行）
- 颜色方案：GitHub 绿色（#ebedf0, #9be9a8, #40c463, #30a14e, #216e39）
- 0个任务：灰色（#ebedf0）
- 1-2个任务：浅绿（#9be9a8）
- 3-4个任务：中绿（#40c463）
- 5-6个任务：深绿（#30a14e）
- 7个以上：最深绿（#216e39）
- 悬停显示 tooltip：日期 + 完成数量
- 显示月份标签（1月, 2月, ...）
- 显示星期标签（日, 一, 二, 三, 四, 五, 六）

### 2. 创建 API (api/dashboard.ts)
```typescript
export interface HeatmapData {
  start_date: string
  end_date: string
  data: Record<string, number>
}

export const dashboardApi = {
  // ... 现有方法
  getHeatmap: (days?: number) => api.get<HeatmapData>('/api/dashboard/heatmap', { params: { days } }),
}
```

### 3. 更新仪表盘 (views/Dashboard.vue)
- 在统计卡片下方添加热力图卡片
- 标题：📅 任务完成热力图

### 4. 更新任务管理页面 (views/Tasks.vue)
- 在页面顶部添加热力图卡片
- 标题：📅 任务完成热力图

### 5. 样式要求
- 热力图格子大小：12x12px
- 格子间距：3px
- 圆角：2px
- tooltip 样式：深色背景，白色文字

### 6. 验收标准
- [ ] 热力图显示正常（52列 x 7行）
- [ ] 颜色根据数量变化
- [ ] 悬停显示 tooltip
- [ ] 月份标签正确
- [ ] 星期标签正确
- [ ] 仪表盘和任务管理页面都有显示
