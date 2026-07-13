<template>
  <div class="page">
    <PageHeader title="数据总览">
      <div class="quick-actions">
        <el-button type="primary" @click="$router.push('/fields')">新增棉田</el-button>
        <el-button @click="$router.push('/agent')">发起 Agent 分析</el-button>
        <el-button @click="$router.push('/history')">查看历史任务</el-button>
        <el-button :loading="pageLoading" @click="loadDashboard">刷新</el-button>
      </div>
    </PageHeader>

    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :span="6">
        <el-card v-loading="section.summary.loading">
          <p>{{ card.label }}</p>
          <h2>{{ card.value }}</h2>
        </el-card>
      </el-col>
    </el-row>
    <el-alert v-if="section.summary.error" class="section-error" :title="section.summary.error" type="error" show-icon :closable="false" />

    <el-row :gutter="16" class="block-row">
      <el-col :span="12">
        <el-card v-loading="section.trend.loading">
          <template #header>最近 7 天咨询趋势</template>
          <el-alert v-if="section.trend.error" :title="section.trend.error" type="error" show-icon :closable="false" />
          <div ref="trendRef" class="chart" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card v-loading="section.action.loading">
          <template #header>推荐操作类型分布</template>
          <el-alert v-if="section.action.error" :title="section.action.error" type="error" show-icon :closable="false" />
          <div ref="actionRef" class="chart" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="block-row">
      <el-col :span="8">
        <el-card v-loading="section.risk.loading">
          <template #header>风险等级分布</template>
          <el-alert v-if="section.risk.error" :title="section.risk.error" type="error" show-icon :closable="false" />
          <div ref="riskRef" class="small-chart" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card v-loading="section.stage.loading">
          <template #header>生育阶段分布</template>
          <el-alert v-if="section.stage.error" :title="section.stage.error" type="error" show-icon :closable="false" />
          <div ref="stageRef" class="small-chart" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card v-loading="section.decision.loading">
          <template #header>推荐采纳率</template>
          <el-alert v-if="section.decision.error" :title="section.decision.error" type="error" show-icon :closable="false" />
          <div ref="decisionRef" class="small-chart" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="block-row equal-height-row">
      <el-col :span="12" class="equal-card-col">
        <el-card v-loading="section.pending.loading" class="dashboard-scroll-card">
          <template #header>待处理任务</template>
          <el-alert v-if="section.pending.error" :title="section.pending.error" type="error" show-icon :closable="false" />
          <el-tabs v-else>
            <el-tab-pane label="待确认方案">
              <div v-if="pendingTasks.pendingDecisionTasks.length" class="task-list">
                <div v-for="item in pendingTasks.pendingDecisionTasks" :key="item.id" class="task-item">
                  <div class="task-main"><b>{{ item.fieldName }}</b><span class="muted">{{ item.description }}</span></div>
                  <StatusTag :value="item.riskLevel" />
                  <el-button link @click="$router.push(`/history/${item.id}`)">详情</el-button>
                </div>
              </div>
              <EmptyState v-else description="暂无待确认任务" />
            </el-tab-pane>
            <el-tab-pane label="中高风险任务">
              <div v-if="pendingTasks.mediumHighRiskTasks.length" class="task-list">
                <div v-for="item in pendingTasks.mediumHighRiskTasks" :key="item.id" class="task-item">
                  <div class="task-main"><b>{{ item.fieldName }}</b><span class="muted">{{ item.description }}</span></div>
                  <StatusTag :value="item.riskLevel" />
                  <el-button link @click="$router.push(`/history/${item.id}`)">详情</el-button>
                </div>
              </div>
              <EmptyState v-else description="暂无中高风险任务" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      <el-col :span="12" class="equal-card-col">
        <el-card v-loading="section.abnormal.loading" class="dashboard-scroll-card">
          <template #header>最近异常棉田</template>
          <el-alert v-if="section.abnormal.error" :title="section.abnormal.error" type="error" show-icon :closable="false" />
          <el-table v-else :data="abnormalFields" empty-text="暂无中高风险棉田">
            <el-table-column prop="fieldName" label="棉田" />
            <el-table-column prop="growthStage" label="阶段" width="100" />
            <el-table-column label="风险" width="100">
              <template #default="{ row }"><StatusTag :value="row.riskLevel" /></template>
            </el-table-column>
            <el-table-column label="操作" width="90">
              <template #default="{ row }"><el-button link @click="$router.push(`/history/${row.taskId}`)">任务</el-button></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="block-row" v-loading="section.recent.loading">
      <template #header>最近 5 条 Agent 任务</template>
      <el-alert v-if="section.recent.error" :title="section.recent.error" type="error" show-icon :closable="false" />
      <el-table v-else :data="recent" empty-text="暂无历史任务">
        <el-table-column prop="fieldName" label="棉田" width="140" />
        <el-table-column prop="description" label="问题摘要" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><StatusTag :value="row.status" /></template>
        </el-table-column>
        <el-table-column label="风险" width="100">
          <template #default="{ row }"><StatusTag :value="row.riskLevel" /></template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="240">
          <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'
