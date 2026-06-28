<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
      <n-space>
        <n-button-group size="small">
          <n-button :type="filter === 'all' ? 'primary' : 'default'" @click="filter = 'all'; fetchDocs()">全部</n-button>
          <n-button :type="filter === 'markdown' ? 'primary' : 'default'" @click="filter = 'markdown'; fetchDocs()">文档</n-button>
          <n-button :type="filter === 'file' ? 'primary' : 'default'" @click="filter = 'file'; fetchDocs()">文件</n-button>
        </n-button-group>
      </n-space>
      <n-space>
        <n-button type="primary" size="small" @click="showCreateModal = true">
          <template #icon><n-icon><DocumentTextOutline /></n-icon></template>
          新建文档
        </n-button>
        <n-upload
          :action="uploadUrl"
          :headers="uploadHeaders"
          :data="{ project_id: route.params.id }"
          :show-file-list="false"
          @finish="handleUploadFinish"
          @error="handleUploadError"
        >
          <n-button size="small">
            <template #icon><n-icon><CloudUploadOutline /></n-icon></template>
            上传文件
          </n-button>
        </n-upload>
      </n-space>
    </div>

    <n-spin :show="loading">
      <n-data-table
        v-if="documents.length"
        :columns="columns"
        :data="documents"
        :row-key="(row) => row.id"
      />
      <n-empty v-else description="暂无文档" />
    </n-spin>

    <n-modal v-model:show="showCreateModal" preset="dialog" title="新建文档" style="width: 500px">
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="80">
        <n-form-item label="文档标题" path="title">
          <n-input v-model:value="formData.title" placeholder="请输入文档标题" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showCreateModal = false">取消</n-button>
        <n-button type="primary" :loading="creating" @click="handleCreate">创建</n-button>
      </template>
    </n-modal>

    <n-modal v-model:show="showPreview" preset="card" title="文件预览" style="width: 80%; max-width: 900px;">
      <div v-if="previewDoc">
        <div v-if="isImage(previewDoc.file_name)" style="text-align: center">
          <img :src="getFileUrl(previewDoc)" style="max-width: 100%; max-height: 70vh" />
        </div>
        <div v-else-if="isPdf(previewDoc.file_name)">
          <iframe :src="getFileUrl(previewDoc)" style="width: 100%; height: 70vh; border: none" />
        </div>
        <div v-else style="text-align: center; padding: 40px; color: #999">
          该文件类型暂不支持预览，请下载后查看。
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, h, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NTag, NSpace, NPopconfirm, useMessage } from 'naive-ui'
import { DocumentTextOutline, CloudUploadOutline } from '@vicons/ionicons5'
import { documentApi } from '@/api'
import dayjs from 'dayjs'

const props = defineProps({ project: Object })
const emit = defineEmits(['refresh'])
const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const creating = ref(false)
const documents = ref([])
const filter = ref('all')
const showCreateModal = ref(false)
const showPreview = ref(false)
const previewDoc = ref(null)
const formRef = ref(null)

const formData = ref({ title: '' })
const formRules = { title: { required: true, message: '请输入文档标题', trigger: 'blur' } }

const uploadUrl = '/api/documents/upload'
const uploadHeaders = { Authorization: `Bearer ${localStorage.getItem('token')}` }

function isImage(name) {
  return /\.(png|jpg|jpeg|gif|svg|webp)$/i.test(name || '')
}

function isPdf(name) {
  return /\.pdf$/i.test(name || '')
}

function getFileUrl(doc) {
  return documentApi.getDownloadUrl(doc.id)
}

function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const columns = [
  {
    title: '标题',
    key: 'title',
    ellipsis: { tooltip: true },
    render: (row) =>
      h('span', { style: 'cursor: pointer; color: #18a058', onClick: () => handleDocClick(row) }, row.title),
  },
  {
    title: '类型',
    key: 'doc_type',
    width: 80,
    render: (row) =>
      h(NTag, { size: 'small', type: row.doc_type === 'markdown' ? 'success' : 'info' },
        () => row.doc_type === 'markdown' ? '文档' : '文件'),
  },
  {
    title: '大小',
    key: 'file_size',
    width: 100,
    render: (row) => row.doc_type === 'file' ? formatSize(row.file_size) : '-',
  },
  {
    title: '创建者',
    key: 'creator',
    width: 100,
    render: (row) => row.creator?.nickname || row.creator?.username || '-',
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 160,
    render: (row) => dayjs(row.updated_at).format('YYYY-MM-DD HH:mm'),
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) =>
      h(NSpace, { size: 'small' }, () => {
        const btns = []
        if (row.doc_type === 'file') {
          btns.push(h(NButton, { size: 'tiny', onClick: () => previewFile(row) }, () => '预览'))
          btns.push(h('a', {
            href: documentApi.getDownloadUrl(row.id),
            target: '_blank',
            style: 'text-decoration: none',
          }, h(NButton, { size: 'tiny' }, () => '下载')))
        }
        btns.push(
          h(NPopconfirm, { onPositiveClick: () => handleDelete(row.id) }, {
            trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
            default: () => '确定删除？',
          })
        )
        return btns
      }),
  },
]

function handleDocClick(doc) {
  if (doc.doc_type === 'markdown') {
    router.push(`/projects/${route.params.id}/docs/${doc.id}`)
  } else {
    previewFile(doc)
  }
}

function previewFile(doc) {
  previewDoc.value = doc
  showPreview.value = true
}

async function handleCreate() {
  try {
    await formRef.value?.validate()
    creating.value = true
    const doc = await documentApi.create({
      title: formData.value.title,
      doc_type: 'markdown',
      content: '',
      project_id: Number(route.params.id),
    })
    showCreateModal.value = false
    formData.value = { title: '' }
    router.push(`/projects/${route.params.id}/docs/${doc.id}`)
  } catch (err) {
    if (err?.detail) message.error(err.detail)
  } finally {
    creating.value = false
  }
}

function handleUploadFinish({ event }) {
  message.success('上传成功')
  fetchDocs()
  emit('refresh')
}

function handleUploadError() {
  message.error('上传失败')
}

async function handleDelete(id) {
  await documentApi.delete(id)
  message.success('已删除')
  fetchDocs()
  emit('refresh')
}

async function fetchDocs() {
  loading.value = true
  try {
    const params = { project_id: route.params.id }
    if (filter.value !== 'all') params.doc_type = filter.value
    documents.value = await documentApi.list(params)
  } finally {
    loading.value = false
  }
}

onMounted(fetchDocs)
</script>
