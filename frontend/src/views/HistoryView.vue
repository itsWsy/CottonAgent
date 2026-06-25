<template>
  <div class="page">
    <PageHeader title="历史任务" />
    <div class="toolbar">
      <el-select v-model="filters.status" clearable placeholder="任务状态"><el-option label="成功" value="success" /><el-option label="运行中" value="running" /><el-option label="失败" value="failed" /></el-select>
      <el-select v-model="filters.fieldId" clearable placeholder="棉田"><el-option v-for="f in fields.fieldList" :key="f.id" :label="f.name" :value="f.id" /></el-select>
      <el-button @click="load">筛选</el-button>
    </div>
    <el-table :data="tasks">
      <el-table-column prop="createdAt" label="创建时间" width="190" />
      <el-table-column prop="fieldName" label="棉田" width="140" />
      <el-table-column prop="description" label="问题摘要" />
      <el-table-column label="状态"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
      <el-table-column label="是否接受"><template #default="{ row }"><StatusTag :value="row.decision" /></template></el-table-column>
      <el-table-column label="操作"><template #default="{ row }"><el-button link @click="$router.push(`/history/${row.id}`)">详情</el-button></template></el-table-column>
    </el-table>
  </div>
</template>
<script setup>
import { onMounted, reactive, ref } from 'vue'
import PageHeader from '../components/common/PageHeader.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { listTasksApi } from '../api/agent'
import { useFieldStore } from '../stores/fields'
const fields = useFieldStore()
const filters = reactive({ status: '', fieldId: null })
const tasks = ref([])
async function load() { tasks.value = await listTasksApi(filters) }
onMounted(async () => { await fields.fetchFields(); await load() })
</script>
