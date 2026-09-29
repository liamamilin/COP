# COP Studio — V1 验收收口开发规划

> 制定日期：2026-09-29  
> 状态：待实施  
> 依据：冻结规格、当前实现、LangChain 完整用户路径审计

## 1. 结论与目标

M0–M8 的主要工程能力已经存在，但 V1 仍有跨层验收缺口，不能继续以“功能已写完”代替“产品已完成”。

本轮不新增 Post-V1 功能，也不另起一个 M9。工作目标是重新打开 M1、M3、M4、M7、M8 的相关验收项，完成以下产品闭环：

```text
创建项目
→ 配置真实生成参数
→ 添加资料 / Web Research
→ 生成可执行 COP
→ 检查证据
→ 编辑并发布
→ 按 Stage 学习并完成练习
→ 查看扩展方向
→ 导出、归档与恢复
```

完成定义：用户不需要离开 COP Studio 搜索“下一步到底怎么做”，并且界面上每个设置、引用、完成状态都与实际后端行为一致。

## 2. 当前基线

当前 LangChain 参考项目：

- 5 Goals、5 Main Processes、22 Stages；
- 22 个 Stage 中，0 个有 example，0 个有 implementation details；
- 5 个 Goal、10 个 Stage 带 evidence refs，但项目实际 Source 为 0；
- 5 个 Practice 带 checkpoint questions，但只能阅读，不能记录完成或答案；
- 3 条 Expansion Map 已存在于 Artifact，但界面不可见；
- Shared Foundation 在 Learn Mode 中只是不可操作的 Stage 00。

这些指标作为本轮修复前基线，最终验收必须用同一套统计重新检查。

## 3. 优先级与依赖

```text
R0 验收基线
 └─ R1 内容契约与质量门禁
     ├─ R2 生成设置链路
     ├─ R3 证据链
     └─ R4 内容展示与编辑
          └─ R5 Learn Mode 闭环
               └─ R6 完整性与项目管理
                    └─ R7 Golden Case + 发布验收
```

R2 与 R3 可以并行；R4 必须基于 R1 的稳定内容结构；R5 必须在 R4 可正确展示 Stage 内容后进行。

## 4. 开发批次

### R0 — 固化失败基线

目标：先用自动化测试准确描述当前缺口，防止后续出现“代码改了但产品仍不可用”。

实施：

- 增加 Artifact operational-completeness 检查器；
- 为当前 LangChain fixture 增加失败断言；
- 增加设置生效矩阵测试；
- 增加 orphan evidence ref 检查；
- 增加前端字段覆盖测试，明确哪些 Artifact 字段必须有用户入口；
- 保留已有 Schema validation，区分：
  - L1：结构合法；
  - L2：内容可执行；
  - L3：用户学习闭环可完成。

验收：

- 新增测试在修复前能够稳定复现缺口；
- 测试失败信息必须指出具体 Goal、Stage 或 Source ID；
- 不修改冻结规格，不破坏旧 Published Version 的可读性。

涉及区域：

- `backend/app/harness/steps/critic_rules.py`
- `backend/app/harness/steps/h120_validate.py`
- `backend/tests/`
- `apps/web/e2e/`

### R1 — 可执行内容契约与生成质量门禁

目标：阻止“只有标题和概念、没有操作方法”的 Candidate 被当作完整 COP。

实施：

- 为 implementation detail 定义稳定字段，至少支持：
  - 标题；
  - 操作说明；
  - 命令或代码（适用时）；
  - 预期结果 / 验证方法；
  - 常见失败或注意事项；
- 每个 Stage 必须有 example；
- 每个可执行 Stage 必须至少有一条 implementation detail；
- Setup、安装、配置类 Stage 必须包含具体命令、配置位置和验证步骤；
- H50 Prompt 明确返回上述内容，Schema 对单条内容做结构约束；
- Critic 增加稳定问题码，例如：
  - `MISSING_STAGE_EXAMPLE`；
  - `MISSING_IMPLEMENTATION_DETAIL`；
  - `SETUP_NOT_ACTIONABLE`；
  - `MISSING_VALIDATION_STEP`；
