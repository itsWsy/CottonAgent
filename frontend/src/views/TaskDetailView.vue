<template>
  <div class="page">
    <PageHeader title="任务详情">
      <el-button :disabled="!detail" @click="exportMarkdown">导出 Markdown</el-button>
      <template #prefix>
        <el-button @click="$router.back()">返回</el-button>
      </template>
    </PageHeader>

    <el-descriptions v-if="detail" border :column="2">
      <el-descriptions-item label="棉田">{{ detail.fieldName }}</el-descriptions-item>
      <el-descriptions-item label="状态"><StatusTag :value="detail.status" /></el-descriptions-item>
      <el-descriptions-item label="风险"><StatusTag :value="detail.riskLevel" /></el-descriptions-item>
      <el-descriptions-item label="决策"><StatusTag :value="detail.decision" /></el-descriptions-item>
      <el-descriptions-item label="症状">{{ detail.symptoms?.join('、') || '-' }}</el-descriptions-item>
      <el-descriptions-item label="天气">{{ detail.weatherTags?.join('、') || '-' }}</el-descriptions-item>
      <el-descriptions-item label="风险依据" :span="2">{{ detail.riskReason }}</el-descriptions-item>
      <el-descriptions-item label="问题" :span="2">{{ detail.description }}</el-descriptions-item>
    </el-descriptions>

    <AgentStepList v-if="detail" :steps="detail.steps" style="margin-top:16px" />

    <el-card v-if="detail" style="margin-top:16px">
      <el-tabs>
        <el-tab-pane label="推荐结果"><RecommendationList :items="detail.recommendations" /></el-tab-pane>
        <el-tab-pane label="7 天计划"><FarmPlanTimeline :items="detail.farmPlan" /></el-tab-pane>
        <el-tab-pane label="推荐依据"><pre>{{ JSON.stringify(detail.evidences, null, 2) }}</pre></el-tab-pane>
        <el-tab-pane label="最终说明">{{ detail.finalAnswer }}</el-tab-pane>
      </el-tabs>
      <div class="toolbar">
        <el-button type="success" :disabled="detail.status !== 'success' || detail.decision !== 'pending'" @click="decide('accept')">接受方案</el-button>
        <el-button type="danger" :disabled="detail.status !== 'success' || detail.decision !== 'pending'" @click="decide('reject')">拒绝方案</el-button>
      </div>
      <div class="disclaimer">结果仅供辅助参考，实际农事操作需由专业人员确认。</div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import StatusTag from '../components/common/StatusTag.vue'
import AgentStepList from '../components/agent/AgentStepList.vue'
import RecommendationList from '../components/recommendation/RecommendationList.vue'
import FarmPlanTimeline from '../components/recommendation/FarmPlanTimeline.vue'
import { acceptTaskApi, getTaskApi, rejectTaskApi } from '../api/agent'

const route = useRoute()
const detail = ref(null)

function formatDate(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 19)
}

async function load() {
  detail.value = await getTaskApi(route.params.taskId)
}

async function decide(type) {
  if (type === 'accept') await acceptTaskApi(detail.value.id)
  else await rejectTaskApi(detail.value.id)
  await load()
}

function recommendationMarkdown(items = []) {
  if (!items.length) return '暂无推荐结果'
  return items.map((item, index) => [
    `${index + 1}. ${item.actionName}（得分：${item.score}，建议第 ${item.expectedDay} 天）`,
    `   - 来源：${item.sourceType || '-'}`,
    `   - 原因：${item.reason || '-'}`,
    ...(item.reasonItems || []).map((reason) => `   - ${reason}`)
  ].join('\n')).join('\n')
}

function planMarkdown(items = []) {
  if (!items.length) return '暂无 7 天计划'
  return items.map((item) => `- 第 ${item.day} 天：${item.actionName}。${item.reason || ''}`).join('\n')
}

function stepsMarkdown(items = []) {
  if (!items.length) return '暂无执行轨迹'
  return items.map((step, index) => [
    `${index + 1}. ${step.name} [${step.status}] ${step.duration || 0}ms`,
    `   - 摘要：${step.summary || '-'}`,
    `   - 工具：${step.toolCall?.toolName || '-'}`
  ].join('\n')).join('\n')
}

function evidencesMarkdown(items = []) {
  if (!items.length) return '暂无推荐依据'
  return items.map((item) => `- ${item.title || item.id}：${item.content || ''}`).join('\n')
}

function buildMarkdown() {
  const task = detail.value
  return `# CottonPilot Agent 分析报告

## 基本信息

- 任务 ID：${task.id}
- 棉田：${task.fieldName}
- 创建时间：${formatDate(task.createdAt)}
- 完成时间：${formatDate(task.completedAt)}
- 状态：${task.status}
- 决策：${task.decision}
- 风险等级：${task.riskLevel}
- 风险依据：${task.riskReason || '-'}

## 原始输入

- 生育阶段：${task.growthStage}
- 症状：${task.symptoms?.join('、') || '-'}
- 天气：${task.weatherTags?.join('、') || '-'}
- 问题描述：${task.description}

## Agent 执行轨迹

${stepsMarkdown(task.steps)}

## 推荐操作

${recommendationMarkdown(task.recommendations)}

## 7 天计划

${planMarkdown(task.farmPlan)}

## 推荐依据

${evidencesMarkdown(task.evidences)}

## 最终说明

${task.finalAnswer || '-'}

## 免责声明

结果仅供辅助参考，实际农事操作需由专业人员确认。
`
}

function exportMarkdown() {
  if (!detail.value) return
  const blob = new Blob([buildMarkdown()], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `cottonpilot-task-${detail.value.id}.md`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Markdown 报告已导出')
}

onMounted(load)
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  background: #f6f8f7;
  padding: 10px;
  border-radius: 6px;
}
.toolbar{
  margin-top: 10px;
}
</style>
