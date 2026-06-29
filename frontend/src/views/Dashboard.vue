<template>
  <div class="dashboard" v-loading="statsStore.loading">
    <h2>仪表盘</h2>

    <!-- 统计卡片行 1 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ statsStore.dashboard?.total_tasks ?? 0 }}</div>
          <div class="stat-label">总任务</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-pending">
          <div class="stat-value">{{ statsStore.dashboard?.pending_count ?? 0 }}</div>
          <div class="stat-label">待办</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-progress">
          <div class="stat-value">{{ statsStore.dashboard?.in_progress_count ?? 0 }}</div>
          <div class="stat-label">进行中</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-done">
          <div class="stat-value">{{ statsStore.dashboard?.completed_count ?? 0 }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-overdue">
          <div class="stat-value" :style="{ color: statsStore.dashboard?.overdue_count ? '#F56C6C' : '' }">
            {{ statsStore.dashboard?.overdue_count ?? 0 }}
          </div>
          <div class="stat-label">逾期</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-today">
          <div class="stat-value">{{ statsStore.dashboard?.today_completed ?? 0 }}</div>
          <div class="stat-label">今日完成</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：最近活动 + 趋势图 -->
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近活动</span>
            <span style="float: right; font-size: 12px; color: #909399">
              本周完成 {{ statsStore.dashboard?.this_week_completed ?? 0 }}
            </span>
          </template>
          <el-empty v-if="!statsStore.dashboard?.recent_activity?.length" description="暂无活动" :image-size="80" />
          <div v-for="a in (statsStore.dashboard?.recent_activity ?? [])" :key="a.time" class="recent-activity">
            <el-tag :type="activityTagType(a.action)" size="small" effect="light">{{ activityLabel(a.action) }}</el-tag>
            <span class="activity-title">{{ a.task_title }}</span>
            <span class="activity-time">{{ formatTime(a.time) }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>任务趋势（近7天完成）</template>
          <div ref="trendChartRef" style="width: 100%; height: 280px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：分类分布 -->
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="24">
        <el-card>
          <template #header>分类分布</template>
          <div ref="pieChartRef" style="width: 100%; height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useStatsStore } from '@/stores/stats'

const statsStore = useStatsStore()
const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()

function activityTagType(action: string) {
  const map: Record<string, string> = { pending: 'info', in_progress: 'warning', completed: 'success', cancelled: 'danger' }
  return map[action] || 'info'
}

function activityLabel(action: string) {
  const map: Record<string, string> = { pending: '待办', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[action] || action
}

function formatTime(timeStr: string) {
  if (!timeStr) return ''
  // 后端返回 ISO 字符串不含时区标识，Chrome 会按 UTC 解析
  // 强制按本地时区解析：去掉 T 换成空格
  const localStr = timeStr.replace('T', ' ')
  const d = new Date(localStr)
  const now = new Date()
  if (isNaN(d.getTime())) return timeStr.slice(0, 16)
  const diffMs = now.getTime() - d.getTime()
  const diffMins = Math.abs(Math.floor(diffMs / 60000))
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}小时前`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}天前`
  return d.toLocaleDateString('zh-CN')
}

function initTrendChart() {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)
  const trend = statsStore.trend
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: trend?.labels ?? [],
      axisLabel: { fontSize: 11 },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      name: '完成任务',
      type: 'line',
      smooth: true,
      data: trend?.values ?? [],
      areaStyle: { opacity: 0.3 },
      itemStyle: { color: '#409EFF' },
    }],
  })
  return chart
}

function initPieChart() {
  if (!pieChartRef.value) return
  const chart = echarts.init(pieChartRef.value)
  const items = statsStore.categoryDist ?? []
  const data = items.map(i => ({
    name: i.name,
    value: i.completed + i.pending + i.in_progress,
  })).filter(d => d.value > 0)

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      name: '任务分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['55%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' },
      },
      data: data.length ? data : [{ name: '无数据', value: 0 }],
    }],
  })
  return chart
}

let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

onMounted(async () => {
  await statsStore.fetchAll()
  await nextTick()
  trendChart = initTrendChart()
  pieChart = initPieChart()
})
</script>

<style scoped>
.dashboard h2 { margin: 0 0 20px; font-size: 20px; color: #303133; }
.stat-cards { margin-bottom: 16px; }
.stat-card { text-align: center; padding: 10px 0; }
.stat-value { font-size: 32px; font-weight: bold; color: #303133; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.recent-activity { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #ebeef5; gap: 8px; }
.recent-activity:last-child { border-bottom: none; }
.activity-title { flex: 1; font-size: 14px; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.activity-time { font-size: 12px; color: #c0c4cc; white-space: nowrap; }
.stat-overdue .stat-value { transition: color 0.3s; }
</style>
