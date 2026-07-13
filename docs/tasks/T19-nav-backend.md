## 目标
实现导航网站的数据库模型和 API，支持分类管理。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建导航分类模型 (models/nav_category.py)
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class NavCategory(Base):
    __tablename__ = "nav_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    icon = Column(String(50), nullable=True, comment="图标")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now())
```

### 2. 创建导航网站模型 (models/nav_site.py)
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class NavSite(Base):
    __tablename__ = "nav_sites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("nav_categories.id"), nullable=False)
    name = Column(String(200), nullable=False, comment="网站名称")
    url = Column(String(500), nullable=False, comment="网站地址")
    icon = Column(String(500), nullable=True, comment="图标URL")
    description = Column(String(500), nullable=True, comment="描述")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now())
    
    category = relationship("NavCategory", backref="sites")
```

### 3. 创建 Schema (schemas/nav.py)
- NavCategoryCreate/Response
- NavSiteCreate/Update/Response

### 4. 实现 API (api/nav.py)
- GET /api/nav/categories - 获取分类列表
- POST /api/nav/categories - 创建分类
- PUT /api/nav/categories/{id} - 更新分类
- DELETE /api/nav/categories/{id} - 删除分类
- GET /api/nav/sites - 获取导航列表（可按分类筛选）
- POST /api/nav/sites - 创建导航
- PUT /api/nav/sites/{id} - 更新导航
- DELETE /api/nav/sites/{id} - 删除导航
- GET /api/nav/stats - 获取统计数据

### 5. 更新 models/__init__.py

## 验收标准
- [ ] 模型创建完成
- [ ] API 可正常调用
- [ ] 支持分类和导航的 CRUD
