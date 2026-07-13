<template>
  <el-timeline>
    <el-timeline-item v-for="item in items" :key="item.actionCode" >
      <div class="plan-item">
        <el-checkbox :model-value="item.status === 'done'" @change="$emit('toggle', item)" />
        <div>
          <b :class="{ done: item.status === 'done' }">{{ item.actionName }}</b>
          <span>{{ `第 ${item.day} 天` }}</span>
          <p>{{ item.reason }}</p>
        </div>
      </div>
    </el-timeline-item>
  </el-timeline>
</template>

<script setup>
defineProps({ items: Array })
defineEmits(['toggle'])
</script>

<style scoped>
.plan-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.done {
  color: #67c23a;
  text-decoration: line-through;
}
p {
  margin: 4px 0 0;
  color: #6b7d71;
}
span{
  margin-left: 8px;
}
</style>
