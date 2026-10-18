# COP Studio — V1 验收收口开发规划

> **优先级说明**：本文管V1 里程碑 M0–M8 的工程实现记录。目标定义、标准（S1–S9）、
> 阶段划分（A0–A5）与当前停靠点以 `docs/COP_GOAL_PLAN_TASK_METHOD.md` 为准。
> 本文出现的实测基线数字若与总纲 §7 不一致，以总纲为准。
>
> 制定日期：2026-09-29  
> 状态：R0–R7 实现完成，自动化门禁全绿；**尚未重新声明 V1 完成**  
> 依据：冻结规格、当前实现、LangChain 完整用户路径审计

> **未完成的两项人工门禁**（自动化无法替代，因此不计入「完成」）：
>
> 1. 真实 Provider / Exa 的受控人工验收——只跑过一次，未记录结果；
> 2. 「只使用 COP Studio，能否完成 LangChain 最小案例」的人工确认。
>
> 自动化门禁实测见 R7 §2 与 §5：后端 274、前端 45、E2E 27 全绿，
> fixture 覆盖率 100%、orphan evidence 0、blocking issue 0。

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

状态：**已完成**（2026-09-29）

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

实现摘要：

新增 `backend/app/domain/quality.py`，把"可不可用"变成一个可断言的对象：

| 层级 | 含义 | 问题码 |
|---|---|---|
| L1 | 结构合法、引用可解析 | `DANGLING_REF`、`ORPHAN_EVIDENCE_REF`、`DUPLICATE_ENTITY_ID` |
| L2 | 内容可执行 | `MISSING_STAGE_EXAMPLE`、`MISSING_IMPLEMENTATION_DETAIL`、`IMPLEMENTATION_DETAIL_NOT_ACTIONABLE`、`SETUP_NOT_ACTIONABLE`、`MISSING_VALIDATION_STEP`、`OPERATION_WITHOUT_COMMON_FAILURES` |
| L3 | 学习闭环可完成 | `WEAK_PRACTICE`、`PRACTICE_WITHOUT_CHECKPOINT`、`EMPTY_EXPANSION_MAP` |

三条设计决定：

1. **"可执行"由 `operation_refs` 判定，不看标题。** 只有 Concept 的 Stage 是阅读步骤，
   强行要求它写 implementation detail 只会逼模型编造无意义内容。
2. **setup 类 Stage 的门槛更高。** 标题命中 `install/setup/configure/安装/配置` 等
   token 时，必须给出可运行命令和验证方法，否则触发 `SETUP_NOT_ACTIONABLE`。
   这正是"Install LangChain"把初学者卡在第一步的原因。
3. **`known_source_ids` 是可选参数。** 不知道项目有哪些 Source 的调用方
   （例如裸 fixture 单元测试）不会收到"全部引用都无法解析"的假报告；
   显式传空集合才会报告。R3 会用真实 Source 集合调用它。

测试结果：

```
后端  160 passed, 12 failed   （12 项全部是本批次固化的缺口基线）
前端   38 passed,  7 failed   （ 7 项全部是 R3/R4/R6 字段覆盖缺口）
```

固化的 19 项失败基线（修复后逐项转绿）：

