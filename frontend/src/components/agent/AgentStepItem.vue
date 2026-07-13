<template>
  <el-collapse-item :name="step.stepId" class="trace-item">
    <template #title>
      <span class="step-title">
        <StatusTag :value="step.status" />
        <b>{{ step.name }}</b>
        <small v-if="step.duration">{{ step.duration }}ms</small>
        <span v-if="step.summary" class="summary">{{ step.summary }}</span>
      </span>
    </template>

    <el-alert v-if="step.errorMessage" :title="step.errorMessage" type="error" :closable="false" />
    <p v-if="step.summary" class="summary-line">{{ step.summary }}</p>

    <div v-if="step.toolCall" class="tool-row">
      <el-tag type="primary" effect="plain">工具：{{ toolLabel(step.toolCall.toolName) }}</el-tag>
      <span class="muted">调用时间：{{ step.toolCall.calledAt || '-' }}</span>
    </div>
    <div v-else class="tool-row">
      <el-tag effect="plain">暂无工具调用</el-tag>
    </div>

    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="步骤 ID">{{ step.stepId }}</el-descriptions-item>
      <el-descriptions-item label="耗时">{{ step.duration || 0 }}ms</el-descriptions-item>
      <el-descriptions-item label="开始时间">{{ step.startTime || '-' }}</el-descriptions-item>
      <el-descriptions-item label="结束时间">{{ step.endTime || '-' }}</el-descriptions-item>
    </el-descriptions>

    <el-tabs class="json-tabs">
      <el-tab-pane label="输入参数">
        <pre>{{ JSON.stringify(step.toolCall?.toolInput || step.input || {}, null, 2) }}</pre>
      </el-tab-pane>
      <el-tab-pane label="观测结果">
        <pre>{{ JSON.stringify(step.toolCall?.observation || {}, null, 2) }}</pre>
      </el-tab-pane>
      <el-tab-pane label="原始输出">
        <pre>{{ JSON.stringify(step.output || {}, null, 2) }}</pre>
      </el-tab-pane>
    </el-tabs>
  </el-collapse-item>
</template>

<script setup>
import StatusTag from '../common/StatusTag.vue'

defineProps({ step: Object })

const toolLabels = {
  consultation_validator: '咨询校验器',
  field_profile_reader: '棉田档案读取器',
  farm_record_reader: '历史记录读取器',
  cotton_knowledge_retriever: '棉花知识检索器',
  multi_factor_recommender: '多因子推荐器',
  seven_day_plan_generator: '7 天计划生成器',
  final_answer_generator: '最终说明生成器',
  task_result_persister: '任务结果持久化器'
}

function toolLabel(name) {
  return toolLabels[name] || name || '未命名工具'
}
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
.summary-line {
  margin: 0 0 12px;
  color: #3f5f4c;
}
.tool-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.muted {
  color: #6b7d71;
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
