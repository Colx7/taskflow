import request from '@/utils/request'

export interface TaskItem {
  id: number
  title: string
  description?: string
  status: string
  priority: string
  category_id: number
  user_id: number
  due_date?: string
  tags?: string[]
  ai_suggestion?: Record<string, any>
  category?: { id: number; name: string; icon?: string; color?: string; sort_order: number }
  created_at?: string
  updated_at?: string
}

export interface TaskListResponse {
  items: TaskItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CreateTaskPayload {
  title: string
  description?: string
  category_id: number
  due_date?: string
  tags?: string[]
}

export interface UpdateTaskPayload {
  title?: string
  description?: string
  status?: string
  priority?: string
  category_id?: number
  due_date?: string
  tags?: string[]
}

// 获取任务列表
export const getTasks = (params: Record<string, any>) => {
  return request.get('/tasks', { params }) as Promise<TaskListResponse>
}

// 创建任务
export const createTask = (data: CreateTaskPayload) => {
  return request.post('/tasks', data) as Promise<TaskItem>
}

// 获取任务详情
export const getTask = (id: number) => {
  return request.get(`/tasks/${id}`) as Promise<TaskItem>
}

// 更新任务
export const updateTask = (id: number, data: UpdateTaskPayload) => {
  return request.put(`/tasks/${id}`, data) as Promise<TaskItem>
}

// 删除任务
export const deleteTask = (id: number) => {
  return request.delete(`/tasks/${id}`)
}

// 批量更新状态
export const batchUpdateStatus = (task_ids: number[], status: string) => {
  return request.patch('/tasks/batch-status', { task_ids, status })
}
