<template>
  <div class="weekly-report">
    <h2>AI 周报</h2>

    <!-- 日期选择和生成按钮 -->
    <el-card shadow="never" style="margin-bottom: 16px">
      <el-form :inline="true">
        <el-form-item label="起始日期">
          <el-date-picker
            v-model="startDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="endDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleGenerate" :loading="weeklyReportStore.generating" :disabled="!startDate || !endDate">
            生成周报
          </el-button>
          <el-button @click="copyReport" :disabled="!weeklyReportStore.report">复制周报</el-button>
          <el-button @click="weeklyReportStore.clearReport">清空</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计摘要 -->
    <el-row :gutter="16" class="summary-cards" v-if="weeklyReportStore.summary">
      <el-col :span="4">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value">{{ weeklyReportStore.summary.total }}</div>
          <div class="summary-label">总任务</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="summary-card summary-done">
          <div class="summary-value">{{ weeklyReportStore.summary.completed }}</div>
          <div class="summary-label">已完成</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="summary-card summary-progress">
          <div class="summary-value">{{ weeklyReportStore.summary.in_progress }}</div>
          <div class="summary-label">进行中</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="summary-card summary-pending">
          <div class="summary-value">{{ weeklyReportStore.summary.pending }}</div>
          <div class="summary-label">待办</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="summary-card summary-cancelled">
          <div class="summary-value">{{ weeklyReportStore.summary.cancelled }}</div>
          <div class="summary-label">已取消</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="summary-card summary-rate">
          <div class="summary-value">{{ completionRate }}%</div>
          <div class="summary-label">完成率</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 周报内容 -->
    <el-card shadow="never" v-loading="weeklyReportStore.loading">
      <div v-if="weeklyReportStore.report" class="report-content" v-html="renderedReport"></div>
      <el-empty v-else description="选择日期范围后点击生成周报" :image-size="120" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { useWeeklyReportStore } from '@/stores/weeklyReport'

const weeklyReportStore = useWeeklyReportStore()
const startDate = ref('')
const endDate = ref('')

// 默认设为上一周
onMounted(() => {
  const now = new Date()
  const dayOfWeek = now.getDay() || 7
  const monday = new Date(now)
  monday.setDate(now.getDate() - dayOfWeek + 1 - 7)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  startDate.value = formatDate(monday)
  endDate.value = formatDate(sunday)
})

function formatDate(d: Date): string {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const completionRate = computed(() => {
  if (!weeklyReportStore.summary) return 0
  const total = weeklyReportStore.summary.completed + weeklyReportStore.summary.in_progress + weeklyReportStore.summary.pending + weeklyReportStore.summary.cancelled
  if (total === 0) return 0
  return Math.round((weeklyReportStore.summary.completed / total) * 100)
})

async function handleGenerate() {
  if (!startDate.value || !endDate.value) {
    ElMessage.warning('请选择日期范围')
    return
  }
  if (startDate.value > endDate.value) {
    ElMessage.warning('起始日期不能晚于截止日期')
    return
  }
  await weeklyReportStore.generate(startDate.value, endDate.value)
  if (weeklyReportStore.report) {
    ElMessage.success('周报生成成功')
  }
}

async function copyReport() {
  if (!weeklyReportStore.report) return
  try {
    await navigator.clipboard.writeText(weeklyReportStore.report)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 将 Markdown 渲染为 HTML
const renderedReport = computed(() => {
  if (!weeklyReportStore.report) return ''
  try {
    return marked.parse(weeklyReportStore.report)
  } catch {
    return weeklyReportStore.report.replace(/\n/g, '<br>')
  }
})
</script>

<style scoped>
.weekly-report h2 { margin: 0 0 20px; font-size: 20px; color: #303133; }
.summary-cards { margin-bottom: 16px; }
.summary-card { text-align: center; padding: 10px 0; }
.summary-value { font-size: 28px; font-weight: bold; color: #303133; }
.summary-label { font-size: 13px; color: #909399; margin-top: 4px; }
.summary-done .summary-value { color: #67C23A; }
.summary-progress .summary-value { color: #E6A23C; }
.summary-pending .summary-value { color: #909399; }
.summary-cancelled .summary-value { color: #F56C6C; }
.summary-rate .summary-value { color: #409EFF; }
.report-content { line-height: 1.8; color: #303133; }
.report-content h1 { font-size: 22px; border-bottom: 2px solid #409EFF; padding-bottom: 8px; margin: 0 0 16px; }
.report-content h2 { font-size: 18px; color: #409EFF; margin: 20px 0 12px; }
.report-content h3 { font-size: 16px; margin: 16px 0 8px; }
.report-content ul, .report-content ol { padding-left: 20px; }
.report-content li { margin: 4px 0; }
.report-content p { margin: 8px 0; }
.report-content strong { color: #303133; }
</style>