| 失败测试 | 观察到的缺口 | 归属批次 |
|---|---|---|
| `test_the_reference_artifact_is_operationally_incomplete` | 22/22 Stage 覆盖率 0% | R1 |
| `test_no_level_two_gap_survives...[MISSING_STAGE_EXAMPLE]` | 22 个 Stage 无 example | R1 |
| `test_no_level_two_gap_survives...[MISSING_IMPLEMENTATION_DETAIL]` | 22 个 Stage 无 implementation detail | R1 |
| `test_no_level_two_gap_survives...[OPERATION_WITHOUT_COMMON_FAILURES]` | 12 个 Operation 无失败模式 | R1 |
| `test_install_langchain_stage_is_actionable_and_verifiable` | 安装 Stage 无命令/无验证 | R1 |
| `test_a_publishable_candidate_has_no_blocking_issue` | 44 项 blocking 未设门禁 | R1 |
| `test_reference_evidence_refs_resolve_to_real_sources` | 15 个 orphan evidence ref | R3 |
| `test_detail_density_changes_the_stage_prompt` | 该设置无人读取 | R2 |
| `test_evidence_density_changes_the_citation_prompt` | 该设置无人读取 | R2 |
| `test_practice_mode_priority_and_all_are_distinguishable` | `priority`/`all` 无区别 | R2 |
| `test_learner_level_from_settings_reaches_the_scope_prompt` | H00 只读 run input | R2 |
| `test_preferred_language_on_a_project_reaches_generation` | 该列只用于展示 | R2 |
| 前端 `common_failures` 无入口 | Operation 页面不渲染 | R4 |
| 前端 `non_goals` 无入口 | Overview 不渲染 | R4 |
| 前端 `prerequisite_goal_refs` 无入口 | Goal 页面不渲染 | R4 |
| 前端 `evidence_refs` 无入口 | 无法打开来源 | R3/R4 |
| 前端 `expansion_map` 无入口 | 界面完全不可见 | R6 |
| 前端 `stages.implementation_details` 不可编辑 | 门禁报错后用户无法修复 | R4 |
| 前端 `operations.common_failures` 不可编辑 | 同上 | R4 |

注意：这些是**真实失败**，不是 skip。`strict=True` 的 xfail 与普通断言的区别在于，
修复后测试会由 XPASS 变为 FAILURE，强制把基线升级为正式断言，
不会出现"绿灯但已不再覆盖缺口"的情况。

验收：

- [x] 新增测试在修复前能够稳定复现缺口；
- [x] 测试失败信息必须指出具体 Goal、Stage 或 Source ID；
- [x] 不修改冻结规格，不破坏旧 Published Version 的可读性。

涉及区域：

- `backend/app/domain/quality.py`（新增）
- `backend/tests/test_operational_quality.py`（新增）
- `backend/tests/test_settings_matrix.py`（新增）
- `apps/web/tests/field-coverage.test.ts`（新增）

### R1 — 可执行内容契约与生成质量门禁

状态：**已完成**（2026-09-29）

目标：阻止“只有标题和概念、没有操作方法”的 Candidate 被当作完整 COP。

实现摘要：

契约定义在**三处必须同时成立**，缺一处就回到“静默产出不可用内容”：

1. **Prompt**（`build_stage_prompt`）不再把 example 与 implementation detail
   列为可选 enrichment，而是显式声明“每个 Stage 强制”，并逐字段说明
   `title` / `action` / `command` / `expected_result` / `caution` 各自的作用。
   Setup 类 Stage 额外要求 `command` 与 `expected_result` 同时存在。
   旧 prompt 只说“produce implementation detail candidates”，模型据此给出
   0% 覆盖率；措辞本身是原因之一。
2. **Schema**（`$defs/ImplementationDetail` / `$defs/Example` + H50 输出 schema）
   把单条内容的结构固定下来。`example` 允许 `null`，因此**旧 Published Version
   仍然可读**；只有新内容被约束。
3. **Gate**（`_final_status` + `content_gate_failures`）让不满足契约的候选进入
   `needs_attention` 而不是 `completed`。

三级问题的判定来自 R0 的 `quality` 模块，不再由模型自我评判：
模型读到自己写的 Stage 会认为“示例已经足够”，这种自评不产生信号。
内容类问题一律把 severity 提升到 `major`，确保 H110 一定运行。

**H110 定向修复**：refine 允许写 `implementation_details`、`example`、
`common_failures` 三个结构化字段。若不允许，门禁报错后用户没有出路——
这正是 DEVELOPMENT_PLAN 要求“用户能在 Draft 中补充命令和验证步骤”的原因。
修复时复用 H50 的 `normalize_detail`，否则同一个字段会因写入它的步骤不同
而产生两种格式。

**发布门禁不阻断，但不再静默**：结构非法仍然 422 拒绝；但内容不完整允许发布
（spec `15` §6 要求 “COP remains useful when incomplete”，用户有权发布半成品），
`POST /drafts/{id}/publish` 的响应新增 `content_gate` 字段，列出全部缺口与
具体 Stage id。读取版本时该字段一律缺席，避免“从未做过的判断”看起来像做过。

