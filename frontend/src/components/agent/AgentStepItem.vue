<template>
  <el-collapse-item :name="step.stepId">
    <template #title>
      <span class="step-title">
        <StatusTag :value="step.status" />
        <b>{{ step.name }}</b>
        <small v-if="step.duration">{{ step.duration }}ms</small>
        <span v-if="step.summary" class="summary">{{ step.summary }}</span>
      </span>
    </template>
    <el-alert v-if="step.errorMessage" :title="step.errorMessage" type="error" :closable="false" />
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="步骤 ID">{{ step.stepId }}</el-descriptions-item>
      <el-descriptions-item label="耗时">{{ step.duration || 0 }}ms</el-descriptions-item>
      <el-descriptions-item label="开始时间">{{ step.startTime || '-' }}</el-descriptions-item>
      <el-descriptions-item label="结束时间">{{ step.endTime || '-' }}</el-descriptions-item>
    </el-descriptions>
    <el-tabs class="json-tabs">
      <el-tab-pane label="输入"><pre>{{ JSON.stringify(step.input || {}, null, 2) }}</pre></el-tab-pane>
      <el-tab-pane label="输出"><pre>{{ JSON.stringify(step.output || {}, null, 2) }}</pre></el-tab-pane>
    </el-tabs>
  </el-collapse-item>
</template>

<script setup>
import StatusTag from '../common/StatusTag.vue'
defineProps({ step: Object })
</script>

<style scoped>
.step-title {
  display: flex;
  gap: 10px;
  align-items: center;
  min-width: 0;
}
.summary {
  color: #6b7d71;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.json-tabs {
  margin-top: 12px;
}
pre {
  white-space: pre-wrap;
  background: #f6f8f7;
  padding: 10px;
  border-radius: 6px;
}
</style>
