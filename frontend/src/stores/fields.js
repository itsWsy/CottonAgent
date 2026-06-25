import { defineStore } from 'pinia'
import { createFieldApi, createRecordApi, deleteFieldApi, deleteRecordApi, getFieldApi, listFieldsApi, listRecordsApi, updateFieldApi } from '../api/fields'

export const useFieldStore = defineStore('fields', {
  state: () => ({ fieldList: [], currentField: null, records: [], loading: false }),
  actions: {
    async fetchFields(params = {}) {
      this.loading = true
      try {
        this.fieldList = await listFieldsApi(params)
      } finally {
        this.loading = false
      }
    },
    async fetchFieldDetail(id) {
      this.currentField = await getFieldApi(id)
      return this.currentField
    },
    async createField(data) {
      const field = await createFieldApi(data)
      await this.fetchFields()
      return field
    },
    async updateField(id, data) {
      const field = await updateFieldApi(id, data)
      await this.fetchFields()
      this.currentField = field
      return field
    },
    async deleteField(id) {
      await deleteFieldApi(id)
      await this.fetchFields()
    },
    async fetchRecords(fieldId) {
      this.records = await listRecordsApi(fieldId)
    },
    async createRecord(fieldId, data) {
      await createRecordApi(fieldId, data)
      await this.fetchRecords(fieldId)
    },
    async deleteRecord(recordId, fieldId) {
      await deleteRecordApi(recordId)
      await this.fetchRecords(fieldId)
    }
  }
})
