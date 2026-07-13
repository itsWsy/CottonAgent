<template>
  <el-container class="layout">
    <el-aside width="220px">
      <div class="brand">棉智策 CottonPilot</div>
      <el-menu router :default-active="$route.path">
        <el-menu-item index="/dashboard">数据总览</el-menu-item>
        <el-menu-item index="/fields">棉田管理</el-menu-item>
        <el-menu-item index="/agent">工作台</el-menu-item>
        <el-menu-item index="/history">历史任务</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <span>农事推荐智能体平台</span>
        <el-button text @click="logout">退出登录</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.brand { padding: 22px 18px; font-weight: 700; color: #24513b; }
.el-aside { background: #eef6ec; border-right: 1px solid #dce8d7; }
.el-header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #edf0ed; }
.el-main { background: #f5f8f4; }
</style>