**Mock Provider 同步升级**为同一契约（`_mock_detail`）。spec `19` 要求 mock
支撑完整验收路径；若 mock 输出旧格式，整套 CI 会绿而真实产品仍然是坏的。

测试结果：

```
后端   183 passed, 11 failed
  新增 tests/test_content_contract.py   26 passed
前端    38 passed,  7 failed  （7 项仍为 R3/R4/R6 字段覆盖缺口）
ruff     All checks passed
typecheck tsc --noEmit 通过
generate-types 幂等，CI stale 检查通过
```

新增断言（`tests/test_content_contract.py`）覆盖：

- 生成结果的 example / implementation detail / common_failures 覆盖率均为 100%；
- 缺少内容的候选 → `needs_attention`，且 `content_gate` 指出具体 Stage id；
- setup Stage 无 command、无 `expected_result` 分别触发对应问题码；
- mock 产出通过 canonical schema 校验（mock 与真实契约同一份）；
- H110 能写入结构化字段、被用户锁定的字段不可被覆盖、空值仍被拒绝；
- 发布完整 COP 时 `content_gate` 为空（负向对照，避免“永远触发”的门禁看起来正常）；
- 读取版本永不带 `content_gate`。

R0 固化的 12 项失败基线中，6 项已由 R1 转为正式断言（生成路径），剩余
6 项重新归属：

| 仍失败 | 新归属 | 说明 |
|---|---|---|
| 5 项 fixture 完整性 | **R7** | seed fixture 需重建为真实可执行内容 |
| 1 项 evidence 解析 | **R3** | orphan evidence ref 需建 Source |

原 R0 表格把 fixture 缺口记在 R1 名下是**归因错误**：R1 修的是生成路径，
seed fixture 是另一份工件。已同步修正测试与文档。

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

状态：**已完成**（2026-09-29）

目标：界面展示的每个设置都真实影响生成结果，并遵守 `run > project > app > built-in` 优先级。

实现摘要：

R0 记录的 5 个死设置已全部接通，每个都有“保存 → 创建 run → Harness 读取”
的端到端测试（`tests/test_settings_matrix.py`，用真实 step 类 + 记录型
provider 驱动，断言 prompt 实际发生变化，而不是断言某个常量被读到）：

| 设置 | 之前 | 现在 |
|---|---|---|
| `detail_density` | 无任何读取 | 进入 H50 prompt，控制 implementation detail 数量与深度 |
| `evidence_density` | 无任何读取 | 进入 H20/H30/H50 的引用策略，控制 `evidence_refs` 数量 |
| `practice_mode` | 仅 `off` 生效 | `priority` / `all` / `off` 三者 prompt 均可区分 |
| `learner_level` | 只读 run input，Settings 值被忽略 | H00 从 `ctx.settings` 读取，Settings 值生效 |
| `preferred_language` | 只用于展示的列 | 进入项目级 generation settings，参与优先级合并 |

同时修掉 Overview 的 `new` / `standard` 硬编码，并统一 `mode` 与
`generation_depth`：此前 `requested_mode` 记录一个值、Harness 读另一个值，
审计时无法回答“这次运行到底用的什么”。

`detail_density` / `evidence_density` 采用**代码层上限**而非仅 prompt 建议，
理由与 `generation_depth` 一致：模型返回 12 条 citation 时，把它裁到 8 条
比在 prompt 里写“请少写”可靠。

测试结果：

```
tests/test_settings_matrix.py   22 passed（此前 17 passed / 5 failed）
后端总计 205 passed, 6 failed（6 项为 R3/R7 遗留）
```

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

状态：**已完成**（2026-09-30）；**证据粒度仍有一个未解问题，见本节末**

目标：任何 Evidence Ref 都能打开真实来源，不再出现 Artifact 声称有证据、Source Manager 却为空的情况。

实现摘要：

**1. 统一 source ID 规则（`backend/app/research/snapshots.py`）**

