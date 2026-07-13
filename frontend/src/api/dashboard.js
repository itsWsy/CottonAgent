import request from '../utils/request'

export const summaryApi = () => request.get('/dashboard/summary')
export const trendApi = () => request.get('/dashboard/task-trend')
export const distributionApi = () => request.get('/dashboard/action-distribution')
export const riskDistributionApi = () => request.get('/dashboard/risk-distribution')
export const growthStageDistributionApi = () => request.get('/dashboard/growth-stage-distribution')
export const decisionDistributionApi = () => request.get('/dashboard/decision-distribution')
export const pendingTasksApi = () => request.get('/dashboard/pending-tasks')
export const abnormalFieldsApi = () => request.get('/dashboard/abnormal-fields')
export const recentTasksApi = () => request.get('/dashboard/recent-tasks')
