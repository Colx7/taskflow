import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDashboardStats, getTrendStats, getCategoryDistribution } from '@/api/stats'
import type { DashboardStats, TrendData, CategoryDistribution as CatDist } from '@/api/stats'

export const useStatsStore = defineStore('stats', () => {
  const dashboard = ref<DashboardStats | null>(null)
  const trend = ref<TrendData | null>(null)
  const categoryDist = ref<CatDist[]>([])
  const loading = ref(false)

  async function fetchDashboard() {
    loading.value = true
    try {
      dashboard.value = await getDashboardStats()
    } finally {
      loading.value = false
    }
  }

  async function fetchTrend(period = 'week', field = 'completed') {
    trend.value = await getTrendStats(period, field)
  }

  async function fetchCategoryDist() {
    const res = await getCategoryDistribution()
    categoryDist.value = res.items
  }

  async function fetchAll() {
    loading.value = true
    try {
      await Promise.all([fetchDashboard(), fetchTrend('week', 'completed'), fetchCategoryDist()])
    } finally {
      loading.value = false
    }
  }

  return { dashboard, trend, categoryDist, loading, fetchDashboard, fetchTrend, fetchCategoryDist, fetchAll }
})