Exa 结果不再是"只活在 checkpoint 里的合成 source"。每个结果写为真正的
`Source` + `SourceDocument` 行，`type=web_search`，并保存 url、title、
bounded excerpt、**抓取时间**、provider。ID 由 URL 单独决定
（`snapshot_source_id()`），因此**同一 URL 重复搜索会复用快照**而不是堆积
重复 Source——两个指向同一页的 Source 会让用户无法判断 Artifact 引用的是哪一个。

没有 URL 的结果**不落库**：无法重新打开的引用不是可追溯性。

**2. 运行期拒绝伪 source id**

H20/H30 只保留 `ctx.source_bundle` 中真实存在的 id，其余丢弃，并在
`step.warning` 中明确报告。伪引用比没有引用更糟：用户看到"有来源"却点不开。

**3. 读取期解析（`_version_detail`）**

`VersionDetail` 新增 `evidence_sources` 映射，由后端解析。前端不做任何查找，
因为"这个引用能不能打开"取决于项目拥有哪些 Source，只有后端知道。
**key 缺失本身就是"无法解析"的信号**，前端据此明确显示而不是静默隐藏。

**4. 发布期不静默**

`POST /drafts/{id}/publish` 响应新增 `unresolved_evidence`，列出每个悬空引用的
`entity_ref` 与 `source_id`。不阻断发布（用户可能明知故为），但绝不静默。

**5. 用户必须能修**

`implementation_details` / `common_failures` 加入可编辑白名单——
**门禁报错却没有修改入口就是死路**。采用 `|` 分隔的按行格式（而非嵌套输入框），
因为 V1 明确排除富文本编辑器；`|` 而非逗号/换行，因为 shell 命令本身含逗号。

**6. UI 入口（`components/evidence-panel.tsx`）**

Stage 与 Goal 页面展示证据区；无法解析的引用显式标注为
"Unresolved source: `<id>` ... cannot be opened"，而不是隐藏。

测试结果：

```
新增 tests/test_evidence_chain.py   20 passed
后端总计 220 passed, 6 failed（6 项全部为 R7 seed fixture）
```

覆盖：快照落库与复用、无 URL 拒绝落库、ID 确定性、伪 id 丢弃并报告、
`evidence_density` 裁剪与 quote 优先、版本读取解析、发布报告悬空引用、
删除 Source 后引用显式变为未解析、重启后快照仍可解析、
fixture 的 6 个 source id 与其 metadata 声明一致。

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

#### R3 未解问题：引用能定位，但不能就地核对

R3 解决的是**可打开**：15 个引用全部解析到真实 Source，0 orphan。
但「可打开」和「可核对」是两件事，实测数据说明了差别：

```
refs                       = 15
refs_without_an_anchor     = 0     每条都带 segment_id，读者知道去哪一段找
refs_without_a_quote       = 15    没有一条带原文，读者仍要自己去翻
coverage.evidence_anchored = 1.0
```

现在的 `EvidenceRef` 是 `{source_id, segment_id, quote_hint}`，挂在 **Goal / Stage
整体**上。所以读者看到的是「这个 Stage 有来源：LangChain agents guide → 某段」，
而不是「这句话由这一段支撑」。

三个具体缺口：

1. **没有 `claim` 字段。** 引用粒度是实体级而非论断级。一个 Stage 有五个句子，
   证据只说明「这整个 Stage 有出处」，无法指认是哪一个断言被支撑。
2. **`quote_hint` 声明了、UI 也渲染了，但 fixture 里 0/15 填写。**
   `EVIDENCE_LIMITS` 里的 `require_quote` 被声明在三处、被任何代码读取零次——
   正是 R0 要消灭的「看起来存在、实际什么都不做」的那类配置。
   现已改为产出 `refs_without_a_quote` 这个真实数字，不再靠声明。
3. **URL 不在 ref 里**，需要 ref → Source 行 → `uri` 两跳。

这些都是设计决定而不是 bug，所以没有在本轮擅自改动：改 `EvidenceRef` 的形状会
影响 schema、export 格式和 H20/H50 的产出约束。

完整的证据等级设计与未决问题清单见 `docs/proposals/evidence-v1.1.md`
（**草案，未实现**）。其中最重要的一条与 `claim` 无关：

