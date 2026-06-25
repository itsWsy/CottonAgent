<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <b>{{ item.actionName }}</b>
        <el-tag>{{ item.sourceType }}</el-tag>
      </div>
    </template>
    <el-progress :percentage="Math.round(item.score * 100)" />
    <p>建议第 {{ item.expectedDay }} 天执行</p>
    <p>{{ item.reason }}</p>
    <el-divider content-position="left">得分拆解</el-divider>
    <div class="score-grid">
      <span>历史序列</span><b>{{ score('transitionScore') }}</b>
      <span>生育阶段</span><b>{{ score('growthStageScore') }}</b>
      <span>知识匹配</span><b>{{ score('knowledgeMatchScore') }}</b>
    </div>
    <el-divider content-position="left">推荐理由</el-divider>
    <ul>
      <li v-for="reason in item.reasonItems || []" :key="reason">{{ reason }}</li>
    </ul>
  </el-card>
</template>

<script setup>
const props = defineProps({ item: Object })
function score(key) {
  const value = props.item.scoreBreakdown?.[key] ?? 0
  return Number(value).toFixed(2)
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
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
