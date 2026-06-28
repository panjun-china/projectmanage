<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
      <n-space>
        <n-button-group size="small">
          <n-button :type="viewMode === 'day' ? 'primary' : 'default'" @click="viewMode = 'day'">日</n-button>
          <n-button :type="viewMode === 'week' ? 'primary' : 'default'" @click="viewMode = 'week'">周</n-button>
          <n-button :type="viewMode === 'month' ? 'primary' : 'default'" @click="viewMode = 'month'">月</n-button>
        </n-button-group>
      </n-space>
      <n-button type="primary" size="small" @click="showModal = true">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        新建任务
      </n-button>
    </div>

    <n-alert v-if="tasksWithoutDates.length" type="warning" style="margin-bottom: 12px">
      有 {{ tasksWithoutDates.length }} 个任务未设置日期范围，无法在甘特图中显示。
    </n-alert>

    <div class="gantt-container" v-if="ganttTasks.length">
      <div class="gantt-table">
        <div class="gantt-header-row">
          <div class="gantt-task-info gantt-header-cell">任务名称</div>
          <div class="gantt-timeline-header">
            <div v-for="date in dateHeaders" :key="date" class="gantt-date-cell" :style="{ width: cellWidth + 'px' }">
              {{ date }}
            </div>
          </div>
        </div>
        <div v-for="task in ganttTasks" :key="task.id" class="gantt-row" @click="editTask(task)">
          <div class="gantt-task-info">
            <span class="gantt-task-name">{{ task.title }}</span>
            <n-tag :type="priorityTagType(task.priority)" size="tiny">{{ priorityLabel(task.priority) }}</n-tag>
          </div>
          <div class="gantt-timeline">
            <div
              class="gantt-bar"
              :style="getBarStyle(task)"
              :class="'gantt-bar-' + task.status"
            >
              <span class="gantt-bar-label">{{ task.assignee?.nickname || '' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <n-empty v-else description="暂无设置日期的任务" />

    <TaskModal
      v-model:show="showModal"
      :task="editingTask"
      :project-id="Number(route.params.id)"
      @saved="fetchTasks"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { AddOutline } from '@vicons/ionicons5'
import { taskApi } from '@/api'
import dayjs from 'dayjs'
import TaskModal from '@/components/TaskModal.vue'

const props = defineProps({ project: Object })
const emit = defineEmits(['refresh'])
const route = useRoute()

const tasks = ref([])
const showModal = ref(false)
const editingTask = ref(null)
const viewMode = ref('day')

const cellWidth = computed(() => {
  return { day: 40, week: 60, month: 80 }[viewMode.value]
})

const ganttTasks = computed(() => tasks.value.filter((t) => t.start_date && t.end_date))
const tasksWithoutDates = computed(() => tasks.value.filter((t) => !t.start_date || !t.end_date))

const dateRange = computed(() => {
  if (!ganttTasks.value.length) return { start: dayjs(), end: dayjs() }
  let start = dayjs(ganttTasks.value[0].start_date)
  let end = dayjs(ganttTasks.value[0].end_date)
  ganttTasks.value.forEach((t) => {
    const s = dayjs(t.start_date)
    const e = dayjs(t.end_date)
    if (s.isBefore(start)) start = s
    if (e.isAfter(end)) end = e
  })
  return { start: start.subtract(1, 'day'), end: end.add(1, 'day') }
})

const dateHeaders = computed(() => {
  const headers = []
  let current = dateRange.value.start
  const end = dateRange.value.end
  while (current.isBefore(end) || current.isSame(end)) {
    if (viewMode.value === 'day') {
      headers.push(current.format('MM/DD'))
      current = current.add(1, 'day')
    } else if (viewMode.value === 'week') {
      headers.push(current.format('MM/DD'))
      current = current.add(7, 'day')
    } else {
      headers.push(current.format('YYYY/MM'))
      current = current.add(1, 'month')
    }
  }
  return headers
})

const totalDays = computed(() => {
  return dateRange.value.end.diff(dateRange.value.start, 'day') + 1
})

function getBarStyle(task) {
  const start = dayjs(task.start_date)
  const end = dayjs(task.end_date)
  const rangeStart = dateRange.value.start

  let leftDays, widthDays
  if (viewMode.value === 'day') {
    leftDays = start.diff(rangeStart, 'day')
    widthDays = end.diff(start, 'day') + 1
  } else if (viewMode.value === 'week') {
    leftDays = start.diff(rangeStart, 'day') / 7
    widthDays = (end.diff(start, 'day') + 1) / 7
  } else {
    leftDays = start.diff(rangeStart, 'month', true)
    widthDays = end.diff(start, 'month', true) + 1 / 30
  }

  return {
    left: leftDays * cellWidth.value + 'px',
    width: Math.max(widthDays * cellWidth.value, 20) + 'px',
  }
}

function priorityTagType(p) {
  return { low: 'default', medium: 'info', high: 'warning', urgent: 'error' }[p] || 'default'
}

function priorityLabel(p) {
  return { low: '低', medium: '中', high: '高', urgent: '紧急' }[p] || p
}

function editTask(task) {
  editingTask.value = task
  showModal.value = true
}

async function fetchTasks() {
  tasks.value = await taskApi.list({ project_id: route.params.id })
  emit('refresh')
}

onMounted(fetchTasks)
</script>

<style scoped>
.gantt-container {
  overflow-x: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #fff;
}

.gantt-table {
  min-width: 100%;
}

.gantt-header-row {
  display: flex;
  border-bottom: 2px solid #eee;
  background: #fafafa;
  position: sticky;
  top: 0;
  z-index: 1;
}

.gantt-header-cell {
  font-weight: 600;
  font-size: 13px;
}

.gantt-task-info {
  width: 220px;
  min-width: 220px;
  padding: 10px 12px;
  border-right: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.gantt-task-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gantt-timeline-header {
  display: flex;
}

.gantt-date-cell {
  text-align: center;
  padding: 10px 0;
  font-size: 12px;
  color: #999;
  border-right: 1px solid #f0f0f0;
}

.gantt-row {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.gantt-row:hover {
  background: #f9f9f9;
}

.gantt-timeline {
  flex: 1;
  position: relative;
  height: 42px;
}

.gantt-bar {
  position: absolute;
  top: 8px;
  height: 26px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: 11px;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
}

.gantt-bar-todo { background: #909399; }
.gantt-bar-in_progress { background: #e6a23c; }
.gantt-bar-testing { background: #409eff; }
.gantt-bar-done { background: #67c23a; }

.gantt-bar-label {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
