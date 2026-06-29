<template>
  <div class="task-list-page">
    <div class="page-header">
      <h2>任务列表</h2>
      <el-button type="primary" @click="openCreate">+ 新建任务</el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="store.filters">
        <el-form-item label="状态">
          <el-select v-model="store.filters.status" placeholder="全部" clearable @change="store.fetchTasks()">
            <el-option label="待办" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="store.filters.priority" placeholder="全部" clearable @change="store.fetchTasks()">
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="store.filters.category_id" placeholder="全部" clearable @change="store.fetchTasks()">
            <el-option v-for="c in store.categories" :key="c.id" :label="c.name" :value="String(c.id)" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="store.filters.keyword" placeholder="搜索标题/描述..." clearable @change="store.fetchTasks()" style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button @click="clearFilters">清空筛选</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 任务表格 -->
    <el-card shadow="never" style="margin-top: 16px">
      <el-table :data="store.tasks" v-loading="store.loading" stripe border>
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityType(row.priority)" effect="light" size="small">{{ priorityLabel(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.category" :style="{ color: row.category.color }">{{ row.category.icon || '' }} {{ row.category.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="截止日" width="120" align="center">
          <template #default="{ row }">{{ row.due_date || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button size="small" type="success" link @click="store.toggleStatus(row.id)">
              {{ row.status === 'completed' ? '撤销' : '完成' }}
            </el-button>
            <el-button size="small" type="primary" link @click="editTask(row)">编辑</el-button>
            <el-popconfirm title="确定删除此任务？" @confirm="store.deleteTask(row.id)">
              <template #reference>
                <el-button size="small" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="store.pagination.totalPages > 1"
        style="margin-top: 16px; justify-content: center"
        background
        layout="prev, pager, next"
        :total="store.pagination.total"
        :page-size="store.pagination.pageSize"
        :current-page="store.pagination.page"
        @current-change="store.setPage"
      />
    </el-card>

    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="showEditDialog" :title="editingTask ? '编辑任务' : '新建任务'" width="500px" @close="resetTaskForm" destroy-on-close>
      <el-form :model="taskForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="taskForm.title" placeholder="任务标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="任务描述" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="taskForm.category_id" placeholder="选择分类" style="width: 100%">
            <el-option v-for="c in store.categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="taskForm.priority" style="width: 100%">
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="taskForm.due_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="taskForm.tags" multiple filterable placeholder="输入后回车添加" style="width: 100%">
            <el-option v-for="t in store.tags" :key="t.id" :label="t.name" :value="t.name" />
          </el-select>
        </el-form-item>

        <!-- AI 智能推荐 -->
        <el-form-item v-if="!editingTask" label="AI 推荐">
          <div class="ai-recommend">
            <el-input
              v-model="aiInputTitle"
              placeholder="输入任务标题后自动分析..."
              @input="onTitleChange"
            />
            <el-alert
              v-if="aiStore.classifyResult"
              :title="'分类: ' + aiStore.classifyResult.category + ' | 优先级: ' + aiStore.classifyResult.priority"
              type="info"
              :closable="false"
              show-icon
              style="margin-top: 8px"
            >
              <template #default>
                <div style="font-size: 12px; color: #909399; margin-top: 4px">{{ aiStore.classifyResult.reason }}</div>
                <el-button size="small" type="primary" @click="applyAiRecommend" style="margin-top: 8px">采纳</el-button>
                <el-button size="small" @click="aiStore.clearResult">忽略</el-button>
              </template>
            </el-alert>
            <el-spin v-else-if="aiStore.isClassifying">AI 分析中...</el-spin>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useTasksStore } from '@/stores/tasks'
import { useAiStore } from '@/stores/ai'
import { getCategories as fetchCategories } from '@/api/categories'

const store = useTasksStore()
const aiStore = useAiStore()
const showEditDialog = ref(false)
const editingTask = ref(false)
const aiInputTitle = ref('')

function openCreate() {
  editingTask.value = false
  Object.keys(taskForm).forEach(k => delete taskForm[k])
  taskForm.priority = 'medium'
  taskForm.status = 'pending'
  aiStore.clearResult()
  showEditDialog.value = true
}

const taskForm = reactive<Record<string, any>>({
  id: undefined,
  title: '',
  description: '',
  category_id: '',
  priority: 'medium',
  due_date: '',
  tags: [] as string[],
  status: 'pending',
})

function statusType(status: string) {
  const map: Record<string, string> = { pending: 'info', in_progress: 'warning', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}
function statusLabel(status: string) {
  const map: Record<string, string> = { pending: '待办', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}
function priorityType(p: string) {
  const map: Record<string, string> = { urgent: 'danger', high: 'warning', medium: '', low: 'info' }
  return map[p] || ''
}
function priorityLabel(p: string) {
  const map: Record<string, string> = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return map[p] || p
}

function editTask(row: any) {
  editingTask.value = true
  Object.assign(taskForm, {
    id: row.id,
    title: row.title,
    description: row.description || '',
    category_id: String(row.category_id),
    priority: row.priority,
    due_date: row.due_date || '',
    tags: row.tags || [],
    status: row.status,
  })
  showEditDialog.value = true
}

function resetTaskForm() {
  Object.keys(taskForm).forEach(k => delete taskForm[k])
  aiStore.clearResult()
  aiInputTitle.value = ''
  editingTask.value = false
}

async function saveTask() {
  if (!taskForm.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  try {
    if (editingTask.value) {
      await store.updateTask(taskForm.id, {
        title: taskForm.title,
        description: taskForm.description,
        category_id: Number(taskForm.category_id),
        priority: taskForm.priority,
        due_date: taskForm.due_date || undefined,
        tags: taskForm.tags,
        status: taskForm.status,
      })
      ElMessage.success('更新成功')
    } else {
      await store.createTask({
        title: taskForm.title,
        description: taskForm.description || undefined,
        category_id: Number(taskForm.category_id),
        due_date: taskForm.due_date || undefined,
        tags: taskForm.tags,
      })
      ElMessage.success('创建成功')
    }
    showEditDialog.value = false
    resetTaskForm()
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  }
}

function clearFilters() {
  store.filters.status = ''
  store.filters.priority = ''
  store.filters.category_id = ''
  store.filters.keyword = ''
  store.fetchTasks()
}

// AI 智能推荐
let classifyTimer: ReturnType<typeof setTimeout> | null = null
async function onTitleChange() {
  const title = aiInputTitle.value.trim()
  if (!title) {
    aiStore.clearResult()
    return
  }
  // 同步到标题输入框
  taskForm.title = title
  if (classifyTimer) clearTimeout(classifyTimer)
  classifyTimer = setTimeout(async () => {
    await aiStore.classify(title, taskForm.description)
  }, 500)
}

function applyAiRecommend() {
  if (!aiStore.classifyResult) return
  const result = aiStore.classifyResult!
  // 分类名映射（兼容中英文）
  const nameMap: Record<string, string> = {
    '工作': '工作', '学习': '学习', '生活': '生活', '健身': '健身', '其他': '其他',
    'work': '工作', 'study': '学习', 'life': '生活', 'fitness': '健身', 'other': '其他',
  }
  const mappedName = nameMap[result.category] || result.category
  const cat = store.categories.find(c => c.name === mappedName || c.name.toLowerCase() === mappedName.toLowerCase())
  if (cat) taskForm.category_id = String(cat.id)
  // 优先级映射：英文 → 中文
  const priorityMap: Record<string, string> = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  taskForm.priority = priorityMap[result.priority] || result.priority
}

onMounted(async () => {
  await Promise.all([store.fetchTasks(), store.fetchCategories()])
})
</script>

<style scoped>
.task-list-page h2 { margin: 0 0 16px; font-size: 20px; color: #303133; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.filter-card :deep(.el-form-item) { margin-bottom: 0; }
.ai-recommend { width: 100%; }
</style>
