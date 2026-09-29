# COP Studio — 工作记忆

> 给新会话的交接文档。开始工作前先读本文件。
> 最后更新：M8 实现完成；V1 验收重新打开（2026-09-29）

> **验收状态更新：** M0–M8 的主要实现已存在，但完整用户路径审计发现内容可执行性、
> 证据追溯、设置生效、Learn Mode 闭环、Expansion Map 和归档恢复仍有缺口。
> 在 `DEVELOPMENT_PLAN.md` 的 R0–R7 全部通过前，不再声明 V1 完成。

## 1. 项目是什么

COP Studio 是一个 local-first 的知识生产 + 学习工作台。它把一个主题或一组资料压缩成
`Domain → Goal → Main Process → Stage → Concept × Operation` 的结构化 COP 工件，
再按这条主线引导学习。

核心主张：**先给结构，再给细节**。反对百科全书式堆砌（Encyclopedia Failure）
和 API 手册式罗列（API Manual Failure）。

## 2. 仓库里有什么

| 路径 | 内容 |
|---|---|
| `apps/web/` | Next.js 15 App Router 阅读/学习工作台（手写 CSS，无 Tailwind） |
| `backend/` | FastAPI + SQLAlchemy 2 + Alembic + 独立 worker |
| `packages/cop-types/generated/` | 由 schema 生成的 TS 类型 |
| `schemas/` | 权威 JSON Schema（唯一真源） |
| `fixtures/` | LangChain 参考工件，供 seed 与测试用 |
| `cop-studio-development-spec-v1.0/` | **冻结的 v1.0 规格**，25 篇文档 |

规格包不要改。实现以它为准，冲突时 `15-coding-agent-instructions.md` 给出优先级。

## 3. 里程碑进度

| 里程碑 | 状态 | 说明 |
|---|---|---|
| M0 骨架 | ✅ | monorepo、FastAPI、迁移、worker、Compose、CI |
| M1 渲染器 | ✅ | schema 校验、seed LangChain 工件、层级渲染 |
| M2 素材 | ✅ | 文本/MD/PDF/URL，SSRF 防护 |
| M3 设置 | ✅ | Fernet 加密 key、Mock + OpenAI 兼容适配器 |
| M4 持久化 Harness | ✅ | 见 §4 |
| M5 草稿/发布/版本 | ✅ | 见 §4.6 |
| M6 局部 AI 精修 | ✅ | 见 §4.9；M8 前审计补齐状态机边界 |
| M7 Learn Mode | ✅ | 见 §4.10；M8 前审计补齐旧版本读取与键盘导航 |
| **M8 导出 + 加固** | ✅ | **本轮完成**，见 §4.12 |

上表记录的是工程实现进度，不等于最终产品验收。规格
`23-coding-agent-milestones.md` 仍规定：**V1 完成 = M0–M8 全部验收通过**。
当前收口工作见根目录 `DEVELOPMENT_PLAN.md`。

## 4. M4 已完成内容

### 4.1 Harness 流水线（`backend/app/harness/`）

14 步，顺序即规格 H00–H130：

```
H00 intake → H10 scope → H20 research brief → H30 goals
→ H40 main processes → H50 stage enrichment
→ H60 canonicalize concepts/operations → H70 branches + shared foundation
→ H80 learning layer → H90 assemble → H100 critic → H110 refine
→ H120 validate/repair → H130 finalize
```

**最关键的设计决策：语义 vs 结构的边界**

交给模型（需要判断力）：
- scope 界定、Goal 提炼、Stage 丰富化、Concept/Operation 命名
- Branch 提议、critic、refiner

交给代码（必须可复现、可校验）：
- ID 生成、最终组装、Shared Foundation 检测、引用解析
- schema 校验、版本边界、diff

**Shared Foundation 检测是代码里的精确 normalized-title 比较，不是模型判断。**
这是本里程碑最重要的取舍：模型在这里自信地答错，会静默把一个 Stage 从主线里删掉，
而这恰恰是产品要防止的失败。

