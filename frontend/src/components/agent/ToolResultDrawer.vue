<template>
  <el-drawer :model-value="visible" title="步骤数据" @close="$emit('close')">
    <pre>{{ JSON.stringify(data, null, 2) }}</pre>
  </el-drawer>
</template>
<script setup>
defineProps({ visible: Boolean, data: null })
defineEmits(['close'])
</script>
