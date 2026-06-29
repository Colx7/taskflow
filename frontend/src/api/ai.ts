import request from '@/utils/request'

export interface ClassifyResult {
  category: string
  priority: string
  reason: string
  suggested_tags: string[]
}

// AI 智能分类
export const classifyTask = (title: string, description?: string) => {
  return request.post('/ai/classify', { title, description }) as Promise<ClassifyResult>
}
