<template>
  <div class="login-page">
    <n-card class="login-card" title="登录" size="large">
      <n-form ref="formRef" :model="formData" :rules="rules">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="formData.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="formData.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="handleLogin">
          登录
        </n-button>
      </n-form>
      <div class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useUserStore } from '@/store/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const formData = ref({
  username: '',
  password: '',
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
    loading.value = true
    await userStore.login(formData.value)
    message.success('登录成功')
    router.push('/projects')
  } catch (err) {
    if (err?.detail) message.error(err.detail)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.register-link {
  margin-top: 16px;
  text-align: center;
  color: #666;
}

.register-link a {
  color: #18a058;
  text-decoration: none;
}
</style>
