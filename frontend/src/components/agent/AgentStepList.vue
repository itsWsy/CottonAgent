<template>
  <el-card>
    <template #header>
      <div class="header">
        <span>Agent 执行轨迹</span>
        <el-tag type="success">{{ toolCallCount }} 次工具调用</el-tag>
      </div>
    </template>
    <el-collapse>
      <AgentStepItem v-for="step in steps" :key="step.stepId" :step="step" />
    </el-collapse>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import AgentStepItem from './AgentStepItem.vue'

const props = defineProps({ steps: Array })
const toolCallCount = computed(() => (props.steps || []).filter((step) => step.toolCall).length)
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
</style>
