# 内容逻辑优化：实施记录

日期：2026-11-03。目标不是生成更多字段，而是让学习者知道问题是什么、
为什么引入一个概念、怎样从材料推出判断，以及判断还有哪些边界。

## 交付与边界

- [x] H40 在原有调用中生成教学计划：中心问题、顺序理由、贯穿案例的事实与假设、
  各步问题、前置、推理安排、检查重点和未解决问题。
- [x] 规范化时与 Stage 一起重写引用。缺步骤、未来前置、丢失计划、计划随深度
  上限被截断，均不能静默通过。旧检查点缺计划时明确标为未验证，不替它编造计划。
- [x] H50 各批共用计划，并取得本批问题与先前内容；必要讲解落到现有
  `why_it_exists`、方法、示例中，不能只留在装配会丢弃的临时字段。
- [x] H80 使用同一计划安排练习与整体解释。整体理由进入既有
  `mental_model.summary/flow`，示例和问题不能各自换案例。
- [x] 内容审查要求指认具体错误论断、缺失推理与反例；禁止把教学模型当现实，
  或用关键词、shell/grep 冒充非编程领域的理解检查。
- [x] H60 修复跨批引用映射。批次获得先前身份清单和全局候选名，保留不确定身份，
  不按前缀/包含关系自动合并；缺绑定时不再附会到全局第一个概念/操作。
- [x] 独立教学侧车补充整体导入与逐步推理结构。旧 Basic 数据仍可读，不自动补讲。
- [x] 概念框架加入确定性契约：占位/过短定义、只用名称自我定义、无角色、
      未被任何 Stage 或 Operation 使用的概念，都会被具名拒绝。裁决在代码里，
      不交给模型自评；模型仍负责判断“定义是否说错了东西”，字符串检查不做这种承诺。
- [x] 概念缺陷进入候选状态（`needs_attention`）与发布回执（`concept_frame`），
      并可被局部修复；修复只改 `definition`/`role`，不能借此悄悄解绑 Stage。
- [x] 独立传播学候选：`/prototypes/communication`，不替换已发布传播学项目。
- [x] 阅读器展示原文的目标理由与整体解释，不由 UI 临时生成因果说明。
- [ ] 真人独立尝试、解释、诊断与迁移：等待实际参与者，不能用模型扮演新手。
- [ ] 未参与调优的任务、多次独立生成与有限预算验证：未执行付费调用。

## 低耦合

1. `teaching_plan` 属于 Harness 计划/检查点；引用校验为独立纯逻辑，不依赖 UI。
2. H40→H50→H60→H80 的顺序保持；没有增加规划模型调用。分批、流式和超时仍
   属于请求执行策略，不改变教学身份或要求以数量达标。
3. 发布数据继续使用 COP 0.1。没有 schema 迁移、数据库写入或自动发布。
4. 实验侧车的 `orientation`、`reasoning` 为可选字段；有导入的候选必须覆盖全部
   步骤推理，且前置引用只指向更早步骤。旧文档不会因此被宣称教学已完整。
5. `TeachingOrientation` 和 `ReasoningWalkthrough` 是纯展示组件；本地笔记继续
   使用独立绑定格式，不接入项目进度或自动评分。

## 可以验证什么

本轮自动化检查覆盖：声明计划的结构与引用完整、特定跨批回归没有错误重绑、
来源 ID 可解析、概念框架没有占位/循环/未使用定义、导入与推理在方法前显示、
本地笔记与内容版本绑定。这些检查不能识别所有泛化文案，也不能证明所有未知输入
都不会发生引用错误。

程序不能证明：理由正确、步骤安排适合所有学习者、来源支持了某个具体因果判断、
学习者已理解，或者生成器能在不同任务上稳定生产。概念契约同样只拒绝
“不可用来推理的定义”，不能证明某个写得很长的定义在事实上是对的。

不以“概念数下降”“只被一个步骤引用的比例下降”证明知识组织改善，也不比较
两个不同领域的数量后就把差异归因于分批。实际错误必须落实到语义和引用。

## 内容依据与复核入口