Refiner 有围栏（`h110_refine.py`）：字段白名单 + 拒绝改 locked path，
模型不能因为读了 critic 报告就顺手覆盖用户手写内容。

### 4.2 队列（`backend/app/jobs/`）

- `generation_runs` 一行 = 一次运行
- 抢占用 `FOR UPDATE SKIP LOCKED`，可多 worker 并行
- 每步后写检查点到 `checkpoint_json`
- `running` 行心跳超时会被重新入队并从最后检查点恢复
- **恢复时逐个跳过已满足的步骤，不做切片**。切片会重跑后面的步骤覆盖前面的检查点，
  产出的 process 集合会和它所基于的 goals 互相矛盾

### 4.3 API（`backend/app/api/generations.py`）

```
POST /api/v1/projects/{project_id}/generation-runs
GET  /api/v1/projects/{project_id}/generation-runs
GET  /api/v1/generation-runs/{run_id}
GET  /api/v1/generation-runs/{run_id}/progress
GET  /api/v1/generation-runs/{run_id}/events      (SSE，支持 Last-Event-ID)
GET  /api/v1/generation-runs/{run_id}/candidate
POST /api/v1/generation-runs/{run_id}/cancel
```

状态机：`queued → running → completed | needs_attention | failed | cancelled`

**绝不自动发布。** run 只产出 candidate，publish 是用户显式动作。

### 4.4 Mock Provider（已重写）

不再返回 `{mock: true}` 占位，而是**合成真正引用一致的 COP**。
理由：规格的验收路径走 mock 模式，stub 会让 M4 无法验证。

5 个场景：`success` / `invalid` / `timeout` / `rate_limit` / `slow`。
`rate_limit` 会重试后失败，报 `PROVIDER_RATE_LIMITED` 和真实原因，不是笼统失败。

### 4.5 前端

- `components/generation-panel.tsx`：SSE 流式进度 + 轮询兜底，10 个用户可见阶段
- `lib/generation-api.ts`：类型 + 状态文案（失败/取消都明确告知"你的资料和历史版本未变"）
- candidate 就绪后 `router.refresh()` 切到工作区

### 4.6 M5 草稿/发布/版本

表结构改动

`drafts` 加了 `source_run_id`，`base_version_id` 改为**可空**（迁移 `0002`）。
可空是必需的：项目第一个 COP 的 run 没有 `base_version_id`，原来 NOT NULL 会让
首版无法走草稿发布。降级脚本会在有 null 行时**报错**而不是偷偷填值。

### 编辑围栏（`backend/app/domain/drafting.py`）

**只允许改文本字段**，`id` 和所有 `*_ref` / `*_refs` 一律拒绝
（`FIELD_NOT_EDITABLE`）。理由和 M4 的 Shared Foundation 一样：结构归代码。
让 PATCH 能改 `stage_refs`，客户端就能静默把一个 Stage 从主线删掉。

**每次写入前全量校验**，不通过就整个请求拒绝，draft 保持字节不变。
先写后校验会留下一个用户看不出坏在哪的半成品。

必填文本不能清空（`FIELD_REQUIRED`）——`title` 空了 schema 直接不过。

### 状态机

```
run(completed|needs_attention) --from-run--> Draft --publish--> COPVersion
COPVersion --from-version--> Draft
```

- **每项目最多一个 draft**，靠 `drafts.project_id` 的 unique 索引，不是 read-then-write
- 第二个 draft 返回 `409 DRAFT_ALREADY_EXISTS`，不覆盖已有草稿
- publish 后 draft 被删除，否则会遮住刚发布的版本
- `failed` / `cancelled` 的 run **不能**转 draft（`CANDIDATE_NOT_AVAILABLE`）

### 不可变性怎么保证的

**根本没有修改版本内容的 endpoint。** `drafts.py` 里没有任何对 `COPVersion` 的
PATCH/DELETE。M8 增加的 POST export subresource 只从 immutable JSON 派生文件。
测试不是去调一个"应该不存在"的接口，而是**扫 OpenAPI 文档**断言没有版本写路由
（导出子资源除外）——这样以后有人加回来也会红。

