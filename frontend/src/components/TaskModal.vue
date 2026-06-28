<template>
  <n-modal v-model:show="visible" preset="dialog" :title="task ? '编辑任务' : '新建任务'" style="width: 600px">
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="left" label-width="80">
      <n-form-item label="任务标题" path="title">
        <n-input v-model:value="formData.title" placeholder="请输入任务标题" />
      </n-form-item>
      <n-form-item label="任务描述">
        <n-input v-model:value="formData.description" type="textarea" placeholder="请输入任务描述" :rows="3" />
      </n-form-item>
      <n-grid :cols="2" :x-gap="16">
        <n-gi>
          <n-form-item label="状态">
            <n-select v-model:value="formData.status" :options="statusOptions" />
          </n-form-item>
        </n-gi>
        <n-gi>
          <n-form-item label="优先级">
            <n-select v-model:value="formData.priority" :options="priorityOptions" />
          </n-form-item>
        </n-gi>
        <n-gi>
          <n-form-item label="负责人">
            <n-select
              v-model:value="formData.assignee_id"
              :options="memberOptions"
              clearable
              placeholder="选择负责人"
            />
          </n-form-item>
        </n-gi>
        <n-gi>
          <n-form-item label="预估工时">
            <n-input-number v-model:value="formData.estimated_hours" :min="0" style="width: 100%" placeholder="小时" />
          </n-form-item>
        </n-gi>
      </n-grid>
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
      <n-button @click="visible = false">取消</n-button>
      <n-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ task ? '保存' : '创建' }}
      </n-button>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { taskApi, projectApi } from '@/api'

const props = defineProps({
  show: Boolean,
  task: Object,
  projectId: Number,
  defaultStatus: { type: String, default: 'todo' },
})
const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const formRef = ref(null)
const submitting = ref(false)
const members = ref([])
const dateRange = ref(null)

const visible = ref(false)
watch(() => props.show, (v) => { visible.value = v })
watch(visible, (v) => emit('update:show', v))

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

const memberOptions = ref([])

const formData = ref({
  title: '',
  description: '',
  status: 'todo',
  priority: 'medium',
  assignee_id: null,
  estimated_hours: 0,
})

const rules = {
  title: { required: true, message: '请输入任务标题', trigger: 'blur' },
}

watch(() => props.show, async (v) => {
  if (v) {
    if (props.task) {
      formData.value = { ...props.task }
      dateRange.value = props.task.start_date && props.task.end_date
        ? [props.task.start_date, props.task.end_date]
        : null
    } else {
      formData.value = {
        title: '',
        description: '',
        status: props.defaultStatus,
        priority: 'medium',
        assignee_id: null,
        estimated_hours: 0,
      }
      dateRange.value = null
    }
    try {
      members.value = await projectApi.getMembers(props.projectId)
      memberOptions.value = members.value.map((m) => ({
        label: m.nickname || m.username,
        value: m.id,
      }))
    } catch {}
  }
})

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    const data = {
      ...formData.value,
      project_id: props.projectId,
      start_date: dateRange.value?.[0] || '',
      end_date: dateRange.value?.[1] || '',
    }
    if (props.task) {
      await taskApi.update(props.task.id, data)
      message.success('任务已更新')
    } else {
      await taskApi.create(data)
      message.success('任务已创建')
    }
    visible.value = false
    emit('saved')
  } catch (err) {
    if (err?.detail) message.error(err.detail)
  } finally {
    submitting.value = false
  }
}
</script>
