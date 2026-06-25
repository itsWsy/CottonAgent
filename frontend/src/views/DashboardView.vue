<template>
  <div class="page">
    <PageHeader title="数据总览" />
    <el-row :gutter="16" v-loading="loading">
      <el-col v-for="card in cards" :key="card.label" :span="6"><el-card><p>{{ card.label }}</p><h2>{{ card.value }}</h2></el-card></el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14"><el-card><template #header>最近 7 天咨询趋势</template><div ref="trendRef" class="chart" /></el-card></el-col>
      <el-col :span="10"><el-card><template #header>推荐操作类型分布</template><div ref="pieRef" class="chart" /></el-card></el-col>
    </el-row>
    <el-card style="margin-top:16px">
      <template #header>最近 5 条 Agent 任务</template>
      <el-table :data="recent">
        <el-table-column prop="fieldName" label="棉田" />
        <el-table-column prop="description" label="问题摘要" />
        <el-table-column label="状态"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
        <el-table-column prop="createdAt" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>
<script setup>
import * as echarts from 'echarts'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import PageHeader from '../components/common/PageHeader.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { distributionApi, recentTasksApi, summaryApi, trendApi } from '../api/dashboard'
const loading = ref(false)
const summary = ref({})
const recent = ref([])
const trendRef = ref()
const pieRef = ref()
let trendChart
let pieChart
const cards = computed(() => [
  { label: '棉田数量', value: summary.value.fieldCount || 0 },
  { label: '本周任务数', value: summary.value.weeklyTaskCount || 0 },
  { label: '待确认方案', value: summary.value.pendingDecisionCount || 0 },
  { label: '中高风险任务', value: summary.value.mediumHighRiskCount || 0 }
])
onMounted(async () => {
  loading.value = true
  const [s, t, d, r] = await Promise.all([summaryApi(), trendApi(), distributionApi(), recentTasksApi()])
  summary.value = s
  recent.value = r
  loading.value = false
  await nextTick()
  trendChart = echarts.init(trendRef.value)
  trendChart.setOption({ xAxis: { type: 'category', data: t.map((x) => x.date.slice(5)) }, yAxis: { type: 'value' }, series: [{ type: 'line', data: t.map((x) => x.count), smooth: true }] })
  pieChart = echarts.init(pieRef.value)
  pieChart.setOption({ tooltip: {}, series: [{ type: 'pie', radius: '65%', data: d.length ? d : [{ name: '暂无推荐', value: 1 }] }] })
})
onBeforeUnmount(() => { trendChart?.dispose(); pieChart?.dispose() })
</script>
<style scoped>
.chart { height: 320px; }
p { color: #6b7d71; margin: 0; }
h2 { margin-bottom: 0; }
</style>
