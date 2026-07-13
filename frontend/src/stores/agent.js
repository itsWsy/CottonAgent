import { defineStore } from 'pinia'
import { acceptTaskApi, createTaskApi, getTaskApi, listTasksApi, rejectTaskApi } from '../api/agent'
import { connectSse } from '../utils/sse'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const LAST_INPUT_KEY = 'cotton_pilot_last_agent_input'

export const FIXED_STEPS = [
  ['validate_input', '校验咨询信息'],
  ['load_field_context', '读取棉田档案'],
  ['load_history_records', '获取历史农事记录'],
  ['retrieve_knowledge', '检索棉花领域知识'],
  ['recommend_next_actions', '推荐下一步农事操作'],
  ['generate_farm_plan', '生成 7 天农事计划'],
  ['generate_final_answer', '生成最终说明'],
  ['save_task_result', '保存任务结果']
]

export const createInitialSteps = () => FIXED_STEPS.map(([stepId, name]) => ({
  stepId,
  name,
  status: 'waiting',
  startTime: null,
  endTime: null,
  duration: 0,
  input: null,
  output: null,
  toolCall: null,
  summary: '',
  errorMessage: ''
}))

function readLastInput() {
  try {
    return JSON.parse(localStorage.getItem(LAST_INPUT_KEY) || 'null')
  } catch {
    return null
  }
}

function writeLastInput(payload) {
  localStorage.setItem(LAST_INPUT_KEY, JSON.stringify(payload))
}

