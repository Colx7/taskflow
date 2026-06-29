import request from '@/utils/request'

export interface WeeklyReportSummary {
  total: number
  completed: number
  in_progress: number
  pending: number
  cancelled: number
}

export interface WeeklyReportResponse {
  report: string
  summary: WeeklyReportSummary
}

// 生成周报
export const generateWeeklyReport = (startDate: string, endDate: string) => {
  return request.post('/ai/weekly-report', { startDate, endDate }) as Promise<WeeklyReportResponse>
}
