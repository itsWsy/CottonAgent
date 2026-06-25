<template>
  <div class="page">
    <PageHeader title="棉田管理"><el-button type="primary" @click="openCreate">新增棉田</el-button></PageHeader>
    <div class="toolbar">
      <el-input v-model="filters.name" placeholder="按名称筛选" clearable />
      <el-select v-model="filters.growthStage" placeholder="生育阶段" clearable><el-option v-for="s in stages" :key="s" :label="s" :value="s" /></el-select>
      <el-button @click="load">筛选</el-button>
    </div>
    <el-row :gutter="16" v-loading="store.loading">
      <el-col v-for="field in store.fieldList" :key="field.id" :span="8"><FieldCard :field="field" @open="goDetail" @edit="openEdit" @delete="remove" /></el-col>
    </el-row>
    <EmptyState v-if="!store.loading && !store.fieldList.length" />
    <FieldFormDialog :visible="dialogVisible" :model="editing" @close="dialogVisible=false" @submit="save" />
  </div>
</template>
<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'
import FieldCard from '../components/field/FieldCard.vue'
import FieldFormDialog from '../components/field/FieldFormDialog.vue'
import { useFieldStore } from '../stores/fields'
const store = useFieldStore()
const router = useRouter()
const filters = reactive({ name: '', growthStage: '' })
const stages = ['播种期', '苗期', '蕾期', '花铃期', '吐絮期']
const dialogVisible = ref(false)
const editing = ref(null)
const load = () => store.fetchFields(filters)
function openCreate() { editing.value = null; dialogVisible.value = true }
function openEdit(field) { editing.value = field; dialogVisible.value = true }
function goDetail(field) { router.push(`/fields/${field.id}`) }
async function save(data) {
  if (editing.value?.id) await store.updateField(editing.value.id, data)
  else await store.createField(data)
  dialogVisible.value = false
  ElMessage.success('已保存')
}
async function remove(field) {
  await ElMessageBox.confirm(`确认删除 ${field.name}？`, '二次确认')
  await store.deleteField(field.id)
}
onMounted(load)
</script>
