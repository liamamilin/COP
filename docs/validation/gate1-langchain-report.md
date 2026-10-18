# Gate 1 — LangChain Capability Acquisition Test

> 日期：2026-09-30
> 被测工件：LangChain Agent Development COP（`fixtures/reference-langchain-cop.json`，22 Stage / 12 Operation / 5 Goal / 5 Practice）
> 目标 Goal：**Build a tool-calling agent**（`goal.tool-agent`）
> 方法：只使用 COP Studio 产出的内容。不查阅 LangChain 官方文档来补全缺口——只有当 COP 明确指向某个 Source 时才打开它。
> 结论摘要：**结构成立，可执行性部分成立，完成能力未证明。**

---

## 0. Step 0 — 工程基线

`make verify`（不干扰运行中的栈）：

```
ruff / eslint / tsc     All checks passed
schema drift            none
backend                 276 passed   (0 failed)
web                      45 passed   (0 failed)
E2E                      27 passed   (0 failed)
```

栈健康：api / web / worker / postgres 全部 up，api 200、web 200。

### 0.1 Step 0 期间发现的环境问题

**E1 — `make seed` 不会升级已存在的参考项目（blocker，阻碍验收）**

数据库里已有一个 `LangChain Agent Development` 项目。`make seed` 检测到同名 domain
后直接返回 `"Reference project already exists"`，不做任何更新。结果：

| | 应用内的 v1/v2 | 仓库当前 fixture |
|---|---|---|
| 有 example 的 Stage | 0 / 22 | 22 / 22 |
| 有 implementation detail 的 Stage | 0 / 22 | 22 / 22 |
| 项目 Sources | 0 | 6 |

也就是说：**任何在升级前执行过 `make seed` 的用户，会永远停留在修复前的工件上**，
而 `make seed` 静默成功、不提示、不提供升级路径。修复前的工件里 0 个 example、
0 条 implementation detail——按当前门禁它根本无法发布。

处理方式：不删除该项目（它有 draft 和学习记录），另建一个独立验收项目
`LangChain Agent Development (Gate 1 validation)`，用与 `make seed` 完全相同的代码路径
生成 v1 与 6 个 Source。

**E2 — 参考项目残留一个未清理的 draft（cosmetic）**

该 draft 由 v2 fork 而来，0 个 locked paths，学习进度 0/5。是测试或手工操作的残留，
`make seed` 也不会清理。

---

## 1. Main Process 评估

**结论：代表能力获取路径，不是文档目录。** 通过。

```
Goal   Build a tool-calling agent
       outcome: The agent can select and call a Python tool during its model loop.
       prereq : goal.basic-agent

Main Process  Build a tool-calling agent
       start  : foundation.langchain-base  (Shared Foundation)
       Stages : Define a tool → Create agent with tools → Invoke → Verify the tool loop
       Operations 沿路径: Define → Create → Attach → Invoke → Verify
```

逐项检查：

- **起点合理？** 是。起点是 Shared Foundation（安装 LangChain + 配置模型 + 设置 API key），
  而不是第一个功能 Stage。所有 Main Process 共用同一个 Foundation，抽取正确。
- **每个 Stage 是否朝 Goal 推进？** 是。四个 Stage 恰好对应工具调用的四个必要环节，
  顺序是能力依赖顺序，不是文档章节顺序。
- **是否为文档目录结构？** 否。`Install / Use tools / Add memory / Build RAG`
  这种教程目录形态被刻意排除在 Goal 之外——`Install` 在 Foundation 里，
  其余是 5 个独立 Goal，每个都是可验证的能力结果。

一个观察：**`stage.foundation.model` 的 `why_it_exists` 为空字符串**，
而 Shared Foundation 本身的 `why_it_exists` 也是空的。这是唯一一处「Stage 未能回答
为什么存在」的情况，且只影响 Foundation。

---

## 2. 逐 Stage 走查（实际执行）

### Stage 1 — Define a tool ✅ 通过

COP 给出的命令，原样执行：

```bash
cat > tools.py <<'PY'
from langchain.tools import tool

@tool
def word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())
PY
```

`expected_result` 给出的验证方式，原样执行：

```bash
python -c "from tools import word_count; print(word_count.invoke('a b c'))"
# → 3
```

**实际输出 `3`，与 COP 声明完全一致。** 这是本工件第一条被真正执行并验证的命令。

---

### Stage 2 — Create agent with tools ❌ **BLOCKER**

COP 给出的命令（原样）：

```bash
python -c "from langchain.agents import create_agent; from langchain_openai import ChatOpenAI; \
from tools import word_count; a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[word_count]); \
print([t.name for t in a.get_tools()])"
```

`expected_result`：*The script prints `['word_count']`.*

