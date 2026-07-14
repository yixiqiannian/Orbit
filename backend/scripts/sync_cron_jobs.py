import sys
import json
sys.path.insert(0, 'G:/g/Hermes/hermes-agent')
from cron.jobs import load_jobs, save_jobs, JOBS_FILE

print(f'JOBS_FILE: {JOBS_FILE}')

# 读取当前文件中的任务
jobs = load_jobs()
print(f'Current jobs in file: {len(jobs)}')

# 从 cronjob 工具获取所有任务
from tools.cronjob_tools import cronjob

result = cronjob(action='list', include_disabled=True)
data = json.loads(result)
all_jobs = data.get('jobs', [])
print(f'All jobs from cronjob: {len(all_jobs)}')

# 找出缺少的任务
existing_ids = {j['id'] for j in jobs}
new_jobs = [j for j in all_jobs if j.get('job_id') not in existing_ids]
print(f'New jobs to add: {len(new_jobs)}')

# 添加新任务
for job in new_jobs:
    schedule_expr = job.get('schedule', '')
    jobs.append({
        'id': job.get('job_id'),
        'name': job.get('name'),
        'prompt': job.get('prompt_preview', ''),
        'skills': job.get('skills', []),
        'schedule': {'kind': 'cron', 'expr': schedule_expr, 'display': schedule_expr},
        'enabled': job.get('enabled', True),
        'state': job.get('state', 'scheduled'),
        'deliver': job.get('deliver', 'local'),
        'workdir': job.get('workdir'),
    })
    print(f'  Added: {job.get("name")} ({job.get("job_id")})')

# 保存
save_jobs(jobs)
print(f'Saved {len(jobs)} jobs to {JOBS_FILE}')
