<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <b>{{ item.actionName }}</b>
        <!-- <el-tag>{{ item.sourceType }}</el-tag> -->
        <el-tag :type="summaryTagType">{{ sourceSummary }}</el-tag>
      </div>
    </template>
    <el-progress :percentage="Math.round(item.score * 100)" />
    <p>建议第 {{ item.expectedDay }} 天执行</p>
    <!-- <p>{{ item.reason }}</p> -->
    <div class="source-tags">
      <el-tag v-for="source in item.candidateSources || []" :key="source" effect="plain">
        {{ sourceLabel(source) }}
      </el-tag>
    </div>
    <el-collapse class="details">
      <el-collapse-item title="查看评分详情与推荐理由">
        <el-divider content-position="left">得分拆解</el-divider>
        <div class="score-grid">
          <span>历史转移</span><b>{{ score('transitionScore') }}</b>
          <span>知识匹配</span><b>{{ score('knowledgeScore') }}</b>
          <span>阶段适配</span><b>{{ score('growthStageScore') }}</b>
          <span>天气影响</span><b>{{ score('weatherSuitabilityScore') }}</b>
          <span>症状紧急度</span><b>{{ score('symptomUrgencyScore') }}</b>
          <span>近期重复</span><b>{{ score('recencyPenaltyScore') }}</b>
        </div>
        <el-divider content-position="left">推荐理由</el-divider>
        <ul>
          <li v-for="reason in item.reasonItems || []" :key="reason">{{ reason }}</li>
        </ul>
      </el-collapse-item>
    </el-collapse>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const sourceSummary = computed(() => {
  const sources = props.item.candidateSources || []
  if (sources.length >= 3) return '综合推荐'
  if (sources.includes('knowledge')) return '知识驱动'
  if (sources.includes('symptom_rule')) return '症状触发'
  if (sources.includes('weather_rule')) return '天气触发'
  if (sources.includes('transition')) return '历史序列'
  if (sources.includes('stage_frequency')) return '阶段高频'
  return '规则推荐'
})

const summaryTagType = computed(() => {
  const sources = props.item.candidateSources || []
  if (sources.length >= 3) return 'success'
  if (sources.includes('knowledge')) return 'success'
  if (sources.includes('symptom_rule')) return 'warning'
  if (sources.includes('weather_rule')) return 'info'
  return ''
})

const props = defineProps({ item: Object })
const sourceLabels = {
  transition: '历史转移',
  knowledge: '知识匹配',
  stage_frequency: '阶段高频',
  weather_rule: '天气规则',
  symptom_rule: '症状规则'
}

function score(key) {
  const value = props.item.scoreBreakdown?.[key] ?? 0
  return Number(value).toFixed(2)
}

function sourceLabel(source) {
  return sourceLabels[source] || source
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}
.source-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.details {
  margin-top: 10px;
}
.score-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 10px;
  color: #5f7166;
}
ul {
  padding-left: 18px;
  margin-bottom: 0;
}
</style>