**实际结果：该命令无法运行。**

```
AttributeError: 'CompiledStateGraph' object has no attribute 'get_tools'
```

`create_agent` 返回的是 `CompiledStateGraph`，其公开的工具相关方法只有 `as_tool`。
**`get_tools()` 不存在。** 该 Stage 的 example 声明的输出 `['word_count']`
是一个无法产生的值——即工件里存在一处**捏造的执行结果**。

> 附注：用真实的 `OPENAI_API_KEY` 才能走到这一行；改用不需 key 的脚本化模型后，
> 错误依旧，说明问题在 API 名称本身，与凭据无关。
> 已找到可用的正确写法（见 §7 建议）。

---

### Stage 3 — Invoke with a tool-requiring request ⚠️ 声明正确，但未按原样执行

COP 的命令需要一次真实模型调用。我**没有使用用户配置的 API key**，
因此改用一个脚本化的 fake model（会在第一轮发出 tool_call、第二轮给出最终答案）
来验证该 Stage 的**核心断言**是否属实。

COP 声明：*Four lines: human, ai (tool call), tool, ai (final answer).*

```
实测 message types : ['human', 'ai', 'tool', 'ai']
与声明一致        : True
tool 返回值        : ['3']
```

**Stage 3 的核心断言成立。** 但命令本身未经真实模型执行。

---

### Stage 4 — Verify the tool loop ⚠️ 声明正确，但未按原样执行

COP 声明：*The list contains a `tool` entry and the assertion passes.*
断言内容：`assert 'tool' in types`

```
实测 'tool' in types : True
```

**Stage 4 的核心断言成立。** 同样未经真实模型执行。

### 2.1 附带发现：Stage 3 / Stage 4 未提示需要 API key

两条命令都用 `ChatOpenAI(model='gpt-4o-mini')`，未设置 key 时会在构造阶段抛
`openai.OpenAIError: Missing credentials`。

这个信息**存在于** Foundation 的第二条 detail（`export OPENAI_API_KEY=...`），
所以只要按 Main Process 顺序走就不会撞上——**顺序处理是正确的**。
但 Stage 自身没有任何回指，单独打开某个 Stage 页面时无从得知。

---

## 3. Operation 评估

**结论：可以回答「我现在到底要做什么」。通过。**

```
Define   Describe and implement a callable capability or contract.
         purpose: Create tools and their callable schema.

Create   Construct a runtime object from configured components.
         purpose: Build an executable agent.

Attach   Connect an optional capability to the agent harness.
         purpose: Add tools, persistence, retrieval, or middleware.

Invoke   Execute a model or agent with an input message/state.

Verify   Check that the intended operational behavior actually occurred.
         purpose: Validate the Goal rather than only configuration.
```

`common_failures` 尤其有价值——它们点名了学习者真正会踩的坑，且经核对确实成立：

- `Create`：*"A string is passed where a model instance is expected, producing a type error."* —— 真实存在该类型检查。
- `Invoke`：*"The result is indexed as an object when it is a dict, so .content raises AttributeError."* —— 与 Stage 3 的 `r['messages'][-1].content` 用法直接相关。
- `Attach`：*"The tool or middleware is added to a list after the agent was constructed, so it is never bound."* —— 与 Stage 2 的 caution 一致。

对照任务给出的判据：Operation 是动作而非主题，**通过**。

---

## 4. Practice 评估 ❌ **BLOCKER**

`practice.tool-agent`：**Build a weather tool agent**

```
1. Define a weather lookup tool.
2. Create an agent with the tool.
3. Ask a question that requires the tool.
4. Inspect execution and confirm the tool result feeds the final response.

expected_outcome: The agent selects the weather tool and returns an answer based on its result.
checkpoint:
  - Why is defining a Tool different from calling it?
  - What loop occurs after the model chooses a Tool?
```

**问题：Stage 教的是 `word_count`（纯函数，零外部依赖），Practice 要的是
weather tool（需要外部数据源）。COP 不提供任何数据源。**

对整个 artifact 做关键词扫描：

```
'http' / 'requests' / 'urllib'   absent
'mock'  / 'stub'   / 'fixture'   absent
'weather'                        PRESENT（仅出现在 Practice 标题与指令里）
```

学习者必须**自己**去发明 weather 数据从哪来——这就是「需要外部检索」。

### 4.1 全局：0 / 5 个 Practice 含任何可执行物

| Practice | 含命令 | 含文件名 | 指令条数 |
|---|---|---|---|
| Create and invoke a minimal agent | no | no | 5 |
| Build a weather tool agent | no | no | 4 |
| Continue a two-turn conversation | no | no | 5 |
| Build a documentation lookup agent | no | no | 5 |
| Add one visible execution control | no | no | 5 |

