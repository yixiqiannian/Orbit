## 目标
实现任务管理模块的增强功能，包括项目管理、任务分类、过期提示，以及修复切换 bug。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建项目模型 (models/project.py)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy.sql import func
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # 项目名称
    description = Column(Text, default="")  # 项目描述
    status = Column(String(20), default="active")  # active/completed/archived
    start_date = Column(Date, nullable=True)  # 开始日期
    end_date = Column(Date, nullable=True)  # 结束日期
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 2. 创建任务分类模型 (models/task_category.py)
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class TaskCategory(Base):
    __tablename__ = "task_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # 分类名称
    icon = Column(String(50), default="📋")  # 图标
    color = Column(String(20), default="#409EFF")  # 颜色
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
```

### 3. 更新任务模型 (models/task.py)
添加字段：
```python
category_id = Column(Integer, ForeignKey("task_categories.id"), nullable=True)  # 分类
project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # 项目
priority = Column(String(20), default="normal")  # low/normal/high/urgent
due_date = Column(Date, nullable=True)  # 截止日期
```

### 4. 创建 Schema (schemas/project.py, schemas/task_category.py)
```python
# Project Schema
class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    task_count: int = 0  # 关联任务数量
    completed_count: int = 0  # 已完成任务数量
    class Config:
        from_attributes = True

# TaskCategory Schema
class TaskCategoryCreate(BaseModel):
    name: str
    icon: str = "📋"
    color: str = "#409EFF"

class TaskCategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    sort_order: int
    class Config:
        from_attributes = True
```

### 5. 创建 API (api/projects.py, api/task_categories.py)
```python
# Projects API
router = APIRouter(prefix="/api/projects", tags=["项目"])

@router.get("/", response_model=List[ProjectResponse])
def list_projects(...)

@router.post("/", response_model=ProjectResponse)
def create_project(...)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(...)

@router.delete("/{project_id}")
def delete_project(...)

# TaskCategories API
router = APIRouter(prefix="/api/task-categories", tags=["任务分类"])

@router.get("/", response_model=List[TaskCategoryResponse])
def list_categories(...)

@router.post("/", response_model=TaskCategoryResponse)
def create_category(...)

@router.delete("/{category_id}")
def delete_category(...)
```

### 6. 更新任务 API (api/tasks.py)
- 添加 category_id、project_id 筛选
- 创建任务时支持 category_id、project_id、due_date

### 7. 更新仪表盘 API (api/dashboard.py)
- 添加即将过期任务列表（3天内到期）
- 添加项目进度统计

### 8. 注册路由 (main.py)
```python
from app.api.projects import router as projects_router
from app.api.task_categories import router as task_categories_router
app.include_router(projects_router)
app.include_router(task_categories_router)
```

### 9. 验收标准
- [ ] 项目 CRUD API 正常
- [ ] 任务分类 CRUD API 正常
- [ ] 任务支持 category_id、project_id、due_date
- [ ] 即将过期任务 API 正常
- [ ] 数据库表创建成功
