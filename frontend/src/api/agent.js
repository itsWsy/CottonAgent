import request from '../utils/request'

export const createTaskApi = (data) => request.post('/agent/tasks', data)
export const listTasksApi = (params) => request.get('/agent/tasks', { params })
export const getTaskApi = (id) => request.get(`/agent/tasks/${id}`)
export const acceptTaskApi = (id) => request.post(`/agent/tasks/${id}/accept`)
export const rejectTaskApi = (id) => request.post(`/agent/tasks/${id}/reject`)
