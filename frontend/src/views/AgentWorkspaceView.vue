<template>
  <div class="page">
    <PageHeader title="Agent 工作台" description="发起棉田农事辅助分析，实时查看工作流执行步骤。" />
    <el-row :gutter="16">
      <el-col :span="8">
        <AgentInputPanel
          :fields="fields.fieldList"
          :selected-field-id="selectedFieldId"
          :running="agent.taskStatus === 'running'"
          @submit="submit"
        />
      </el-col>
      <el-col :span="16">
        <el-card class="progress-card">
          <template #header>
            <div class="card-header">
              <span>执行进度</span>
              <StatusTag v-if="agent.taskStatus !== 'idle'" :value="agent.taskStatus" />
            </div>
          </template>
          <el-progress :percentage="agent.progressPercent" :status="agent.taskStatus === 'failed' ? 'exception' : undefined" />
          <p class="muted">
            {{ agent.currentRunningStep ? `当前步骤：${agent.currentRunningStep.name}` : '等待任务开始或任务已结束' }}
          </p>
          <el-alert
            v-if="agent.sseMessage"
            :title="agent.sseMessage"
            :type="agent.sseStatus === 'reconnecting' ? 'warning' : 'info'"
            :closable="false"
          />
        </el-card>
        <AgentStepList :steps="agent.steps" class="step-list" />
      </el-col>
    </el-row>

    <el-card style="margin-top:16px">
      <template #header>
        <div class="card-header">
          <span>分析结果</span>
          <el-button @click="showEvidence = true">查看推荐依据</el-button>
        </div>
      </template>
      <el-alert v-if="agent.errorMessage" :title="agent.errorMessage" type="error" :closable="false" />
      <el-descriptions v-if="agent.riskLevel" :column="2" border class="risk-box">
        <el-descriptions-item label="风险等级"><StatusTag :value="agent.riskLevel" /></el-descriptions-item>
        <el-descriptions-item label="判定依据">{{ agent.riskReason }}</el-descriptions-item>
      </el-descriptions>
      <el-tabs>
        <el-tab-pane label="推荐操作"><RecommendationList :items="agent.recommendations" /></el-tab-pane>
        <el-tab-pane label="7 天计划"><FarmPlanTimeline :items="agent.farmPlan" /></el-tab-pane>
        <el-tab-pane label="Agent 总结"><AgentAnswer :answer="agent.answer" /></el-tab-pane>
      </el-tabs>
      <div class="toolbar">
        <el-button type="success" :disabled="agent.taskStatus !== 'success' || agent.decision !== 'pending'" @click="agent.acceptTask()">接受方案</el-button>
        <el-button type="danger" :disabled="agent.taskStatus !== 'success' || agent.decision !== 'pending'" @click="agent.rejectTask()">拒绝方案</el-button>
        <StatusTag :value="agent.decision" />
      </div>
      <div class="disclaimer">结果仅供辅助参考，实际农事操作需由专业人员确认。</div>
    </el-card>
    <EvidenceDrawer :visible="showEvidence" :items="agent.evidences" @close="showEvidence = false" />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import StatusTag from '../components/common/StatusTag.vue'
import AgentInputPanel from '../components/agent/AgentInputPanel.vue'
import AgentStepList from '../components/agent/AgentStepList.vue'
import AgentAnswer from '../components/agent/AgentAnswer.vue'
import RecommendationList from '../components/recommendation/RecommendationList.vue'
import FarmPlanTimeline from '../components/recommendation/FarmPlanTimeline.vue'
import EvidenceDrawer from '../components/recommendation/EvidenceDrawer.vue'
import { useFieldStore } from '../stores/fields'
import { useAgentStore } from '../stores/agent'

const route = useRoute()
const fields = useFieldStore()
const agent = useAgentStore()
const showEvidence = ref(false)
const selectedFieldId = computed(() => Number(route.query.fieldId) || null)

async function submit(payload) {
  try {
    await agent.createTask(payload)
  } catch (error) {
    ElMessage.error(error.message)
  }
}

onMounted(() => fields.fetchFields())
onBeforeUnmount(() => agent.closeTaskStream())
</script>

<style scoped>
.progress-card {
  margin-bottom: 16px;
}
.step-list {
  margin-top: 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.muted {
  color: #6b7d71;
}
.risk-box {
  margin-bottom: 16px;
}
</style>