**Stage 有命令，Practice 没有。** 这是一条系统性的分界：COP 教得会，但不要求你做出东西。

对照：RAG Goal 的 *Stage* 确实给了具体数据路径
（`TextLoader('notes.txt')`），但连它也要求学习者自己先造出 `notes.txt`。

### 4.2 Checkpoint 是概念题，不是产物题

两道 checkpoint 都在问「为什么」和「发生了什么」，都可以靠背概念回答，
不需要真的做出 agent。R5 的机制（必须作答才能完成 Practice）因此被架空——
**填了字就算完成，但没有任何东西证明完成了。**

---

## 5. Executable Evidence 观测

按要求，只测量现状，不改 schema。

### 5.1 Practice 级（任务指定的表）

| Practice | Runnable | Executed | Result Verified |
|---|---|---|---|
| Create and invoke a minimal agent | no | n/a | n/a |
| Build a weather tool agent | no | n/a | n/a |
| Continue a two-turn conversation | no | n/a | n/a |
| Build a documentation lookup agent | no | n/a | n/a |
| Add one visible execution control | no | n/a | n/a |

**0 / 5。** Practice 层不存在可执行证据这一层。

### 5.2 Stage 级（我额外测的，因为这是唯一存在命令的层）

环境：`python3.10` venv，`langchain 1.4.3` + `langchain-openai`。
**未使用用户配置的真实 LLM key。**

| Stage | 命令 | 已执行 | 结果已验证 | 备注 |
|---|---|---|---|---|
| Foundation · Install LangChain | yes | **yes** | **yes** | 打印 `1.4.3`，与声明一致 |
| Foundation · Set the API key | yes | no | n/a | 需用户凭据，本次不执行 |
| Foundation · Configure a model | yes | no | n/a | 需用户凭据 |
| Tool · Define a tool | yes | **yes** | **yes** | 打印 `3`，与声明一致 |
| Tool · Create agent with tools | yes | **yes** | **FAILED** | `AttributeError: get_tools` |
| Tool · Invoke | yes | no | 声明离线验证成立 | 需真实模型 |
| Tool · Verify the tool loop | yes | no | 声明离线验证成立 | 需真实模型 |

**22 个 Stage 中，本次实际执行 3 条，其中 2 条通过、1 条失败。**
其余 19 条未经执行——这正是本批次要测量的状态。

---

## 6. 证据链观测

R3 的修复有效：6 个 Source 全部解析，URL 真实可开。

```
lc-overview   -> https://docs.langchain.com/oss/python/langchain/overview
lc-agents     -> https://docs.langchain.com/oss/python/langchain/agents
lc-tools      -> https://docs.langchain.com/oss/python/langchain/tools
lc-memory     -> .../long-term-memory
lc-retrieval  -> .../retrieval
lc-middleware -> .../middleware
```

但在本 Goal 路径上：

- **Stage 2 / Stage 3 的 `evidence_refs` 为空**——4 个 Stage 里有 2 个零证据。
- Goal 与 Stage 1 / Stage 4 的引用带 `segment_id` 但 `quote_hint` 为 null。
- 引用挂在 **Stage 整体**上，读者无法知道是哪一句话被支撑。

即「可打开」已解决，「可核对」没有。

### 6.1 复核：`segment_id` 是纯装饰字段（审阅时确认）

第 6 节写「引用带 `segment_id`」，需要补一句这个字段的实际效果。逐处核查：

| 位置 | 用途 |
|---|---|
| `schemas/cop-artifact.schema.json` | 字段存在，string |
| `backend/app/domain/cop_models.py:12` | `segment_id: str \| None = None` |
| `backend/app/harness/providers/mock.py:123` | 生成 `seg:{8位哈希}` |
| `backend/app/domain/quality.py:550` | **仅用于判断「有无锚点」的非零判断** |
| `apps/web/components/evidence-panel.tsx:23` | **仅类型声明，渲染时未使用** |

结论：`segment_id` 存在、被 15 个引用携带，但后端只拿它做布尔判断，
前端从不渲染。它不对应源文档中的任何位置——源文档是纯文本，无分段结构、无锚点。

**实际点击行为**：`evidence-panel.tsx:59` 渲染
`/projects/{id}/sources#source-{uuid}`，即跳到 Source Manager 里那条素材。
读者得到「此引用来自某个 source」，得不到「来自哪一段」。

叠加 `refs_without_a_quote = 15/15`（`quote_hint` 全为 null），
界面上连一句摘录都不显示。**信息在最后一步丢失。**

---

## 7. 阻塞项汇总

### B1 — Stage 2 的命令无法运行，且 example 声明了不可能的输出

