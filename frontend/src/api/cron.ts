import api from './index'

export interface CronJob {
  id: string
  name: string
  schedule: string
  enabled: boolean
  last_run?: string | null
  status?: string | null
}

export interface CronExecution {
  id: number
  cron_job_id: string
  status: string
  result?: string
  error_message?: string
  executed_at: string
}

export const cronApi = {
  listJobs() {
    return api.get<any, CronJob[]>('/api/cron/jobs/list')
  },
  runJob(jobId: string) {
    return api.post<any, { success: boolean; message: string }>(`/api/cron/jobs/${jobId}/run`)
  },
  listExecutions(jobId?: string) {
    return api.get<any, CronExecution[]>('/api/cron/executions', { params: { job_id: jobId } })
  }
}