### 前端

- `lib/draft-editing.ts`：实体 → 可编辑字段的扁平化，字段名与后端白名单一一对应
- `components/draft-editor.tsx`：单实体编辑表单。保存失败**保留用户输入**
- `components/draft-toolbar.tsx`：发布/放弃，两步确认
- `/projects/[id]/draft` 草稿总览，`/projects/[id]/draft/[kind]/[id]` 单实体编辑
- `/projects/[id]/versions` 版本历史，显示 parent 关系和 Immutable 标记

**`buildPatch(original, current)` 只发改动过的字段**，不是发整张表单。
发全量的话，一次保存会覆盖掉用户没碰过的字段。

### 4.7 浏览器测试抓到的两个 bug

单测和 SSR 检查都看不出来，只有真的点按钮才会暴露。

**1. `"5 main processs"`**（复数拼接）
`ENTITY_LABELS[kind] + "s"` 对 "Main Process" 不成立——它是唯一一个
本身以单数名词结尾的多词实体名。改成显式的 `ENTITY_PLURALS` 映射 + `entityCountLabel()`。

**2. `router.push()` 静默失败**（更严重）
`start-draft-button.tsx` 原本是 `router.push(...)` 紧接着 `router.refresh()`。
结果：**POST 返回 201，draft 建好了，但 URL 纹丝不动**，用户被卡在版本历史页，
看不见自己刚建的 draft。Playwright 抓到的是 `waitForURL` 超时；
手动抓请求才看到 RSC 请求被 `ERR_ABORTED`。

改成 `window.location.assign()`。这是**主动降级**，不是最优解：
客户端导航理论上更好，但这里 push 不可靠，而"创建完必须能到达"是硬需求。
draft 编辑页本身很重，mutation 之后整页重载反而合理。**这是一个 workaround，
根因没查清**（Next 15 + standalone 产物下 `push` 解析成功却不导航）。

> 教训：`docker compose build` 有缓存层，源码改了但镜像里还是旧代码。
> 改前端后用 `make web-rebuild`（= `build --no-cache`）。
> **这个坑今天踩了两次**，症状都是"按钮明明绑了 onClick 却没反应"——
> 看起来极像应用 bug，其实是镜像里跑的还是旧代码。
> 以后改前端第一件事：`make web-rebuild`。

### 4.8 SSE 进度流的 E2E

`apps/web/e2e/progress-stream.spec.ts` + `stream-helpers.ts`。

关键做法：**用 mock 的 `slow` 场景把 run 拖住**，否则 `success` 场景一秒就结束，
任何中间态断言都是碰运气。`setMockScenario()` 直接 PATCH `/settings`，
每个用例 `afterEach` 复位成 `success`，并软删自己建的 project。

三个用例各自的真实风险点：

1. **流式推进**：不能只断言"有 step 事件"，还要断言事件带 `id:`
   —— 没有 id，断线就没法续传。`recordStreamEvents()` 包了 `EventSource`，
   记录 `type#lastEventId#data`。
2. **取消**：断言用户看到的话里有"previous versions are unchanged"。
   一个看起来像数据丢失的取消是最糟的失败方式。
3. **断流降级**：把 `window.EventSource` 换成会抛异常的函数，然后断言
   transport 行显示 **Polling** 而不是 Streaming。
   这条是"不许对用户撒谎"：流已经死了还说在流式推送，会让卡住的 run 看起来还活着。

> 写第 3 条时我踩了个坑：本来想断言"断线重连从 lastEventId 续传"，
> 但 `slow` 场景下 run 会在断言窗口内跑完，`active` 变 false，
> transport 行整个消失，测试变成随机通过/失败。
> **所以这条只保留可确定的部分（降级不撒谎 + 不卡死），
> 续传语义交给后端已有的 `test_event_stream_honours_last_event_id_for_reconnect`。**

