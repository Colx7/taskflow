import { defineStore } from 'pinia'
import { ref } from 'vue'
import { generateWeeklyReport } from '@/api/weeklyReport'
import type { WeeklyReportSummary } from '@/api/weeklyReport'

export const useWeeklyReportStore = defineStore('weeklyReport', () => {
  const report = ref('')
  const summary = ref<WeeklyReportSummary | null>(null)
  const loading = ref(false)
  const generating = ref(false)

  async function generate(startDate: string, endDate: string) {
    loading.value = true
    generating.value = true
    try {
      const res = await generateWeeklyReport(startDate, endDate)
      report.value = res.report
      summary.value = res.summary
    } finally {
      loading.value = false
      generating.value = false
    }
  }

  function clearReport() {
    report.value = ''
    summary.value = null
  }

  return { report, summary, loading, generating, generate, clearReport }
})
