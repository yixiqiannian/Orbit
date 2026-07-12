import api from './index'

export interface CronJob {
  id: string
  name: string
  schedule: string
  prompt: string
  enabled: boolean
  last_run?: string
  last_status?: string
  next_run?: string
}

export interface CronExecution {
  id: string
  job_id: string
  executed_at: string
  status: 'success' | 'error'
  result?: string
  error_message?: string
}

export const cronApi = {
  listJobs() {
    return api.get<any, CronJob[]>('/api/cron/jobs')
  },

  runJob(jobId: string) {
    return api.post<any, { message: string }>(`/api/cron/jobs/${jobId}/run`)
  },

  pauseJob(jobId: string) {
    return api.post(`/api/cron/jobs/${jobId}/pause`)
  },

  resumeJob(jobId: string) {
    return api.post(`/api/cron/jobs/${jobId}/resume`)
  },

  listExecutions(jobId?: string) {
    return api.get<any, CronExecution[]>('/api/cron/executions', {
      params: { job_id: jobId }
    })
  }
}