- H110 只修复有问题的 Stage，不重写用户锁定内容；
- 发布前执行 L2 检查。旧 Published Version 继续可读，新 Candidate 不满足则进入 `needs_attention`。

验收：

- 新生成的 LangChain COP：Stage example 覆盖率 100%；
- 可执行 Stage implementation detail 覆盖率 100%；
- “Install LangChain” 页面包含安装命令、Provider 配置、最小运行代码和成功验证；
- 缺少关键内容的模型输出不会静默通过；
- Mock Provider 与真实 Provider 都满足相同契约。

涉及区域：

- `schemas/cop-artifact.schema.json`
- `packages/cop-types/generated/`
- `backend/app/harness/prompts.py`
- `backend/app/harness/schemas.py`
- `backend/app/harness/steps/h50_stages.py`
- `backend/app/harness/steps/critic_rules.py`
- `backend/app/harness/steps/h110_refine.py`

### R2 — 修复生成设置链路

目标：界面展示的每个设置都真实影响生成结果，并遵守 `run > project > app > built-in` 优先级。

实施：

- 新建项目时保存 learner level；
- `preferred_language` 进入项目级 Generation Settings，而不是只作为展示字段；
- 去掉 Overview 中硬编码的 `new` / `standard`；
- 统一 `mode` 与 `generation_depth`，避免请求记录与实际执行不一致；
- 在 Project Settings 中提供项目级生成覆盖项；
- Generation Panel 显示本次运行的最终有效设置，并允许必要的 run override；
- 将 `detail_density` 接入 H50 内容密度；
- 将 `evidence_density` 接入 H20/H30/H50 的引用策略；
- 明确 `practice_mode=priority|all|off` 的实际行为；
- 在 run metrics 中保存 effective settings 快照，便于审计。

验收：

- 每个设置都有“保存 → 创建 run → Harness 读取”的集成测试；
- 项目中文设置能生成中文 Artifact；
- advanced learner 与 new learner 的输出要求不同；
- compact/detailed、minimal/high 不再产生相同 Prompt；
- UI 显示值、run 记录值、Harness 实际值一致。

涉及区域：

- `apps/web/components/new-project-form.tsx`
- `apps/web/components/generation-panel.tsx`
- `apps/web/components/project-settings-form.tsx`
- `backend/app/api/settings.py`
- `backend/app/api/generations.py`
- `backend/app/jobs/runner.py`
- `backend/app/harness/steps/`

### R3 — 建立可解析的证据链

目标：任何 Evidence Ref 都能打开真实来源，不再出现 Artifact 声称有证据、Source Manager 却为空的情况。

实施：

- 为 Evidence Ref 建立统一解析器；
- 普通 Source 与 Exa Search Result 使用同一可追溯 source ID 规则；
- 将 Web Research 结果持久化为项目 Source Snapshot，至少保留：
  - URL；
  - 标题；
  - bounded excerpt；
  - 抓取时间；
  - provider；
- Candidate 发布前检查全部 evidence refs 可解析；
- Source 被删除时阻止产生悬空引用，或保留不可变快照；
- Stage、Goal 页面增加 Evidence 区域，可跳转到 Source Preview；
- Markdown/JSON export 保留引用和来源清单。

验收：

- orphan evidence refs = 0；
- 任何 Stage/Goal 引用都能从 UI 打开来源；
- 开启 Exa 后，搜索结果在服务重启后仍可追溯；
- 未提供来源时，不生成伪造 source ID；
- Evidence density 设置有可验证差异。

涉及区域：

- `backend/app/research/`
- `backend/app/jobs/worker.py`
- `backend/app/api/sources.py`
- `backend/app/db/models.py`
- `apps/web/components/source-manager.tsx`
- Goal / Stage 页面
- export 生成器

