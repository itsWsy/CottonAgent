<template>
  <el-dialog :model-value="visible" :title="model?.id ? '编辑棉田' : '新增棉田'" width="560px" @close="$emit('close')">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
      <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
      <el-form-item label="品种" prop="variety"><el-input v-model="form.variety" /></el-form-item>
      <el-form-item label="面积" prop="area"><el-input-number v-model="form.area" :min="1" /></el-form-item>
      <el-form-item label="地区" prop="region"><el-input v-model="form.region" /></el-form-item>
      <el-form-item label="生育阶段" prop="growthStage"><el-select v-model="form.growthStage"><el-option v-for="s in stages" :key="s" :label="s" :value="s" /></el-select></el-form-item>
      <el-form-item label="播种日期"><el-date-picker v-model="form.sowingDate" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="$emit('close')">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
  </el-dialog>
</template>
<script setup>
import { reactive, ref, watch } from 'vue'
const props = defineProps({ visible: Boolean, model: Object })
const emit = defineEmits(['close', 'submit'])
const stages = ['播种期', '苗期', '蕾期', '花铃期', '吐絮期']
const formRef = ref()
const form = reactive({ name: '', variety: '', area: 1, region: '', growthStage: '苗期', sowingDate: '', description: '' })
const rules = { name: [{ required: true, message: '请输入名称' }], variety: [{ required: true, message: '请输入品种' }], region: [{ required: true, message: '请输入地区' }] }
watch(() => props.model, (val) => Object.assign(form, { name: '', variety: '', area: 1, region: '', growthStage: '苗期', sowingDate: '', description: '' }, val || {}), { immediate: true })
async function submit() {
  await formRef.value.validate()
  emit('submit', { ...form })
}
</script>