### 4.9 M6 局部 AI 精修

`target` 字段一直是死的

M4 的 `GenerationRunCreate` 就有 `target`，存进了 `requested_input`，
但**没有任何代码读它**。也就是说"局部精修"当时会静默地重新生成整个 COP——
正是这个里程碑要防的事：为了改一句话，把周围的东西全重写一遍。

现在 `load_context()` 读它并路由到 `TARGETED_PIPELINE`（只有 H100 → H140）。
工件从**当前 draft** 取，没有 draft 才退回已发布版本——
针对用户没在看的旧内容提改动，before/after 会和屏幕对不上。

### locked_paths 终于有了落点（迁移 0003）

M5 故意留的坑。Harness 的 `locked_paths` 是 run 内的，
而精修是**另一个 run**，所以锁无处可存。`drafts.locked_paths` 解决它。

**只锁真正变了的字段。** PATCH 可能重发整张表单，
无差别上锁会让内容永久不可精修。`apply_entity_edit` 因此返回
`(artifact, changed_fields)` 两个值。

### accept 时要重新检查锁

不能信任提议时算过的结果：用户可能在预览还开着的时候改了那个字段。
所以 accept 会再查一遍 `draft.locked_paths`，
并且 draft 若已变动（`patch_is_stale`）就整个拒绝——
否则会把用户更新的内容静默覆盖掉。

### 状态机

`generating → ready → accepted | rejected | expired`，
存在 `generation_runs.patch_state`（迁移 0004，带 CHECK 约束）。
`ready` 只在 patch 真的存在时才写，所以失败的精修不会显示一个空预览。

patch 有 30 分钟 TTL，并且**预览时会标记 `stale`**。

### 测试发现的一个真问题

mock 的 `_mock_refine` 只在有 `recommended_change` 时产出 revision。
定向精修在没有用户指令时就没有可回显的文本，于是**什么都不产出**，
大部分 accept/reject 测试直接 skip——绿灯但是因为错误的原因。
现在没指令时它会确定性地合成一个改写。

> 变异测试的一个教训：我先破坏 `patches.py` 里的锁检查，**100 个测试全过**。
> 因为真正过滤的是 H110 的 `is_locked`，`patches.py` 那道是**第二道防线**。
> 破坏 `h110_refine.is_locked` 才真的挂了一个测试。
> 冗余防御会让某些变异"活下来"，这不一定说明没覆盖。

### 4.10 M7 Learn Mode

进度属于**版本**，不属于项目。这是 M7 最重要的一条：
切换版本必须看到**各自的**进度，而不是互相覆盖。

`learning_progress` 原本没有唯一约束，`PUT` 会写出重复行。
迁移 0005 加了 `unique (version_id, goal_id, coalesce(stage_id, ''))`：

- 用 `coalesce` 是因为 `stage_id` 可空（Goal 级完成），
  普通 unique 索引把每个 NULL 视为不同，正好在最不容易发现的地方放过重复
- 必须用 `op.execute` 写原生 SQL：alembic 的 `create_index` 会把表达式
  当列名加引号，Postgres 报 `column "coalesce(...)" does not exist`
- 同理不能用 `ON CONFLICT ON CONSTRAINT`（那只接受真正的约束，
  表达式上的 unique 索引不算），要用 `index_elements` 做索引推断

**Goal 完成是推导出来的，不存储。** 存了就得在每次重开 Stage 时失效，
最后一定和它所依据的 Stage 行对不上。

状态机只允许 `completed → in_progress`（重看/重置），其余按文档顺序。

前端：Stage 勾选是**乐观更新**。原本依赖 `router.refresh()` 回填，
UI 要等一次网络往返才变，测试里表现为"点了没反应"。
改成先本地更新、失败再回滚。

### 4.11 M4–M7 完整审计（M8 开始前）

逐项对照里程碑规格并跑回归后，修了四个会破坏状态边界的问题：