> **Level 2（Executable Evidence）形式上已经存在，但从未被执行过。**
> 22 个 Stage 都有 `command` + `expected_result`，测试只断言字符串非空，
> 没有任何一处运行并比对结果。对一个主张「压缩成**可执行**能力路径」的
> 产品，这比缺 `claim` 字段更严重。Gate 1 会实测这一点。

### R4 — 补齐内容展示与修订能力

状态：**已完成**（2026-09-30）

目标：Artifact 中已经存在的重要信息都能被用户看到；用户可以修复内容，而不必直接编辑 JSON。

实现摘要：

**Stage 内容收敛到单一组件（`components/stage-content.tsx`）**

R4 的核心不是"多加几个字段"，而是**消除两套渲染**。Learn Mode 与 Stage 页面
此前各自渲染 Stage 字段，并已经漂移：Learn 显示 implementation detail，
Stage 页面完全不显示。两者都未显示 evidence。新组件成为唯一渲染入口。

内容按"读者如何行动"排序，而不是按 schema 字段顺序：

1. **HOW TO DO IT** — 逐条 detail，`command` 独立代码块 + 复制按钮，
   `expected_result` / `caution` 用左边框区分
2. **EXAMPLE** — `input` / `output` 各自成块
3. **EVIDENCE** — 可解析则链接到 Source，不可解析则显式标注
4. **WHEN IT GOES WRONG** — 关联 Operation 的 `common_failures`，
   并链接回 Operation 页
5. **CONCEPTS** — 紧凑内联（Stage 页）/ 折叠（Learn）

**其余入口补齐**

- Operation 页面：`common_failures`（原本存储在 12 个 Operation 上、**无处渲染**）
- Goal 页面：`prerequisite_goal_refs`（prerequisites）、`evidence_refs`
- Overview：`domain.non_goals`（原本 4 条 non-goals 完全不可见）
- `StageContent` 与 `EvidencePanel` 为纯展示组件，可在 server 与 client
  两侧复用

**代码/命令安全渲染**

`<pre><code>{value}</code></pre>`，children 而非 `dangerouslySetInnerHTML`。
implementation detail 是模型输出，其中的 `<` `>` `&` 不得被浏览器解释。

**Draft Editor 支持结构化字段**

`implementation_details` / `common_failures` 加入可编辑白名单，
采用 `|` 分隔的按行格式（每行 `title | action | command | expected | caution`）。
**门禁报错却没有修改入口就是死路**——这是 R1 与 R4 的直接耦合点。
分隔符选 `|` 而非逗号/换行：shell 命令本身含逗号，而粘贴的多行命令会被
换行格式静默拆成多条 detail。字段名与后端解析器共用常量。

测试结果：

```
后端   260 passed, 6 failed（6 项全部为 R7 seed fixture）
前端    45 passed（字段覆盖测试全绿，含 expansion_map）
typecheck / eslint  通过
```

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

状态：**已完成**（2026-09-30）

目标：用户不仅能阅读 Stage，还能实际完成 Foundation、Practice 和 Checkpoint，并在刷新后恢复状态。

实现摘要：

**数据模型：迁移 0006**

`learning_progress` 增加 `kind` 判别列（`stage` / `foundation` / `practice` /
`checkpoint`），而不是新建三张几乎相同的表。旧唯一索引
`(version_id, goal_id, coalesce(stage_id,''))` **无法区分 Foundation Stage 行与
主线 Stage 行**——两者 `goal_id` 都为 NULL，会互相冲突。新索引加入 `kind`。

`notes` 字段被复用为 checkpoint 的**答案**：活动身份是
`(version, kind, goal, stage)`，`notes` 是学习者自己的文本，**不能进索引**，
否则同一活动可以被两条不同答案各写一次。

**Foundation 属于 Version，不属于 Goal**

Foundation Stage 记录时 `goal_id` 必须为空串。这是关键设计：每个 Main Process
都从同一批 Foundation Stage 开始，若按 Goal 存储，"我学过没有"就取决于当前
在看哪个 Goal。后端对不匹配组合返回 422（`FOUNDATION_NEEDS_NO_GOAL` /
`STAGE_NOT_FOUNDATION`），而不是默默存一个模糊的行。

