<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>咨询输入</span>
        <el-dropdown trigger="click" @command="applyTemplate">
          <el-button text>套用模板</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="tpl in templates" :key="tpl.key" :command="tpl.key">{{ tpl.name }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="选择棉田" prop="fieldId">
        <el-select v-model="form.fieldId" filterable placeholder="请选择棉田">
          <el-option v-for="f in fields" :key="f.id" :label="`${f.name} · ${f.growthStage}`" :value="f.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="生育阶段" prop="growthStage">
        <el-select v-model="form.growthStage">
          <el-option v-for="s in stages" :key="s" :label="s" :value="s" />
        </el-select>
      </el-form-item>
      <el-form-item label="症状标签" prop="symptoms">
        <el-checkbox-group v-model="form.symptoms">
          <el-checkbox-button v-for="s in symptoms" :key="s" :label="s" />
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="天气标签" prop="weatherTags">
        <el-checkbox-group v-model="form.weatherTags">
          <el-checkbox-button v-for="w in weather" :key="w" :label="w" />
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="问题描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="4" maxlength="300" show-word-limit />
      </el-form-item>
      <el-alert title="结果仅供辅助参考，实际农事操作需由专业人员确认。" type="warning" :closable="false" />
      <div class="actions">
        <el-button type="primary" :loading="running" :disabled="running" @click="submit">发起分析</el-button>
        <el-button :disabled="running" @click="reset">重置</el-button>
      </div>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({ fields: Array, selectedFieldId: Number, running: Boolean, initialValue: Object })
const emit = defineEmits(['submit'])
const formRef = ref()
const stages = ['播种期', '苗期', '蕾期', '花铃期', '吐絮期']
const symptoms = ['叶片发黄', '叶片卷曲', '叶片斑点', '发现蚜虫', '发现棉铃虫', '植株生长缓慢', '落蕾', '杂草较多']
const weather = ['高温', '低温', '少雨', '连续降雨', '大风', '正常']
const templates = [
  { key: 'pest', name: '虫情问题模板', growthStage: '花铃期', symptoms: ['发现蚜虫', '叶片卷曲'], weatherTags: ['高温'], description: '最近部分棉株叶片卷曲，并发现虫情迹象，接下来几天应该如何安排监测和记录？' },
  { key: 'growth', name: '长势问题模板', growthStage: '蕾期', symptoms: ['植株生长缓慢', '叶片发黄'], weatherTags: ['正常'], description: '近期棉株长势偏慢，部分叶片发黄，需要如何安排田间巡查和长势评估？' },
  { key: 'rain', name: '雨后检查模板', growthStage: '花铃期', symptoms: ['叶片斑点'], weatherTags: ['连续降雨'], description: '连续降雨后田间出现叶片异常，需要如何安排雨后检查和复查？' },
  { key: 'weed', name: '杂草问题模板', growthStage: '苗期', symptoms: ['杂草较多'], weatherTags: ['正常'], description: '田间杂草较多，想安排后续监测、记录和复查计划。' }
]
const form = reactive({ fieldId: null, growthStage: '花铃期', symptoms: [], weatherTags: [], description: '' })

const tagValidator = (_rule, _value, callback) => {
  if (!form.symptoms.length && !form.weatherTags.length) callback(new Error('请至少选择一个症状或天气标签'))
  else callback()
}
const rules = {
  fieldId: [{ required: true, message: '请选择棉田', trigger: 'change' }],
  growthStage: [{ required: true, message: '请选择生育阶段', trigger: 'change' }],
  symptoms: [{ validator: tagValidator, trigger: 'change' }],
  weatherTags: [{ validator: tagValidator, trigger: 'change' }],
  description: [
    { required: true, message: '请填写问题描述', trigger: 'blur' },
    { min: 0, max: 300, message: '问题描述长度需在 0 到 300 字之间', trigger: 'blur' }
  ]
}

watch(() => props.selectedFieldId, (id) => {
  if (id && !form.fieldId) form.fieldId = Number(id)
}, { immediate: true })

watch(() => props.initialValue, (value) => {
  if (value) Object.assign(form, { ...value, fieldId: value.fieldId ? Number(value.fieldId) : form.fieldId })
}, { immediate: true, deep: true })

function applyTemplate(key) {
  const tpl = templates.find((item) => item.key === key)
  if (!tpl) return
  Object.assign(form, {
    fieldId: form.fieldId || props.selectedFieldId || null,
    growthStage: tpl.growthStage,
    symptoms: [...tpl.symptoms],
    weatherTags: [...tpl.weatherTags],
    description: tpl.description
  })
  formRef.value?.clearValidate()
}

async function submit() {
  await formRef.value.validate()
  emit('submit', { ...form })
}

function reset() {
  Object.assign(form, { fieldId: props.selectedFieldId || null, growthStage: '花铃期', symptoms: [], weatherTags: [], description: '' })
  formRef.value?.clearValidate()
}
</script>

<style scoped>
.card-header,
.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.actions {
  justify-content: flex-start;
  margin-top: 14px;
}
</style>
