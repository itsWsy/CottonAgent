<template>
  <div class="login">
    <el-card class="box">
      <h2>棉智策 CottonPilot</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码" prop="password"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-button type="primary" :loading="loading" class="full" @click="submit">登录</el-button>
      </el-form>
      <p>测试账号：admin / 123456</p>
    </el-card>
  </div>
</template>
<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: 'admin', password: '123456' })
const rules = { username: [{ required: true, message: '请输入用户名' }], password: [{ required: true, message: '请输入密码' }] }
async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await auth.login(form)
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}
</script>
<style scoped>
.login { min-height: 100vh; display: grid; place-items: center; background: #eef6ec; }
.box { width: 380px; }
.full { width: 100%; }
p { color: #6b7d71; }
</style>
