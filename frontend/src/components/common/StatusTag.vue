<template>
  <el-tag :type="typeMap[value] || 'info'">{{ labelMap[value] || value }}</el-tag>
</template>

<script setup>
defineProps({ value: String })
const typeMap = {
  success: 'success',
  running: 'warning',
  failed: 'danger',
  idle: 'info',
  pending: 'info',
  accepted: 'success',
  rejected: 'danger',
  high: 'danger',
  medium: 'warning',
  low: 'success'
}
const labelMap = {
  success: '成功',
  running: '运行中',
  failed: '失败',
  idle: '未开始',
  pending: '待确认',
  accepted: '已接受',
  rejected: '已拒绝',
  high: '高风险',
  medium: '中风险',
  low: '低风险'
}
</script>
