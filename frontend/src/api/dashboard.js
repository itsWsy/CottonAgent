import request from '../utils/request'

export const summaryApi = () => request.get('/dashboard/summary')
export const trendApi = () => request.get('/dashboard/task-trend')
export const distributionApi = () => request.get('/dashboard/action-distribution')
export const recentTasksApi = () => request.get('/dashboard/recent-tasks')
