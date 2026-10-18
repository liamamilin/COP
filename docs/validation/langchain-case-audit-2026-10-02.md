# LangChain Case 全面审查 · 2026-10-02

## 结论

目前不能把 LangChain Case 标记为「完整、可信、可独立完成的 golden case」。

原项目仍缺执行内容；补充内容的 Gate 1 项目有完整的结构和页面，但存在可复现的命令错误、断裂的数据流、错误的知识说明和不足以证明成功的验收条件。核心问题不是 Stage 不够多，而是「学习者能否只靠本 Case 从零完成目标」尚未成立。

本次只审查，没有修改业务代码、fixture、已发布版本、学习进度或项目状态，也没有使用真实 API key 或发起付费模型调用。

## 1. 当前审查的是哪个版本

通过只读 API 核实了两个活跃项目，不能混为一谈。

| 项目 | 当前版本 | Stage | 有 Example 的 Stage | 有执行细节的 Stage | 判断 |
| --- | --- | --- | --- | --- | --- |
| LangChain Agent Development · `f1895f04-0d7d-47e0-bdbb-dfcf58bbb32e` | v2 | 22 | 0 | 0 | 仍是目录型旧内容 |
| LangChain Agent Development (Gate 1 validation) · `9163c3df-05ef-4d0f-ae27-cb906f262540` | v1 | 22 | 22 | 22 | 本报告详细审查对象；内容仍不可靠 |

Gate 1 有 2 个 Foundation Stage、5 条 Main Process、5 个 Practice、6 个 Branch；22 个 Stage 中只有 10 个有 evidence_refs。

对产品内当前发布的 Gate 1 artifact 和本地 reference fixture 分别执行了相同的离线检查，下面列出的核心错误两处都存在。

旧项目未自动升级不是猜测：[seed.py](/Users/milin/2026/软件开发/COP/backend/app/scripts/seed.py:66) 按 domain 找到已存在项目后直接返回。重新 seed 不会给它生成更新版本。后续应提供明确的版本升级路径，保留原发布版本和学习进度，不要覆盖用户内容。

## 2. 对用户提出的三个问题的判定

### 2.1 Keep it simple：默认应是脚本，不是长 one-liner

同意。`python -c` 本身合法，适合导入检查、环境探针和一次性演示；它不适合成为多 Stage 能力训练的唯一载体。

当前 Basic 的 Create / Invoke / Inspect 三步分别重新创建 agent。Create 设置了 system_prompt，Invoke 和 Inspect 没有保留它；Inspect 还改用 `hi` 发起新的调用，并不是查看上一步的执行结果。

从用户角度，它看起来是一条连续路径；从运行时角度，它是三个独立进程。这种差异没有被说明。

建议默认路径是「创建一个最小 `agent.py` → 在同一个程序中创建、调用、检查 → `python agent.py`」。每个 Stage 说明自己向同一个文件新增或修改哪一段。one-liner 放入“快速验证”备选，不要为了短而隐藏变量生命周期、文件依赖和配置。

“其他创建方式”也要分层，不能把运行载体、模型配置和 Agent 架构混成一张替代列表：

| 层次 | 默认 | 有用的备选 | 应说明的边界 |
| --- | --- | --- | --- |
| 运行载体 | `.py` 脚本 | `python -c` / Notebook | 独立进程不共享变量；Notebook 有执行顺序和 kernel 环境问题 |
| 模型初始化 | 显式配置的 `ChatOpenAI(...)` | `create_agent(model="openai:...")`；`init_chat_model(...)` 后传入 | 第三方 endpoint 建议用可清楚展示配置的 model instance；快捷字符串仍需 provider 包和配置 |
| 标准 Agent | LangChain v1 `create_agent` | 增加 tools、checkpointer、middleware、response_format | 这些多数是同一个工厂的配置，不是完全不同的架构 |
| 非标准流程 | 保持标准 Agent 主线 | 自定义 LangGraph 工作流 | 多节点、确定性路由等应作为扩展，不强迫入门者先学图编排 |
| 老版本代码 | 当前 v1 API | 旧 `create_react_agent` 的迁移说明 | 不是当前主线的同等推荐分支 |

官方将 `init_chat_model` 定义为统一模型初始化入口，并给出了旧 Agent API 的迁移关系：[LangChain v1 migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)。

### 2.2 Key / Endpoint：内容部分已补，但仍有“隐藏知识”

