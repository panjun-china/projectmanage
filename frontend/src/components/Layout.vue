<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider
      bordered
      :collapsed="collapsed"
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      :native-scrollbar="false"
      style="background: #fff"
    >
      <div class="logo">
        <n-icon size="28" color="#18a058">
          <CubeOutline />
        </n-icon>
        <span v-if="!collapsed" class="logo-text">项目管理平台</span>
      </div>
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />
    </n-layout-sider>
    <n-layout>
      <n-layout-header bordered style="height: 56px; display: flex; align-items: center; justify-content: flex-end; padding: 0 24px;">
        <n-space align="center">
          <n-dropdown :options="userMenuOptions" @select="handleUserMenuSelect">
            <n-button quaternary>
              <template #icon>
                <n-icon><PersonOutline /></n-icon>
              </template>
              {{ userStore.user?.nickname || userStore.user?.username }}
            </n-button>
          </n-dropdown>
        </n-space>
      </n-layout-header>
      <n-layout-content
        content-style="padding: 20px;"
        :native-scrollbar="false"
        style="background: #f5f7f9"
      >
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  CubeOutline,
  FolderOpenOutline,
  PersonOutline,
  LogOutOutline,
} from '@vicons/ionicons5'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const collapsed = ref(false)

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = [
  {
    label: '项目列表',
    key: 'projects',
    icon: renderIcon(FolderOpenOutline),
  },
]

const activeKey = computed(() => {
  if (route.path.startsWith('/projects')) return 'projects'
  return ''
})

function handleMenuSelect(key) {
  router.push(`/${key}`)
}

const userMenuOptions = [
  { label: '退出登录', key: 'logout', icon: renderIcon(LogOutOutline) },
]

function handleUserMenuSelect(key) {
  if (key === 'logout') {
    userStore.logout()
  }
}
</script>

<style scoped>
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 56px;
  gap: 8px;
  border-bottom: 1px solid #efeff5;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}
</style>