- **Stage**：Create agent with tools（`stage.tool.create-agent`）
- **学习者实际做了什么**：在 Stage 1 成功生成 `tools.py` 后，原样复制 Stage 2 的命令执行
- **失败类型**：unclear Operation（Operation/Stage 声明了一个不存在的 API）
- **影响**：**blocker** — 4 个 Stage 的第 2 步即中断，Goal 无法完成
- **建议的 COP 改动**：把验证方式改为实际存在的接口。已实测可用写法：

  ```python
  print(list(create_agent(model, tools=[word_count]).get_graph().nodes["tools"].data.tools_by_name))
  # → ['word_count']
  ```

  同时删除或改写 example 里 `output: ['word_count']` 这一无法产生的声明。
  更根本的做法：Stage 的 `expected_result` 应来自实际执行结果，而非人工撰写。

### B2 — Practice 需要 COP 未提供的数据源，无法独立完成

- **Stage**：Practice · Build a weather tool agent（`practice.tool-agent`）
- **学习者实际做了什么**：完成 4 个 Stage 后尝试按 Practice 指令做 weather tool
- **失败类型**：missing Concept（如何为「外部能力」提供数据，COP 未涉及）
- **影响**：**blocker** — 即使修好 B1，Goal 仍无法通过 Practice 完成
- **建议的 COP 改动**：(a) 让 Practice 复用 Stage 已教会的 `word_count` 式纯函数，
  或显式提供 weather 的桩数据；(b) 每个 Practice 至少给出
  「要产出的文件 + 运行命令 + 预期输出」三件套。

### B3 — 0 / 5 个 Practice 含可执行物

- **Stage**：全部 5 个 Practice
- **失败类型**：missing Practice instruction
- **影响**：**friction** — 贯穿全部 Goal，非单点
- **建议的 COP 改动**：把 Practice 的验收条件从「概念上理解」改为「产出一个可运行的东西」，
  并让 checkpoint 询问该产物（例如「你的工具被调用时，消息序列里第几条是 tool？」）。

### B4 — Checkpoint 可用背诵通过

- **Stage**：全部 5 个 Practice
- **失败类型**：missing Practice instruction
- **影响**：**friction**
- **建议的 COP 改动**：checkpoint 绑定产物而非概念。

### B5 — 2 / 4 个 Stage 零证据

- **Stage**：`stage.tool.create-agent`、`stage.tool.invoke`
- **失败类型**：source/evidence problem
- **影响**：**friction**
- **建议的 COP 改动**：为这两个 Stage 补 `lc-agents` 的引用——它们讲的正是
  「工具如何绑定」「如何触发调用」，正是 `lc-agents` 覆盖的内容。

### B6 — `make seed` 不升级已存在的参考项目

- **Stage**：项目生命周期（非 learner 路径，但阻断验收）
- **失败类型**：other
- **影响**：**blocker**（对升级前的用户）
- **建议的 COP 改动**：`make seed` 检测到已存在项目时，比较其版本与当前 fixture，
  不一致则提示或提供 `--upgrade`；至少不要静默返回成功。

### B7 — 端点配置在 22 个 Stage 中出现 0 次（审阅时发现）

- **Stage**：Install LangChain（`stage.foundation.install`）· Configure a model
- **学习者实际做了什么**：按 COP 导出 key 后直接跑 Stage 1「Create the agent」
- **失败类型**：missing Concept
- **影响**：**blocker**（对使用第三方 OpenAI 兼容端点的学习者）
- **实测证据**：

  ```
  ChatOpenAI(model='gpt-4o-mini')          ← 构造成功，不报错
    .invoke('reply with the word ok')      ← 401 Incorrect API key
  ```

  构造阶段永远成功，所以 Stage 1 看起来完全正常。真正调用才炸，而错误信息是
  `Incorrect API key provided ... You can find your API key at
  https://platform.openai.com/account/api-keys`——**主动把学习者引向 OpenAI 官方控制台**。
  用第三方端点的人会照着去找 key，找不到，误以为自己 key 配错；其实 key 是对的，
  **错的是端点从未被设置**。COP 里没有任何地方提过端点，所以这个误诊无法自我纠正。

- **全文关键词计数**（22 Stage）：

  ```
  base_url 0   endpoint 0   OPENAI_BASE_URL 0   api_base 0   openai_compatible 0
  出现的环境变量仅：OPENAI_API_KEY
  ```

- **与 COP 自身 caution 的矛盾**：`stage.foundation.model` 写
  「A 401 here means the key or the model name is wrong」，
  **漏了「也可能是端点」**——而在第三方端点场景下这恰是最常见原因。
