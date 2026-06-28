<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>我的项目</h2>
      <n-button type="primary" @click="showCreateModal = true">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        新建项目
      </n-button>
    </div>

    <n-spin :show="loading">
      <n-grid :cols="3" :x-gap="16" :y-gap="16" v-if="projects.length">
        <n-gi v-for="project in projects" :key="project.id">
          <n-card hoverable style="cursor: pointer" @click="router.push(`/projects/${project.id}`)">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>{{ project.name }}</span>
                <n-tag :type="statusTagType(project.status)" size="small">
                  {{ statusLabel(project.status) }}
                </n-tag>
              </div>
            </template>
            <n-ellipsis :line-clamp="2" style="color: #666; min-height: 40px;">
              {{ project.description || '暂无描述' }}
            </n-ellipsis>
            <div style="margin-top: 12px; display: flex; justify-content: space-between; color: #999; font-size: 13px;">
              <span>{{ project.owner?.nickname || project.owner?.username }}</span>
              <span>{{ formatDate(project.created_at) }}</span>
            </div>
            <template #action>
              <div style="display: flex; justify-content: flex-end; gap: 8px" @click.stop>
                <n-button size="small" @click="editProject(project)">编辑</n-button>
                <n-popconfirm @positive-click="handleDelete(project.id)">
                  <template #trigger>
                    <n-button size="small" type="error">删除</n-button>
                  </template>
                  确定要删除该项目吗？
                </n-popconfirm>
              </div>
            </template>
          </n-card>
        </n-gi>
      </n-grid>
      <n-empty v-else description="暂无项目，点击右上角创建" />
    </n-spin>

    <n-modal v-model:show="showCreateModal" preset="dialog" :title="editingProject ? '编辑项目' : '新建项目'" style="width: 500px">
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="80">
        <n-form-item label="项目名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入项目名称" />
        </n-form-item>
        <n-form-item label="项目描述" path="description">
          <n-input v-model:value="formData.description" type="textarea" placeholder="请输入项目描述" :rows="3" />
        </n-form-item>
        <n-form-item label="时间范围">
          <n-date-picker
            v-model:formatted-value="dateRange"
            type="daterange"
            clearable
            value-format="yyyy-MM-dd"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showCreateModal = false">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ editingProject ? '保存' : '创建' }}
        </n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { projectApi } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const message = useMessage()
const loading = ref(false)
const submitting = ref(false)
const projects = ref([])
const showCreateModal = ref(false)
const editingProject = ref(null)
const formRef = ref(null)
const dateRange = ref(null)

const formData = ref({ name: '', description: '' })
const formRules = {
  name: { required: true, message: '请输入项目名称', trigger: 'blur' },
}

function statusTagType(status) {
  return { active: 'success', archived: 'default', completed: 'info' }[status] || 'default'
}

function statusLabel(status) {
  return { active: '进行中', archived: '已归档', completed: '已完成' }[status] || status
}

function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD')
}

async function fetchProjects() {
  loading.value = true
  try {
    projects.value = await projectApi.list()
  } finally {
    loading.value = false
  }
}

function editProject(project) {
  editingProject.value = project
  formData.value = { name: project.name, description: project.description }
  dateRange.value = project.start_date && project.end_date ? [project.start_date, project.end_date] : null
  showCreateModal.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    const data = {
      ...formData.value,
      start_date: dateRange.value?.[0] || '',
      end_date: dateRange.value?.[1] || '',
    }
    if (editingProject.value) {
      await projectApi.update(editingProject.value.id, data)
      message.success('项目已更新')
    } else {
      await projectApi.create(data)
      message.success('项目已创建')
    }
    showCreateModal.value = false
    editingProject.value = null
    formData.value = { name: '', description: '' }
    dateRange.value = null
    fetchProjects()
  } catch (err) {
    if (err?.detail) message.error(err.detail)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  try {
    await projectApi.delete(id)
    message.success('项目已删除')
    fetchProjects()
  } catch (err) {
    if (err?.detail) message.error(err.detail)
  }
}

onMounted(fetchProjects)
</script>
