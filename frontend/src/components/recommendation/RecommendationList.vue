<template>
  <div class="list">
    <RecommendationCard v-for="item in items" :key="item.actionCode" :item="item" />
    <el-empty v-if="!items?.length" description="暂无推荐" />
  </div>
</template>
<script setup>
import RecommendationCard from './RecommendationCard.vue'
defineProps({ items: Array })
</script>
<style scoped>
.list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
</style>