- **M4 崩溃恢复**：H100 critic 与 H110 refine 共用 `critic_report`，旧判断会把
  “critic 已完成”误当成“refine 已完成”。检查点现在记录精确 `completed_steps`；
  旧检查点在不确定时安全重跑 H110。
- **M5 版本 lineage**：从旧版本 fork 的草稿发布时，parent 曾被强制改成最新版本。
  现在优先使用 `draft.base_version_id`，真正保留 fork 来源。
- **M6 patch 状态机**：定向 run 创建即进入 `generating`；未 ready 的 patch 不能 reject；
  前端轮询会识别 run 失败并停止，不再无限等待。
- **M7 版本隔离**：`?version=` 过去只切了进度，页面工件仍取 latest。
  现在读取精确版本并核对 project ownership；增加版本选择、前后 Stage 导航、
  显式完成/重开按钮，implementation detail 默认折叠。

对应回归覆盖了“critic 后崩溃恢复”“旧版本 fork parent”“ready 前 reject”以及
“v1/v2 内容与进度同时隔离”。

### 4.12 M8 导出 + 运行加固

**导出**

`POST /api/v1/versions/{version_id}/exports` 支持：

- canonical JSON；
- 单文件可读 Markdown；
- 带 README、artifact.json、逐 Stage/Concept/Operation 文件的 Markdown ZIP。

文件名包含 `-vN`。浏览器端显式读取 `Content-Disposition`，API CORS 暴露该响应头；
导出只读 published artifact，不经过 Draft，也不改变版本。

**运行与可用性**

- `make backup` / `make restore BACKUP=...` 现在操作真正的 Compose PostgreSQL 与
  `/data` volume；先停写入服务，失败也会自动重启。
- 真实执行过一次 backup → 校验 SQL/tar → 恢复同一快照 → 服务健康与记录数检查。
- light/dark/system 与 comfortable/compact 不再是死设置；保存后立即应用。
- 增加 skip link、统一 `:focus-visible`、原生 `<details>` 与键盘 Learn/Export E2E。
- 增加最终 `not-found` 页面；已有全局 error state 保留。
- 选择器建立 WeakMap 索引，200 Stage 渲染不再反复线性查找。
- 增加数 MB 文本、1000 events、100 versions 的性能门槛。
- `scripts/generate-types.py` 从 canonical schema 生成 TS 类型；CI 先生成再检查 diff。
- 增加根级 `.dockerignore`，构建上下文由约 144 MB 降到约 9 KB，避免本地缓存、
  测试 trace 与虚拟环境再次挤满 Docker 磁盘。

冻结端到端路径现已自动化：创建项目 → 粘贴素材 → Mock 生成 → 建 Draft → 发布 →
Learn 中用键盘完成 Stage → 版本页用键盘下载 Markdown，并检查文件内容。

### 4.13 客户端导航加固

最终验收发现 Learn 目标选择的旧 E2E 用 `page.goto(href)` 绕过了真实点击。
生产跟踪确认：Next 15 在同一路径只改变查询参数时会发出正确的 RSC 请求，API 与
RSC 都返回 200，但浏览器端将流标记为 `ERR_ABORTED`，URL 不提交。关闭预取无效。

- Learn 的版本/目标选择改为原生锚点；仍是标准键盘链接，但用完整文档导航避开
  该框架路径。真实点击连续 10 次通过。
- E2E 不再 `page.goto` 目标链接，并增加项目侧栏 Learn → Version history 的真实点击。
- Draft 创建后继续用 `window.location.assign`；这是写操作后的有意刷新，确保新 Draft
  从服务端状态重新渲染，而不是依赖易被取消的 RSC 转换。

### 4.14 真实 Provider + Exa 验收

- Command Code OpenAI-compatible `/models` 与 `/chat/completions` 真实请求成功；
  Exa `/search` 真实请求成功，返回 5 条受限摘要并进入 Harness checkpoint。
- 真实模型首次暴露适配器忽略 JSON Schema；现在每次 structured call
  都显式带 schema，返回值再经 `Draft202012Validator` 验证。
