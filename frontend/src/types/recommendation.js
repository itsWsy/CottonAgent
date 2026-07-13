/**
 * @typedef {Object} Recommendation
 * @property {string} actionCode
 * @property {string} actionName
 * @property {number} score
 * @property {Object} scoreBreakdown
 * @property {number} scoreBreakdown.transitionScore
 * @property {number} scoreBreakdown.knowledgeScore
 * @property {number} scoreBreakdown.growthStageScore
 * @property {number} scoreBreakdown.weatherSuitabilityScore
 * @property {number} scoreBreakdown.symptomUrgencyScore
 * @property {number} scoreBreakdown.recencyPenaltyScore
 * @property {number} scoreBreakdown.finalScore
 * @property {number} expectedDay
 * @property {string} reason
 * @property {string[]} reasonItems
 * @property {string[]} candidateSources
 * @property {string} sourceType
 */
export {}
