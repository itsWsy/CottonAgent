<template>
  <el-card class="field-card" shadow="hover" @click="$emit('open', field)">
    <template #header><b>{{ field.name }}</b></template>
    <p>{{ field.variety }} · {{ field.region }}</p>
    <p>{{ field.area }} 亩 · {{ field.growthStage }}</p>
    <p class="desc">{{ field.description }}</p>
    <div class="actions" @click.stop>
      <el-button size="small" @click="$emit('edit', field)">编辑</el-button>
      <el-button size="small" type="danger" @click="$emit('delete', field)">删除</el-button>
    </div>
  </el-card>
</template>
<script setup>
defineProps({ field: { type: Object, required: true } })
defineEmits(['open', 'edit', 'delete'])
</script>
<style scoped>
.field-card { cursor: pointer; }
.desc { color: #6b7d71; min-height: 22px; }
.actions { display: flex; justify-content: flex-end; gap: 8px; }
</style>
