import { defineStore } from 'pinia'
import { ref } from 'vue'
import { classifyTask } from '@/api/ai'
import type { ClassifyResult } from '@/api/ai'

export const useAiStore = defineStore('ai', () => {
  const classifyResult = ref<ClassifyResult | null>(null)
  const isClassifying = ref(false)

  async function classify(title: string, description?: string) {
    isClassifying.value = true
    try {
      classifyResult.value = await classifyTask(title, description)
      return classifyResult.value
    } finally {
      isClassifying.value = false
    }
  }

  function clearResult() {
    classifyResult.value = null
  }

  return { classifyResult, isClassifying, classify, clearResult }
})