**Goal 完成 = Foundation ∧ Stages ∧ Practice ∧ Checkpoints**

仍然是**推导**，不存储。但推导的输入从 1 个变成 3 个。响应新增 `blocked_by`：
一个空进度条又不说原因的 Goal，和坏掉的进度条无法区分。

Practice 状态本身也是推导的：有答案但没勾完成 → `in_progress`。
否则正在做题的人会被告知"尚未开始"。

**Checkpoint 身份 = 问题原文**

答案存在 `notes`，问题原文作为 `stage_id`（主键的一部分）。问题被改写会产生
新行而不是静默覆盖旧答案。空答案被拒绝——清空是删除操作，不是空写入。

**UI**

- `PracticeCard` 从只读变为可完成：状态、每题答案框、失焦保存
- "完成练习"在所有 checkpoint 未答时禁用，并说明原因
- `PracticeRecorder` 让 Goal / Main Process 页面也能记录，不只在 Learn Mode
- Learn 顶部新增 Foundation 清单（整个版本一份）

测试结果：

```
新增 tests/test_learning_loop.py   22 passed
原有 tests/test_learning.py        15 passed（M7 回归保持）
迁移 0006 已应用，测试库已重跑
```

覆盖：Foundation 未完成时 Goal 不完成、Foundation 跨 Goal 只存一份、
Foundation 不能挂在 Goal 下、 Practice 未做时 Goal 不完成、
只答 checkpoint 不足以完成、答案跨刷新保留、回答不存在的问题被拒、
空答案被拒、重复作答替换而非追加、v1/v2 记录隔离、
同一活动并发写只产生一行、Foundation 行与 Stage 行可共存、
无 Practice 的 COP 仍可完成。

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

状态：**已完成**（2026-09-30）

目标：收口剩余 V1 可见能力和刚发现的管理断点。

实现摘要：

**Expansion Map 可见（`app/projects/[projectId]/page.tsx`）**

3 条 Expansion 原本存在于 artifact 且**界面完全不可见**。现在渲染，
每条链接回它所依附的 Goal——"Structured output"因此不是抽象话题，
而是从学习者已经到过的地方出发的方向。

**Archive / Restore**

`GET /projects?status=archived` 精确过滤（`include_archived` 保留兼容）。
`POST /projects/{id}/restore` 只改 status：**Source、版本、学习记录全部保留**，
这正是 Archive 存在而 Delete 不存在的全部理由。
被删除的项目**不能 restore**——否则 Delete 就只是步骤更多的 Archive。

**Duplicate 从"只存在于 API"变为可用**

`POST /projects/{id}/duplicate` 之前只复制 Project 行，产出一个空项目。现在复制：

- **Sources 及其抽取文本**（不复用 `blob_path`：两个 Source 指向同一磁盘文件，
  删一个可能带走另一个的文本）
- **最新已发布版本**（重新生成会得到不同的 COP，而 duplicate 的意义是
  "从已知起点尝试一个修订"；版本号重置为 1，因为副本没有那段历史）
- **generation settings**（否则副本会静默换一种语言或深度重新生成）

UI 放在 Overview 的 manage 区域，而不是只放在没人看的 Settings 里。

**Delete 与 Archive 明确区分**

此前 UI 只有一个 Archive，按钮文案是 "DANGEROUS ACTIONS"，且无路可回——
用户因此学会"archive 就是没了"。现在：

- 分区标题改为 PROJECT LIFECYCLE
- 两个按钮视觉区分（`.danger-button` 用 `--warn` 色）
- 确认文案明确写出区别：Archive 可从首页恢复，Delete 不能
- 已归档项目的设置页只显示 Restore

**首页区分 Active 与 Archived 数量**，归档项目折叠列出并可打开。

测试结果：

```
新增 tests/test_project_lifecycle.py   16 passed
后端   260 passed, 6 failed（6 项全部为 R7 seed fixture）
前端 typecheck / eslint / 45 tests 通过
```

覆盖：归档隐藏、status 过滤、include_archived 兼容、归档保留全部数据、
restore 幂等、已删除项目不可 restore、Delete 与 Archive 的可见性差异、
软删除保留磁盘数据、duplicate 独立性（删原项目不影响副本）、
duplicate 携带 settings、跳过内容选项、未发布时也能 duplicate、
归档项目可 duplicate、已删除不可 duplicate、副本标题可辨识。

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

