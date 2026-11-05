# 核心学习闭环：研究结论与实验切片

## 边界

这一轮验证的是**产品核心承诺**：把陌生领域变成一条能理解、能完成、能判断、
能迁移的能力路径。它不追求再做一个界面增量。

新增的 `LearningUnit` 是**独立、绑定内容版本的实验侧车**，不是冻结的 COP 0.2，
也不迁移数据库。已发布的 COP 0.1、生成流程和现有项目保持原样。要在项目计划中
把 A2/A4 标成完成，仍需真实学习者验收。

## 研究结论与产品取舍

2026-11-02 直接核对的官方公开资料：

1. [IES/WWC, Organizing Instruction and Study to Improve Student Learning (2007)](https://ies.ed.gov/ncee/wwc/PracticeGuide/1)。
   建议交替使用完整示例与问题解决，连接抽象和具体表征，并采用解释性问题与
   检索再暴露。产品取舍：先解释对象与操作的关系，走通一个连续案例，再在揭示
   支持前要求预测或解释。
2. [NRC, How Experts Differ from Novices (2000)](https://www.nationalacademies.org/read/9853/chapter/5)。
   专家知识是围绕概念组织的，不是孤立事实清单；领域专长不等于教学专长。
   产品取舍：把概念映射到操作和状态变化，配通俗例子与易混对比。
3. [NRC, Learning and Transfer (2000)](https://www.nationalacademies.org/read/9853/chapter/6)。
   迁移不同于重复同一程序；反馈、对比案例和渐进提示很重要。产品取舍：把
   “做完、解释、诊断、近变式”分开记录，用帮助使用情况代替点击即掌握的结论。
4. [LangChain Agents 文档](https://docs.langchain.com/oss/python/langchain/agents)。
   核对了 model、harness、messages 与调用的当前角色。当前官方文档**不能**认证
   仓库旧固定依赖 profile；已有离线测试是另一类实现证据。本轮未调用 provider。

以上资料支持设计取舍，不构成“COP Studio 对目标用户有效”的研究证据。
搜索集成当时不可用（HTTP 402），因此直接读取官方公开页面，未登录、未付费。

## 实际交付

| 层 | 位置 | 职责 |
|---|---|---|
| 教学契约 | `backend/app/domain/learning_unit.py` | 学习起点、路径边界、输入输出、概念因果、完整方法、示例、检查、练习与验收；只做结构校验 |
| 检查器 CLI | `scripts/check-learning-unit.py` | 读两个本地 JSON，输出 `structure-and-bindings-only` 清单；不执行候选命令 |
| 内容绑定 | `sha256-canonical-json-v1` | 教学与源 COP 相互绑定；任一内容变化即拒绝混用 |
| 作者样板 | `examples/langchain-basic/build_learning_unit.py` | 确定性构建，默认只检查，`--write` 只写两个新 fixture |
| 教学单元 | `fixtures/langchain-basic-learning-unit.json` | 中文教学，英文路径标签；复用已有五个 Stage 与代码，不复制可执行实现 |
| 清单 | `fixtures/langchain-basic-learning-unit.manifest.json` | 结构检查结果与未验证范围 |
| 生成类型 | `schemas/learning-unit.experimental.schema.json`、`packages/cop-types/generated/learning-unit.ts` | 独立子路径 `@cop-studio/cop-types/learning-unit` |
| 阅读器 | `apps/web/components/learning-unit-reader.tsx` | 只读绑定内容，显式路径边界，渐进提示，本地记录；不回写项目进度 |
| 入口 | `/prototypes/learning-unit` | 可从 Basic 原型进入，标注实验、未发布 |
| 真人验收 | `docs/LEARNING_UNIT_ACCEPTANCE.md` | 基线、尝试记录、解释/诊断/迁移、延迟复测与停止规则；状态仍为 PENDING |

### 解耦

- 教学契约、校验、生成类型、样板内容、阅读器、本地观察记录各自独立。
- Basic 读者**不导入**项目 Stage 渲染器；来源方法仍由绑定 artifact 提供，
  但项目界面改版不会悄悄改变教学页。
- 本地记录使用独立格式 `cop-learning-observation/0.1`，不调用学习进度 API；
  导出/导入拒绝不同单元版本、未知问题、未知步骤和异常提示次数。
- 没有新增数据库表、迁移、发布路径或后台任务；COP 0.1 Schema 未改动。

## 内容设计

- 两条显式路径：`offline`（部分目标，验证工程管线）与 `provider`（完整目标，
  需本人凭据、网络和费用许可）。阅读器默认部分路径，明确“完成离线不等于 Goal
  完成”。
- 五步均给出：真实起点与就绪检查、概念通俗解释/例子/对比、概念→操作的因果链、
  来源 artifact 中的完整方法、工作案例、检查依据与失败解释、练习。
- 所有来源 `implementation_details` 都被映射到明确路径；无路径时检查器报
  `UNCOVERED_METHOD`。
- 概念、操作、产物、检查、示例和问题均按路径覆盖；缺失即拒绝，不靠放宽规则。
- 输出只看可验证的形态：文件必须有完整可解析正文；运行时生成的 JSON 不伪造正文。
- 不把 Agent 对象作为跨步骤输入：它只存在于同一脚本进程，跨步骤依赖的是文件。

## 验证证据

- 前端：typecheck、lint、**110** 个单元/渲染测试通过。
- 后后端：学习契约、非代码契约、生成类型、教学上下文、阅读契约、细化与离线
  Harness 回归共 **86** 个测试通过；Scoped Ruff 通过。
- 学习契约测试覆盖：旧内容、无效 artifact、错误目标/顺序、重复、缺失/未来输入、
  进程内对象跨步骤交接、缺文件正文、无效 Python/JSON、私密内容、路径缺口、
  未覆盖方法、空方法、示例不一致、检查/练习/路径缺口、验收不足。
- 浏览器隔离回归通过：绑定方法显示、概念→方法→检查顺序、渐进提示、本地
  保存/重载/导出/导入、路径专属内容、失败关闭、移动端顺序；**无写请求、无
  provider 调用、无真实项目删除**。
- 样板构建幂等：连续 `--write` 字节一致；源 `fixtures/langchain-basic-cop.json`
  未修改。
- 实际 Next 页面已可访问，SSR 含绑定内容且未显示版本不匹配。

未运行：需要 `TEST_DATABASE_URL` 的全量数据库测试（会截断测试库），
以及任何付费/真实 provider 调用。

## 尚未成立

- 这份手写样板不能证明**稳定自动生成**；生成器尚未改造成先定教学计划再派生内容。
- 结构检查不判断事实正确、方法是否足以完成、回答语义或学习迁移。
- 阅读器的本地记录是**未验证自我报告**；没有自动评分、没有掌握度结论。
- 真人验收状态为 **PENDING**。必须由未参与编写的人按 `LEARNING_UNIT_ACCEPTANCE.md`
  实际尝试、解释、诊断并完成近变式；此前不能宣称核心产品目标已达成。
- 下一道门是：修正样板暴露的教学缺陷 → 提炼最小契约 → 再以独立领域和独立
  学习者验证生成稳定性（需另行明确预算）。