import StatusTag from '../components/common/StatusTag.vue'
import {
  abnormalFieldsApi,
  decisionDistributionApi,
  distributionApi,
  growthStageDistributionApi,
  pendingTasksApi,
  recentTasksApi,
  riskDistributionApi,
  summaryApi,
  trendApi
} from '../api/dashboard'

const summary = ref({})
const recent = ref([])
const pendingTasks = ref({ pendingDecisionTasks: [], mediumHighRiskTasks: [] })
const abnormalFields = ref([])

const trendRef = ref()
const actionRef = ref()
const riskRef = ref()
const stageRef = ref()
const decisionRef = ref()
const charts = []

const section = reactive({
  summary: state(),
  trend: state(),
  action: state(),
  risk: state(),
  stage: state(),
  decision: state(),
  pending: state(),
  abnormal: state(),
  recent: state()
})

const pageLoading = computed(() => Object.values(section).some((item) => item.loading))
const cards = computed(() => [
  { label: '棉田数量', value: summary.value.fieldCount || 0 },
  { label: '本周任务数', value: summary.value.weeklyTaskCount || 0 },
  { label: '待确认方案', value: summary.value.pendingDecisionCount || 0 },
  { label: '中高风险任务', value: summary.value.mediumHighRiskCount || 0 }
])

function state() {
  return { loading: false, error: '' }
}

function formatDate(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 19)
}

function disposeCharts() {
  while (charts.length) charts.pop()?.dispose()
}

function addChart(el, option) {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption(option)
  charts.push(chart)
}

function pieOption(data) {
  const visibleData = data.filter((item) => Number(item.value) > 0)
  return { tooltip: {}, series: [{ type: 'pie', radius: '65%', data: visibleData.length ? visibleData : [{ name: '暂无数据', value: 1 }] }] }
}

async function loadSection(key, loader) {
  section[key].loading = true
  section[key].error = ''
  try {
    return await loader()
  } catch (error) {
    section[key].error = error.message
    return null
  } finally {
    section[key].loading = false
  }
}

async function loadDashboard() {
  disposeCharts()
  const [summaryData, trendData, actionData, riskData, stageData, decisionData, pendingData, abnormalData, recentData] = await Promise.all([
    loadSection('summary', summaryApi),
    loadSection('trend', trendApi),
    loadSection('action', distributionApi),
    loadSection('risk', riskDistributionApi),
    loadSection('stage', growthStageDistributionApi),
    loadSection('decision', decisionDistributionApi),
    loadSection('pending', pendingTasksApi),
    loadSection('abnormal', abnormalFieldsApi),
    loadSection('recent', recentTasksApi)
  ])
  if (summaryData) summary.value = summaryData
  if (pendingData) pendingTasks.value = pendingData
  if (abnormalData) abnormalFields.value = abnormalData
  if (recentData) recent.value = recentData
  await nextTick()
  if (trendData && !section.trend.error) addChart(trendRef.value, { tooltip: {}, xAxis: { type: 'category', data: trendData.map((x) => x.date.slice(5)) }, yAxis: { type: 'value' }, series: [{ type: 'line', data: trendData.map((x) => x.count), smooth: true }] })
  if (actionData && !section.action.error) addChart(actionRef.value, pieOption(actionData))
  if (riskData && !section.risk.error) addChart(riskRef.value, pieOption(riskData))
  if (stageData && !section.stage.error) addChart(stageRef.value, pieOption(stageData))
  if (decisionData && !section.decision.error) addChart(decisionRef.value, pieOption(decisionData))
}

function resizeCharts() {
  charts.forEach((chart) => chart.resize())
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('resize', resizeCharts)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  disposeCharts()
})
</script>

<style scoped>
.quick-actions {
  display: flex;
  gap: 10px;
}
.block-row {
  margin-top: 16px;
}
.equal-height-row {
  align-items: stretch;
}
.equal-card-col {
  display: flex;
}
.dashboard-scroll-card {
  width: 100%;
}
:deep(.dashboard-scroll-card .el-card__body) {
  height: 360px;
  overflow-y: auto;
  overflow-x: hidden;
}
.chart,
.small-chart {
  height: 320px;
}
.small-chart {
  height: 260px;
}
p {
  color: #6b7d71;
  margin: 0;
}
h2 {
  margin-bottom: 0;
}
.task-list {
  display: grid;
  gap: 10px;
}
.task-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 10px;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eef2ee;
}
.task-main {
  display: grid;
  gap: 4px;
  min-width: 0;
}
.muted {
  color: #6b7d71;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
