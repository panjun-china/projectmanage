<template>
  <div>
    <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
      <n-button type="primary" size="small" @click="openCreate()">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        新建任务
      </n-button>
    </div>

    <div class="kanban-board">
      <div v-for="col in columns" :key="col.key" class="kanban-column">
        <div class="kanban-column-header" :style="{ borderTopColor: col.color }">
          <span>{{ col.label }}</span>
          <n-badge :value="getColumnTasks(col.key).length" :max="99" />
        </div>
        <div
          class="kanban-column-body"
          @dragover.prevent
          @drop="handleDrop($event, col.key)"
        >
          <div
            v-for="task in getColumnTasks(col.key)"
            :key="task.id"
            class="kanban-card"
            draggable="true"
            @dragstart="handleDragStart($event, task)"
            @click="editTask(task)"
          >
            <div class="kanban-card-title">{{ task.title }}</div>
            <div class="kanban-card-meta">
              <n-tag :type="priorityTagType(task.priority)" size="tiny">
                {{ priorityLabel(task.priority) }}
              </n-tag>
              <span v-if="task.assignee" class="assignee">
                {{ task.assignee.nickname || task.assignee.username }}
              </span>
            </div>
            <div v-if="task.end_date" class="kanban-card-date">
              {{ task.end_date }}
            </div>
          </div>
          <div v-if="!getColumnTasks(col.key).length" class="kanban-empty">
            暂无任务
          </div>
        </div>
      </div>
    </div>

    <TaskModal
      v-model:show="showModal"
      :task="editingTask"
      :project-id="Number(route.params.id)"
      :default-status="defaultStatus"
      @saved="fetchTasks"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { taskApi } from '@/api'
import TaskModal from '@/components/TaskModal.vue'

const props = defineProps({ project: Object })
const emit = defineEmits(['refresh'])
const route = useRoute()
const message = useMessage()

const tasks = ref([])
const showModal = ref(false)
const editingTask = ref(null)
const defaultStatus = ref('todo')
let draggedTask = null

const columns = [
  { key: 'todo', label: '待办', color: '#909399' },
  { key: 'in_progress', label: '进行中', color: '#e6a23c' },
  { key: 'testing', label: '测试中', color: '#409eff' },
  { key: 'done', label: '已完成', color: '#67c23a' },
]

function getColumnTasks(status) {
  return tasks.value.filter((t) => t.status === status)
}

function priorityTagType(p) {
  return { low: 'default', medium: 'info', high: 'warning', urgent: 'error' }[p] || 'default'
}

function priorityLabel(p) {
  return { low: '低', medium: '中', high: '高', urgent: '紧急' }[p] || p
}

function openCreate(status = 'todo') {
  editingTask.value = null
  defaultStatus.value = status
  showModal.value = true
}

function editTask(task) {
  editingTask.value = task
  showModal.value = true
}

function handleDragStart(e, task) {
  draggedTask = task
  e.dataTransfer.effectAllowed = 'move'
}

async function handleDrop(e, newStatus) {
  if (!draggedTask || draggedTask.status === newStatus) return
  try {
    await taskApi.updateStatus(draggedTask.id, newStatus)
    draggedTask.status = newStatus
    emit('refresh')
  } catch (err) {
    message.error('状态更新失败')
  }
  draggedTask = null
}

async function fetchTasks() {
  tasks.value = await taskApi.list({ project_id: route.params.id })
  emit('refresh')
}

onMounted(fetchTasks)
</script>

<style scoped>
.kanban-board {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 16px;
}

.kanban-column {
  flex: 1;
  min-width: 260px;
  background: #f5f7f9;
  border-radius: 8px;
  border-top: 3px solid #ddd;
}

.kanban-column-header {
  padding: 12px 16px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kanban-column-body {
  padding: 8px;
  min-height: 200px;
}

.kanban-card {
  background: #fff;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s;
}

.kanban-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.kanban-card-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.kanban-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.assignee {
  color: #666;
}

.kanban-card-date {
  margin-top: 6px;
  font-size: 12px;
  color: #999;
}

.kanban-empty {
  text-align: center;
  padding: 40px 0;
  color: #ccc;
  font-size: 13px;
}
</style>
