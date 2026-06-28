<template>
  <div v-if="project">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <n-button text @click="router.push('/projects')">
          <template #icon><n-icon><ArrowBackOutline /></n-icon></template>
        </n-button>
        <h2>{{ project.name }}</h2>
        <n-tag :type="statusTagType(project.status)" size="small">{{ statusLabel(project.status) }}</n-tag>
      </div>
      <div style="display: flex; align-items: center; gap: 12px;">
        <n-statistic label="任务" :value="project.task_count" style="text-align: center">
          <template #suffix>
            <span style="font-size: 14px; color: #18a058"> / {{ project.done_count }} 完成</span>
          </template>
        </n-statistic>
        <n-statistic label="成员" :value="project.member_count" style="text-align: center" />
        <n-statistic label="文档" :value="project.doc_count" style="text-align: center" />
      </div>
    </div>

    <n-progress
      type="line"
      :percentage="progressPercent"
      :indicator-placement="'inside'"
      style="margin-bottom: 16px;"
    />

    <n-tabs type="line" :value="activeTab" @update:value="handleTabChange">
      <n-tab name="kanban">看板</n-tab>
      <n-tab name="list">列表</n-tab>
      <n-tab name="gantt">甘特图</n-tab>
      <n-tab name="docs">文档</n-tab>
    </n-tabs>

    <div style="margin-top: 16px;">
      <router-view :project="project" @refresh="fetchProject" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowBackOutline } from '@vicons/ionicons5'
import { projectApi } from '@/api'

const router = useRouter()
const route = useRoute()
const project = ref(null)

const activeTab = computed(() => {
  const path = route.path
  if (path.includes('/kanban')) return 'kanban'
  if (path.includes('/list')) return 'list'
  if (path.includes('/gantt')) return 'gantt'
  if (path.includes('/docs')) return 'docs'
  return 'kanban'
})

const progressPercent = computed(() => {
  if (!project.value || !project.value.task_count) return 0
  return Math.round((project.value.done_count / project.value.task_count) * 100)
})

function statusTagType(status) {
  return { active: 'success', archived: 'default', completed: 'info' }[status] || 'default'
}

function statusLabel(status) {
  return { active: '进行中', archived: '已归档', completed: '已完成' }[status] || status
}

function handleTabChange(tab) {
  router.push(`/projects/${route.params.id}/${tab}`)
}

async function fetchProject() {
  project.value = await projectApi.get(route.params.id)
}

onMounted(fetchProject)
watch(() => route.params.id, fetchProject)
</script>
