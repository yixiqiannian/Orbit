## 目标
实现 GitHub 风格的热力图 API，统计每天已完成的任务数量。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建 API (api/dashboard.py 中添加)
```python
@router.get("/heatmap")
def get_heatmap(
    days: int = Query(365, ge=30, le=730),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务完成热力图数据"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, cast, Date
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # 按日期分组统计已完成任务数量
    results = (
        db.query(
            cast(Task.updated_at, Date).label('date'),
            func.count(Task.id).label('count')
        )
        .filter(
            Task.status == 'completed',
            cast(Task.updated_at, Date) >= start_date,
            cast(Task.updated_at, Date) <= end_date
        )
        .group_by(cast(Task.updated_at, Date))
        .all()
    )
    
    # 转换为字典格式
    heatmap = {}
    for row in results:
        heatmap[str(row.date)] = row.count
    
    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "data": heatmap
    }
```

### 2. 验收标准
- [ ] API 返回过去一年每天的任务完成数量
- [ ] 数据格式：`{"start_date": "2025-07-15", "end_date": "2026-07-15", "data": {"2026-07-10": 3, "2026-07-11": 1, ...}}`
- [ ] 性能：单次查询，不循环