- 本轮候选与原内容的逐项问题见 `CONTENT_LOGIC_AUDIT.md`。
- 推理展示引用开放教材 *Communication in the Real World* 的
  [The Communication Process](https://socialsci.libretexts.org/Bookshelves/Communication/Introduction_to_Communication/Communication_in_the_Real_World_-_An_Introduction_to_Communication_Studies/01%3A_Introduction_to_Communication_Studies/1.02%3A_The_Communication_Process)，
  2026-11-03 实际读取；区分模型简化、编码/解码、反馈和语境。案例是作者虚构，
  不是教材中的实证结果。引用范围见候选的 `sources.scope`。
- 学习设计依据延续 `CORE_LEARNING_EXECUTION.md` 中已列出的 IES/WWC、NRC
  原则，不以引用这些原则冒充 COP 的效果研究。

## 本轮不做

不修改已发布教程，不重跑收费生成，不静默替换用户草稿，不对相似概念猜测归并，
不抑制错误提示冒充修好，不重启服务触发排队任务，也不把真人验收标为完成。

## 最终工程验收（2026-11-03）

- 前端 `pnpm typecheck`、`pnpm lint` 通过；16 个测试文件，**129 tests passed**。
- 后端：新增 `tests/test_concept_frame.py`（27 项）与
  `test_content_contract.py` 的 3 项端到端断言。完整后端套件在隔离的
  `cop_test` 上 **475 passed**（3 条 warning 是旧 `canonicalize()` 兼容路径的
  显式不确定性提示）。概念契约在真实 fixture 上零误报，同时在占位/循环/
  未使用样例上按预期拒绝。
- 9 个浏览器回归脚本全部通过（含实际 `/settings`、项目库、教学单元、
  10 个已发布页面 × 4 种视口）；均无控制台/水合错误，无写请求。
- `.github/workflows/ci.yml` 的 e2e job 不再安装 Playwright 捆绑浏览器。
- `uv run ruff check app tests ../examples/communication-basics/build_learning_unit.py`
  通过；communication builder 默认漂移检查 0 issues；实验 schema/types 无漂移。
- communication 样板覆盖四步理由与推理、方法前的结论边界、空命令、逐级提示、
  笔记保存/重载/换步恢复、复核、错误绑定拒绝与响应式宽度。
- 修复了已填答题框重新挂载时标签定位不稳定的问题：问题与帮助字段用固定文本
  `aria-labelledby`，不把恢复的答案混入标签查询；回归继续按完整标签定位。
- 实际 Next 页面用干净 Chrome 只读验收：四步内容可见、复核可到达、
  390/760/1440px 无横向溢出，未捕获 console/page/hydration errors，
  未出现非 GET/HEAD 请求。桌面和移动端截图已人工查看。
- 两个列出项目的列表、最新版本与学习进度，与执行前快照逐字节相同；SHA256：
  `c0e113a401a27a14c6b4c9f08e6ae1b5571d9827e0d5eea3c7ba00c7b50fc93e`。
  这是所查询范围的数据对照，不是全库审计。
- 本轮未重启 API/worker 以外的服务；未执行新的 live-provider 生成。
  发布 COP 0.1 schema/types 与迁移没有改动。

入口：<http://localhost:3000/prototypes/communication>。这是独立手工候选，
原传播学发布版本没有被改写。示例后的练习不计作盲测，真人与稳定生产仍 pending。

## 浏览器工具安全边界（2026-11-03）

`@playwright/test@1.64.1` 捆绑 Chromium 156.0.8078.4；CVE-2026-118306、
118331、118344、118348 要到 156.0.8078.73 才修复，且 Playwright 的
`chromiumSandbox` 默认是 `false`。已实测核对产物与文档，未凭传闻判断。

处理方式不是删除验证能力，而是：

- 新增 `apps/web/scripts/safe-browser.mjs`：拒绝 `chromium` 捆绑引擎，
  强制 `chromiumSandbox: true`，并比对运行版本不低于 156.0.8078.73；
- 9 个浏览器回归脚本与 `playwright.config.ts` 统一走该入口；
- CI 不再执行 `playwright install chromium`，改为要求 runner 自带 Chrome 并显式失败。

架构影响：本次只改测试工具层。`apps/web/app`、`components`、`lib`、`packages`、
`backend/app` 均无 Playwright 引用，依赖方向仍是测试依赖应用，未反向耦合。
详见 `BROWSER_TOOLING_SECURITY.md`。

未做：不声称系统 Chrome 已足够安全（版本守卫只能拒绝旧版本），也不声称完成全依赖审计
（当前 registry 镜像没有 audit 端点）。

## 下一道验收门

先让符合声明起点的人试读候选前两步，记录第一次不明白“为什么”的位置；
再完成一个反例和一个近变式。必要时继续改候选。只有这一门过后，才讨论扩大
生产验证与正式数据契约，不能从手工样板直接宣布产品核心目标已经达成。
