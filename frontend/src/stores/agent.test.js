import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { useAgentStore } from './agent'

describe('agent store applySseEvent', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('handles step_start and step_success', () => {
    const store = useAgentStore()
    store.applySseEvent({ type: 'step_start', taskId: 't1', timestamp: 1, data: { stepId: 'validate_input', stepName: '校验咨询信息' } })
    expect(store.steps[0].status).toBe('running')
    store.applySseEvent({ type: 'step_success', taskId: 't1', timestamp: 2, data: { stepId: 'validate_input', duration: 10, output: { toolCall: { toolName: 'consultation_validator' } }, summary: '已校验' } })
    expect(store.steps[0].status).toBe('success')
    expect(store.steps[0].duration).toBe(10)
    expect(store.completedToolCalls).toHaveLength(1)
  })

  it('handles recommendations and completed', () => {
    const store = useAgentStore()
    store.applySseEvent({ type: 'recommendations', taskId: 't1', timestamp: 1, data: [{ actionCode: 'A', actionName: '操作', score: 0.8, scoreBreakdown: { finalScore: 0.8 }, reasonItems: ['测试理由'] }] })
    expect(store.recommendations).toHaveLength(1)
    store.applySseEvent({ type: 'completed', taskId: 't1', timestamp: 2, data: { decision: 'pending' } })
    expect(store.taskStatus).toBe('success')
  })

  it('tracks sse heartbeat and closes on failed', () => {
    const store = useAgentStore()
    store.applySseEvent({ type: 'heartbeat', taskId: 't1', timestamp: 1, data: {} })
    expect(store.sseStatus).toBe('connected')
    store.applySseEvent({ type: 'failed', taskId: 't1', timestamp: 2, data: { errorMessage: 'boom' } })
    expect(store.sseStatus).toBe('closed')
  })

  it('handles failed', () => {
    const store = useAgentStore()
    store.applySseEvent({ type: 'failed', taskId: 't1', timestamp: 1, data: { errorMessage: 'boom' } })
    expect(store.taskStatus).toBe('failed')
    expect(store.errorMessage).toBe('boom')
  })
})
