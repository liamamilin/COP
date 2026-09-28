# COP Studio — 工作记忆

> 给新会话的交接文档。开始工作前先读本文件。
> 最后更新：M5 完成时（2026-09-28）

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
| **M5 草稿/发布/版本** | ✅ | **本轮完成**，见 §4.6 |
| M6 局部 AI 精修 | ⬜ | **下一步** |
| M7 Learn Mode | ⬜ | |
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

## 5. 测试与命令

```bash
make test        # 自动起 cop_test 库 + 跑后端/前端测试
make test-db     # 只建测试库，留着便于迭代
make test-backend
make lint
make up / make down
```

后端套件**需要真实 PostgreSQL**，因为 job 抢占、崩溃恢复、唯一约束都是 PG 行为。
无库时**直接 fail 而不是 skip** —— 绿色的测试必须意味着队列真的被执行过。

当前基线：`make test` = 78 后端 + 25 前端，全绿。
其中 30 个是 M5 草稿/发布/版本测试，14 个队列/API，21 个流水线。

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

- **仍没有浏览器实测**。桌面浏览器始终未连接本会话。
  M4 的 SSE 重连、M5 的草稿表单保存/发布，只覆盖到
  单测 + SSR 输出 + curl 打真实容器 API，**没有验证过浏览器里的交互**。
  交互部分（表单脏状态、发布确认框、toast）风险最高，接上浏览器后优先补。
- 前端无 Tailwind/shadcn/TanStack/Zod（规格推荐但未采用，手写约 560 行 CSS）。
  样式质量尚可，但 `settings.appearance.theme` 是**死设置**——能存能选，
  CSS 里没有对应逻辑。属于规格 `15` §13 禁止的"按钮无功能"。
- `scripts/` 缺 `generate-types.*`（规格 `22` 要求）。CI 已在检测
  `packages/cop-types/generated` 陈旧，但生成器本身不存在，
  所以那个检查目前永远不会失败。
- CI 已有 schema 一致性检查 + TS 类型陈旧检测，但无 Playwright E2E
  （规格 `12` 要求）。
- **M5 没做草稿的 `locked_paths` 记录**，M6 会需要（见 §8）。

## 8. 下一步：M6 局部 AI 精修

M5 的 draft 基础设施已就位，M6 直接往上加：

```
GET  /generation-runs/{run_id}/candidate-patch
POST /generation-runs/{run_id}/candidate-patch/accept
POST /generation-runs/{run_id}/candidate-patch/reject
```

验收（规格 `23`）：reject 不改任何东西、accept 只改 Draft、
locked/用户编辑过的兄弟内容要保住。

**关键点：用户手改过的路径必须记下来。** M4 的 `HarnessContext.locked_paths`
已经存在，但那是 run 内的。M6 的 accept 是把 patch 打到 **Draft** 上，
所以需要一份跨 run 的"这些字段是用户写的"记录——
M5 的 PATCH 目前**没有**记录它，这是 M6 要补的第一个东西。
建议给 `drafts` 加 `locked_paths` JSONB，M5 的每次 PATCH 顺手追加。

其余不变量继续遵守（规格 `16`、`24`）：

- Published version 不可变
- 每项目最多一个 active draft
- 发布是显式动作，AI 永不静默覆盖用户内容
- API 路径用 `/processes`，domain 名用 `MainProcess`（规格 `24` §4）
- 前端所有工件渲染走 `artifactSelectors`（`lib/artifact-selectors.ts`）

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
| 规格里程碑 | `cop-studio-development-spec-v1.0/docs/23-coding-agent-milestones.md` |
| 冻结范围 | `cop-studio-development-spec-v1.0/docs/19-v1-scope-freeze.md` |
| 跨层命名契约 | `cop-studio-development-spec-v1.0/docs/24-cross-layer-consistency.md` |
