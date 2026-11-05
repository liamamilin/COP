# LangChain Python 1.x Agent：有证据的可能性地图

调研日期：2026-11-05（Asia/Shanghai）。目标是发现能完成的任务和可获得的结果。

LangChain Python 1.x 在 Agent 开发中的用户任务、可获得的结果、可复用控制能力及明确标注的 LangGraph、Deep Agents、外部集成与平台扩展。

本轮保留 **52 项来源支持的可能性**（24 项 LangChain 公开入口或组合模式，28 项扩展实现），另有 **1 项待验证方向**。使用 **66 个来源页面/文件**，在收集与去重后分为 **8 个用途组**。数量不是完整性或质量分数。

## 版本与组件边界

依据当前官方 Python 文档和 [LangChain 包 manifest](https://github.com/langchain-ai/langchain/blob/master/libs/langchain_v1/pyproject.toml)，目标版本为 **LangChain 1.4.9**（Python >=3.10,<4）。[Deep Agents manifest](https://github.com/langchain-ai/deepagents/blob/main/libs/deepagents/pyproject.toml) 显示 **0.7.32**（Python >=3.11,<4），依赖 LangChain >=1.4.8,<2。这里只记录所读版本，未声称全部功能自 1.0 起存在。

| 标注 | 具体含义 |
|---|---|
| 核心 · LangChain API | 有 LangChain Python 公开入口；仍需模型、应用工具和运行资源。 |
| 核心 · LangGraph 运行/存储 | 通过 LangChain 接口配置，但 checkpointer、store 和执行引擎来自 LangGraph。 |
| 核心 · 手工组合模式 | 文档展示用 LangChain 原语自行组装；不是默认附带的成品。 |
| 扩展 · LangGraph | 直接使用图、路由、状态迁移、历史分支等更底层编排。 |
| 扩展 · Deep Agents | 需 deepagents 的文件系统、记忆封装、子代理或 rubric 等。 |
| 扩展 · 外部集成/应用/平台 | 结果依赖连接器、提供方、独立应用、LangSmith 或其他资源。 |

**容易误认的边界：** LangChain 中间件汇总页也介绍 Deep Agents 组件；本地图按实际 Python 导入与依赖判定。TodoList 规划在 LangChain 中有原生中间件；目录式技能、成品子代理和文件 backend 等另行标明。旧的 AgentExecutor 等 classic 功能不直接算作 1.x 核心。

**证据状态：** 每项的逐字短摘录、原文位置及抓取依据存于 [possibilities.json](possibilities.json) 的 `sources` 与 `evidence_refs`，正文逐项链接原始出处。`source_supported` 表示原始资料支持该结果，不代表本机已执行或通过人工验收。没有条目自行标为 `reviewed`。

## 先看实际可提出的需求

- “查我们的数据库，纠正 SQL 执行错误后解释结果。” → SQL Agent，需数据库工具、驱动与授权。
- “协调排期并起草邮件，发送前让我审核。” → LangChain 专家组合与 HITL；真实日历/邮件连接器需另接。
- “根据文档或多个资料源回答并列出依据。” → 检索组件、LangGraph 路由，或现成 Deep Agents 应用。
- “研究一个主题，交付引用报告或按品牌风格生成图文。” → Deep Agents / GPT Researcher 等应用；搜索、图片与文档转换另有依赖。
- “修改代码，跑检查，交付 PR。” → Open SWE 的完整工程应用，不能简化为 LangChain 核心一键完成。

## 用途导航

- [完成业务任务并与人协作](#grp-business)（7 项确认）
- [查询数据与研究资料](#grp-knowledge)（6 项确认）
- [生成并交付工作成果](#grp-deliverables)（6 项确认）
- [保存上下文并持续工作](#grp-continuity)（7 项确认）
- [组织专家与复杂任务](#grp-coordination)（8 项确认）
- [适配模型与交互方式](#grp-interaction)（5 项确认）
- [限制风险并应对失败](#grp-control)（8 项确认）
- [验证质量并投入运行](#grp-operations)（5 项确认）

<a id="grp-business"></a>

## 完成业务任务并与人协作

### 让助手查询数据、调用业务工具并完成多步任务

**核心 · LangChain API · p-tool-loop**

Agent 根据任务选择工具、读取结果并继续行动，直到给出最终答复或达到停止条件。

**条件与限制：** 需要支持工具调用的模型，以及开发者实际实现和授权的工具；LangChain 不会自动获得业务系统权限或凭空实现工具。

**来源：** [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)（Introduction）；[LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)（Introduction; Dynamic tool selection）。

### 按用户身份、偏好和当前场景调整助手行为

**核心 · LangChain API · p-personalize**

同一 Agent 可根据应用提供的用户角色、环境和资料改变指令、语气及业务上下文。

**条件与限制：** 身份和凭据来自可信应用上下文；提示词中的角色说明不是权限系统，服务端工具仍需独立鉴权。

**来源：** [Context engineering in LangChain agents](https://docs.langchain.com/oss/python/langchain/context-engineering)（System prompt / Runtime Context example）。

### 在不同阶段只向 Agent 提供适用的工具

**核心 · LangChain API · p-tool-policy**

依据认证状态、权限、功能开关或任务阶段调整可见工具集，减少误选和无关工具干扰。

**条件与限制：** 需编写中间件策略；隐藏模型可见工具不等于完成服务端访问控制，动态加入的工具还需提供执行处理。

**来源：** [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)（Introduction; Dynamic tool selection）。

### 让人审核、修改或拒绝即将执行的业务动作

**核心 · LangChain 入口 · LangGraph 运行/检查点 · p-approve**

工具调用可暂停等待用户决定，审核者可改参数后继续，或拒绝该动作并把反馈交给 Agent。

**条件与限制：** 需要 HumanInTheLoopMiddleware、checkpointer、线程标识及审核交互；持久暂停依赖 LangGraph 存储。只对已配置的调用生效。

**来源：** [LangChain human review and user responses](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)（Interrupt decision types; approval, edit, reject, respond）。

交叉用途：限制风险并应对失败。

### 遇到缺失信息时暂停并取得人的回答

**核心 · LangChain 入口 · LangGraph 运行/检查点 · p-ask-user**

Agent 可提出需要人补充的问题，把回答作为工具结果再继续任务。

**条件与限制：** 需配置适合 ask_user 的 respond 决策及应用交互。respond 不是拒绝副作用动作的替代方式；文档基准为当前 1.4.9，未声称 1.0 已具备全部决策类型。

**来源：** [LangChain human review and user responses](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)（Interrupt decision types; approval, edit, reject, respond）。

### 构建协调排期、日历事项和邮件沟通的助手

**扩展 · 业务连接器 + LangChain 组合 · p-meetings**

通过日历与邮件两个专家，形成查空闲时间、安排事件及起草通知的联合流程。

**条件与限制：** 官方个人助理教程的业务工具是示例或模拟实现；实际接入日历和邮件必须另写或选用连接器并授权。人工审批需要配置，教程不证明已连接用户真实账户。

**案例与证据类型：** 官方 supervisor 教程把日历与邮件子 Agent 封装为工具，并加入发送前的人工审核。（官方业务模拟教程）

**来源：** [Calendar and email assistant tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents-personal-assistant)（Overview; mock calendar and email tools）。

### 让多阶段业务在满足前置条件后才进入下一步

**扩展 · LangChain + LangGraph 状态迁移 · p-staged-support**

构建持续对话流程，例如先确认保修资格，再收集问题，最后提供解决方案或转交处理。

**条件与限制：** 所引 handoff 实现使用 LangChain 中间件和 LangGraph Command 状态更新；需要定义业务状态、合法迁移和真实工具。客服教程中的模拟操作不证明真实退款或转人工已接通。

**案例与证据类型：** 官方 customer-support 示例展示保修状态与问题类型收集，再进入解决阶段。（官方业务模拟教程）

**来源：** [LangChain handoffs using LangGraph state commands](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)（When to use; Basic implementation）；[Stateful customer-support tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs-customer-support)（Overview; support states; tools）。


<a id="grp-knowledge"></a>

## 查询数据与研究资料

### 让 Agent 在指定目录中定位文件与文本内容

**核心 · LangChain API · p-local-search**

通过文件名模式和内容检索找到相关本地文件，为代码或资料任务提供上下文。

**条件与限制：** 需配置 FilesystemFileSearchMiddleware 的根路径和可访问文件；这是 Glob/Grep 检索，不是语义向量检索，也不是完整文件编辑器。

**来源：** [FilesystemFileSearchMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/file_search/FilesystemFileSearchMiddleware)（Overview / introductory paragraph）。

### 用自然语言询问数据库并取得查询结果

**扩展 · 外部工具集成 · p-sql**

Agent 可查表结构、生成 SQL、读取执行结果，并根据数据库错误修正查询后作答。

**条件与限制：** 官方实现需要 langchain-community 的 SQLDatabase / SQLDatabaseToolkit、数据库驱动与访问权限，使用 Chinook SQLite 示例。必须限制数据库权限、资源与允许的查询；并非核心包自带数据库或保证查询正确。

**案例与证据类型：** 官方 Python 1.x SQL agent 教程使用 create_agent 和 Chinook 数据库；本轮只核对文档和代码，未执行查询。（官方可运行教程，本轮未执行）

**来源：** [SQL question-answering agent](https://docs.langchain.com/oss/python/langchain/sql-agent)（Overview; Build your SQL agent; Chinook example）。

### 用文档和检索证据回答问题并提供出处

**扩展 · 检索组件 / Deep Agents 应用 · p-docs-qa**

Agent 可以查询 PDF、私有知识库或文档服务，将相关材料作为回答依据并输出来源链接。

**条件与限制：** 需要加载器、嵌入模型、向量库或已有知识库接口。当前官方 RAG 教程使用 Deep Agents；Chat LangChain 还需要 Managed Deep Agents、MCP 和支持库等应用组件。带引文不保证结论被来源支持。

**实现边界：** 可自行用 create_agent 包装检索工具；本文所核对的现成 RAG/部署案例包含额外组件，不能把全部应用归给 LangChain 核心。

**案例与证据类型：** 当前 Chat LangChain 项目将文档问答部署为 Managed Deep Agent；另有官方 PDF 检索与带引用 RAG 教程。（维护者描述的已部署应用及官方教程）

**来源：** [PDF semantic search with LangChain](https://docs.langchain.com/oss/python/langchain/knowledge-base)（Overview; PDF loading, embeddings, vector stores）；[Evidence-based RAG application with Deep Agents](https://docs.langchain.com/oss/python/deepagents/rag)（View example trace; What you will build）；[Chat LangChain deployed documentation assistant](https://github.com/langchain-ai/chat-langchain/blob/master/README.md)（Overview; Features）；[Chat LangChain Python dependencies](https://github.com/langchain-ai/chat-langchain/blob/master/pyproject.toml)（project.dependencies）。

交叉用途：完成业务任务并与人协作。

### 围绕主题进行多轮资料研究并生成引用报告

**扩展 · Deep Agents / 独立研究应用 · p-research**

围绕问题拆解检索、整理材料并综合成带引用的研究报告，而不是只返回一次搜索结果。

**条件与限制：** 需要搜索服务、模型及应用的研究逻辑。Deep Agents research 示例需 deepagents 和 Tavily 等；独立 GPT Researcher 虽声明 LangChain >=1.0，也同时依赖 langchain-classic，不能当作纯 create_agent 方案或保证报告无误。

**案例与证据类型：** Deep Agents 官方 deep_research 示例与独立开发者 GPT Researcher 项目都提供研究应用；后者依赖清单明确列出 LangChain v1 和 classic。（官方示例与独立项目，本轮未执行）

**来源：** [Deep Agents research example](https://github.com/langchain-ai/deepagents/blob/main/examples/deep_research/README.md)（Custom Instructions; usage）；[Deep research example dependencies](https://github.com/langchain-ai/deepagents/blob/main/examples/deep_research/pyproject.toml)（project.dependencies）；[GPT Researcher project](https://github.com/assafelovic/gpt-researcher/blob/main/README.md)（Introduction; Features）；[GPT Researcher declared Python dependencies](https://github.com/assafelovic/gpt-researcher/blob/main/requirements.txt)（LangChain v1 requirements）。

交叉用途：生成并交付工作成果。

### 复用 MCP 服务提供的查询与动作工具

**扩展 · LangChain MCP 接口 + 外部服务 · p-mcp**

发现远端 MCP 服务的工具并交给 Agent 调用，复用文档搜索或其他服务能力。

**条件与限制：** 当前 1.4.9 文档使用 langchain.mcp.MCPAdapter、langchain[mcp] 和 FastMCP，另需真实 MCP 服务及授权。其他旧项目可能使用 langchain-mcp-adapters，二者不能不加区分。具体能力由服务提供，不是核心包自带所有连接器。

**版本：** 按当前 1.4.9 接口核对；未把 MCPAdapter 路径宣称为所有 1.x 均支持。

**来源：** [LangChain MCPAdapter and MCP service integration](https://docs.langchain.com/oss/python/langchain/mcp)（Introduction; Quickstart; docs MCP example）。

### 让 Agent 查询当前网页资料再作答

**扩展 · 搜索工具服务 · p-web-search**

通过搜索工具取得当前网页结果及相关材料，支持时效性问题和研究任务。

**条件与限制：** 所引实现需 langchain-tavily、Tavily 服务与 API 凭据；搜索质量、页面访问和费用由服务决定，搜索结果本身不保证真实性。

**来源：** [Tavily search tool integration](https://docs.langchain.com/oss/python/integrations/tools/tavily_search)（Introduction; TavilySearch setup and usage）。


<a id="grp-deliverables"></a>

## 生成并交付工作成果

### 把任务结果提取为应用可直接使用的结构化记录

**核心 · LangChain API · p-structured**

得到符合指定字段和类型的联系人、分类或其他结构化结果，便于校验、入库或交给后续流程。

**条件与限制：** 需要适合的 schema 及模型能力；格式与字段校验不证明内容事实正确。原生结构输出和工具调用同时使用还受模型限制。

**版本：** 以 1.4.9 文档为基准；模型 profile 自动识别需 >=1.1，ProviderStrategy.strict 需 >=1.2。

**来源：** [LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output)（Introduction; ContactInfo example; error handling）。

### 让 Agent 在持续会话中执行命令并读取结果

**核心 · LangChain API · p-shell**

Agent 可使用同一个 shell 会话运行项目命令、检查文件或调用已有程序。

**条件与限制：** 需显式配置执行环境与策略。默认 HostExecutionPolicy 是宿主执行，不会自动隔离；Docker 等策略另需对应设施，输出遮蔽也不是防泄露边界。

**来源：** [ShellToolMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/shell_tool/ShellToolMiddleware)（Introduction; execution policies）。

交叉用途：限制风险并应对失败。

### 把研究报告导出为可交付的文档文件

**扩展 · 独立应用扩展 · p-report-export**

使用现成研究应用的导出流程，得到 PDF、Word 等格式的报告成品。

**条件与限制：** 所引实现来自 GPT Researcher，并需要其文档转换依赖和模板；LangChain 返回文本或结构化结果不等于原生生成排版完善的 Word / PDF。

**案例与证据类型：** GPT Researcher README 的 Features 列出报告格式导出，requirements 包括 python-docx、md2pdf 等。（独立项目说明）

**来源：** [GPT Researcher project](https://github.com/assafelovic/gpt-researcher/blob/main/README.md)（Introduction; Features）。

### 按品牌风格制作文章、社交内容和配图

**扩展 · Deep Agents + 外部图像工具 · p-content**

把品牌规范、按需写作技能、研究委派和图像工具组合，生成文章或社交文案及封面素材。

**条件与限制：** 需要 deepagents、写作技能与品牌资料，图像生成另需 Google 模型工具和凭据；研究可选 Tavily。示例以保存素材为结果，不自动获得社交平台发布权限。

**案例与证据类型：** 官方 Content Builder 示例将 AGENTS.md、skills 和子代理配置结合，输出 post.md 与图片文件。（官方应用示例，本轮未执行）

**来源：** [Deep Agents content-builder example](https://github.com/langchain-ai/deepagents/blob/main/examples/content-builder-agent/README.md)（Introduction; architecture; output）；[Content-builder example dependencies](https://github.com/langchain-ai/deepagents/blob/main/examples/content-builder-agent/pyproject.toml)（project.dependencies）。

### 从工程任务出发修改代码、验证并交付 PR

**扩展 · Open SWE · Deep Agents · LangGraph · p-coding-pr**

通过完整工程 Agent 应用调查代码库、实现修改、运行检查，并把变更交付为拉取请求。

**条件与限制：** 所引 Open SWE 需要 Deep Agents、LangGraph、代码工具、沙箱、GitHub 授权和应用 UI；当前原样部署还依赖 Managed Deep Agents。项目声明仍在活跃开发且不保证稳定，不能视为 LangChain 核心自动编程能力。

**版本：** 所读 Open SWE manifest 要求 Python >=3.14、deepagents==0.7.32、langchain[mcp]>=1.4.8；不是 LangChain 本身的最低 Python 版本。

**案例与证据类型：** Open SWE README 和 Python 依赖清单明确区分 Deep Agents、LangGraph 以及应用自有工程工具。（维护者描述的应用，本轮未部署）

**来源：** [Open SWE engineering agent](https://github.com/langchain-ai/open-swe/blob/main/README.md)（Introduction; How it works; deployment note）；[Open SWE component dependencies](https://github.com/langchain-ai/open-swe/blob/main/pyproject.toml)（project.dependencies; requires-python）。

交叉用途：组织专家与复杂任务。

### 以文件形式保存、修改和复用任务成果

**扩展 · Deep Agents 文件系统 · p-files**

Agent 可把中间材料和最终成果组织为文件，并在后续步骤继续读取或编辑。

**条件与限制：** 需 Deep Agents 的 FilesystemMiddleware 和合适 backend。StateBackend 是线程内虚拟文件，FilesystemBackend 写真实磁盘，跨线程持久化需 StoreBackend 等；核心 create_agent 不默认附送这整套文件系统。

**来源：** [Deep Agents filesystem backends](https://docs.langchain.com/oss/python/deepagents/backends)（FilesystemBackend; StateBackend; CompositeBackend）。


<a id="grp-continuity"></a>

## 保存上下文并持续工作

### 让助手在同一会话中记住前文并继续任务

**核心 · LangChain 入口 · LangGraph 运行/检查点 · p-conversation-memory**

后续问题可以引用同一线程的已有消息和状态，而无需每次重新解释背景。

**条件与限制：** 通过 create_agent 的 checkpointer 接口启用，底层是 LangGraph。需稳定 thread_id；内存型示例不会跨进程持久保存，生产需数据库后端及用户隔离。

**来源：** [LangChain conversation memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)（Overview; Usage）。

### 让长对话在上下文接近上限时继续进行

**核心 · LangChain API · p-summarize**

按阈值压缩较早消息并保留近期上下文，降低整段历史塞满模型窗口的风险。

**条件与限制：** 需要摘要模型或自定义摘要器；摘要可能遗漏信息，不是无限或无损记忆。

**来源：** [SummarizationMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/summarization/SummarizationMiddleware)（Overview / introductory paragraph）。

### 跨会话记住用户资料、偏好和已保存的知识

**核心 · LangChain 入口 · LangGraph Store · p-long-memory**

在新对话中查回以前保存的信息，而不只依赖当前聊天历史。

**条件与限制：** create_agent 提供 store 接口，实际存储由 LangGraph Store 承担；需设计用户命名空间、读写工具和持久后端。内存型 Store 不能跨进程保存，存储记录不等于模型被重新训练。

**来源：** [LangChain memory using LangGraph stores](https://docs.langchain.com/oss/python/langchain/long-term-memory)（Introduction; Usage; Memory storage）。

### 在流程失败或服务重启后从持久状态恢复

**扩展 · LangGraph 检查点运行时 · p-recover**

通过检查点保存已完成步骤，让长任务在条件满足时继续，而不是总从头开始。

**条件与限制：** 需 LangGraph checkpointer、持久存储和正确线程身份；恢复受 durability 模式影响。未完成步骤和外部副作用仍可能重做，需幂等设计，不能宣称恰好执行一次。

**来源：** [LangGraph checkpoint recovery](https://docs.langchain.com/oss/python/langgraph/checkpointers)（Fault-tolerance; durability modes）。

### 从历史检查点重放或分支探索另一条方案

**扩展 · LangGraph 历史重放 · p-replay**

可查看历史状态，修改某一步的状态后继续，比较不同路径的任务结果。

**条件与限制：** 需要保留检查点及相关应用交互；重放会重新执行后续模型和 API 调用，可能产生费用或副作用，不是只读回看缓存。

**来源：** [LangGraph replay and branching](https://docs.langchain.com/oss/python/langgraph/use-time-travel)（Introduction; replay; fork）。

### 把过大的工具内容移出上下文并按需取回

**扩展 · Deep Agents 上下文管理 · p-offload**

长任务中可把大段结果存到 backend，用路径和预览替代，然后按需读取或搜索细节。

**条件与限制：** 需 Deep Agents 的上下文管理和文件 backend；不代表模型能同时理解任意大资料。自动 offload、摘要和文件保留有各自阈值与存储策略。

**来源：** [Deep Agents context offloading](https://docs.langchain.com/oss/python/deepagents/context-engineering)（Context compression / Offloading）。

### 把反馈保存为后续会话可使用的指令文件

**扩展 · Deep Agents 文件记忆 · p-instruction-memory**

允许 Agent 读取已配置的记忆文件，并在获准时更新偏好或经验供下一次任务使用。

**条件与限制：** 需 deepagents 的 memory 配置和持久 backend；应划分用户/组织命名空间及可写权限。更新文件不是模型权重学习，也不保证反馈正确或能力持续提高。

**来源：** [Deep Agents durable instruction files](https://docs.langchain.com/oss/python/deepagents/memory)（How memory works; Scoped memory）。

交叉用途：完成业务任务并与人协作。


<a id="grp-coordination"></a>

## 组织专家与复杂任务

### 把复杂工作整理为可更新的任务清单

**核心 · LangChain API · p-plan**

Agent 可创建和更新结构化待办，让用户看到计划、进度和待完成事项。

**条件与限制：** 使用 LangChain 的 TodoListMiddleware 即可；清单是模型维护的计划记录，不证明每项已真正完成，Deep Agents 也可按配置复用。

**来源：** [TodoListMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/todo/TodoListMiddleware)（Overview / introductory paragraph）。

### 把不同领域的工作交给专家助手并汇总

**核心 · LangChain 手工组合模式 · p-specialists**

主 Agent 可把专长不同的子 Agent 当作工具调用，让每个专家只处理其领域任务。

**条件与限制：** LangChain 示例通过开发者自行封装工具实现；需要设计输入输出与上下文传递，不是调用 create_agent 就自动生成团队。Deep Agents 提供另一条内置实现路径。

**实现边界：** 核心路径：create_agent + 自定义工具包装；成品子代理中间件属于 deepagents，不能把两个路径混为一个内置功能。

**来源：** [LangChain specialist-agent composition pattern](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents)（Introduction; Basic implementation）；[Deep Agents built-in subagent support](https://docs.langchain.com/oss/python/deepagents/subagents)（Introduction; configuration; context isolation）。

### 在需要时才加载某项专业知识或操作流程

**核心 · LangChain 手工组合模式 · p-skills**

一个助手可以按任务加载领域指令、模板或参考资料，避免把全部知识预先放入上下文。

**条件与限制：** LangChain 文档展示自定义 load_skill 工具模式；目录式 SKILL.md 发现与加载是 Deep Agents 的内置能力。脚本是否能执行还取决于额外工具和权限。

**实现边界：** 手工工具模式不等于自动支持 Agent Skills 目录规范；后者需 deepagents 或自行开发。

**来源：** [LangChain custom skills pattern](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)（Introduction; Basic implementation; built-in support boundary）；[Deep Agents packaged skill loading](https://docs.langchain.com/oss/python/deepagents/skills)（Introduction; Usage）。

### 并行咨询不同资料系统后综合回答

**扩展 · LangGraph 路由编排 · p-multi-source**

把一个问题分配给不同领域或数据源的专家，并把相关结果合成为统一答案。

**条件与限制：** 所引 router 使用 LangGraph Command / Send、状态图和 LangChain 专家；GitHub、Notion、Slack 教程工具是模拟接口，真实使用需连接器、鉴权及数据权限。

**案例与证据类型：** 官方多源知识库路由教程演示 GitHub、Notion 与 Slack 三类资料的并行分发。（官方数据源模拟教程）

**来源：** [Multi-source knowledge base routing example](https://docs.langchain.com/oss/python/langchain/multi-agent/router-knowledge-base)（Overview; mock source agents; Send routing）。

交叉用途：查询数据与研究资料。

### 把固定业务步骤与 Agent 自主决策放入同一流程

**扩展 · LangGraph 直接编排 · p-hybrid-workflow**

对必须按顺序执行的步骤保留代码控制，同时让部分步骤自主决定调用哪些工具。

**条件与限制：** 需要直接使用 LangGraph 的图或 Functional API 编排状态、分支和停止条件；这比 create_agent 的标准循环更底层，不会自动理解业务规则。

**来源：** [LangGraph workflow patterns](https://docs.langchain.com/oss/python/langgraph/workflows-agents)（Introduction; Orchestrator-worker）。

### 动态拆分复杂任务并汇总多个工作结果

**扩展 · LangGraph 直接编排 · p-fanout**

编排器可按当前输入生成子任务，分配给多个 worker，再综合它们的输出。

**条件与限制：** 需要 LangGraph 的 orchestrator-worker 模式、Send 分发、结果汇聚与并发预算；并行不保证更快或更准确，需管理冲突和重复工作。

**来源：** [LangGraph workflow patterns](https://docs.langchain.com/oss/python/langgraph/workflows-agents)（Introduction; Orchestrator-worker）。

### 后台运行长任务并让主助手继续响应

**扩展 · Deep Agents 异步子代理 · p-background-workers**

主 Agent 可启动后台子任务，同时继续与用户交互，并查询进展、补充指令或取消任务。

**条件与限制：** 需要 Deep Agents 异步子代理及相应工作端配置；Agent Server 的完成通知等能力取决于运行环境。这与 Python async/await 同步等待模式不同。

**版本：** 所读文档的任务通知需 deepagents>=0.7.26；update_strategy、webhook 和 notify_parent 等部分选项需 >=0.7.30，其中多项标为 Beta。

**来源：** [Deep Agents background subagents](https://docs.langchain.com/oss/python/deepagents/async-subagents)（Introduction; prerequisites; task control）。

### 按明确标准反复检查和修订草稿

**扩展 · Deep Agents rubric · Beta · p-rubric**

用评分规则和 grader 模型反馈驱动多轮改写，直到规则满足或达到迭代终止条件。

**条件与限制：** 需要 Deep Agents RubricMiddleware、调用时的 rubric 和迭代上限；它是模型自评，不等于独立评审或事实证明。必须检查终止状态，不能把最后一次草稿自动当作通过。

**版本：** deepagents>=0.6.5；文档标为 Beta。

**来源：** [Deep Agents RubricMiddleware API](https://reference.langchain.com/python/deepagents/middleware/rubric/RubricMiddleware)（Introduction; termination states）。

交叉用途：生成并交付工作成果。


<a id="grp-interaction"></a>

## 适配模型与交互方式

### 为不同请求或任务阶段选择合适的模型

**核心 · LangChain API · p-model-routing**

可替换模型提供方，或按当前状态与复杂度选择不同模型，平衡能力、成本和时延。

**条件与限制：** 需要相应提供方集成和可用凭据；切换接口统一不代表模型行为、工具能力或价格相同。路由策略由应用实现。

**来源：** [LangChain model capabilities and selection](https://docs.langchain.com/oss/python/langchain/models)（Overview; Dynamic model selection; Multimodal）。

### 边执行边向用户展示答复和任务进展

**核心 · LangChain 入口 · LangGraph 运行/检查点 · p-stream**

应用可连续展示生成中的文本、Agent 步骤状态和工具自定义进度，避免只能等待最终答案。

**条件与限制：** 需应用消费流并构建界面；底层模型决定 token 流式能力，进度显示不等于任务成功。

**来源：** [LangChain streaming](https://docs.langchain.com/oss/python/langchain/streaming)（Capabilities; agent progress; LLM tokens）。

### 通过语音与能调用工具的助手对话

**扩展 · 语音服务 + 应用集成 · p-voice**

将说话输入转换为文本，交给 Agent 处理业务工具，再把答复转换为可播放语音。

**条件与限制：** 需要 STT、TTS、音频客户端及实时传输。官方 Python 示例使用 AssemblyAI、Cartesia 与 WebSocket；语音识别和合成不是 LangChain 模型循环自身完成的。

**案例与证据类型：** 官方 voice-sandwich-demo 让三明治店订单 Agent 连接语音识别与合成流程。（官方端到端参考应用）

**来源：** [LangChain voice-agent application](https://docs.langchain.com/oss/python/langchain/voice-agent)（Overview; Sandwich architecture; AssemblyAI and Cartesia example）。

### 让 Agent 使用图片等多模态资料处理任务

**扩展 · 模型提供方能力 · p-multimodal**

向有相应能力的模型提供图片、音频或其他支持的内容，并结合工具处理结果。

**条件与限制：** LangChain 提供消息与模型接口，识图、语音或视频能力来自具体模型及集成；格式和支持范围必须逐提供方确认，不能把文本模型自动变成视觉模型。

**来源：** [LangChain model capabilities and selection](https://docs.langchain.com/oss/python/langchain/models)（Overview; Dynamic model selection; Multimodal）。

### 用本地开放权重模型驱动工具型助手

**扩展 · Ollama 运行时与集成 · p-local-model**

通过 Ollama 模型集成运行 Agent，减少对远端模型 API 的依赖。

**条件与限制：** 需要 Ollama、langchain-ollama、适合工具调用的模型及本地算力；模型支持程度不同，外部工具、搜索和遥测仍可能联网，不能等同于整个系统离线。

**来源：** [Ollama local model integration](https://docs.langchain.com/oss/python/integrations/chat/ollama)（Overview; tool calling example）。


<a id="grp-control"></a>

## 限制风险并应对失败

### 对特定个人信息进行检测、遮蔽或阻断处理

**核心 · LangChain API · p-pii**

可在配置的位置识别邮箱、信用卡等 PII，并按策略脱敏或阻止相应内容流转。

**条件与限制：** 需配置检测类型、策略和覆盖输入/输出/工具结果的位置；不保证发现全部敏感信息，也不自动完成合规。

**版本：** 流式 wire output 随 apply_to_output 脱敏的文档要求 langchain>=1.3.2。

**来源：** [LangChain guardrails](https://docs.langchain.com/oss/python/langchain/guardrails)（Built-in PII; deterministic and model-based guardrails）。

### 按业务规则检查输入、输出与工具行为

**核心 · LangChain API · p-guardrails**

在 Agent 生命周期中加入确定性规则或模型审核，对不合适的输入、结果或动作进行拦截和反馈。

**条件与限制：** 需要实现判定规则、处理动作与测试；模型审核可能误判，不能据此宣称免疫提示注入或保证输出正确。

**来源：** [LangChain guardrails](https://docs.langchain.com/oss/python/langchain/guardrails)（Built-in PII; deterministic and model-based guardrails）。

### 在模型或外部工具短暂失败后重试任务步骤

**核心 · LangChain API · p-retry**

对选定异常采用可配置退避重试，提高临时网络或服务故障下继续完成请求的机会。

**条件与限制：** 需配置异常范围、重试次数与终止行为；带副作用的工具必须处理幂等，重试不保证一定成功。

**来源：** [ModelRetryMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/model_retry/ModelRetryMiddleware)（Overview / introductory paragraph）；[ToolRetryMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/tool_retry/ToolRetryMiddleware)（Overview / introductory paragraph）。

### 把工具错误反馈给模型以修正后续调用

**核心 · LangChain API · p-tool-repair**

将可处理的执行异常转换为模型能读取的错误结果，让 Agent 有机会改参数或改计划继续。

**条件与限制：** 需选择可披露的错误及处理策略；这与自动重试不同，不应将原始异常中的秘密直接反馈给模型。

**版本：** ToolErrorMiddleware 文档要求 langchain>=1.3.14。

**来源：** [ToolErrorMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/tool_error/ToolErrorMiddleware)（Overview / introductory paragraph）。

### 在主模型不可用时尝试其他模型完成请求

**核心 · LangChain API · p-fallback**

主模型调用出错后按顺序尝试备用模型，避免服务完全依赖单一提供方。

**条件与限制：** 需准备备用模型及凭据，并确认工具、结构输出和模型参数兼容；不会自动保证质量与成本等价。

**来源：** [ModelFallbackMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/model_fallback/ModelFallbackMiddleware)（Overview / introductory paragraph）。

### 限制 Agent 无限调用带来的开销与循环

**核心 · LangChain API · p-budgets**

为单次运行或线程设置模型和工具调用次数上限，达到阈值后终止或限制继续执行。

**条件与限制：** 调用次数上限不是精确金额或 token 账单上限；跨运行计数需相应持久状态，并定义终止后的用户体验。

**来源：** [ModelCallLimitMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/model_call_limit/ModelCallLimitMiddleware)（Overview / introductory paragraph）；[ToolCallLimitMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/tool_call_limit/ToolCallLimitMiddleware)（Overview / introductory paragraph）。

### 从大量工具中选出当前问题相关的一小组

**核心 · LangChain API · p-tool-selection**

在主模型决策前用选择器缩小候选工具范围，减少无关工具描述占用上下文。

**条件与限制：** 需要选择器模型及工具描述；增加一次选择成本，且可能漏选关键工具，不是权限检查。

**来源：** [LLMToolSelectorMiddleware API](https://reference.langchain.com/python/langchain/agents/middleware/tool_selection/LLMToolSelectorMiddleware)（Overview / introductory paragraph）。

### 把代码和文件操作放到隔离执行环境

**扩展 · Deep Agents + 沙箱 · p-sandbox**

为 Agent 配置独立的运行空间，用于运行代码、命令和处理任务文件。

**条件与限制：** 需 Deep Agents sandbox backend 和具体沙箱运行时或服务；网络、凭据、配额与持久生命周期仍需配置。不能把本地 FilesystemBackend 或宿主 shell 误当沙箱。

**来源：** [Deep Agents isolated execution backends](https://docs.langchain.com/oss/python/deepagents/sandboxes)（Introduction; provider configuration）。


<a id="grp-operations"></a>

## 验证质量并投入运行

### 测试 Agent 流程而不触发真实业务操作

**核心 · LangChain API · p-test-without-actions**

可用固定模型响应或工具仿真覆盖工具选择、错误和流程分支，减少测试对真实服务副作用的依赖。

**条件与限制：** 固定 fake 模型可不调用 API；LLMToolEmulator 仍会调用模型并可能收费。仿真结果不是实际业务成功证据，也不替代真实集成测试。

**来源：** [LangChain unit testing with fake models](https://docs.langchain.com/oss/python/langchain/test/unit-testing)（Introduction; Mock chat model）；[LLMToolEmulator API](https://reference.langchain.com/python/langchain/agents/middleware/tool_emulator/LLMToolEmulator)（Overview / introductory paragraph）。

### 追查 Agent 为什么选错工具、失败或变慢

**扩展 · LangSmith 平台 · p-trace**

记录模型、工具和步骤轨迹，从调用细节及运行指标中定位问题。

**条件与限制：** 需 LangSmith SDK/集成与对应平台或自托管配置；外发内容、采样和保留策略由应用配置。它是外部观测能力，不是核心循环自动提供完整运营平台。

**来源：** [LangSmith tracing and observability](https://docs.langchain.com/langsmith/observability)（Overview; investigate and monitor）。

### 比较 Agent 版本并把失败案例变为回归测试

**扩展 · LangSmith 平台 · p-evaluate**

基于数据集、规则或评审器比较版本表现，也可在生产交互上运行在线评估。

**条件与限制：** 需 LangSmith 评估工具、测试数据、评审标准及运行预算；自动分数的有效性取决于评审器，不能当作人工验收。

**来源：** [LangSmith evaluation](https://docs.langchain.com/langsmith/evaluation)（Offline and online evaluation）。

### 把 Agent 部署为可供应用调用和扩展的服务

**扩展 · LangSmith Deployment / Agent Server · p-deploy**

利用部署运行时提供线程、运行管理、实时流式与横向扩展等服务能力。

**条件与限制：** 需要 LangSmith Deployment / Agent Server 及配套基础设施；云、自托管和混合部署各有许可、账户及资源要求，不是安装 langchain 即获得托管服务。

**来源：** [LangSmith managed deployment](https://docs.langchain.com/langsmith/deployments)（Introduction; environments; licensing）。

### 按固定时间自动运行重复的 Agent 工作

**扩展 · LangSmith 部署调度 · p-schedule**

部署后的助手可按计划执行报告、提醒或其他周期工作，而不依赖用户每次发消息。

**条件与限制：** 所引 cron 能力来自 LangSmith Deployment / Agent Server；需要部署、输入和调度策略，并正确换算 UTC 时间，实际动作依赖已授权工具。LangChain 核心没有自动附带调度服务。

**来源：** [Scheduled Agent Server runs](https://docs.langchain.com/langsmith/cron-jobs)（Introduction; cron runs）。

## 待验证

### 让 Python Agent 的结果组成可交互业务界面

**待验证 · p-generative-ui**

待验证方向：用结构化结果连接前端组件目录，生成表单、卡片或看板式交互。

已找到官方 json-render / A2UI 前端方案，但所读具体接入示例是 TypeScript。尚未核对 Python 1.x 到该前端的完整运行链路，因此不列为已确认 Python 成果。

已读取的线索：[Declarative generative UI integration pattern](https://docs.langchain.com/oss/python/langchain/frontend/generative-ui)。这不是 Python 端运行成功的证据。

## 实际项目和教程证据的区别

| 项目/示例 | 所见结果 | 归属与限制 |
|---|---|---|
| Chat LangChain | 文档和支持知识问答 | 维护者描述的已部署应用；依赖 Managed Deep Agents、LangChain MCP 和支持库。 |
| Open SWE | 调查、修改、验证并交付 PR | Deep Agents + LangGraph + 工程基础设施；原样部署还需 Managed Deep Agents，项目仍在开发。 |
| GPT Researcher | 引用报告及文档导出 | 独立开发者应用；明确同时依赖 LangChain v1 与 classic，未复现效果声明。 |
| Deep Research / Content Builder | 多步研究、品牌图文素材 | 官方应用示例，另需搜索、图像、模型等依赖；本轮未运行。 |
| SQL / voice-sandwich-demo | 数据库问答、语音订单流程 | 官方可运行参考教程，需数据库或语音服务；本轮未执行。 |
| 日历邮件 / 客服 / 多源路由 | 协作与状态流示范 | 业务工具含模拟或占位实现；不能据此宣称真实账户已接通。 |

## 资料覆盖与缺口

查阅类别包括官方概览和版本说明、Python API 参考、指南与教程、官方应用和依赖文件、独立开发者项目，以及外部集成与平台文档。原始来源共 66 页/文件，其中少量用于限定版本和组件归属。

- 52 项来源支持与 1 项待验证方向描述本轮保留结果，不是完整性指标；没有独立人工基准或跨任务覆盖率。
- 未运行真实模型、付费搜索、数据库、邮件、日历、沙箱或 GitHub 写操作来复现这些应用；来源支持不等于本机运行成功。
- 只对 LangChain 1.4.9 wheel 做静态源码存在性检查，没有安装或执行第三方代码。未对全部集成、LangGraph、Deep Agents 与平台版本建立完整兼容矩阵。
- 官方文档和 API 参考会持续更新。没有明确写出的首次支持版本不作推断；当前可用不表示任意 1.0 环境都可用。
- 部分原 LangChain 检索/RAG 路径已重定向到 Deep Agents 教程；本文按实际实现标注，不因为 URL 或导航栏出现 LangChain 就归为核心。
- LangChain 的长期记忆与会话记忆都有公开入口，但引擎、checkpointer、store 属于 LangGraph；核心标签指公开入口，不表示底层由 LangChain 独立实现。
- 官方日历邮件、客服与多源路由教程包含模拟工具；没有把它们当作真实账户、退款或三方企业系统已打通的证据。
- GPT Researcher 是含 LangChain v1、langchain-classic 及多种独立组件的应用；它的报告与导出能力不能整体归给 LangChain 1.x。
- 没有对每一个第三方工具进行调查。浏览器/桌面控制、复杂文档生成、机器人、金融或临床领域专用 Agent 不在已确认覆盖范围。
- 生成式 UI 的官方材料已读取，但所核对的具体前端示例是 TypeScript；Python 端完整接入未复核，保留为 proposed。
- 引用链接、schema 验证、护栏、评分与持久化都不构成事实正确、权限安全、精确一次执行或任务成功的保证。
- 没有独立人工语义审查或用户验收；所有 confirmed 条目仍为 source_supported，任何条目均未自行授予 reviewed。

## 先发现、后分类的记录

1. 先核对 Python 1.x 官方概览、release、包 manifest 与文档索引，设定范围；未预设用途分类。
2. 结果视角：从 Agent、工具、模型、记忆、结构输出、流式和中间件资料提取可观察结果。
3. 案例视角：检查 SQL、客服、排期邮件、语音教程，以及 Chat LangChain、Open SWE、Deep Research、Content Builder、GPT Researcher 的说明与依赖。
4. 扩展视角：检查 LangGraph、Deep Agents、MCP、Ollama、Tavily、LangSmith 等组件的新增结果与前提。
5. 缺口复查：补查异步任务、历史分支、恢复语义、调度、测试与界面；生成式 UI 的 Python 链路证据不足，保留 proposed。
6. 规范化、去重：合并模型/工具重试、合并 token/进度流、合并 PDF 检索与知识库问答，将手工专家/技能模式与 Deep Agents 成品路径写在同一结果里。
7. 候选稳定后按用户目的分为八组并加少量交叉标签，再逐项核对引文、依赖归属和版本限定。

**停止依据：** 主要用途已有多类来源支持，后续资料多为同类实现、内部细节或未确认版本的旧项目；不为扩充数量提升弱证据。

## 校验与可复核范围

实际结果：**全部指定检查通过**。66/66 个来源的短摘录均与已抓原文匹配；技能的 14 项测试通过，LangChain 1.4.9 发布包的 17 个模块/API 静态检查通过。详情见 [validation-report.txt](validation-report.txt)。包括技能 JSON 校验、技能自身的正反例测试、逐项引文与所抓原文匹配、Markdown/JSON 一致性和 1.4.9 wheel 的静态 API 检查。

静态检查仅下载并读取 wheel ZIP，解析源码以确认 17 个模块中的所需 API 存在，未安装、导入或执行第三方代码。它不验证整套应用能运行，也不检查某次模型输出是否正确。

```sh
python3 .agents/skills/p-discovery/scripts/validate.py outputs/langchain-agent/possibilities.json
python3 -m unittest discover -s .agents/skills/p-discovery/tests -v
```
