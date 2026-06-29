import request from '@/utils/request'

// 获取分类列表
export const getCategories = () => {
  return request.get('/categories')
}

// 创建分类
export const createCategory = (data: { name: string; icon?: string; color?: string; sort_order?: number }) => {
  return request.post('/categories', data)
}

// 更新分类
export const updateCategory = (id: number, data: Record<string, any>) => {
  return request.put(`/categories/${id}`, data)
}

// 删除分类
export const deleteCategory = (id: number) => {
  return request.delete(`/categories/${id}`)
}
