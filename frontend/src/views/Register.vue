<template>
  <div class="register-page">
    <n-card class="register-card" title="注册" size="large">
      <n-form ref="formRef" :model="formData" :rules="rules">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="formData.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="formData.email" placeholder="请输入邮箱" />
        </n-form-item>
        <n-form-item label="昵称" path="nickname">
          <n-input v-model:value="formData.nickname" placeholder="请输入昵称（选填）" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="formData.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
            @keyup.enter="handleRegister"
          />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="handleRegister">
          注册
        </n-button>
      </n-form>
      <div class="login-link">
        已有账号？<router-link to="/login">立即登录</router-link>
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
  email: '',
  nickname: '',
  password: '',
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  email: { required: true, message: '请输入邮箱', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
}

async function handleRegister() {
  try {
    await formRef.value?.validate()
    loading.value = true
    await userStore.register(formData.value)
    message.success('注册成功')
    router.push('/projects')
  } catch (err) {
    if (err?.detail) message.error(err.detail)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 400px;
}

.login-link {
  margin-top: 16px;
  text-align: center;
  color: #666;
}

.login-link a {
  color: #18a058;
  text-decoration: none;
}
</style>
