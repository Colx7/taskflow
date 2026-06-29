import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getTasks, createTask as createTaskApi, updateTask as updateTaskApi, deleteTask as deleteTaskApi, batchUpdateStatus as batchApi } from '@/api/tasks'
import { getCategories as apiGetCategories } from '@/api/categories'
import type { TaskItem, CreateTaskPayload, UpdateTaskPayload } from '@/api/tasks'

export interface TaskFilters {
  status: string
  priority: string
  category_id: string
  keyword: string
  sort_by: string
  sort_order: string
}

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<TaskItem[]>([])
  const pagination = ref({ page: 1, pageSize: 20, total: 0, totalPages: 0 })
  const filters = ref<TaskFilters>({
    status: '', priority: '', category_id: '', keyword: '', sort_by: 'created_at', sort_order: 'desc',
  })
  const selectedIds = ref<number[]>([])
  const loading = ref(false)
  const categories = ref<Array<{ id: number; name: string; icon?: string; color?: string; sort_order: number }>>([])

  async function fetchTasks() {
    loading.value = true
    try {
      const params: Record<string, any> = {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        sort_by: filters.value.sort_by,
        sort_order: filters.value.sort_order,
      }
      if (filters.value.status) params.status = filters.value.status
      if (filters.value.priority) params.priority = filters.value.priority
      if (filters.value.category_id) params.category_id = Number(filters.value.category_id)
      if (filters.value.keyword) params.keyword = filters.value.keyword

      const res = await getTasks(params)
      tasks.value = res.items
      pagination.value = { page: res.page, pageSize: res.page_size, total: res.total, totalPages: res.total_pages }
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    try {
      const res = await apiGetCategories()
      categories.value = res
    } catch {
      categories.value = []
    }
  }

  async function createTask(data: CreateTaskPayload) {
    await createTaskApi(data)
    await fetchTasks()
  }

  async function updateTask(id: number, data: UpdateTaskPayload) {
    await updateTaskApi(id, data)
    await fetchTasks()
  }

  async function deleteTask(id: number) {
    await deleteTaskApi(id)
    await fetchTasks()
  }

  async function toggleStatus(id: number) {
    const task = tasks.value.find(t => t.id === id)
    const newStatus = task?.status === 'pending' ? 'completed' : 'pending'
    await updateTask(id, { status: newStatus })
  }

  async function batchToggleStatus(ids: number[]) {
    await batchApi(ids, 'completed')
    await fetchTasks()
  }

  function clearSelection() {
    selectedIds.value = []
  }

  function setPage(page: number) {
    pagination.value.page = page
    fetchTasks()
  }

  return {
    tasks, categories, pagination, filters, selectedIds, loading,
    fetchTasks, fetchCategories, createTask, updateTask, deleteTask,
    toggleStatus, batchToggleStatus, clearSelection, setPage,
  }
})
