import request from '@/utils/request'

export interface DashboardStats {
  total_tasks: number
  pending_count: number
  in_progress_count: number
  completed_count: number
  cancelled_count: number
  overdue_count: number
  today_completed: number
  this_week_completed: number
  by_priority: Record<string, number>
  recent_activity: Array<{
    task_title: string
    action: string
    time: string
  }>
}

export interface TrendData {
  labels: string[]
  values: number[]
}

export interface CategoryDistribution {
  name: string
  completed: number
  pending: number
  in_progress: number
}

export interface StatsCategoryDistribution {
  items: CategoryDistribution[]
}

// 仪表盘统计概览
export const getDashboardStats = () => {
  return request.get('/stats/dashboard') as Promise<DashboardStats>
}

// 趋势统计
export const getTrendStats = (period: string = 'week', field: string = 'completed') => {
  return request.get('/stats/trend', { params: { period, field } }) as Promise<TrendData>
}

// 分类分布
export const getCategoryDistribution = () => {
  return request.get('/stats/category-distribution') as Promise<StatsCategoryDistribution>
}
