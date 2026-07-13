<template>
  <el-form :inline="true" :model="form" class="record-form">
    <el-form-item label="操作">
      <el-select v-model="form.actionCode" class="action-select" popper-class="action-select-popper" @change="syncName">
        <el-option v-for="a in actions" :key="a.code" :label="a.name" :value="a.code" />
      </el-select>
    </el-form-item>
    <el-form-item label="日期">
      <el-date-picker v-model="form.operationDate" value-format="YYYY-MM-DD" />
    </el-form-item>
    <el-form-item label="说明">
      <el-input v-model="form.description" class="description-input" />
    </el-form-item>
    <el-form-item class="submit-item">
      <el-button type="primary" @click="$emit('submit', { ...form })">新增记录</el-button>
    </el-form-item>
    <!-- <el-button type="primary" @click="$emit('submit', { ...form })">新增记录</el-button> -->
  </el-form>
</template>

<script setup>
import { reactive } from 'vue'

defineEmits(['submit'])

const actions = [
  { code: 'FIELD_SCOUTING', name: '田间巡查' },
  { code: 'PEST_SAMPLE', name: '增加虫情采样' },
  { code: 'COUNT_DENSITY', name: '记录虫口密度' },
  { code: 'GROWTH_ASSESSMENT', name: '长势评估' },
  { code: 'WEED_MONITOR', name: '杂草监测' }
]
const form = reactive({
  actionCode: 'FIELD_SCOUTING',
  actionName: '田间巡查',
  operationDate: new Date().toISOString().slice(0, 10),
  description: ''
})

function syncName() {
  form.actionName = actions.find((a) => a.code === form.actionCode)?.name || form.actionCode
}
</script>

<style scoped>
.record-form {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: nowrap;
  overflow-x: auto;
  padding-bottom: 4px;
}
.record-form :deep(.el-form-item) {
  margin-right: 0;
  margin-bottom: 0;
  flex: 0 0 auto;
}
.action-select {
  width: 220px;
}
.description-input {
  width: 320px;
}
.submit-item {
  margin-left: 4px;
}
</style>

<style>
.action-select-popper {
  min-width: 220px !important;
}
</style>