- **第二层问题**：`gpt-4o-mini` 是 OpenAI 模型名。第三方端点用别的模型名
  （本机为 `deepseek/deepseek-v4-flash`），所以「装 provider」在内容层面也不成立。
- **建议的 COP 改动**：(a) `Install LangChain` 增加一条 detail 讲
  `export OPENAI_BASE_URL=...`，说明不设则默认走 api.openai.com；
  (b) 修正 `Configure a model` 的 caution，写入「也可能是端点」并说明
  401 消息里的 OpenAI 地址是误导而非 key 出错的证据；
  (c) 给一个可自查动作（如 `curl $OPENAI_BASE_URL/models`）区分 key 错与端点错。

### B8 — Evidence 只能跳到 source 页面，不能定位到段落（审阅时发现）

- **Stage**：全部含 `evidence_refs` 的 Stage
- **学习者实际做了什么**：点击 Stage 页的 `LangChain overview` 证据链接
- **失败类型**：source/evidence problem
- **影响**：**friction**（不是 blocker，但削弱产品最核心的承诺）
- **实测行为**：`evidence-panel.tsx:59` 渲染
  `/projects/{id}/sources#source-{uuid}`，跳到 Source Manager 里那条素材。
  读者得到「此引用来自某个 source」，得不到「来自哪一段」。
  叠加 `quote_hint` 15/15 为 null，界面上连一句摘录都不显示。
- **根因**：`segment_id` 是纯装饰字段——后端只拿它做非零判断
  （`quality.py:550`），前端只声明不使用（`evidence-panel.tsx:23`）。
  它不对应源文档任何位置：源文档是纯文本，无分段结构、无锚点。
- **建议的 COP 改动**：分三档，代价递增。
  - **A 界面诚实化**（便宜，纯前端 + 后端一处解析判断，不碰 schema）：
    `segment_id` 有值但无法解析时明确写「未定位到具体段落」，
    `quote_hint` 缺失时不假装有据可查。**不解决定位，但停止误导。**
  - **B 摘录优先**（改内容不改结构）：生成时要求 `quote_hint` 填源文档中
    真实存在的那句话，界面显示摘录，读者可自行在素材中检索。
  - **C 真锚点**（贵）：给源文档建分段结构，`segment_id` 指向真实偏移，
    Source Manager 高亮该段。**此项属于已推迟的
    `docs/proposals/evidence-v1.1.md` Level 1 主张级证据。**
- **建议顺序**：A 立即（停止误导）；B 在 Gate 2 之后，
  先观察真实 provider 生成的 `quote_hint` 质量再定阈值；C 等 v1.1 决策。

> **前提**：A/B/C 都无法解决「引用到底准不准」。摘录可能是模型编的，
> 锚点可能指向错误段落。`quote_hint` 填满 15/15 之后，
> 仍然无法证明这些摘录真实存在。那需要 v1.1 的可验证主张。

### B9 — 3 处写文件命令要求学习者同时懂 shell 与 LangChain（审阅时发现，已修）

- **Stage**：Define a tool · Wrap the retriever as a tool · Write the guardrail middleware
- **失败类型**：missing Concept（但经核查**不是普遍问题**）
- **影响**：**friction**
- **实测分布**（23 条 implementation_detail）：

  ```
  纯 langchain/python   16    ← 单行 python -c，无 shell 语法
  纯 shell                3    ← 全在 Foundation（venv / pip / export）
  混杂两类                3    ← 全是 cat > file <<'PY'
  ```

  所以「混杂两类知识」不是全局写法问题，而是**写文件这一个动作**带来的。
- **16 个 Concept 里没有任何一个覆盖 shell 或文件系统**：

  ```
  Tool, Tool schema, Agent, Agent loop, Model, Message, State, Persistence,
  Thread, Retrieval, Middleware, Prompt, Harness, Knowledge source, LangChain
  ```

  学习者在 `stage.tool.define` 需要同时理解 heredoc 语法、`@tool`、类型注解，
  **三者无任何一层铺垫**，而这在这条路径上只出现 3 次。

#### 走过的弯路：选项 1（改写法）已被证伪

最初判断是「heredoc 换成 `python -c` 即可去�� shell 层」。**实测三种变体全部失败**：

| 变体 | 失败原因 |
|---|---|
| `open().write('''...''')` | `search.py` 里的 `"\n".join()` 被外层字符串先解释转义，写出断行引号 → `SyntaxError: unterminated string literal` |
| `r"""..."""` | shell 单引号与 Python 三引号嵌套 → `SyntaxError: invalid syntax` |
| `chr(10)` 拼接 | 产出 `return chr(10).join(...)`，已不是要教的内容，且缩进仍传不对 |

