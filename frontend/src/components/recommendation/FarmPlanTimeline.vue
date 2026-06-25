<template>
  <el-timeline>
    <el-timeline-item v-for="item in items" :key="item.actionCode" :timestamp="`第 ${item.day} 天`">
      <b>{{ item.actionName }}</b>
      <p>{{ item.reason }}</p>
    </el-timeline-item>
  </el-timeline>
</template>

<script setup>
defineProps({ items: Array })
</script>
