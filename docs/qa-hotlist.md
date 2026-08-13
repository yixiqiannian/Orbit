# Orbit 热榜模块 T6 QA 验收报告

- 日期: 2026-08-13
- 执行: qa-engineer（kanban t_312fe3ae，hotlist 模块端到端验收）
- 依据: `docs/plans/2026-08-13-hotlist.md` T6 章节
- 浏览器: 本地 Chrome via CDP（browser-harness / agent-browser，与 T5 同套 harness），截图落盘 `G:\Orbit\qa_shots\`

## 环境

| 项 | 值 | 状态 |
|----|----|------|
| 后端 | `cd G:\Orbit\backend && venv\Scripts\python.exe -m uvicorn app.main:app --port 8000` | ✅ 运行中（:8000，health/API 全部响应） |
| 前端 dev | vite dev server :5173 | ✅ 运行中 |
| 登录 | admin / orbit2026（JWT，localStorage 写入） | ✅ 成功 |
| 数据库 | MySQL（hotlist_items 表，source+hot_date+rank 唯一约束） | ✅ 读写正常 |

## 1. 后端启动 ✅

uvicorn 正常监听 :8000，无启动报错；登录、热榜全部接口实测可通。

## 2. 三端点全通 + 数据真实性 ✅

JWT 登录后依次实测（脚本 `qa_shots/qa_hotlist_api.py`）：

| 端点 | 结果 |
|------|------|
| `POST /api/auth/login` | 200，拿到 access_token |
| `POST /api/hotlist/fetch/?source=github` | 200，`{"message":"抓取完成，新增 17 条","count":17}`（清库后首次抓取） |
| `GET /api/hotlist/?source=github` | 200，date=2026-08-13，items=17（rank 升序，字段 title/url/description/language/stars_today/stars_total/forks 完整） |
| `GET /api/hotlist/sources/` | 200，`[{"key":"github","name":"GitHub Trending","url":"https://github.com/trending"}]` |

**数据真实性对照**（脚本 `qa_shots/qa_hotlist_crosscheck.py`，DB 数据 vs 实网抓取的 github.com/trending 页面解析结果）:
- DB items: 17，Live trending 解析: 17
- 匹配数: **17/17**（要求 ≥5，PASS）
- DB top5 = Live top5: cathrynlavery/diagram-design, macro-inc/macro, semantica-agi/semantica, stablyai/orca, msitarzewski/agency-agents
- 星级为实时值（如 diagram-design stars_total 11,535 → 重新抓取后 11,647，数据为当日真实快照）

## 3. 边界用例 ✅

| 用例 | 结果 |
|------|------|
| 无 token 访问 `GET /api/hotlist/` | **401** ✅ |
| 无 token 访问 `GET /api/hotlist/sources/` | **401** ✅ |
| `POST /api/hotlist/fetch/?source=unknown` | **400** `暂不支持数据源: unknown` ✅ |
| 重复 fetch（同日同源） | **200，count=0**（幂等去重生效）✅ |
| `GET /api/hotlist/?source=unknown` | 200 空列表（查询不报错，符合设计） |

## 4. 前端构建 + 页面渲染 ✅

- `npx vite build` ✅ 通过（1.79s；仅有 chunk>500kB 提示，为既有问题非本次引入）
- 浏览器访问 `/hotlist`（真实登录后）：热榜页完整渲染 17 条，排名徽章 / 仓库名外链 / 描述 / 语言 tag / 今日+总 Star / Fork 全部可见
- 截图（`G:\Orbit\qa_shots\`）：
  - `hotlist_list.png` — 浅色模式列表全量渲染（195KB）
  - `hotlist_dark.png` — 深色模式玻璃卡片（192KB）
  - `hotlist_empty_state.png` — 切到 2026-08-01 空态「当天暂无热榜数据，点击立即抓取获取」（190KB）
  - `hotlist_after_reload.png` / `hotlist_persisted.png` — 刷新后数据仍在（DB 持久化）
- 样式实测（getComputedStyle）：卡片 `rgba(17,24,39,0.85)` + `backdrop-filter: blur(20px)` + 圆角 16px；1/2/3 名徽章分别为金/银/铜渐变；仓库外链 `target=_blank rel="noopener noreferrer"`
- 控制台 JS 错误：**0 个**（全程 Runtime.exceptionThrown / console.error 为零）

## 5. 全链路（页面操作 → 数据出现 → 刷新仍在）✅

1. 清空当天 DB 数据（删 17 行）→ 刷新页面 → 空态正确显示
2. 点击「立即抓取」→ toast **「抓取完成，新增 17 条」** → 列表 17 条数据出现
3. 再次点击 → toast「抓取完成，新增 0 条」（幂等）
4. 刷新页面 → 17 条仍在（从 DB 读出，非前端缓存）→ **持久化验证通过**

## 通过项 / 问题项清单

### 通过项（9/9）

- [x] P1 后端启动正常（uvicorn :8000）
- [x] P2 fetch → list → sources 三端点全通，JWT 认证生效
- [x] P3 数据真实：与 github.com/trending 实网对照 17/17 匹配（≥5 达标）
- [x] P4 边界：无 token 401、source=unknown 400、重复 fetch count=0 幂等
- [x] P5 前端 `npx vite build` 通过
- [x] P6 浏览器实测 /hotlist 列表渲染（截图存证，5 张 PNG）
- [x] P7 全链路：清库 → 页面「立即抓取」→ 数据出现 → 刷新后仍在（DB 持久化）
- [x] P8 UI 细节：金/银/铜排名徽章、语言 tag、Star/Fork 统计、外链新窗口、深色玻璃卡片、空态引导
- [x] P9 浏览器控制台全程 0 JS 错误

### 问题项

- [ ] 无阻塞问题。备注（非缺陷）：
  1. `npx vite build` 报 chunk >500kB 警告（Dashboard 1.1MB 单体 chunk，既有现象，建议后续路由级分包，不影响功能）
  2. 重复抓取同一日返回 count=0 属预期幂等行为；若未来需要强制刷新当日数据，需另行设计覆盖策略

## 结论

**验收通过。** 热榜模块后端 API、数据真实性、边界处理、前端渲染、深/浅模式、空态与全链路持久化全部实测通过，无阻塞缺陷。证据（API 脚本输出 + 5 张浏览器截图）均落盘于 `G:\Orbit\qa_shots\`。