状态：**已完成**（2026-09-30）

目标：用一个真实、完整、可操作的 LangChain 案例证明产品闭环，而不是只证明页面能打开。

#### 1. Fixture 重建（`backend/scripts/enrich_langchain_fixture.py`）

用脚本而非手改 JSON 重建 seed fixture。22 个 Stage 逐条写入真实的 LangChain 1.x
命令、预期输出和初学者会踩的坑；12 个 Operation 补 `common_failures`。
理由是手改 22 个 Stage 必然重演本批次要修的缺口——写出看似合理但没跑过的示例。

同时生成 `fixtures/reference-langchain-sources.json`：fixture 引用的 6 个 source
id **作为 fixture 的一部分**被交付，seed 为每条创建真实 `Source` + `SourceDocument`
行。引用可追溯的前提是被引用的东西存在；不随 fixture 交付 Source，就是
「引用看起来像证据，用户却点不开」。

#### 2. 门禁实测（同一套统计，不用估计值）

```
stage_example 覆盖率              = 1.0   (22/22)
implementation_detail 覆盖率      = 1.0   (22/22 可执行 Stage)
operation_common_failures 覆盖率  = 1.0   (12/12)
orphan evidence refs              = 0
blocking L2 issues                = 0
expansion_map 条目                = 3
practices with checkpoints        = 5/5
"Install LangChain" 有 command     = True
"Install LangChain" 有 expected   = True
shared foundations                = 1 组，覆盖 2 个 Stage
```

#### 3. 完整用户路径（`apps/web/e2e/golden-case.spec.ts`）

单条测试走完：创建项目 → 设置生效 → Source → 生成 → Draft 编辑
implementation detail → 发布 → Stage 页看到方法/示例/证据 → Expansion Map 可见
→ non-goals 可见 → Learn 完成 Foundation / Stage / Practice / Checkpoint →
Goal 完成（经服务端 `blocked_by` 确认）→ 刷新后进度仍在 → 导出 Markdown
→ 归档 → 恢复 → 版本与学习记录均存活。

两条断言上的设计决定：

- **等待服务端，不等待 DOM。** 面板有乐观更新，DOM 断言在写入确认前就通过，
  紧接其后的服务端断言就会因为「还没追上」而失败。Goal 完成以 `blocked_by`
  为准——UI 说完成而服务端不认可，正是本批次要消除的 bug。
- **每个活动单独确认。** Stage 与 Checkpoint 逐个点击并轮询服务端状态。
  面板每次保存后 `router.refresh()` 会重渲染列表，连续点多个会与之竞争，
  结果是某些 Stage 被重复标记。

#### 4. 修复过程中发现并修掉的三个真问题

**(a) Mock 的确定性 fallback 依赖了错误的 id 假设。**
`_synthesise_refinement` 在 artifact 的 `goals` 集合里找目标实体，但 H140 故意
只发送 `targeted_artifact_view`（单个实体），没有集合可搜。于是**每一次定向
refine 都提出空 patch**：用户看到空 diff 且没有任何解释，表现为功能损坏而不是
「无需修改」。同时 `_mock_refine` 用按首个点切分 `entity_ref` 的方式推导实体键，
仅因为生成的 id 恰好以类型开头才碰巧可用。

**(b) `_issues_for` 构造了不存在的 entity_ref。**
它用 `{entity_type}.{entity_id}`，而 id 本身已带类型前缀，于是得到
`goal.goal.basic-agent`——没有这样的实体。两个后果都伪装成别的问题：
作用域过滤永远匹配不到真实 critic issue（每次 refine 都退回合成的
「用户要求改进」），refiner 拿到的是无法解析的引用。
两个 bug 方向相反、互相抵消，所以整套 refine 测试一直是绿的。

