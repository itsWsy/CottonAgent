<template>
  <div class="page">
    <PageHeader title="历史任务">
      <el-button :loading="loading" @click="load">刷新</el-button>
    </PageHeader>

    <el-card class="filter-card">
      <el-form :model="filters" label-width="84px">
        <el-row :gutter="12">
          <el-col :span="6">
            <el-form-item label="任务状态">
              <el-select v-model="filters.status" clearable placeholder="全部状态">
                <el-option label="运行中" value="running" />
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="风险等级">
              <el-select v-model="filters.riskLevel" clearable placeholder="全部风险">
                <el-option label="低风险" value="low" />
                <el-option label="中风险" value="medium" />
                <el-option label="高风险" value="high" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="决策状态">
              <el-select v-model="filters.decision" clearable placeholder="全部决策">
                <el-option label="待确认" value="pending" />
                <el-option label="已接受" value="accepted" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="棉田">
              <el-select v-model="filters.fieldId" clearable filterable placeholder="全部棉田">
                <el-option v-for="f in fields.fieldList" :key="f.id" :label="f.name" :value="f.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="关键词">
              <el-input v-model="filters.keyword" clearable placeholder="搜索问题描述" @keyup.enter="search" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <div class="filter-actions">
              <el-button type="primary" @click="search">筛选</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-alert v-if="errorMessage" class="error-alert" :title="errorMessage" type="error" show-icon :closable="false" />

    <el-table :data="tasks" v-loading="loading" empty-text="暂无历史任务">
      <el-table-column prop="createdAt" label="创建时间" width="200">
        <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
      </el-table-column>
      <el-table-column prop="fieldName" label="棉田" width="140" />
      <el-table-column prop="description" label="问题摘要" min-width="260" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }"><StatusTag :value="row.status" /></template>
      </el-table-column>
      <el-table-column label="风险" width="100">
        <template #default="{ row }"><StatusTag :value="row.riskLevel" /></template>
      </el-table-column>
      <el-table-column label="决策" width="110">
        <template #default="{ row }"><StatusTag :value="row.decision" /></template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }"><el-button link @click="$router.push(`/history/${row.id}`)">详情</el-button></template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        @size-change="load"
        @current-change="load"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import PageHeader from '../components/common/PageHeader.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { listTasksApi } from '../api/agent'
import { useFieldStore } from '../stores/fields'

const fields = useFieldStore()
const loading = ref(false)
const errorMessage = ref('')
const tasks = ref([])
const dateRange = ref([])
const filters = reactive({ status: '', riskLevel: '', decision: '', fieldId: null, keyword: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

watch(dateRange, (range) => {
  filters.dateFrom = range?.[0] || ''
  filters.dateTo = range?.[1] || ''
})

function formatDate(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 19)
}

function buildParams() {
  const params = { page: pagination.page, pageSize: pagination.pageSize }
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) params[key] = value
  })
  return params
}

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listTasksApi(buildParams())
    tasks.value = result.items || []
    pagination.total = result.total || 0
    pagination.page = result.page || pagination.page
    pagination.pageSize = result.pageSize || pagination.pageSize
  } catch (error) {
    errorMessage.value = `历史任务加载失败：${error.message}`
  } finally {
    loading.value = false
  }
}

function search() {
  pagination.page = 1
  load()
}

function resetFilters() {
  Object.assign(filters, { status: '', riskLevel: '', decision: '', fieldId: null, keyword: '', dateFrom: '', dateTo: '' })
  dateRange.value = []
  search()
}

onMounted(async () => {
  await fields.fetchFields()
  await load()
})
</script>

<style scoped>
.filter-card,
.error-alert {
  margin-bottom: 16px;
}
.filter-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
