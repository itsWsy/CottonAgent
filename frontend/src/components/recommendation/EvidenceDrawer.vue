<template>
  <el-drawer :model-value="visible" title="推荐依据" size="560px" @close="$emit('close')">
    <el-tabs>
      <el-tab-pane label="知识库依据">
        <el-empty v-if="!items?.length" description="暂无知识库依据" />
        <el-card v-for="item in items" :key="item.id" class="evidence">
          <template #header>
            <div class="evidence-header">
              <b>{{ item.title }}</b>
              <el-tag type="success">匹配分 {{ item.matchScore }}</el-tag>
            </div>
          </template>
          <p>{{ item.content }}</p>
          <div class="tags">
            <el-tag v-for="reason in item.matchReasons" :key="reason" type="warning" effect="light">
              {{ reason }}
            </el-tag>
          </div>
          <p class="source">来源：{{ item.source }}</p>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="说明">
        <p>推荐依据来自棉田档案、历史农事记录、本地棉花知识库和农事序列统计。</p>
        <p>系统只输出监测、记录、复查等辅助性建议，不生成具体农药名称、剂量或自动执行建议。</p>
      </el-tab-pane>
    </el-tabs>
  </el-drawer>
</template>

<script setup>
defineProps({ visible: Boolean, items: Array })
defineEmits(['close'])
</script>

<style scoped>
.evidence {
  margin-bottom: 12px;
}
.evidence-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}
.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.source {
  color: #6b7d71;
}
</style>
