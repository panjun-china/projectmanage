<template>
  <div v-if="doc" style="height: calc(100vh - 140px); display: flex; flex-direction: column;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <n-button text @click="router.push(`/projects/${route.params.id}/docs`)">
          <template #icon><n-icon><ArrowBackOutline /></n-icon></template>
        </n-button>
        <n-input
          v-if="editingTitle"
          v-model:value="doc.title"
          size="small"
          style="width: 300px"
          @blur="saveTitle"
          @keyup.enter="saveTitle"
          autofocus
        />
        <h3 v-else @dblclick="editingTitle = true" style="cursor: pointer" title="双击编辑标题">
          {{ doc.title }}
        </h3>
      </div>
      <n-space>
        <n-text depth="3" style="font-size: 13px">
          {{ saving ? '保存中...' : '已保存' }}
        </n-text>
        <n-button size="small" @click="handleSave">保存</n-button>
      </n-space>
    </div>

    <div style="flex: 1; overflow: hidden;">
      <MdEditor
        v-model="doc.content"
        :theme="'light'"
        style="height: 100%"
        @on-save="handleSave"
        @on-change="autoSave"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ArrowBackOutline } from '@vicons/ionicons5'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { documentApi } from '@/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const doc = ref(null)
const saving = ref(false)
const editingTitle = ref(false)
let saveTimer = null

async function fetchDoc() {
  doc.value = await documentApi.get(route.params.docId)
}

async function handleSave() {
  if (!doc.value) return
  saving.value = true
  try {
    await documentApi.update(doc.value.id, {
      title: doc.value.title,
      content: doc.value.content,
    })
  } catch (err) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

function saveTitle() {
  editingTitle.value = false
  handleSave()
}

function autoSave() {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(handleSave, 2000)
}

onMounted(fetchDoc)
onUnmounted(() => {
  if (saveTimer) clearTimeout(saveTimer)
})
</script>