不能说当前 Gate 1 完全没有说明：Install Foundation 已有 key / endpoint detail，Configure model 也明确说后续命令从环境取配置。这是已完成的补充，不应当再次报告为完全缺失。

但问题仍然成立：

- 普通 Stage 未显示或链接这些前置要求；从 Create agent 直接进入时看不到配置来源。
- `.env` 路径只说“需要某种加载器”，没有给安装、`load_dotenv()`、文件查找路径和加载时机。复制保存 `.env` 不等于 Python 自动读取它。
- 统一硬编码 `gpt-4o-mini`，没有说明第三方网关的模型名、权限和 tool-calling 能力可能不同。
- COP Studio 自己的服务端凭据不会自动进入用户本地教程脚本；两者没有明确区分。
- 没有定义配置优先级和冲突处理；`OPENAI_BASE_URL` 对实际客户端有效，但 `m.openai_api_base` 可能仍是 `None`，不能据此断言 endpoint 没生效。
- “打印 key 验证”会把密钥放到终端、日志或截图。应该验证“是否配置”，而不是显示密钥本身。
- 即使构造时不发网络请求，`ChatOpenAI` 也可能立即要求 key。本次清空相关环境变量后，构造直接抛出 Missing credentials。

官方说明了显式 base_url、OPENAI_API_BASE、OPENAI_BASE_URL 的解析关系；当前 Case 关于最后一个变量“被静默忽略”的断言错误：[ChatOpenAI integration](https://docs.langchain.com/oss/python/integrations/chat/openai)。

### 2.3 `create_agent` 是否合法

对 LangChain v1：合法，而且是官方推荐入口；`system_prompt=` 也合法，不需要为了传静态系统提示而另加 Prompt 模板或 State Modifier。

用户提出的判断适用于部分旧版本资料，不能套到当前 v1 Case 上。官方明确说明从旧 `langgraph.prebuilt.create_react_agent` 迁移到 `langchain.agents.create_agent`：[官方迁移说明](https://docs.langchain.com/oss/python/migrate/langchain-v1)。

本次在 `langchain==1.4.3` 中实际导入，并分别构造了：model instance、`"openai:gpt-4o-mini"` 和 `"gpt-4o-mini"` 三种形式，均返回 CompiledStateGraph；均未调用远端。

因此应修的是版本契约与错误 caution，而不是把正确的 `create_agent` 改成旧 API。

## 3. 优先处理的确定性问题

优先级：P1 = 阻断执行、教错关键知识或造成虚假验收；P2 = 严重影响独立学习、判断与复现。中间件目前没有真正的删除工具，以下不声称它已造成实际数据删除。

### LC-01 · P1 · RAG 命令复制后即语法错误

位置：[fixture](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:733)，生成源：[enrich_langchain_fixture.py](/Users/milin/2026/软件开发/COP/backend/scripts/enrich_langchain_fixture.py:530)。

`search.py` 的 docstring 包含字面量反斜杠 `\"\"\"`。带引号的 heredoc 不会移除这些反斜杠。提取命令里的 Python 原文进行 AST 检查，结果是第 7 行 `SyntaxError: unexpected character after line continuation character`。

这不是 heredoc 未闭合，Case 却把 import failure 几乎都归因于 heredoc，进一步误导排查。

### LC-02 · P1 · 修完引号，RAG 仍检索不到数据

位置：[准备资料](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:694)、[检索工具](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:733)。

前一步的 `chunks` 只存在于一个 `python -c` 进程中，退出后丢失；后一步另起进程，`search.py` 初始化 `CHUNKS=[]`，没有加载、注入或恢复这些 chunks。

只在诊断内存中修正引号、不修改 fixture 后，调用工具的结果是 `no match`。此外，split_documents 产生 Document，检索代码却假定列表元素是 str，即使补上连接也要说明类型转换。

Case 的检索示例写成 `search_notes('retry limit')`，但该函数已经被 `@tool` 转为 StructuredTool；在本次环境中直接这样调用抛出 TypeError，应展示 `.invoke(...)` 的准确形式。

### LC-03 · P1 · “grounded” 验收会接受无资料结果

位置：[verify-grounding](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:833)。

当前只断言有 ToolMessage，然后打印其内容长度。`no match` 也是 8 个字符，所以会被打印成 `grounded in 8 chars`；它不检查相关段落，也不检查最终答案是否使用资料。

建议验证：检索命中目标来源 → ToolMessage 含明确资料事实 → 最终答案正确引用该事实；加一个资料没有答案的问题，要求明确说明未知。简单关键词检索可以作为最小默认方案，不必为了“看起来像 RAG”强制引入向量库，但必须有真实的数据通路。

### LC-04 · P1 · 中间件演示与承诺不一致，且验收漏掉允许路径

位置：[guard](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:901)、[verify](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:969)。

- 要防止的是 delete_project，但实际 `tools=[]`，没有任何删除动作或可观察的副作用。
- 对最后一条消息做子串检查，`UNCONFIRMED delete` 包含 `CONFIRM`，离线实测会被允许。
- `Hello` 也被拒绝，没有按“危险操作需要确认”的语义区分请求。
- 如果以后真的接入工具，before_model 会在循环中再次执行，最后一条可能是 ToolMessage，不能始终把它当用户授权。
- 标题、action 和 example 说“阻止后再允许”，实际 command 只测阻止；一个永远拒绝的实现也能通过。

应选择诚实的一条主线：要么明确这是输入校验玩具示例，不声称实现 human approval；要么用无破坏性的模拟工具演示真实中断、审批、恢复与允许/拒绝结果。节点 hook 和 wrap hook 也应分别讲清：[Custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom)。

### LC-05 · P1 · 多处关键知识说明错误

| 位置 | Case 当前说法 | 本次核实 |
| --- | --- | --- |
| [Basic Create](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:321)；Operation Create | 模型字符串会导致 type error | v1 支持字符串，实测两种字符串均可构造 |
| [Foundation endpoint](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:233) | OPENAI_BASE_URL 被静默忽略 | 实测 SDK 的有效 base_url 正确采用它；LangChain 字段仍可为 None |
| [Define tool](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:420) | 无 docstring 仍可用，只是很少被选 | 没有 docstring 且没显式 description 的 @tool 在装饰时抛 ValueError |
| [State invoke](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:628) | 返回列表末尾是用户问题，不能用 [-1] | 正常完成两轮无工具调用后，末尾是第二轮 AI 回复 |
| [State example](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:635) | 必须传同一个 config 对象 | 新建两个 config 字典、保持同一 thread_id 也能恢复历史 |
| [State expected](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:657) | 第二轮只有 human / ai / human 三条 | 离线框架实测为 human / ai / human / ai 四条 |
| [Basic Invoke](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-cop.json:357) | 加工具后 index 0 是模型的工具请求 | 对该输入来说 index 0 仍是用户消息；同一 Stage 的 example.note 也与 caution 自相矛盾 |

关于工具 description 的官方说明：[Tools](https://docs.langchain.com/oss/python/langchain/tools)。关于完成调用后读取末尾回复与 checkpointer 的官方示例：[Short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)。

对 interrupted / streaming / 自定义图等非普通完成态不能一概承诺末尾都是最终答案；但当前 Case 没有那些配置，不能用它们解释这里的错误输出。

### LC-06 · P2 · 示例输出没有绑定真实输入

- 资料只有约 130 个字符，500/50 切分实际得到 1 chunk，example 却写 17。
- `the quick brown fox jumps` 有 5 个词，Tool invoke example 却写 `tool(3)`。
- `create_agent(...)` 本身返回 graph，不输出 `created`；`created` 来自另一个 `print`。构造表达式和终端输出应分清。
- Define tool 的 example 只有不完整函数声明，却标输出 3；不是可复制运行的完整示例。
- 预期四条工具循环消息是简单单工具路径的示意，不是所有模型每次必然执行的契约。

这里不要求 LLM 的自然语言答案逐字固定；要求确定性输入、程序行为和展示的观测结果对应，非确定性回答明确标注“示例”。

## 4. 用户体验与教学设计缺口

### LC-07 · P1 · Foundation 第二步没有正常浏览入口

已修复的部分：Main Process 中的 Foundation 卡片现在能点击，并进入 Install Stage。这一旧缺陷不再成立。

仍存在的部分：

- 卡片只指向 foundation.stage_refs[0]。
- Foundation Stage 不属于 main_process.stage_refs，因此 StagePage 的 Process Context 不会显示 Foundation 内部的两个阶段，也没有 Next 指向 Configure a model。
- Learn 页面列出 Install / Configure model，但只渲染文本和 Mark complete，没有 Open 链接或执行内容。

以上均已只读浏览器核实。用户看得到“配置模型”这个名称，却不能顺着主线打开它。资料在 JSON 中存在，不等于用户找得到。

实现位置：[ProcessRail](/Users/milin/2026/软件开发/COP/apps/web/components/process-rail.tsx:30)、[StagePage](/Users/milin/2026/软件开发/COP/apps/web/app/projects/[projectId]/stages/[stageId]/page.tsx:17)、[LearnView](/Users/milin/2026/软件开发/COP/apps/web/components/learn-view.tsx:203)。

### LC-08 · P2 · 前置知识、运行条件与排查规则仍隐含

应明确 Python 版本、已测试依赖版本、shell/OS、工作目录、虚拟环境激活状态、文件位置、环境变量作用域与 .env 加载策略。当前默认 shell 命令属于 POSIX 风格，不是 Windows 通用命令；可以只支持 macOS/Linux 主线，但必须声明边界。

当前 `pip install -U` 没有经过验证的版本组合，Python 3.10+ 要求也没写。RAG 的额外依赖埋在 expected_result 中，学习者先运行 import 才可能发现缺包。

错误排查也应改成有条件的诊断，不能写成绝对判据：

- 模型名不对不一定 401；endpoint 路径或模型不存在可能出现其他状态码。
- 429 不一定仅是短期速率限制，应看服务端错误类型。
- 直接模型调用成功，不保证后续永远没有凭据、额度或模型能力问题。
- 路径不对通常是加载器报错，不是必然得到零 chunks。
- 没有 tool call 不一定纯粹是 prompt 错，可能涉及模型能力、schema、网关兼容性或工具绑定。

### LC-09 · P2 · Branch 只是泛泛提示，没有可做的选择

当前 6 个 Branch 主要各是一句描述。Basic Create 没有任何 branch_refs；模型 provider、工具形式、RAG 架构等既没有选择条件，也没有独立配置与可执行例子。

`branch.langgraph-advanced` 只关联 parent_process_ref，没有 Stage branch_refs；ProcessPage 不渲染 Process Branch，Stage selector 只看 branch_refs，因此这个扩展在当前展示路径中漏掉。Learn 页没有呈现分支。

相关实现：[branch selector](/Users/milin/2026/软件开发/COP/apps/web/lib/artifact-selectors.ts:79)、[ProcessPage](/Users/milin/2026/软件开发/COP/apps/web/app/projects/[projectId]/processes/[processId]/page.tsx:22)。

分支需要说明“什么时候选 / 改哪些配置 / 增加什么依赖 / 如何验证 / 如何回到主线”。不需要列举所有 API。尤其 2-step RAG 和 agentic RAG 的目标不同，不能不加解释就当成同一 Goal 的等价替换。

### LC-10 · P1 · Practice 仍不能证明能力获得

5 个 Practice 都没有明确的文件产物、完整执行入口、可核对输出或验收程序。Checkpoint 基本是概念问答。

天气 Practice 与 Stage 的 word_count 例子不一致：没有 weather fixture、数据源选择或无需另一个付费 API 的最小实现。中间件 Practice 让用户选 retry / human approval，但 Stage 实际只实现了关键词输入 guard，两条能力不能自动互相替代。

UI 与 backend 要求非空 checkpoint answer，但不会校验答案是否正确，也没有运行产物。因此“completed”目前代表自报完成，不是 verified。自报可以保留，但应诚实命名，不应据此宣称 Case 已验证。

实现位置：[PracticeCard](/Users/milin/2026/软件开发/COP/apps/web/components/practice-card.tsx:47)、[learning.py](/Users/milin/2026/软件开发/COP/backend/app/api/learning.py:258)。

### LC-11 · P2 · 证据能打开，不代表能核对

- 6 份 reference Source 的 text 是脚本中写死的简短摘要，不是本次下载的文档段落。应明确标注摘要来源，避免看起来像真实抓取快照。
- Source `lc-memory` 标题与正文讲 short-term memory，链接却指向 long-term-memory。
- Source 的 `create_agent(model, tools, system_prompt)` 写法如果按代码复制，会把 keyword-only 参数当成第三个位置参数。
- `segment_id` 没被 EvidencePanel 用于定位具体段落，跳转只是 Source 行；本 Case 又没有 quote_hint。
- 12 个 Stage 零证据；安装、配置、API 返回语义等关键断言没有精准对应到官方内容。

位置：[sources fixture](/Users/milin/2026/软件开发/COP/fixtures/reference-langchain-sources.json:12)、[sources generator](/Users/milin/2026/软件开发/COP/backend/scripts/enrich_langchain_fixture.py:35)、[EvidencePanel](/Users/milin/2026/软件开发/COP/apps/web/components/evidence-panel.tsx:60)。

URL 可解析、source_id 不孤立是必要条件，但不是事实正确性或证据匹配的验收。

## 5. 22 个 Stage 的逐项判定

下面的“可成立”指静态内容或离线构造契约，不表示已经用真实服务商完成模型调用。

| Stage | 当前判定 | 主要缺口 |
| --- | --- | --- |
| Foundation · Install | 需修正 | 默认版本/OS/目录未声明；.env 路径不完整；endpoint 断言错误；示例安装命令漏 provider 包 |
| Foundation · Configure model | 需修正 | 普通浏览入口断裂；诊断说法绝对化；有效 endpoint 观测方式不准确 |
| Basic · Create | API 可成立，说明错误 | 模型字符串被误判；隐藏前置条件；脚本与模型初始化备选缺失 |
| Basic · Invoke | 需修正 | 重建并丢失前一步 system_prompt；index 0 说明错误 |
| Basic · Inspect | 需修正 | 创建并调用新 agent，不是检查上一阶段结果 |
| Tools · Define | 主命令可成立，说明错误 | 无 docstring 的失败行为说错；example 不是完整输入；工具形式备选缺细节 |
| Tools · Create | 当前构造方式可成立 | 已不再使用 get_tools；深入 graph node.data 做检查比较依赖内部结构，缺公开契约说明 |
| Tools · Invoke | 未验证真实模型选择 | 可直接计数的问题不保证用工具；5/3 输出错配；精确四消息预期过强 |
| Tools · Verify loop | 验收不足 | 只查 ToolMessage 存在，未查工具名、参数、结果和最终回答关联 |
| State · Configure persistence | 默认构造可成立 | SqliteSaver 备选只提名称，无安装、连接生命周期和重启验证 |
| State · Create | 构造可成立 | 应说明 checkpointer 与 thread_id 的职责、后续何时必须带配置 |
| State · Invoke thread | 调用模式可成立，说明错误 | 最后消息与“同一 config 对象”说明错误 |
| State · Verify memory | 预期输出错误 | 四消息被写成三消息；缺不同 thread 的对照与明确重启边界 |
| RAG · Prepare | 需修正 | notes.txt 已补；依赖安装位置不当；chunks 不落盘/共享；实际 1 chunk 却写 17 |
| RAG · Expose retrieval tool | 阻断 | 语法错误；CHUNKS 永远为空；直接调用 @tool 示例错误 |
| RAG · Create agent | 受前一步阻断 | 依赖 search.py 不可导入；定义的检索 prompt 后续没有保留 |
| RAG · Invoke | 受前一步阻断 | 只打印类型，看不到检索文本；重建时丢失检索 prompt |
| RAG · Verify grounding | 虚假验收 | no match 也能被称为 grounded；不验证事实来源 |
| Middleware · Choose control | 目标未闭合 | 防 delete_project 的文字契约没有对应工具与副作用 |
| Middleware · Configure | 玩具校验而非审批 | UNCONFIRMED 绕过；正常请求误拦；最后消息未必是用户授权 |
| Middleware · Attach | 构造可成立 | tools=[] 没有危险动作；hook 类型与执行顺序缺细分 |
| Middleware · Verify | 验收不足 | command 只测 blocked，与 title/action/example 承诺的 allowed 路径不一致 |

## 6. 开发者与质量工程角度的根因

### LC-12 · P1 · 现有门禁检查“存在”，没有证明“可用”

本次将有语法错误、错误输出和空数据流的 reference fixture 输入现有 `check_artifact`，返回 `[]`，没有任何质量问题。

检查实现主要验证字段非空、引用存在、Stage 有 example/detail、setup 有 command/validation、Practice 有 checkpoint；不会执行代码、检查输入输出一致性或追踪跨 Stage 产物。[quality.py](/Users/milin/2026/软件开发/COP/backend/app/domain/quality.py:350)。

因此此前产品测试通过和这份 Case 内容错误并不矛盾：测试覆盖了结构与交互契约，还没覆盖领域知识与学习者执行链。应独立记录内容验证状态，不能用 publish、100% 字段覆盖或进度完成替代。

还需建立生成源、fixture、已发布 artifact 的同步规则。本次多数内容由 enrich_langchain_fixture.py 生成，未来只手改 fixture 会被脚本再生覆盖；只改生成器又不会自动升级数据库里的旧项目。metadata 目前也没有 tested_with、实际验证时间与逐项结果。

## 7. 最小整改方向与验收标准

不建议先扩写成 LangChain 百科。保留 5 个 Goal，先让一个默认路径真正闭合，再添加小而明确的备选。

### 第一批：恢复内容可信度

修 RAG 引号、资料连接、工具调用形式、grounding 判据；修 Agent 字符串、endpoint、docstring、消息列表等错误说明；改中间件目标或补齐安全的可观察模拟动作及正反例。

验收：确定性命令都能在隔离环境运行；Example 的输入和程序输出一致；不存在“no match 也算成功”“永远拒绝也算正确控制”的测试。

### 第二批：消除隐藏知识与路径断裂

补全 Foundation 导航；默认使用小脚本；显式配置 key / base_url / model 与 .env 加载策略；声明版本、shell、工作目录和产物生命周期。只打印非敏感配置诊断。

每个可执行 Stage 至少回答：

1. 我从哪个起点开始，必须先完成什么？
2. 需要哪些输入、配置、依赖文件？各自从哪里来？
3. 在哪里创建/修改什么文件，在什么目录执行什么命令？
4. 哪个对象或文件要传给下一阶段，如何保持它？
5. 哪些输出是确定性的，哪些只是模型回答示例？
6. 什么结果证明本阶段达成，而不只是程序没有报错？
7. 常见错误如何区分，不依赖用户未被告知的知识？
8. 有哪些值得选择的备选，什么条件下使用？

### 第三批：把 Practice 变成最小可交付任务

| Goal | 最小交付与验收 |
| --- | --- |
| Basic | 一个能重复运行的 agent.py；配置验证；同一次运行的输入与最终回复 |
| Tools | 完整本地工具与可观测调用；核对 name/args/result；最终回答确实使用该结果 |
| State | 同 thread 的两轮；不同 thread 的对照；明确内存模式退出即丢失；持久化备选单独验证重启 |
| RAG | 本地资料 → 可查询数据 → tool result → 最终事实；未知问题不臆造；检索失败不得通过 |
| Middleware | 一个无破坏性模拟动作；拒绝、允许、绕过输入测试；如教 human approval，则真的展示中断与恢复 |

参考 Stage 和 Practice 应使用同一最小任务。天气任务如果保留，提供本地可确定数据；不要默默增加第三个 API 的申请需求。

### 第四批：发布、证据与维护闭环

给原项目产生显式新版本；不要覆盖旧版本或自动移动学习进度。修复摘要来源标识与证据定位；增加语法/导入、离线执行、跨 Stage 数据流、结果语义和浏览器入口测试。

只有默认路径和 Practice 完成后，再补 provider、tool 形式、存储方式、RAG 架构等备选。Branch 至少提供条件、最小变更、验证与返回主线；扩展不要求初学者全部完成。

发布 Case 的最终判据：一个只具备声明的 Python 基础、没有额外 LangChain 隐藏知识的用户，能只用该 Case 完成 5 个最小任务；验收者能凭保存的产物与结果独立核对。

## 8. 本次验证边界

- 完整阅读了当前 22 个 Stage、5 个 Practice、6 个 Branch、相关 Concept / Operation / Evidence 与生成源。
- 只读检查了两个发布项目的数据，浏览器检查了 Basic Stage、Basic Process、Foundation Install 和 Learn 页面；没有点击完成或提交答案。
- 从当前发布 artifact 和本地 fixture 各提取 22 段嵌入的 Python 代码：21 段语法可解析，1 段明确语法错误。语法通过不代表依赖、网络、行为或跨阶段执行成功。
- 隔离临时环境：Python 3.10，langchain 1.4.3、langchain-openai 1.6.7、langchain-core 1.6.6、langgraph 1.2.12、openai 3.23.0、langchain-community 0.4.2、langchain-text-splitters 1.1.2。这是本次测试组合，不是已经为所有用户验收的推荐依赖锁。
- 验证了真实库的导入、构造、endpoint 解析、无 key 错误、tool description 错误与消息历史契约。State 与 middleware 调用使用离线脚本化模型；它们验证框架与 guard 行为，不证明真实 LLM 的回答能力或服务商兼容性。
- RAG 语法修正在诊断内存中进行，仅为暴露下一层空数据问题，没有修改产品产物。
- 没有端到端跑完 22 个 Stage 的真实模型调用，没有验证用户服务商的模型名、tool calling、额度和错误码；这些必须在明确的测试模型、授权与预算下另验。
- 原先 get_tools API 错误、notes.txt 完全缺失、Foundation 卡片完全不可点击等旧问题已有修复，本报告不将它们当作现存问题。

本次新增文件仅为这份审查报告。
