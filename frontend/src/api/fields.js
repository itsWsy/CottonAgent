import request from '../utils/request'

export const listFieldsApi = (params) => request.get('/fields', { params })
export const createFieldApi = (data) => request.post('/fields', data)
export const getFieldApi = (id) => request.get(`/fields/${id}`)
export const updateFieldApi = (id, data) => request.put(`/fields/${id}`, data)
export const deleteFieldApi = (id) => request.delete(`/fields/${id}`)
export const listRecordsApi = (fieldId) => request.get(`/fields/${fieldId}/records`)
export const createRecordApi = (fieldId, data) => request.post(`/fields/${fieldId}/records`, data)
export const deleteRecordApi = (id) => request.delete(`/records/${id}`)