### R4 — 补齐内容展示与修订能力

目标：Artifact 中已经存在的重要信息都能被用户看到；用户可以修复内容，而不必直接编辑 JSON。

实施：

- Stage 页面展示：
  - implementation details；
  - example；
  - evidence；
  - validation result；
  - common failures（通过关联 Operation）；
- 支持命令、代码和普通说明的安全渲染与复制；
- Learn Mode 与普通 Stage 页面复用同一内容组件，避免两处渲染漂移；
- Draft Editor 支持编辑 example 和 implementation details；
- 保持结构字段和引用字段只读；Evidence 的修改通过选择 Source 完成，而不是手写 ID；
- Goal 页面展示 prerequisite Goals 和 evidence；
- Domain Overview 展示 non-goals；
- Operation 页面展示 common failures。

验收：

- Artifact 必须字段的前端覆盖测试通过；
- 用户能在 Draft 中补充一个命令和验证步骤，发布后正确显示；
- 长代码、空字段和旧版本不会导致页面崩溃；
- Stage 与 Learn 对相同内容的渲染一致。

涉及区域：

- `apps/web/app/projects/[projectId]/stages/[stageId]/page.tsx`
- `apps/web/components/learn-view.tsx`
- `apps/web/components/draft-editor.tsx`
- `apps/web/lib/draft-editing.ts`
- Goal / Operation / Overview 页面

### R5 — 完成 Learn Mode 学习闭环

目标：用户不仅能阅读 Stage，还能实际完成 Foundation、Practice 和 Checkpoint，并在刷新后恢复状态。

实施：

- Shared Foundation Stage 可打开、可学习、可记录进度；
- Foundation 进度按 Version 共享，不为每个 Goal 重复计算；
- Practice 增加状态：`not_started | in_progress | completed`；
- Checkpoint 支持答案或自评，并记录更新时间；
- Goal 完成规则明确为：
  - 必需 Foundation 完成；
  - Main Process Stages 完成；
  - 对应 Minimal Practice 完成；
- 显示继续学习位置；
- 支持重新打开 Stage/Practice；
- 旧 Version 的学习记录保持隔离。

数据设计建议：

- 保留现有 Stage Progress；
- 新增 Practice/Checkpoint progress，而不是把不同活动塞进 Stage notes；
- Foundation progress 使用 version + stage 的共享键；
- 数据库约束保证幂等写入。

验收：

- 刷新和服务重启不丢 Foundation、Stage、Practice、Checkpoint 进度；
- 未完成 Practice 时 Goal 不显示完成；
- v1/v2 进度互不污染；
- Learn Mode 完整键盘操作通过 E2E。

涉及区域：

- 数据库迁移与 `backend/app/db/models.py`
- `backend/app/api/learning.py`
- `apps/web/components/learn-view.tsx`
- `apps/web/app/projects/[projectId]/learn/page.tsx`

### R6 — 完整性展示与项目生命周期

目标：收口剩余 V1 可见能力和刚发现的管理断点。

实施：

- 在 Overview 或 Learn 完成区展示 Expansion Map；
- Expansion item 可关联下一个 Goal、能力或外部来源；
- 增加 Archived Projects 页面；
- 支持 Restore；
- 首页明确区分 Active 与 Archived 数量；
- 增加 Duplicate UI；
- Delete 保持二次确认，并明确与 Archive 的区别；
- 统一中英文文案，确保 Artifact 语言与产品导航语言不混淆。

验收：

- 当前 3 条 Expansion Map 可见；
- 归档项目可查找、恢复且数据不丢失；
- Duplicate 得到独立项目；
- Delete 不会被误当成 Archive；
- 没有死按钮或只能通过 API 完成的常规管理动作。

涉及区域：

- Project Overview / Home 页面
- Project Settings
- `apps/web/lib/api.ts`
- Projects API