- 修复了 UI 设置按 `generation.*` 嵌套、Harness 却按顶层读取的真实路径 bug；
  fast 模式现在在代码层限制为最多 4 Goals × 5 Stages。
- H60 不再重放 implementation details/example/evidence；H140 只发送目标实体。
  Provider 内部重试耗尽后不再被 Harness 乘法式重试。
- 真实 fast 任务已完整产出并通过校验：4 Goals、4 Main Processes、
  20 Stages、58 Concepts、20 Operations、4 Practices；16 次模型调用全部一次成功、
  0 次重试，候选已转成 active Draft。
- 同一 progress phase 中前一步完成时不再过早显示 `done`；要等该 phase
  的所有步骤都完成。

## 5. 测试与命令

```bash
make test        # 自动起 cop_test 库 + 跑后端/前端测试
make test-db     # 只建测试库，留着便于迭代
make test-backend
make test-e2e    # 浏览器测试，需要 make up 先起栈
make lint
make typecheck
make generate-types
make backup
make restore BACKUP=backups/cop-studio-YYYYMMDD-HHMMSS
make up / make down
```

后端套件**需要真实 PostgreSQL**，因为 job 抢占、崩溃恢复、唯一约束都是 PG 行为。
无库时**直接 fail 而不是 skip** —— 绿色的测试必须意味着队列真的被执行过。

当前基线：135 个后端 + 29 个前端单元/渲染测试，全绿。
后端包含 M4–M7 状态回归、Provider schema/Exa 回归、6 个导出测试与
3 个大数据量门槛。
浏览器层 `make test-e2e` = 25 个，跑真实 Compose 栈：
M5 草稿全流程 8 个、冻结 V1/M8 2 个、M4 进度流 3 个、
M6 精修 5 个、M7 学习 7 个。

> **加字段后必须重跑 `make test-db` / `make test-db-reset`。**
> pytest 的 `db` fixture 只 TRUNCATE，不 ALTER。schema 没跟上时
> 报的是 `UndefinedColumn`，看不出是哪个改动引起的。
> Makefile 现在会在迁移后打这句提示。

后端测试跑之前必须 `make test-db`（或 `make test`）起 `cop_test` 库。
直接 `uv run pytest` 会 13 error + 1 failed——这是 conftest 的 fail-fast 设计，
不是代码坏了。

## 6. 踩过的坑（重要，别再踩）

### 6.1 测试会 TRUNCATE 开发库

`db` fixture 每个 case 之间 TRUNCATE 所有表。早期 `make test` 指向 Compose 的
`cop` 库，直接删掉了本地项目和素材。

**已修**：测试用独立库 `cop_test`（独立端口 55432），
`conftest.py` 见到库名是 `cop`/`postgres`/`template1` **直接拒绝运行**。

### 6.2 本机可能有 PostgreSQL 占用 5432

`localhost:5432` 可能连到 Homebrew 的本地库而不是 Compose 容器，
症状是"某个库存在、某个库不存在"这种诡异现象。
端口已改为 `POSTGRES_HOST_PORT` 可配置，测试用 55432。**不要 kill 用户的库。**

### 6.3 仓库 `.env` 是给 Docker 用的

`DATA_DIR=/data` 在宿主机上不存在或只读，测试会因此在 app lifespan 里失败。
测试用 `TEST_DATA_DIR` 指向临时目录。

### 6.4 规格文档自身有笔误

`docs/05-data-model.md` §3 的"顶层形状"示例 JSON **漏了 `stages`**，
但 `cop-artifact.schema.json` 的 `required` 和 Pydantic 模型都要求它
（spec `25` §5 明确 "stages is first-class and required"）。
遇到冲突时以 schema 文件和 Pydantic 模型为准。

### 6.5 容器里的 `alembic upgrade head` 会打印无关的架构提示

`This program built for i386-apple-darwin11.3.0` 是 uv 链接触发的噪音，
不是错误。判断成功与否看 `alembic_version` 表或后续 API 是否可用。