**(c) E2E 套件的正确性依赖 spec 顺序。**
provider 是**全局状态**，此前由 `frozen-v1.spec.ts` 的 `finally` 负责恢复——
它恢复的是开发者真实的 OpenAI 兼容端点。之后运行的所有 spec 于是发起真实网络
调用、产不出 candidate，失败方式看起来像产品回归。
现在 mock 由 `globalSetup` 设为整轮前置条件，由 `globalTeardown` 还原，
并**读回校验**：还原不完整会打印警告而不是静默失败。

#### 5. 测试结果

```
后端   274 passed          （0 failed）
前端    45 passed          （0 failed）
E2E     27 passed          （0 failed）
ruff / eslint / tsc       通过
generate-types 幂等        通过
```

新增 `backend/tests/test_mock_provider_contract.py`（5 项）锁定 mock 与真实
provider 的同一契约：定向 payload、无指令时仍提出修改、用户指令优先、
完整 artifact payload 仍可用、锁定实体绝不提出。

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

### 5.1 本地环境陷阱（两个都真实发生过）

**`127.0.0.1:8000` 不是 COP Studio。** 本机另有一个 Python 服务监听
IPv4 `127.0.0.1:8000`。COP Studio 监听 `127.0.0.1:8010`——
用 8000 手工验证会命中**另一个服务**并读到完全不同的 JSON，
而它同样返回 200，看起来像成功。判身份要看 `openapi.json` 的 `info.title`。

> **本节以下为当时（容器时代）的记录，容器层现已整体移除。**
> 当时的第二个陷阱是「任何一次普通的 `docker compose up` 都会丢掉测试库端口」：
> 测试库用 55432，而 `make up` 用默认 5432 重建容器，端口随之消失，
> 此后 `pytest` 全部报 `Connection refused`。
> 现在测试库与开发库**按名字**隔离（`cop_test` / `cop_studio`），
> 同一台 PostgreSQL 上没有端口可丢，这个陷阱不复存在。

### 5.2 Provider 是全局状态

E2E 整轮使用 Mock Provider，由 `globalSetup` 设置、`globalTeardown` 还原。
**不要在单个 spec 里改 provider 再恢复**——这会让套件的正确性依赖 spec 顺序：
还原成开发者真实端点后，之后运行的 spec 会发起真实网络调用，失败方式看起来
像产品回归。`globalTeardown` 会读回校验，还原不完整时打印警告。

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

## 9. 标准 COP 样板推进（2026-10-03）

统一目标、阶段、任务编号与工作方法入口：[COP_GOAL_PLAN_TASK_METHOD.md](/Users/milin/2026/软件开发/COP/docs/COP_GOAL_PLAN_TASK_METHOD.md)。

采用 `docs/proposals/cop-quality-standard-and-production-v1.md` 的 A0–A5 顺序。本次只交付 **A1 / Basic 子样板的工程原型**，不是完整 A1 或完整 LangChain。

- [x] 独立脚本、显式 key / endpoint / model / .env 规则、同次结果保存与 Inspect。
- [x] 独立 5 Stage COP、可选择且能回接的 Branch、实际交付物 / 语义 / 迁移 Practice、诚实来源摘要。
- [x] Foundation 阅读与导航、Learn 备选展示、复制结果反馈、只读原型预览。
- [x] 干净环境安装；13 项样板离线、26 项无库后端、54 项前端测试；typecheck / lint 通过。
- [x] Basic 内容审核完成（无阻塞性问题，若干信息负担改进已实施）。
- [x] Tools T01 任务定义草案已完成（产品目录查询），待用户确认。
- [ ] Basic 真实 provider / 回答语义 / 目标用户独立 Practice 验收。
- [ ] A1 Tools 样板实现（T02–T08）；后续 A2 契约、A3 五 Goal、A4 Harness、A5 泛化稳定性。

预览：`http://127.0.0.1:3000/prototypes/langchain-basic`。Basic 入口：`examples/langchain-basic/README.md`。Tools 入口：`examples/langchain-tools/README.md`。
详细记录及未执行范围：`docs/validation/langchain-basic-prototype-2026-10-03.md`。Tools 任务定义：`docs/proposals/tools-task-definition-v1.md`。

未修改既有发布数据、原五目标 fixture 或 Schema；未使用真实 API key。不要把离线固定回复、结构检查绿灯或页面可见当作真实能力已验。
