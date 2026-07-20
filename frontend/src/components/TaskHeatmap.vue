<template>
  <div class="heatmap-container">
    <div class="heatmap-wrapper">
      <!-- 星期标签 -->
      <div class="weekday-labels">
        <span v-for="(label, i) in weekdayLabels" :key="i" class="weekday-label">{{ label }}</span>
      </div>

      <!-- 热力图主体 -->
      <div class="heatmap-body">
        <!-- 月份标签 -->
        <div class="month-labels">
          <span
            v-for="(month, i) in monthLabels"
            :key="i"
            class="month-label"
            :style="{ left: month.left + 'px' }"
          >{{ month.label }}</span>
        </div>

        <!-- 格子 -->
        <div class="heatmap-grid" ref="gridRef">
          <div
            v-for="(week, wi) in weeks"
            :key="wi"
            class="heatmap-week"
          >
            <div
              v-for="(day, di) in week"
              :key="di"
              class="heatmap-cell"
              :style="{ backgroundColor: getColor(day.count) }"
              @mouseenter="(e) => showTooltip(e, day)"
              @mouseleave="hideTooltip"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="heatmap-legend">
      <span class="legend-label">少</span>
      <div
        v-for="(color, i) in legendColors"
        :key="i"
        class="legend-cell"
        :style="{ backgroundColor: color }"
      />
      <span class="legend-label">多</span>
    </div>

    <!-- Tooltip -->
    <Teleport to="body">
      <div
        v-if="tooltip.visible"
        class="heatmap-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      >
        <div class="tooltip-date">{{ tooltip.date }}</div>
        <div class="tooltip-count">{{ tooltip.count }} 个任务完成</div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface DayData {
  date: string
  count: number
}

interface Props {
  data?: Record<string, number>
  startDate?: string
  endDate?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => ({}),
  startDate: '',
  endDate: ''
})

const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  date: '',
  count: 0
})

const colorScale = [
  '#ebedf0', // 0
  '#9be9a8', // 1-2
  '#40c463', // 3-4
  '#30a14e', // 5-6
  '#216e39'  // 7+
]

const legendColors = colorScale

function getColor(count: number): string {
  if (count <= 0) return colorScale[0]
  if (count <= 2) return colorScale[1]
  if (count <= 4) return colorScale[2]
  if (count <= 6) return colorScale[3]
  return colorScale[4]
}

// 计算日期范围
const dateRange = computed(() => {
  const end = props.endDate ? new Date(props.endDate) : new Date()
  const start = props.startDate
    ? new Date(props.startDate)
    : new Date(end.getTime() - 364 * 24 * 60 * 60 * 1000)

  // 调整到周日开始
  const startDay = start.getDay()
  const adjustedStart = new Date(start)
  adjustedStart.setDate(adjustedStart.getDate() - startDay)

  return { start: adjustedStart, end }
})

// 生成网格数据（52列 x 7行）
const weeks = computed(() => {
  const result: DayData[][] = []
  const { start } = dateRange.value
  const data = props.data || {}

  let current = new Date(start)

  for (let w = 0; w < 53; w++) {
    const week: DayData[] = []
    for (let d = 0; d < 7; d++) {
      const dateStr = formatDate(current)
      week.push({
        date: dateStr,
        count: data[dateStr] || 0
      })
      current.setDate(current.getDate() + 1)
    }
    result.push(week)
  }

  return result
})

// 星期标签
const weekdayLabels = computed(() => ['', '一', '', '三', '', '五', ''])

// 月份标签
const monthLabels = computed(() => {
  const labels: { label: string; left: number }[] = []
  const { start } = dateRange.value
  let current = new Date(start)
  let lastMonth = -1

  for (let w = 0; w < 53; w++) {
    const month = current.getMonth()
    if (month !== lastMonth) {
      const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
      labels.push({
        label: monthNames[month],
        left: w * 15 // 12px cell + 3px gap
      })
      lastMonth = month
    }
    current.setDate(current.getDate() + 7)
  }

  return labels
})

function formatDate(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatDisplayDate(dateStr: string): string {
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = d.getMonth() + 1
  const day = d.getDate()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${y}年${m}月${day}日 星期${weekdays[d.getDay()]}`
}

function showTooltip(e: MouseEvent, day: DayData) {
  const rect = (e.target as HTMLElement).getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: rect.left + rect.width / 2,
    y: rect.top - 10,
    date: formatDisplayDate(day.date),
    count: day.count
  }
}

function hideTooltip() {
  tooltip.value.visible = false
}
</script>

<style scoped>
.heatmap-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.heatmap-wrapper {
  display: flex;
  gap: 8px;
}

.weekday-labels {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding-top: 22px; /* 为月份标签留空间 */
}

.weekday-label {
  width: 20px;
  height: 12px;
  line-height: 12px;
  font-size: 11px;
  color: #909399;
  text-align: right;
}

.heatmap-body {
  position: relative;
  overflow-x: auto;
}

.month-labels {
  position: relative;
  height: 20px;
}

.month-label {
  position: absolute;
  font-size: 11px;
  color: #909399;
}

.heatmap-grid {
  display: flex;
  gap: 3px;
  margin-top: 2px;
}

.heatmap-week {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.heatmap-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  cursor: pointer;
  transition: outline 0.1s;
  outline: 1px solid rgba(0, 0, 0, 0.06);
}

.heatmap-cell:hover {
  outline: 2px solid #606266;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
}

.legend-label {
  font-size: 11px;
  color: #909399;
}

.legend-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  outline: 1px solid rgba(0, 0, 0, 0.06);
}

.heatmap-tooltip {
  position: fixed;
  z-index: 9999;
  transform: translate(-50%, -100%);
  background: #303133;
  color: #fff;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.heatmap-tooltip::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #303133;
}

.tooltip-date {
  font-weight: 500;
  margin-bottom: 2px;
}

.tooltip-count {
  color: #e4e7ed;
}
</style>
