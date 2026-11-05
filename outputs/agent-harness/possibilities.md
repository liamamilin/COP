# Agent Harness 可能性地图

范围：研究包围模型的执行系统能够帮助交付的任务结果；这是架构与方法类别，不是一款统一产品。以 Deep Agents、Claude Agent SDK 及官方工程实验为具名实现，不把某一实现的功能泛化给所有 Harness。

资料截点：2026-11-05。本图有 18 项来源支持的结果，来自 12 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

本主题没有单一“内置功能”基线，所有确认条目均标 extension，意为具体框架或工程路线能够实现。必须采用条目所列组件并进行开发与配置；架构名称本身不提供现成能力。

## 地图导航

- [接续并控制长任务进度](#g-sustain)
- [在有限上下文中保留和复用知识](#g-context)
- [组织专长与后台工作](#g-delegate)
- [连接工具并约束执行环境](#g-execute)
- [用实际评价改进交付](#g-feedback)

<a id="g-sustain"></a>
## 接续并控制长任务进度

### `p-long-work` 跨上下文窗口逐步推进长时工程任务

通过初始化、进展文件和接续提示，让后续会话接手已有工程状态并继续完成工作。

**扩展／具名实现路线 · 有来源支持。** Claude Agent SDK 的工程实验路线；需显式交接工件、验收标准和接续策略，不保证任意长任务自动成功。

来源：[s-long：Effective harnesses for long-running agents \ Anthropic · 页面正文；本次 HTML 提取正文第 27–27 行（不是 HTML 源码行号）](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)。

### `p-rollback` 从代理引入的坏改动恢复可用工程状态

把阶段进展保存为可追踪的版本，在后续迭代中回退有问题的改动并接续工作。

**扩展／具名实现路线 · 有来源支持。** 示例依赖 git、提交纪律及进展记录；文件外的副作用需另外设计补偿。

来源：[s-long：Effective harnesses for long-running agents \ Anthropic · 页面正文；本次 HTML 提取正文第 58–58 行（不是 HTML 源码行号）](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)。

### `p-planning` 跟踪多步任务的计划和执行进度

让代理维护结构化任务清单，为长任务保留待做、进行中与完成情况的可见依据。

**扩展／具名实现路线 · 有来源支持。** Deep Agents v0.7 起 task planning 为可选能力，需显式添加 TodoListMiddleware；不是所有 Harness 默认启用。

来源：[s-deep：Deep Agents overview · Task planning；取回 Markdown第 429–429 行](https://docs.langchain.com/oss/python/deepagents/overview.md)。

<a id="g-context"></a>
## 在有限上下文中保留和复用知识

### `p-context` 把大型中间结果卸载到外部上下文

把冗长工具结果保存到文件等外部上下文，在需要时回读，减少完整结果持续占用会话窗口。

**扩展／具名实现路线 · 有来源支持。** Deep Agents 的工具结果外部化路线；需要文件或其他持久上下文及回读工具，仍需管理可访问性、存储与关键约束。

来源：[s-deep：Deep Agents overview · Choose how to run Deep Agents；取回 Markdown第 27–27 行](https://docs.langchain.com/oss/python/deepagents/overview.md)。

证据说明：此条仅描述大型工具结果的外部化；历史压缩与摘要接续统一由 p-compaction 表达。

### `p-just-in-time` 让代理按当前任务查找所需文件上下文

通过文件检索等工具在需要时取回资料，避免把整个项目一次塞进提示。

**扩展／具名实现路线 · 有来源支持。** Anthropic 提出的上下文工程路线；需要检索工具与可访问文件，不保证检索完整性或免受过期资料影响。

来源：[s-context：Effective context engineering for AI agents \ Anthropic · 页面正文；本次 HTML 提取正文第 59–59 行（不是 HTML 源码行号）](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)。

### `p-compaction` 在会话接近上下文上限时保留关键摘要继续工作

以总结后的任务状态接续后续上下文，减少窗口耗尽对长对话连续性的影响。

**扩展／具名实现路线 · 有来源支持。** 需支持压缩或重启交接的实现；不同模型与任务表现不同，摘要不保证无损。

来源：[s-context：Effective context engineering for AI agents \ Anthropic · 页面正文；本次 HTML 提取正文第 65–65 行（不是 HTML 源码行号）](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)。

### `p-skills` 把领域流程作为可复用技能交给不同代理

打包工作流、参考资料和脚本，让代理按需读取专业说明并在多个项目中复用。

**扩展／具名实现路线 · 有来源支持。** Deep Agents skills 目录与 Agent Skills 规范；脚本、服务权限、资料更新和适用条件需单独管理。

来源：[s-skills：Skills · Skills；取回 Markdown第 11–11 行](https://docs.langchain.com/oss/python/deepagents/skills.md)。

### `p-memory` 在不同对话中沿用可更新的经验文件

把代理需要长期保存的事实、工作约定和经验写入记忆文件，在后续对话重新读取。

**扩展／具名实现路线 · 有来源支持。** Deep Agents memory 与持久化 backend；访问范围、写入质量和冲突处理需管理，文件记忆不是参数训练。

来源：[s-memory：Memory · Memory；取回 Markdown第 17–17 行](https://docs.langchain.com/oss/python/deepagents/memory.md)。

<a id="g-delegate"></a>
## 组织专长与后台工作

### `p-specialists` 把复杂子任务交给隔离上下文的专长代理

主代理只接收子任务最终结果，使大量检索或分析细节留在子代理上下文中。

**扩展／具名实现路线 · 有来源支持。** Deep Agents 同步子代理实现；需定义职责、工具和输入输出，调度成本与质量需评估。

来源：[s-subagents：Subagents · Why use subagents?；取回 Markdown第 30–30 行](https://docs.langchain.com/oss/python/deepagents/subagents.md)。

### `p-model-mix` 为不同子任务配置各自的说明和模型

把需要不同模型能力的工作交给各自配置的子代理，以专门指令完成对应结果。

**扩展／具名实现路线 · 有来源支持。** Deep Agents 自定义 subagents；需相应模型账户、权限和预算，不保证混用后更优或更便宜。

来源：[s-subagents：Subagents · Why use subagents?；取回 Markdown第 36–36 行](https://docs.langchain.com/oss/python/deepagents/subagents.md)。

### `p-background` 保持前台交互并调整后台执行的任务

后台子代理并发工作时，主代理继续处理用户输入，并可跟踪、追加指令或取消子任务。

**扩展／具名实现路线 · 有来源支持。** Deep Agents Async subagents 需要实现 Agent Protocol 的服务；不同于进程内同步子代理，部署和状态需配置。

来源：[s-async：Async subagents · Async subagents；取回 Markdown第 9–9 行](https://docs.langchain.com/oss/python/deepagents/async-subagents.md)。

<a id="g-execute"></a>
## 连接工具并约束执行环境

### `p-storage` 把临时资料与长期记忆分配到不同存储

按虚拟路径把任务文件、长期记忆等交给不同后台保存，使文件生命周期与用途相匹配。

**扩展／具名实现路线 · 有来源支持。** Deep Agents CompositeBackend 等具名实现；应用需配置路由、存储与用户命名空间。

来源：[s-backends：Backends · Backends；取回 Markdown第 16–16 行](https://docs.langchain.com/oss/python/deepagents/backends.md)。

### `p-file-policy` 限制代理可读写的目录和文件范围

在文件工具进入后台存储前应用访问规则，拒绝不被允许的读取或写入。

**扩展／具名实现路线 · 有来源支持。** Deep Agents filesystem permissions；只覆盖对应内置文件工具。LocalShellBackend 的 shell 可访问主机，不能把虚拟路径模式当作安全沙箱。

来源：[s-backends：Backends · Permissions；取回 Markdown第 990–990 行](https://docs.langchain.com/oss/python/deepagents/backends.md)。

### `p-sandbox` 让代理在隔离环境执行代码并产出文件

给代理可运行命令的环境，用于编程、数据计算或文稿工件生产，并与宿主资源建立边界。

**扩展／具名实现路线 · 有来源支持。** 需 Deep Agents sandbox backend 与具体提供商或隔离设施；可访问文件、网络和凭据取决于配置，不作绝对隔离保证。

来源：[s-sandbox：Sandboxes · Sandboxes；取回 Markdown第 7–7 行](https://docs.langchain.com/oss/python/deepagents/sandboxes.md)。

### `p-approval` 在外部动作执行前让人批准或修改参数

对指定工具调用暂停审阅，允许批准、编辑、拒绝或提供替代人工反馈。

**扩展／具名实现路线 · 有来源支持。** Deep Agents HITL middleware 与 LangGraph 中断、检查点和审阅入口；需明确哪些工具受控。

来源：[s-human：Human-in-the-loop · Human-in-the-loop；取回 Markdown第 9–9 行](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop.md)。

### `p-tools` 把外部系统的工具接入代理执行循环

发现 MCP 服务器工具并适配为代理可调用的操作，把搜索、数据库或业务服务接进任务。

**扩展／具名实现路线 · 有来源支持。** 该资料描述 LangChain MCPAdapter；需 langchain[mcp]>=1.4.0，当前为 beta，并需 MCP 服务器与认证。不是所有 Harness 都实现同一适配器。

来源：[s-mcp：Model Context Protocol (MCP) · Model Context Protocol (MCP)；取回 Markdown第 9–9 行](https://docs.langchain.com/oss/python/langchain/mcp.md)。

<a id="g-feedback"></a>
## 用实际评价改进交付

### `p-build-evaluate` 用规划、生成和评价循环迭代完整应用

给生成过程提供独立评价和具体反馈，分解工作并多轮改进完整应用。

**扩展／具名实现路线 · 有来源支持。** Anthropic Claude Agent SDK 工程实验；评价准则、模型和工具需配置，文中实验结果不构成普遍质量承诺。

来源：[s-harness-design：Harness design for long-running apps \ Anthropic · 页面正文；本次 HTML 提取正文第 29–29 行（不是 HTML 源码行号）](https://www.anthropic.com/research/harness-design-long-running-apps)。

### `p-browser-evaluation` 让代理在真实网页中操作并给出实现评价

给评价代理浏览器工具，使其亲自导航和检查正在运行的界面，而非仅凭代码或静态截图评估。

**扩展／具名实现路线 · 有来源支持。** 文中使用 Playwright MCP；需实际应用环境和评价准则，模型主观评分不等于可用性或用户验收结论。

来源：[s-harness-design：Harness design for long-running apps \ Anthropic · 页面正文；本次 HTML 提取正文第 47–47 行（不是 HTML 源码行号）](https://www.anthropic.com/research/harness-design-long-running-apps)。

## 资料覆盖与发现过程

先从执行、上下文、状态、工具与人类控制中提取可观察结果；不以内部模块名作为 P。
示例视角补读 Anthropic 长任务接续和完整应用迭代实验，把跨会话继续、git 回退与真实浏览器评价保留为不同结果。
扩展视角调查 Deep Agents 的 backend、沙箱、记忆、技能、同步与异步子代理、HITL 和 MCP 连接；依赖全部明确写进条目。
归一化时把工具列表和多个沙箱供应商合并进对应结果；未将供应商名、API 参数或任意“自动化所有工作”拆成 P。
复查上下文工程与长期应用实验后，更多材料主要重复已发现的接续、委派和反馈机制；未证实的运行保证保留为缺口。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未对不同 Harness、模型和任务做统一基准或长时可靠性测量；实验中的成功案例不能外推到所有工程。
- 未把无限执行、无损记忆、自动正确、绝对沙箱安全或无人监督上线列为已确认能力。
- 长期任务预算、可观测性、外部副作用补偿、租户隔离和特定部署产品尚需按选用实现深入验证。
- 部分当前接口有明确版本门槛，如 Deep Agents v0.7 的可选 planning，以及 LangChain 1.4 的 beta MCP 接口；未承诺与旧示例兼容。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