**根因**：heredoc 之所以被用在这里，唯一理由就是它能**原样传递任意字节**。
那 16 条单行命令与这 3 条多行文件命令的约束完全不同——前者的形式简洁不能推广到后者。
换掉 heredoc 不能简化难度，只会把它转移到三层引号转义上。

#### 最终修法：保留 heredoc，在上下文解释（不新增 Concept）

1. **`Install LangChain` 新增第 3 条 detail**「Point the SDK at your provider, if it is not OpenAI」
   —— 消除 B7。`export OPENAI_BASE_URL=...`，并说明不设则默认走 api.openai.com。
2. **`Install LangChain` 新增第 4 条 detail**「Read the heredoc used to write files」
   —— 解释 `<<'TAG'` 的作用、单引号为何要加（阻止 `$HOME` 展开）、
   结束标记必须顶格。caution 里写明「这是唯一解释 heredoc 的地方，
   用到它的 Stage 假定你读过这里」。
3. **修正 `Configure a model` 的 caution**：401 可能是 key / 端点 / 模型名三者之一，
   按此顺序排查；并说明第三方端点下错误信息提到 platform.openai.com 是**误导而非证据**。
4. **3 处 heredoc 的 `expected_result` 补落盘确认**（`ls tools.py` / `python -c "import search"`），
   因为不再依赖 shell 的即时反馈；导入失败通常意味着 heredoc 未闭合，而不是 Python 写错。

> **Concept 数保持 16。** shell 不是这门课的能力目标，
> 把它 elevate 成第 17 个 Concept 是把工具细节当概念；
> 而 Foundation Stage 本来就是讲 shell 那一层的位置（venv / pip / export 都在那里）。

#### 审阅追问引出的第二个缺口：15 条命令没有一条说 key 从哪来

追问「setup 设了 key 和 endpoint，什么时候用」后实测：

```
15 条 ChatOpenAI 命令，全部是 ChatOpenAI(model='gpt-4o-mini')
api_key    全文 0 次
base_url   全文 0 次
```

机制上靠环境变量隐式生效，**但 COP 从未说明这一点**。
后果：学习者在 Foundation 导出了 key，到 Stage 1 看到 `ChatOpenAI(model=...)`
里没有 key，会读成「Foundation 那几步没用」或「我漏了一步」——
**因果链在 Foundation 和第一个 Stage 之间断开。**

已在 `stage.foundation.model` 补第 2 条 detail「Every later command reads these
from the environment」，包含一条自查命令
（`print('key set:', bool(m.openai_api_key)); print('endpoint:', m.openai_api_base)`），
并说明 `endpoint: None` 在 OpenAI 官方场景下是**正确**的，
以免与「`None` endpoint 导致后续 401」混淆。

#### 第二次证伪：端点变量名我写错了

上一轮写入的 `OPENAI_BASE_URL` **是错的**，实测：

```
OPENAI_BASE_URL  -> None      （被静默忽略）
OPENAI_API_BASE   -> https://api.example.com/v1   （正确）
```

显式传 `base_url=` 参数一定生效，环境变量则是 `OPENAI_API_BASE`。
错名的唯一症状就是 B7 那个 401，所以已把「变量名是 `OPENAI_API_BASE`，
不是 `OPENAI_BASE_URL`」直接写进 caution。

> 这是本次会话第三次「先写进 COP 再实测推翻」（heredoc 替换、`/models` 自查、变量名）。
> 共同教训：**这类内容必须逐条执行验证，不能靠合理推断**——
> 尤其当它恰好是「错了也不会立刻报错」的那类（被忽略的环境变量、无鉴权的自查端点）。

---

## 7.1 Process 全量审查（不做抽样）

前四项发现（Foundation 不可点、端点缺失、heredoc 无解释、key 来源不明）
都是学习者撞上后我逐个补的——**那不是方法**。因为补的四处恰好全在
`process.tool-agent` 一条线上，剩下 4 条 process 我从未走过。

改为机械化全扫，判据三条：
1. 每个 Stage 导入了哪个文件？该文件由哪个 Stage 创建？在同一条 process 内吗？
2. 哪些命令隐式使用 Foundation 导出的环境变量？
3. 哪些命令用了非 LangChain 语法（heredoc）？

### 7.1.1 Main Process 拓扑复核：无缺口

```
process.basic-agent      stages=3  start=foundation.langchain-base
process.tool-agent       stages=4  start=foundation.langchain-base
process.stateful-agent   stages=4  start=foundation.langchain-base
process.agentic-rag      stages=5  start=foundation.langchain-base
process.controlled-agent stages=4  start=foundation.langchain-base
```

五条都正确指向同一 Foundation；无孤儿 Stage；每个 Stage 恰好属于一条 process
（仅 2 个 Foundation Stage 属 0 条 process，符合预期）。
**第 1 节「process 代表能力获取路径而非文档目录」的判定经复核仍成立。**

