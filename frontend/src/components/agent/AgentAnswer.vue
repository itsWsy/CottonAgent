<template>
  <el-card>
    <template #header>Agent 总结</template>
    <p>{{ answer || '任务完成后展示总结。' }}</p>
  </el-card>
</template>
<script setup>
defineProps({ answer: String })
</script>
