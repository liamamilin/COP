# LangGraph 可能性地图

范围：面向 Agent 与业务流程开发者，研究 LangGraph Python 运行时能够交付的任务结果；以 2026-11-05 实际文档为准，明确区分 Python 包、存储适配器、LangChain 示例、独立 UI 与 LangSmith 服务。

资料截点：2026-11-05。本图有 21 项来源支持的结果，来自 17 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

core 指 LangGraph 的执行与状态原语；extension 指另需工具包、完整示例项目、界面或托管服务。资料支持不等于已经配置或实测。

## 地图导航

- [编排并推进复杂任务](#g-workflows)
- [保留上下文并从中断继续](#g-continuity)
- [让人理解和控制执行](#g-control)
- [交付检索与业务应用](#g-applications)
- [提供交互界面与生产服务](#g-delivery)

<a id="g-workflows"></a>
## 编排并推进复杂任务

### `p-hybrid` 把规则步骤与模型判断串成可执行业务流程

让固定校验、条件分支和模型决策共用一份任务状态，执行有明确边界的多步业务流程。

**内置／核心能力 · 有来源支持。** LangGraph Python；节点、路由和外部操作需开发者实现，模型能力来自所接入模型。

来源：[s-overview：LangGraph overview · LangGraph overview；取回 Markdown第 9–9 行](https://docs.langchain.com/oss/python/langgraph/overview.md)。

### `p-parallel` 并行完成互不依赖的子任务

让多个模型任务同时开展，再收集其结果，用于多角度分析或独立材料处理。

**内置／核心能力 · 有来源支持。** 开发者定义并行分工、聚合方式、并发和调用预算；提速取决于任务与外部服务。

来源：[s-patterns：Workflows and agents · Parallelization；取回 Markdown第 232–232 行](https://docs.langchain.com/oss/python/langgraph/workflows-agents.md)。

### `p-route` 按问题内容分流到不同处理专长

将用户请求送到适合的业务路线，例如商品咨询、退货或退款处理。

**内置／核心能力 · 有来源支持。** 分类模型、条件边和业务规则须配置；示例模式不附带真实电商服务接入。

来源：[s-patterns：Workflows and agents · Routing；取回 Markdown第 365–365 行](https://docs.langchain.com/oss/python/langgraph/workflows-agents.md)。

### `p-revise` 依据评价反馈反复改进一份结果

生成初稿后进行评价，把具体反馈交回生成步骤，在达到标准或停止条件后交付。

**内置／核心能力 · 有来源支持。** 定义评价标准、最大循环与终止规则；自动评价不能证明结果正确或取代独立评审。

来源：[s-patterns：Workflows and agents · Evaluator-optimizer；取回 Markdown第 772–772 行](https://docs.langchain.com/oss/python/langgraph/workflows-agents.md)。

### `p-tool-loop` 让 Agent 在任务中选择工具并继续决策

在循环中根据模型判断与工具结果确定下一步，而不是只返回一次模型回答。

**内置／核心能力 · 有来源支持。** 需能调用工具的模型及工具执行节点；权限、循环上限和输出验证由应用负责。

来源：[s-patterns：Workflows and agents · Workflows and agents；取回 Markdown第 10–10 行](https://docs.langchain.com/oss/python/langgraph/workflows-agents.md)。

### `p-modular-team` 把流程模块复用于不同 Agent

将一组节点封装成子图供其他图重复调用，减少重复编排，并允许团队分别实现模块。

**内置／核心能力 · 有来源支持。** 使用子图组织流程；共享状态键或输入输出转换需设计。子图不自动赋予领域专家能力。

来源：[s-subgraphs：Subgraphs · Subgraphs；取回 Markdown第 12–12 行](https://docs.langchain.com/oss/python/langgraph/use-subgraphs.md)。

<a id="g-continuity"></a>
## 保留上下文并从中断继续

### `p-conversation` 接续同一用户的多轮对话

保存会话状态，使同一线程后续请求能沿用之前消息及任务进展。

**内置／核心能力 · 有来源支持。** 配置 checkpointer 和 thread_id；进程重启后的保留需持久化存储，不能只用内存实现。

来源：[s-memory：Memory · Memory；取回 Markdown第 9–9 行](https://docs.langchain.com/oss/python/langgraph/add-memory.md)。

### `p-remember` 跨对话记住用户偏好和已知事实

把偏好与知识存到跨线程的数据空间，后续任务按用户或应用命名空间重新读取。

**内置／核心能力 · 有来源支持。** 生产需要持久化 Store、访问隔离和更新规则；语义检索还需嵌入模型及索引配置。

来源：[s-store：Stores · Stores；取回 Markdown第 9–9 行](https://docs.langchain.com/oss/python/langgraph/stores.md)。

### `p-resume` 从保存的任务进度继续中断工作

恢复已保存状态，继续暂停或失败的任务，而不必让用户从头重新提交全部上下文。

**内置／核心能力 · 有来源支持。** 配置可持久化 checkpointer；外部写入仍须设计幂等和补偿，不承诺所有副作用只执行一次。

来源：[s-persistence：Persistence · Persistence；取回 Markdown第 9–9 行](https://docs.langchain.com/oss/python/langgraph/persistence.md)。

### `p-failure-recovery` 为暂时失败的任务配置自动重试与恢复路线

根据失败类型重试步骤，限制等待时间，并在重试耗尽后交给恢复逻辑处理。

**内置／核心能力 · 有来源支持。** 策略需显式配置；逐节点超时与错误处理要求 LangGraph 1.2+，不意味着任意操作可安全重复。

来源：[s-faults：Fault tolerance · Fault tolerance；取回 Markdown第 11–11 行](https://docs.langchain.com/oss/python/langgraph/fault-tolerance.md)。

<a id="g-control"></a>
## 让人理解和控制执行

### `p-approval` 在执行关键动作前等待人工审阅

暂停运行并向审阅者呈现数据，获得外部输入后继续对应任务。

**内置／核心能力 · 有来源支持。** 需 checkpointer、稳定 thread_id、恢复入口与审阅界面；不得把中断误当作已经执行外部操作。

来源：[s-interrupts：Interrupts · Interrupts；取回 Markdown第 7–7 行](https://docs.langchain.com/oss/python/langgraph/interrupts.md)。

### `p-time-travel` 回到历史进度比较另一条执行路线

选取过去检查点重放后续步骤，或修改状态后分叉，比较替代决策产生的结果。

**内置／核心能力 · 有来源支持。** 需保存检查点；检查点后的模型调用、API 请求和中断会重新执行，可能产生费用与不同结果。

来源：[s-time：Use time-travel · Overview；取回 Markdown第 14–14 行](https://docs.langchain.com/oss/python/langgraph/use-time-travel.md)。

### `p-live-progress` 向用户实时呈现回答和执行进展

把运行中的文本、状态变化或自定义进展逐步送到调用者，减少等待最终结果时的信息盲区。

**内置／核心能力 · 有来源支持。** 前端需消费流并处理断线；本页 v2 输出格式需 LangGraph 1.1+，v1.2 另有 event streaming。

来源：[s-streaming：Streaming · Basic usage；取回 Markdown第 17–17 行](https://docs.langchain.com/oss/python/langgraph/streaming.md)。

### `p-targeted-tests` 独立检查复杂流程中指定的一段行为

绕过完整长流程，对节点及选定执行片段做自动化测试，定位局部改动的影响。

**扩展／具名实现路线 · 有来源支持。** 另需 pytest 等测试工具；隔离执行可能绕过整体持久化语义，还需真实集成与端到端测试。

来源：[s-test：Test · Partial execution；取回 Markdown第 92–92 行](https://docs.langchain.com/oss/python/langgraph/test.md)。

<a id="g-applications"></a>
## 交付检索与业务应用

### `p-sql` 用自然语言向数据库提问并得到查询结果

由自定义 SQL Agent 读取数据库结构、构造查询并使用执行结果回答问题。

**扩展／具名实现路线 · 有来源支持。** 需 LangChain SQL 工具、模型和数据库连接；最小权限、查询校验及必要人工批准必须单独配置。

来源：[s-sql：Build a custom SQL agent · Build a custom SQL agent；取回 Markdown第 7–7 行](https://docs.langchain.com/oss/python/langgraph/sql-agent.md)。

### `p-rag` 根据问题决定是否检索私有或选定资料后回答

在需要资料支撑时检索文档，把结果交给模型；简单交互可直接响应。

**扩展／具名实现路线 · 有来源支持。** 需文档导入、切分、嵌入、向量库和模型；来源权限与回答正确性需另验。

来源：[s-rag：Build a custom RAG agent with LangGraph · Build a custom RAG agent with LangGraph；取回 Markdown第 7–7 行](https://docs.langchain.com/oss/python/langgraph/agentic-rag.md)。

### `p-retrieve-again` 在检索资料不相关时改写问题继续查找

先判断检索内容是否相关，若不相关则改写问题再检索，避免直接用无关材料作答。

**扩展／具名实现路线 · 有来源支持。** 这是教程中需自行装配的条件分支与循环，不是所有 LangGraph 应用默认具备的行为。

来源：[s-rag：Build a custom RAG agent with LangGraph · Grade documents；取回 Markdown第 245–245 行](https://docs.langchain.com/oss/python/langgraph/agentic-rag.md)。

### `p-support-email` 建立能分类、查资料并提交人工审阅的客服邮件流程

将来信意图识别、知识检索、回复草稿、问题追踪和必要人工升级连接为一条服务流程。

**扩展／具名实现路线 · 有来源支持。** 官方设计教程；邮件发送、知识库与工单系统需自行连接，示例业务要求不表示现成 SaaS 成品。

来源：[s-email：Thinking in the Graph API · Thinking in the Graph API；取回 Markdown第 11–11 行](https://docs.langchain.com/oss/python/langgraph/thinking-in-graph-api.md)。

### `p-research` 改造开放深度研究项目来交付研究结果

采用 Open Deep Research 的可配置实现，连接搜索及模型开展多步主题研究。

**扩展／具名实现路线 · 有来源支持。** 需另行部署该项目并配置模型与搜索工具；README 中历史排名不作为当前质量或效果保证。

来源：[s-research：🔬 Open Deep Research · 🔬 Open Deep Research；取回 Markdown第 5–5 行](https://github.com/langchain-ai/open_deep_research/blob/1b7d2e80db9faa586165c60e09096dbbfd483a64/README.md#L5-L5)。

<a id="g-delivery"></a>
## 提供交互界面与生产服务

### `p-chat-interface` 给 Agent 提供可查看工具动作的对话界面

使用独立的 Agent Chat UI，让用户在浏览器对话并查看工具调用、中断与调试状态。

**扩展／具名实现路线 · 有来源支持。** 需另装 Next.js Agent Chat UI 并连接兼容 Agent Server；不是 langgraph Python 包自带网页。

来源：[s-ui：Agent Chat UI · Agent Chat UI；取回 Markdown第 7–7 行](https://docs.langchain.com/oss/python/langgraph/ui.md)。

### `p-managed-service` 把状态化 Agent 发布为可管理的生产服务

利用 LangSmith Deployment 运行 Agent，获得部署基础设施、实时交互与横向扩展入口。

**扩展／具名实现路线 · 有来源支持。** 另用 LangSmith Deployment，选择 Cloud、BYOC 或自托管路线；账户、费用、基础设施和服务限制需另核。

来源：[s-deploy：LangSmith Deployment · LangSmith Deployment；取回 Markdown第 7–7 行](https://docs.langchain.com/langsmith/deployment.md)。

## 资料覆盖与发现过程

结果视角先提取状态接续、人工介入、容错、流式反馈和控制流结果，没有先套用其他主题的分类。
示例视角补读邮件客服、自定义 SQL、Agentic RAG 和 Open Deep Research，保留“开发示例”与“已部署产品”的区别。
扩展视角检查子图、局部测试、独立 Chat UI 与 LangSmith 部署。把多种 checkpointer/数据库适配器合并进结果及条件，没有按包名拆分 P。
补漏复查 Graph API、Stores 与运行时概述后，新增资料主要落在已识别的状态、控制流和记忆结果；将数据库、UI 和托管服务边界补入条件后停止本轮。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未安装运行全部例子，也未对模型正确率、生产吞吐、故障恢复的外部副作用做实测。
- 官方当前文档含 1.1、1.2 新接口；不能推定旧版本支持所有条目，升级需按项目依赖与迁移说明核对。
- 未把任意外部 API 的 exactly-once 执行、无限任务时长或自动消除幻觉列为已确认能力。
- 生产部署、跨租户权限、各数据库适配器兼容性与费用需在目标环境验证；LangSmith 不能归入开源包内置。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
