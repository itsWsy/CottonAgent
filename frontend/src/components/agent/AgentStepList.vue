<template>
  <el-card>
    <template #header>Agent 执行步骤</template>
    <el-collapse>
      <AgentStepItem v-for="step in steps" :key="step.stepId" :step="step" />
    </el-collapse>
  </el-card>
</template>

<script setup>
import AgentStepItem from './AgentStepItem.vue'
defineProps({ steps: Array })
</script>
