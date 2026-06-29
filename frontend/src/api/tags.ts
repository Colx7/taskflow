import request from '@/utils/request'

// 获取标签列表
export const getTags = () => {
  return request.get('/tags')
}

// 创建标签
export const createTag = (data: { name: string; color?: string }) => {
  return request.post('/tags', data)
}

// 删除标签
export const deleteTag = (id: number) => {
  return request.delete(`/tags/${id}`)
}