export const useAgentStore = defineStore('agent', {
  state: () => ({
    taskId: '',
    taskStatus: 'idle',
    steps: createInitialSteps(),
    recommendations: [],
    farmPlan: [],
    evidences: [],
    answer: '',
    decision: 'pending',
    riskLevel: '',
    riskReason: '',
    safetyConstraints: [],
    agentTrace: [],
    errorMessage: '',
    sseStatus: 'idle',
    sseMessage: '',
    lastInput: readLastInput(),
    recentRunningTask: null,
    closeSse: null
  }),
  getters: {
    progressPercent(state) {
      const done = state.steps.filter((step) => step.status === 'success').length
      return Math.round((done / state.steps.length) * 100)
    },
    currentRunningStep(state) {
      return state.steps.find((step) => step.status === 'running') || null
    },
    completedToolCalls(state) {
      return state.steps.map((step) => step.toolCall).filter(Boolean)
    },
    canRetry(state) {
      return state.taskStatus === 'failed' && Boolean(state.lastInput)
    }
  },
  actions: {
    async createTask(payload) {
      this.lastInput = { ...payload }
      writeLastInput(this.lastInput)
      this.resetTask({ keepLastInput: true })
      const data = await createTaskApi(payload)
      this.taskId = data.taskId
      this.taskStatus = data.status
      this.connectTaskEvents(data.taskId)
      return data
    },
    async retryLastTask() {
      if (!this.lastInput) throw new Error('暂无可重试的原始输入')
      return this.createTask(this.lastInput)
    },
    async fetchRecentRunningTask() {
      const result = await listTasksApi({ status: 'running', page: 1, pageSize: 1 })
      this.recentRunningTask = result.items?.[0] || null
      return this.recentRunningTask
    },
    async restoreTask(taskId) {
      await this.fetchTaskDetail(taskId)
      if (this.taskStatus === 'running') this.connectTaskEvents(taskId)
    },
    connectTaskEvents(taskId) {
      if (this.closeSse) this.closeSse()
      this.sseStatus = 'connecting'
      this.sseMessage = '正在连接实时事件流'
      this.closeSse = connectSse(
        `${API_BASE}/agent/tasks/${taskId}/events`,
        (event) => this.applySseEvent(event),
        {
          onOpen: () => {
            this.sseStatus = 'connected'
            this.sseMessage = '实时事件流已连接'
          },
          onError: () => {
            this.sseStatus = 'reconnecting'
            this.sseMessage = '实时连接中断，正在尝试恢复'
            if (this.taskId) this.fetchTaskDetail(this.taskId).catch(() => {})
          },
          onClose: () => {
            if (this.taskStatus === 'running') {
              this.sseStatus = 'reconnecting'
              this.sseMessage = '实时连接已关闭，等待恢复'
            }
          }
        }
      )
    },
    /**
     * @param {import('../types/agent').SseEvent} event
     */
    applySseEvent(event) {
      const data = event.data || {}
      if (event.type === 'task_snapshot') {
        this.taskId = data.id
        this.taskStatus = data.status === 'success' ? 'success' : data.status === 'failed' ? 'failed' : 'running'
        this.steps = data.steps?.length ? data.steps : createInitialSteps()
        this.recommendations = data.recommendations || []
        this.farmPlan = data.farmPlan || []
        this.evidences = data.evidences || []
        this.answer = data.finalAnswer || ''
        this.decision = data.decision || 'pending'
        this.riskLevel = data.riskLevel || ''
        this.riskReason = data.riskReason || ''
        this.safetyConstraints = data.safetyConstraints || []
        this.agentTrace = data.agentTrace || []
        this.errorMessage = data.errorMessage || ''
        if (this.taskStatus !== 'running') this.closeTaskStream()
        return
      }
      if (event.type === 'heartbeat') {
        this.sseStatus = 'connected'
        this.sseMessage = '实时事件流正常'
      }
      if (event.type === 'step_start') this.patchStep(data.stepId, { status: 'running', startTime: new Date(event.timestamp).toISOString() })
      if (event.type === 'step_success') {
        this.patchStep(data.stepId, {
          status: 'success',
          endTime: new Date(event.timestamp).toISOString(),
          duration: data.duration || 0,
          output: data.output,
          toolCall: data.output?.toolCall || null,
          summary: data.summary || ''
        })
      }
      if (event.type === 'step_failed') this.patchStep(data.stepId, { status: 'failed', errorMessage: data.errorMessage || '步骤失败' })
      if (event.type === 'recommendations') this.recommendations = data
      if (event.type === 'farm_plan') this.farmPlan = data
      if (event.type === 'evidences') this.evidences = data
      if (event.type === 'answer') this.answer = data.answer || ''
      if (event.type === 'completed') {
        this.taskStatus = 'success'
        this.decision = data.decision || this.decision
        this.riskLevel = data.riskLevel || this.riskLevel
        this.riskReason = data.riskReason || this.riskReason
        this.safetyConstraints = data.safetyConstraints || this.safetyConstraints
        this.agentTrace = data.agentTrace || this.completedToolCalls
        this.sseStatus = 'closed'
        this.sseMessage = '任务已完成，实时连接已关闭'
        this.closeTaskStream()
      }
      if (event.type === 'failed') {
        this.taskStatus = 'failed'
        this.errorMessage = data.errorMessage || '任务失败'
        this.sseStatus = 'closed'
        this.sseMessage = '任务失败，实时连接已关闭'
        this.closeTaskStream()
      }
    },
    patchStep(stepId, patch) {
      const index = this.steps.findIndex((step) => step.stepId === stepId)
      if (index >= 0) this.steps[index] = { ...this.steps[index], ...patch }
    },
    async fetchTaskDetail(taskId) {
      const data = await getTaskApi(taskId)
      this.applySseEvent({ type: 'task_snapshot', taskId, timestamp: Date.now(), data })
      return data
    },
    async acceptTask() {
      await acceptTaskApi(this.taskId)
      this.decision = 'accepted'
    },
    async rejectTask() {
      await rejectTaskApi(this.taskId)
      this.decision = 'rejected'
    },
    closeTaskStream() {
      if (this.closeSse) this.closeSse()
      this.closeSse = null
    },
    resetTask(options = {}) {
      this.closeTaskStream()
      this.taskId = ''
      this.taskStatus = 'idle'
      this.steps = createInitialSteps()
      this.recommendations = []
      this.farmPlan = []
      this.evidences = []
      this.answer = ''
      this.decision = 'pending'
      this.riskLevel = ''
      this.riskReason = ''
      this.safetyConstraints = []
      this.agentTrace = []
      this.errorMessage = ''
      this.sseStatus = 'idle'
      this.sseMessage = ''
      if (!options.keepLastInput) this.lastInput = readLastInput()
    }
  }
})