### R7 — Golden Case、完整 E2E 与发布判定

目标：用一个真实、完整、可操作的 LangChain 案例证明产品闭环，而不是只证明页面能打开。

实施：

- 重建 deterministic LangChain reference fixture；
- fixture 必须包含真实可执行的 setup、代码、验证步骤、practice、checkpoint 和 evidence；
- 增加完整用户 E2E：
  1. 创建项目；
  2. 选择语言和 learner level；
  3. 添加 Source；
  4. 可选 Exa research；
  5. 生成 Candidate；
  6. 查看 Evidence；
  7. 建 Draft 并编辑 implementation detail；
  8. 发布；
  9. 完成 Foundation、Stage、Practice、Checkpoint；
  10. 查看 Expansion Map；
  11. 导出；
  12. 归档并恢复；
- 对真实 Provider 跑一次受控验收，不把实时网络调用放入 CI；
- 更新 README、MEMORY 和验收清单。

最终发布门禁：

- Backend、Frontend、E2E 全绿；
- 22/22 Stage 有 example；
- 所有可执行 Stage 有 implementation detail；
- 0 orphan evidence refs；
- 所有 UI 设置都有生效测试；
- Foundation/Stage/Practice/Checkpoint 进度均可恢复；
- Expansion Map 可见；
- Archived Project 可恢复；
- 从创建项目到导出、归档的完整路径无死路；
- 人工验收能够回答：“只使用 COP Studio，我能否完成这个 LangChain 最小案例？”

只有以上门禁全部满足，才能重新把 V1 标记为完成。

## 5. 测试策略

每个批次都必须同时提供三层测试：

1. Backend unit/integration：内容规则、设置优先级、数据约束、引用解析；
2. Frontend component/SSR：字段是否展示、空态、旧版本兼容；
3. Playwright E2E：真实点击路径、刷新恢复、错误反馈。

关键回归集合：

- Mock Provider：success、invalid、timeout、rate limit、slow；
- OpenAI-compatible structured output；
- 有 Source / 无 Source / Exa Source；
- 中文 / 英文；
- new / advanced learner；
- 旧 Published Version；
- 200 Stage 大工件；
- 归档/恢复和备份/恢复。

## 6. 交付节奏

建议每个批次独立提交和验收，不把所有修复堆到一个大改动中。

| 批次 | 相对规模 | 建议验收点 |
|---|---:|---|
| R0 | S | 缺口被测试稳定复现 |
| R1 | L | 新 Candidate 内容可执行 |
| R2 | M | 设置端到端生效 |
| R3 | L | 引用全部可追溯 |
| R4 | L | 内容可见、可编辑 |
| R5 | L | 学习闭环可完成 |
| R6 | M | Expansion 与归档恢复可用 |
| R7 | L | Golden Case 与完整 E2E 通过 |

单开发者/单 Agent 的粗略工作量为 8–12 个有效开发日；实际时间取决于真实 Provider 输出稳定性和 Learning Progress 数据迁移复杂度。

## 7. 明确不进入本轮

以下内容继续保持 Post-V1，不用于扩大本轮范围：

- semantic/vector search；
- PDF export；
- GitHub/Drive/Notion/Slack ingestion；
- 协作、账户、云同步；
- 自适应课程、间隔重复；
- 富文本编辑器；
- 多 Provider 路由。

本轮只解决 `Produce COP → Manage COP → Learn COP` 的真实性与完整性。

## 8. 执行记录规则

- 每完成一个批次，在本文件标记状态并附测试结果；
- 每次更改 canonical schema 后必须重新生成 TypeScript 类型；
- 每次前端容器代码变化后使用无缓存 rebuild 验证实际镜像；
- 不用测试 fixture 的绿灯代替真实 Provider 验收；
- 不把“字段存在于 JSON”视为“用户功能已完成”；
- 不在所有发布门禁通过前再次声明 V1 完成。
