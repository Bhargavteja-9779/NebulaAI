import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

export const fetchNodes = () => api.get('/nodes').then(r => r.data)
export const fetchJobs = () => api.get('/jobs').then(r => r.data)
export const fetchLeaderboard = () => api.get('/trust/leaderboard').then(r => r.data)
export const fetchSchedulerLogs = () => api.get('/scheduler/logs').then(r => r.data)
export const fetchAgentLogs = () => api.get('/scheduler/agent-logs').then(r => r.data)
export const fetchExperiments = () => api.get('/orchestrate/experiments').then(r => r.data)
export const fetchDigitalTwin = (jobId) => api.get(`/simulate/digital-twin/${jobId}`).then(r => r.data)

export const submitJob = (data) => api.post('/jobs/submit', data).then(r => r.data)
export const orchestrate = (data) => api.post('/orchestrate', data).then(r => r.data)
export const simulateFailure = (nodeId, jobId) =>
  api.post(`/simulate/failure?node_id=${nodeId}${jobId ? `&job_id=${jobId}` : ''}`).then(r => r.data)
export const simulateRecovery = (nodeId) =>
  api.post(`/simulate/recovery?node_id=${nodeId}`).then(r => r.data)

// Real Distributed Training API
export const fetchDistStatus = () => api.get('/dist/training-status').then(r => r.data)
export const startDistTraining = (targetRounds, batches) => 
  api.post('/dist/start-training', { target_rounds: targetRounds, batches_per_round: batches }).then(r => r.data)
export const resetDistTraining = () => api.post('/dist/reset').then(r => r.data)

export default api
