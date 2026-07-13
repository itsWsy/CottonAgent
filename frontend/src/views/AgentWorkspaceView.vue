<template>
  <div class="page">
    <PageHeader title="Agent 工作台" description="基于棉田档案、历史记录、本地知识和多因子评分器生成可追踪的农事辅助建议。" />
    <el-alert
      v-if="agent.recentRunningTask && agent.taskStatus !== 'running'"
      class="agent-banner"
      type="warning"
      :closable="false"
      show-icon
    >
      <template #title>
        检测到一个未完成任务：{{ agent.recentRunningTask.fieldName || '未知棉田' }}
        <el-button link type="primary" @click="restoreRecentTask">恢复任务</el-button>
      </template>
    </el-alert>
    <!-- <el-alert
      class="agent-banner"
      type="info"
      :closable="false"
      title="本页展示一个可落地 Agent：按步骤调用工具、记录观测结果、持久化任务状态，并通过 SSE 实时回传执行轨迹。"
    /> -->

    <el-row :gutter="16">
      <el-col :span="8">
        <AgentInputPanel
          :fields="fields.fieldList"
          :selected-field-id="selectedFieldId"
          :running="agent.taskStatus === 'running'"
          :initial-value="agent.lastInput"
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
          <el-button v-if="agent.canRetry" class="retry-btn" type="primary" @click="retry">基于原始输入重试</el-button>
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
      <el-alert v-if="agent.safetyConstraints.length" class="safety-box" type="warning" :closable="false">
        <template #title>安全约束</template>
        <ul>
          <li v-for="item in agent.safetyConstraints" :key="item">{{ item }}</li>
        </ul>
      </el-alert>
      <el-tabs>
        <el-tab-pane label="推荐操作"><RecommendationList :items="agent.recommendations" /></el-tab-pane>
        <el-tab-pane label="7 天计划"><FarmPlanTimeline :items="agent.farmPlan" @toggle="togglePlanItem" /></el-tab-pane>
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
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

async function retry() {
  try {
    await agent.retryLastTask()
  } catch (error) {
    ElMessage.error(error.message)
  }
}

async function restoreRecentTask() {
  await agent.restoreTask(agent.recentRunningTask.id)
}

function togglePlanItem(item) {
  item.status = item.status === 'done' ? 'pending' : 'done'
}

function beforeUnload(event) {
  if (agent.taskStatus !== 'running') return
  event.preventDefault()
  event.returnValue = 'Agent 任务仍在运行，确定要离开吗？'
}

watch(() => agent.taskStatus, (status, oldStatus) => {
  if (oldStatus === 'running' && status === 'success') ElMessage.success('分析完成，可查看推荐结果')
})

onBeforeRouteLeave(async () => {
  if (agent.taskStatus !== 'running') return true
  try {
    await ElMessageBox.confirm('Agent 任务仍在运行，离开页面后可稍后恢复任务。确定离开吗？', '任务运行中', { type: 'warning' })
    return true
  } catch {
    return false
  }
})

onMounted(async () => {
  await fields.fetchFields()
  await agent.fetchRecentRunningTask().catch(() => {})
  window.addEventListener('beforeunload', beforeUnload)
})
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnload)
  agent.closeTaskStream()
})
</script>

<style scoped>
.agent-banner {
  margin-bottom: 16px;
}
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
.risk-box,
.safety-box {
  margin-bottom: 16px;
}
.retry-btn {
  margin-top: 12px;
}
ul {
  margin: 0;
  padding-left: 18px;
}
.toolbar{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}
</style>