### 7.1.2 但依赖确实存在，且 schema 无处表达

全扫发现 **8 处跨 Stage 文件依赖**，全部隐式：

```
stage.tool.create-agent      导入 tools.py  <- stage.tool.define
stage.tool.invoke            导入 tools.py
stage.tool.verify-loop       导入 tools.py
stage.rag.create-agent       导入 search.py  <- stage.rag.expose-retrieval-tool
stage.rag.invoke             导入 search.py
stage.rag.verify-grounding   导入 search.py
stage.middleware.attach      导入 guard.py   <- stage.middleware.configure
stage.middleware.verify      导入 guard.py
```

`stage_refs: [a, b, c]` 只表达**顺序**。若 c 依赖 a 产出的文件，
这个依赖在 schema 里**没有字段可放**——于是只能靠文字暗示。
这正是「process 拓扑对、但走起来有缺口」的机制。

> **结构性结论**：`this_stage_requires` 这类字段在当前 schema 中不存在。
> 本轮用文字显式化 8 处（治标）；是否加字段是 schema 决策，留待审阅。

### 7.1.3 全扫发现的两个新缺口（此前未察觉）

**N1 — `stage.rag.prepare-knowledge-access` 第一条命令必然失败**

它 `TextLoader('notes.txt').load()`，而**全文没有任何地方创建 `notes.txt`**。
实测该命令在真实环境下报 `ModuleNotFoundError: langchain_community`
（附带发现：这一步还需要 `langchain-community` 与 `langchain-text-splitters`
两个包，Foundation 只装了 `langchain` 与 `langchain-openai`）。

这条 Stage 之前没被撞到，是因为 RAG 是第 4 个 Goal，前面 3 个先挡住了。

**修复**：`stage.rag.prepare-knowledge-access` 新增第 1 条 detail 创建
`notes.txt`（三行可验证内容），原加载命令降为第 2 条，并在
`expected_result` 里补上需额外安装的两个包。

**N2 — 我自己上一轮引入的污染**

为解释 heredoc 而加的示例命令原本写的是 `cat > notes.txt`——
**与 RAG 路径需要的文件同名**。学习者若先执行该示例，会得到一个只含
一行 `$HOME` 的 `notes.txt`，导致 RAG 全程检索到错误内容且不报错。
已改名 `heredoc-demo.txt`，并在 heredoc 那条 caution 里补上
「它写的文件必须是后续 Stage 真正会读的那个」。

> N2 是本轮最严重的一处：**我修 B9 时亲手造了一个新的静默数据污染**。
> 它不会报错，只会让 RAG 的验证结果失去意义。

### 7.1.4 本轮修复汇总

| 项 | 内容 | 验证 |
|---|---|---|
| 依赖显式化 | 8 处导入补「该文件由哪一步创建」 | 8/8 落地，措辞一致 |
| N1 | RAG 首个 Stage 自建 `notes.txt` + 补两个额外依赖包 | schema 校验通过 |
| N2 | heredoc 示例改名 `heredoc-demo.txt` | 全文已无 `cat > notes.txt` |
| B7/B9/依赖来源 | Foundation 3 条 detail + `Configure a model` 2 条 | 浏览器实测 detail 齐全 |

`make verify`：lint / typecheck / schema drift(none) / 276 / 45 / 27 全绿。
**Concept 数保持 16。**

### 7.1.5 仍未处理（需要 schema 或产品决策）

- **B2 / B3 / B4** — Practice 产物契约：命令放在哪一层。这是最大的一处结构缺口。
- **B8** — 证据定位：分 A/B/C 三档，A 档不碰 schema 可立即做。
- **Stage 间依赖是否需要字段** — 8 处已用文字治标，根治需 schema 变更。
- **`process.stateful-agent` 未逐 Stage 走查** — 全扫只发现「隐式用 key/endpoint」
  这一类已处理的问题，但它的 `thread_id` / checkpointer 语义是否讲清，
  仍需人工走一遍。

#### 一处自查建议被实测推翻并改写

最初写入的判据是 `curl $OPENAI_BASE_URL/models` 区分 401（key 错）与 404（端点错）。
**实测不成立**：

```
假 key 打 api.commandcode.ai/provider/v1/models   → 200，返回完整模型列表
完全不带 key                                        → 200，同样返回列表
```

该网关根本不校验 `/models` 的 key。已改为「用一次真实调用验证」，
并把这个陷阱本身写进 caution——**这正是 B7 想解决的那类误导**，
一个错误的自查建议比没有更糟。

---

## 8. 核心假设判定

