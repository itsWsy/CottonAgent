<template>
  <div class="page">
    <PageHeader :title="field?.name || '棉田详情'">
      <template #prefix>
        <el-button @click="goBack">返回</el-button>
      </template>
      <el-button type="primary" @click="$router.push({ path: '/agent', query: { fieldId: field?.id } })">去 Agent 工作台</el-button>
    </PageHeader>

    <el-descriptions v-if="field" :column="3" border>
      <el-descriptions-item label="品种">{{ field.variety }}</el-descriptions-item>
      <el-descriptions-item label="地区">{{ field.region }}</el-descriptions-item>
      <el-descriptions-item label="面积">{{ field.area }} 亩</el-descriptions-item>
      <el-descriptions-item label="生育阶段">{{ field.growthStage }}</el-descriptions-item>
      <el-descriptions-item label="播种日期">{{ field.sowingDate }}</el-descriptions-item>
      <el-descriptions-item label="描述">{{ field.description }}</el-descriptions-item>
    </el-descriptions>

    <el-card style="margin-top:16px">
      <template #header>历史农事记录</template>
      <FarmRecordForm @submit="addRecord" />
      <FarmRecordTimeline :records="store.records" @delete="removeRecord" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageHeader from '../components/common/PageHeader.vue'
import FarmRecordForm from '../components/field/FarmRecordForm.vue'
import FarmRecordTimeline from '../components/field/FarmRecordTimeline.vue'
import { useFieldStore } from '../stores/fields'

const route = useRoute()
const router = useRouter()
const store = useFieldStore()
const field = computed(() => store.currentField)

function goBack() {
  router.back()
}

async function addRecord(data) {
  await store.createRecord(Number(route.params.id), data)
}

async function removeRecord(record) {
  await store.deleteRecord(record.id, Number(route.params.id))
}

onMounted(async () => {
  await store.fetchFieldDetail(Number(route.params.id))
  await store.fetchRecords(Number(route.params.id))
})
</script>
