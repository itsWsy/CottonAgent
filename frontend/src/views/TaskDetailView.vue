<template>
  <div class="page">
    <PageHeader title="任务详情" />
    <el-descriptions v-if="detail" border :column="2">
      <el-descriptions-item label="棉田">{{ detail.fieldName }}</el-descriptions-item>
      <el-descriptions-item label="状态"><StatusTag :value="detail.status" /></el-descriptions-item>
      <el-descriptions-item label="风险"><StatusTag :value="detail.riskLevel" /></el-descriptions-item>
      <el-descriptions-item label="决策"><StatusTag :value="detail.decision" /></el-descriptions-item>
      <el-descriptions-item label="症状">{{ detail.symptoms?.join('、') }}</el-descriptions-item>
      <el-descriptions-item label="天气">{{ detail.weatherTags?.join('、') }}</el-descriptions-item>
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
import PageHeader from '../components/common/PageHeader.vue'
import StatusTag from '../components/common/StatusTag.vue'
import AgentStepList from '../components/agent/AgentStepList.vue'
import RecommendationList from '../components/recommendation/RecommendationList.vue'
import FarmPlanTimeline from '../components/recommendation/FarmPlanTimeline.vue'
import { acceptTaskApi, getTaskApi, rejectTaskApi } from '../api/agent'

const route = useRoute()
const detail = ref(null)

async function load() {
  detail.value = await getTaskApi(route.params.taskId)
}

async function decide(type) {
  if (type === 'accept') await acceptTaskApi(detail.value.id)
  else await rejectTaskApi(detail.value.id)
  await load()
}

onMounted(load)
</script>