注意 `stages` 是**必填的一等实体**，spec `05-data-model.md` §3 的示例 JSON
漏了它，但 `cop-artifact.schema.json` 和 Pydantic 模型都要求。信后者。

## 7. 已知风险与非阻塞缺口

- `Last-Event-ID` 断线续传在后端有确定性测试，浏览器侧只测断流后降级轮询。
  `slow` run 在续传断言窗口内可能结束，当前没有加入会随机失败的 E2E。
- M2 的 TXT/Markdown/PDF/URL 有后端集成覆盖；冻结浏览器路径按规格只走 pasted text。
  后续可补各上传类型的浏览器覆盖，但不阻塞 V1 主环。
- 客户端导航在 standalone build 曾出现 `<Link>` / `router.push` 偶发不导航；
  mutation 后的关键跳转使用 `window.location.assign`，Learn 导航使用原生 `<a>`。
  25 个真实 Chromium 场景均通过，但根因仍值得单独排查。
- 桌面内嵌浏览器曾出现与 Chromium 不同的 hydration 行为；交互验收以
  `make test-e2e` 的干净 Chromium 为准。

## 8. V1 状态与后续方向

M0–M8 已按冻结范围实现。最终不变量继续遵守（规格 `16`、`24`）：

- Published version 不可变；
- 每项目最多一个 active draft；
- 发布是显式动作，AI 永不静默覆盖用户内容；
- API 路径用 `/processes`，domain 名用 `MainProcess`。

在扩大功能面之前，优先处理上节的客户端导航根因，并根据真实使用反馈决定
是否补更多素材类型的浏览器覆盖。不要把 spec `19` 明确排除的账号、协作、
向量搜索、PDF export、Redis、图编辑器等重新带回 V1。

## 9. 常用文件速查

| 用途 | 路径 |
|---|---|
| 权威 schema | `schemas/cop-artifact.schema.json` |
| Pydantic 域模型 | `backend/app/domain/cop_models.py` |
| 生成的 TS 类型 | `packages/cop-types/generated/index.ts` |
| Pipeline 顺序 / 阶段名 | `backend/app/harness/steps/__init__.py` |
| 每步 JSON Schema | `backend/app/harness/schemas.py` |
| Prompt 构造 | `backend/app/harness/prompts.py` |
| 稳定 ID 规则 | `backend/app/harness/ids.py` |
| 前端选择器 | `apps/web/lib/artifact-selectors.ts` |
| 草稿编辑围栏 | `backend/app/domain/drafting.py` |
| 草稿/版本 API | `backend/app/api/drafts.py` |
| 前端草稿编辑 | `apps/web/lib/draft-editing.ts` |
| 流水线测试 | `backend/tests/test_harness_pipeline.py` |
| 队列/API 测试 | `backend/tests/test_generation_runs.py` |
| 草稿/版本测试 | `backend/tests/test_drafts.py` |
| 浏览器 E2E | `apps/web/e2e/`（draft-loop / progress-stream / refinement / learn-mode） |
| 学习进度 API | `backend/app/api/learning.py` |
| 精修 patch 领域逻辑 | `backend/app/domain/patches.py` |
| 精修 API | `backend/app/api/patches.py` |
| 导出 API / 渲染 | `backend/app/api/exports.py` / `backend/app/domain/exports.py` |
| 类型生成器 | `scripts/generate-types.py` |
| 备份 / 恢复 | `scripts/backup.sh` / `scripts/restore.sh` |
| M8 冻结路径 E2E | `apps/web/e2e/frozen-v1.spec.ts` |
| 规格里程碑 | `cop-studio-development-spec-v1.0/docs/23-coding-agent-milestones.md` |
| 冻结范围 | `cop-studio-development-spec-v1.0/docs/19-v1-scope-freeze.md` |
| 跨层命名契约 | `cop-studio-development-spec-v1.0/docs/24-cross-layer-consistency.md` |
