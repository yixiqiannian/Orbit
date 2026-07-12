import api from './index'

export interface TaskStats {
  total: number
  pending: number
  in_progress: number
  completed: number
  completed_today: number
  overdue: number
}

export interface CronStats {
  total_jobs: number
  success_rate: number
}

export interface ReadingStats {
  total_books: number
  reading: number
  finished: number
}

export interface RecentTask {
  id: string
  title: string
  status: string
}

export interface RecentExecution {
  id: string
  cron_job_name: string
  status: string
}

export interface DashboardData {
  tasks: TaskStats
  cron: CronStats
  reading: ReadingStats
  recent_tasks: RecentTask[]
  recent_executions: RecentExecution[]
}

export const dashboardApi = {
  getStats() {
    return api.get<any, DashboardData>('/api/dashboard')
  }
}