> 「用户能否使用一个 COP 工件来获得能力，而不只是读一份结构化文档？」

**答案：目前不能完整获得能力，但失败点不是「结构」，而是「命令未被验证」与
「Practice 不产出物」。**

支持「假设成立」的部分：

- 目标以可验证的能力结果表述，不是「理解 X」。
- Main Process 顺序是能力依赖顺序，Shared Foundation 抽取正确。
- Operation 是动作，且 `common_failures` 点名的陷阱经核对真实存在。
- **Stage 1 的命令与预期结果完全正确**——不是模板文本，是真的能跑。
- **工具循环的核心断言（Stage 3 / 4）经离线验证成立**。

否定「已完成能力获得」的部分：

- 4 步路径在**第 2 步**被一个不存在的 API 阻断。
- 走完 4 步后，**Practice 无法完成**，且没有任何产物产出。
- 22 个 Stage 的命令中，本次实际执行 3 条。这不是「COP 教不会」，
  而是「COP 的命令从未被运行过」。

**因此「COP 退化成高级目录」这个风险并未发生**——工件明显比教程目录强。
真实风险是另一个，且更具体：

> **COP 承诺可执行性，但它的可执行性是断言的，不是被证明的。**

Stage 1 之所以通过，是因为它足够简单。Stage 2 之所以失败，是因为没人跑过它。
B1 不是一个孤立笔误，它精确标出了整批工件的可信度边界：凡是被执行过的部分是对的，
没被执行过的部分没有任何保证。

这也是最值得肯定的一点：**门禁（`command` + `expected_result` 必填）只检查字段存在，
不检查内容可运行。** 门禁通过率 100%，而 Stage 2 的命令 100% 无法运行。

---

## 9. 建议的下一步（仅描述，未实施）

按任务要求不实现、不改 schema、不改 prompt。优先级排序：

1. **执行验证层**（最高优先）。为 Stage 的 `command` 建立「至少被真实执行过一次」
   的记录，与 `expected_result` 比对。这直接消除 B1 这一类问题的根因，
   也让 R1 的内容门禁从「字段存在」升级为「内容可用」。
2. **Practice 产物契约**。Practice 必须声明要产出的文件 / 命令 / 预期输出，
   并让 checkpoint 询问该产物。消除 B2 / B3 / B4。
3. **端点配置**。消除 B7。这是 B1 的同构问题：Stage 内容按 OpenAI 官方假设写成，
   第三方端点场景下 401 报错会误导学习者去查官方控制台。
4. **seed 升级路径**。消除 B6。
5. **证据诚实化**。先做 B8 的 A 档（不碰 schema，停止误导）；
   补 B5（Stage 2 / 3 零证据）；B 档摘录留到 Gate 2 之后观察真实质量；
   C 档真锚点与 claim 级证据按 `docs/proposals/evidence-v1.1.md` 决定。

第 1 项与第 2 项是这个产品与「会生成漂亮结构的文档生成器」之间的分界线。

### 9.1 审阅期间已修（不属于上述待办）

以下三项在审阅阶段发现并当场修复，因为它们挡住了验收路径本身。
记录在此以免与待办混淆：

| 问题 | 修复 | 验证 |
|---|---|---|
| B1 Stage 2 `get_tools()` 不存在 | 改 `enrich_langchain_fixture.py` 生成器（非手改产物） | 新命令输出 `['word_count']`，与 `expected_result` 及此前捏造的 `example.output` 三者一致 |
| 命令不换行，横向溢出 | `globals.css` `.detail-code pre` 改 `pre-wrap` + `overflow-wrap: anywhere`；另修两处 `nowrap` 链接 | 279 字符命令折行、无横向溢出；heredoc 8 行缩进与 `PY` 闭合完好 |
| Shared Foundation 不可点击（起点不可达） | `process-rail.tsx` foundation 改 `<Link>`，补 `↗` 与「· N STAGES」标签 | 5 个节点全为 `<A>`；点击实际导航到 `stage.foundation.install` |
| B7 端点缺失 · B9 heredoc 无解释 · key 来源未说明 | `enrich_langchain_fixture.py` 补 3 条 Foundation detail、修 401 caution、3 处 `expected_result` 加落盘确认 | 浏览器实测 detail 齐全、Concept 仍 16 个；heredoc 命令原样执行 `$HOME` 未展开；`key set: True` 两种场景均符合预期；`make verify` 全绿 |

> 第一行三项修的是**界面与装配**，第二项修的是**内容层**，但两者都只补「缺失的知识」，
> 不放宽任何 Stage 的通过标准。
> **B2 / B3 / B4（Practice 产物契约）与 B8（证据定位）仍未实施**，
> 那是结构决策，按上面的优先级等待。
