/**
 * @typedef {Object} AgentStep
 * @property {string} stepId
 * @property {string} name
 * @property {'waiting'|'running'|'success'|'failed'} status
 * @property {string|null} startTime
 * @property {string|null} endTime
 * @property {number} duration
 * @property {unknown} input
 * @property {unknown} output
 * @property {Object|null} toolCall
 * @property {string} summary
 * @property {string} errorMessage
 *
 * @typedef {Object} SseEvent
 * @property {string} type
 * @property {string} taskId
 * @property {number} timestamp
 * @property {unknown} data
 */
export {}
