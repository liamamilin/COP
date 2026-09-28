# COP Studio — 工作记忆

> 给新会话的交接文档。开始工作前先读本文件。
> 最后更新：M6 完成时（2026-09-28）

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
| **M6 局部 AI 精修** | ✅ | **本轮完成**，见 §4.9 |
| M7 Learn Mode | ⬜ | **下一步** |
| M8 导出 + 加固 | ⬜ | |

规格 `23-coding-agent-milestones.md`：**V1 完成 = M0–M8 全部验收通过**。

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

**根本没有写版本号的 endpoint。** `drafts.py` 里没有任何对 `COPVersion` 的
PATCH/DELETE。测试不是去调一个"应该不存在"的接口，而是**扫 OpenAPI 文档**
断言没有 mutating 路由（`test_no_endpoint_can_mutate_a_published_version`）——
这样以后有人加回来也会红。

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
> 改前端后必须 `docker compose build --no-cache web`，否则你会对着
> 一个"改了没生效"的产物调试很久。我在这上面浪费了好几轮。

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

### `target` 字段一直是死的

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

## 5. 测试与命令

```bash
make test        # 自动起 cop_test 库 + 跑后端/前端测试
make test-db     # 只建测试库，留着便于迭代
make test-backend
make test-e2e    # 浏览器测试，需要 make up 先起栈
make lint
make up / make down
```

后端套件**需要真实 PostgreSQL**，因为 job 抢占、崩溃恢复、唯一约束都是 PG 行为。
无库时**直接 fail 而不是 skip** —— 绿色的测试必须意味着队列真的被执行过。

当前基线：`make test` = 100 后端 + 28 前端，全绿。
其中 22 个是 M6 patch 测试，30 个 M5 草稿/版本，14 个队列/API，21 个流水线。
浏览器层 `make test-e2e` = 16 个，跑真实 Compose 栈，约 45 秒：
M5 草稿全流程 8 个、M4 进度流 3 个、M6 精修 5 个。

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

## 7. 已知缺口

- **Playwright E2E 已就位**，`make test-e2e` 跑，CI 有独立 `e2e` job，
  目前 11 个用例：
  - M5 草稿全流程 8 个：fork / 编辑 / 刷新后仍在 / 发布并记 parent /
    版本不可变 / 拒绝编辑保留输入 / 放弃需确认 / 单草稿规则 / 复数标题
  - M4 进度流 3 个：流式推进到完成 / 取消并保留工作 / 断流降级为轮询
  - M6 精修 5 个：before/after 预览且提议不落盘 / reject 不动任何东西 /
    accept 只改 Draft / **手写句子扛过一次精修** / 无 draft 时不提供入口
- **覆盖缺口**：
  - M2 素材上传/URL、M3 设置与 provider 连接测试，都还没有
  - 键盘可达性（M8 要求）没有覆盖
  - `Last-Event-ID` 断线续传只在**后端**有测试，浏览器侧没做。
    原因是 `slow` 场景下 run 会在断言窗口内跑完，transport 行先消失，
    写出来只会是随机通过。与其加一个 flaky 的，不如等有更稳的注入点。
- 桌面浏览器（Electron）里 React **不完整 hydrate**：loading.tsx 的 Suspense
  fallback 一直留在 DOM，只有一小部分元素挂上 fiber，点任何按钮都没反应。
  **这个现象只在桌面浏览器出现，Playwright 的干净 Chromium 完全正常**
  （74/96 元素 hydrate，无报错），所以判定是桌面会话环境问题，不是应用缺陷。
  以后验证交互一律用 `make test-e2e`，别用桌面浏览器下结论。
- 前端无 Tailwind/shadcn/TanStack/Zod（规格推荐但未采用，手写约 560 行 CSS）。
  样式质量尚可，但 `settings.appearance.theme` 是**死设置**——能存能选，
  CSS 里没有对应逻辑。属于规格 `15` §13 禁止的"按钮无功能"。
- `scripts/` 缺 `generate-types.*`（规格 `22` 要求）。CI 已在检测
  `packages/cop-types/generated` 陈旧，但生成器本身不存在，
  所以那个检查目前永远不会失败。
- CI 已有 schema 一致性检查 + TS 类型陈旧检测 + Playwright E2E（`e2e` job）。


## 8. 下一步：M7 Learn Mode

M6 的 patch 基础设施已就位，M7 直接往上加：

```
GET /projects/{project_id}/learning-progress
PUT /projects/{project_id}/learning-progress
```

表 `learning_progress` 已存在（`project_id` + `version_id` + `goal_id` +
`stage_id` + `status` + `notes`），缺的是 API + UI。

验收（规格 `23`）：刷新不丢进度、切换工件版本不损坏进度记录、
**完整 Main Process 始终可见**。

**最后一个不变量最容易违反。** 前端所有工件渲染必须走 `artifactSelectors`
（`lib/artifact-selectors.ts`），并且任何进度相关的 UI 都不能
"只渲染当前 Stage"——用户在任何时刻都要能看到主线全貌，
这是产品主张（先给结构再给细节）的核心，破坏它比丢进度更严重。

其余不变量继续遵守（规格 `16`、`24`）：

- Published version 不可变
- 每项目最多一个 active draft
- 发布是显式动作，AI 永不静默覆盖用户内容
- API 路径用 `/processes`，domain 名用 `MainProcess`（规格 `24` §4）

M8 之前还欠的：素材上传/URL 的 E2E、设置与 provider 的 E2E、
键盘可达性（规格 `12` 要求）、`scripts/generate-types.*`（规格 `22` 要求，
现在 CI 那个"类型是否陈旧"的检查永远不会失败）。

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
| 浏览器 E2E | `apps/web/e2e/`（draft-loop / progress-stream / refinement） |
| 精修 patch 领域逻辑 | `backend/app/domain/patches.py` |
| 精修 API | `backend/app/api/patches.py` |
| 规格里程碑 | `cop-studio-development-spec-v1.0/docs/23-coding-agent-milestones.md` |
| 冻结范围 | `cop-studio-development-spec-v1.0/docs/19-v1-scope-freeze.md` |
| 跨层命名契约 | `cop-studio-development-spec-v1.0/docs/24-cross-layer-consistency.md` |
