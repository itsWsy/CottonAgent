<template>
  <el-timeline class="record-timeline">
    <el-timeline-item v-for="record in records" :key="record.id" :timestamp="record.operationDate">
      <b>{{ record.actionName }}</b>
      <span> {{ record.description }}</span>
      <el-button link type="danger" @click="$emit('delete', record)">删除</el-button>
    </el-timeline-item>
  </el-timeline>
</template>

<script setup>
defineProps({ records: Array })
defineEmits(['delete'])
</script>

<style scoped>
.record-timeline {
  margin-top: 16px;
}
</style>
