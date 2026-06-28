<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
      <n-space>
        <n-select
          v-model:value="filters.status"
          :options="statusOptions"
          placeholder="状态筛选"
          clearable
          style="width: 130px"
          @update:value="fetchTasks"
        />
        <n-select
          v-model:value="filters.priority"
          :options="priorityOptions"
          placeholder="优先级筛选"
          clearable
          style="width: 130px"
          @update:value="fetchTasks"
        />
      </n-space>
      <n-button type="primary" size="small" @click="openCreate">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        新建任务
      </n-button>
    </div>

    <n-data-table
      :columns="columns"
      :data="tasks"
      :loading="loading"
      :row-key="(row) => row.id"
      :pagination="{ pageSize: 20 }"
    />

    <TaskModal
      v-model:show="showModal"
      :task="editingTask"
      :project-id="Number(route.params.id)"
      @saved="fetchTasks"
    />
  </div>
</template>

<script setup>
import { ref, h, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { NTag, NButton, NSpace, NPopconfirm, useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { taskApi } from '@/api'
import TaskModal from '@/components/TaskModal.vue'

const props = defineProps({ project: Object })
const emit = defineEmits(['refresh'])
const route = useRoute()
const message = useMessage()
const loading = ref(false)
const tasks = ref([])
const showModal = ref(false)
const editingTask = ref(null)

const filters = ref({ status: null, priority: null })

const statusOptions = [
  { label: '待办', value: 'todo' },
  { label: '进行中', value: 'in_progress' },
  { label: '测试中', value: 'testing' },
  { label: '已完成', value: 'done' },
]

const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' },
  { label: '高', value: 'high' },
  { label: '紧急', value: 'urgent' },
]

const statusMap = { todo: '待办', in_progress: '进行中', testing: '测试中', done: '已完成' }
const statusTagType = { todo: 'default', in_progress: 'warning', testing: 'info', done: 'success' }
const priorityMap = { low: '低', medium: '中', high: '高', urgent: '紧急' }
const priorityTagType = { low: 'default', medium: 'info', high: 'warning', urgent: 'error' }

const columns = [
  { title: '标题', key: 'title', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => h(NTag, { type: statusTagType[row.status], size: 'small' }, () => statusMap[row.status]),
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    render: (row) => h(NTag, { type: priorityTagType[row.priority], size: 'small' }, () => priorityMap[row.priority]),
  },
  {
    title: '负责人',
    key: 'assignee',
    width: 100,
    render: (row) => row.assignee?.nickname || row.assignee?.username || '-',
  },
  { title: '开始日期', key: 'start_date', width: 110, render: (row) => row.start_date || '-' },
  { title: '截止日期', key: 'end_date', width: 110, render: (row) => row.end_date || '-' },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    render: (row) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'tiny', onClick: () => editTask(row) }, () => '编辑'),
        h(
          NPopconfirm,
          { onPositiveClick: () => deleteTask(row.id) },
          {
            trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
            default: () => '确定删除？',
          }
        ),
      ]),
  },
]

function openCreate() {
  editingTask.value = null
  showModal.value = true
}

function editTask(task) {
  editingTask.value = task
  showModal.value = true
}

async function deleteTask(id) {
  await taskApi.delete(id)
  message.success('已删除')
  fetchTasks()
}

async function fetchTasks() {
  loading.value = true
  try {
    const params = { project_id: route.params.id }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    tasks.value = await taskApi.list(params)
    emit('refresh')
  } finally {
    loading.value = false
  }
}

onMounted(fetchTasks)
</script>
