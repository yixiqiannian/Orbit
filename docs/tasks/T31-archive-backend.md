## 目标
实现任务归档功能，每月自动归档已完成任务。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 更新任务模型 (models/task.py)
添加字段：
```python
archived = Column(Boolean, default=False)  # 是否归档
archived_month = Column(String(7), nullable=True)  # 归档月份，如 2026-07
```

### 2. 创建归档 API (api/tasks.py)
```python
@router.post("/archive")
def archive_tasks(
    month: str = Query(None, description="归档月份，如 2026-07，不传则归档上月"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """归档已完成的任务"""
    from datetime import datetime, timedelta
    
    if not month:
        # 默认归档上月
        today = datetime.now()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        month = last_day_last_month.strftime("%Y-%m")
    
    # 查找需要归档的任务
    # 条件：status=completed, created_at 在指定月份, 未归档
    year, month_num = map(int, month.split('-'))
    start_date = datetime(year, month_num, 1)
    if month_num == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month_num + 1, 1)
    
    tasks = db.query(Task).filter(
        Task.status == TaskStatus.COMPLETED,
        Task.created_at >= start_date,
        Task.created_at < end_date,
        Task.archived == False
    ).all()
    
    for task in tasks:
        task.archived = True
        task.archived_month = month
    
    db.commit()
    
    return {
        "message": f"已归档 {len(tasks)} 个任务到 {month}",
        "count": len(tasks),
        "month": month
    }
```

### 3. 更新任务列表 API
添加筛选参数：
```python
@router.get("/")
def list_tasks(
    ...
    archived: Optional[bool] = None,
    archived_month: Optional[str] = None,
    ...
):
    query = db.query(Task)
    ...
    if archived is not None:
        query = query.filter(Task.archived == archived)
    if archived_month:
        query = query.filter(Task.archived_month == archived_month)
    ...
```

### 4. 添加定时归档任务
在 Hermes 中创建定时任务，每月1号执行：
```
任务名：任务归档
调度：0 0 1 * *  (每月1号 00:00)
Prompt：调用 API POST /api/tasks/archive 归档上月已完成任务
```

### 5. 更新仪表盘 API
添加归档统计：
```python
# 上月归档任务数
last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
archived_count = db.query(Task).filter(
    Task.archived == True,
    Task.archived_month == last_month
).count()

# 本月已完成任务数
this_month = datetime.now().strftime("%Y-%m")
completed_this_month = db.query(Task).filter(
    Task.status == TaskStatus.COMPLETED,
    Task.created_at >= datetime.now().replace(day=1)
).count()
```

### 6. 验收标准
- [ ] 数据库字段添加成功
- [ ] 归档 API 正常工作
- [ ] 任务列表支持 archived 筛选
- [ ] 定时归档任务创建成功
- [ ] 仪表盘显示归档统计
