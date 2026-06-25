<template>
  <el-card>
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

const props = defineProps({ fields: Array, selectedFieldId: Number, running: Boolean })
const emit = defineEmits(['submit'])
const formRef = ref()
const stages = ['播种期', '苗期', '蕾期', '花铃期', '吐絮期']
const symptoms = ['叶片发黄', '叶片卷曲', '叶片斑点', '发现蚜虫', '发现棉铃虫', '植株生长缓慢', '落蕾', '杂草较多']
const weather = ['高温', '低温', '少雨', '连续降雨', '大风', '正常']
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
    { min: 10, max: 300, message: '问题描述长度需在 10 到 300 字之间', trigger: 'blur' }
  ]
}

watch(() => props.selectedFieldId, (id) => {
  if (id) form.fieldId = Number(id)
}, { immediate: true })

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
.actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}
</style>
