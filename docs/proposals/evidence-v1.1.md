# Evidence v1.1 — 设计草案

> 状态：**草案，未实现**。本文档不改变任何行为，也不修改冻结规格。
> 目的：在改 `EvidenceRef` 之前先把问题定义清楚，并让 Gate 1 / Gate 2 的实测
> 结果来决定设计，而不是让设计先跑在事实前面。
>
> 依据：R3 的实测数据（见 §1），以及 2026-09-30 关于证据粒度与证据等级的讨论。

## 1. 现状：实测，不是估计

LangChain 参考工件（22 Stage / 12 Operation / 5 Goal）：

```
refs                       = 15
orphan refs                = 0     全部解析到真实 Source
refs_without_an_anchor     = 0     每条都带 segment_id
refs_without_a_quote       = 15    没有一条带原文
```

当前 `EvidenceRef`：

```json
{ "source_id": "lc-memory", "segment_id": "short-term-memory", "quote_hint": "..." }
```

它挂在 **Goal / Stage 整体**上。所以一个 Stage 里写了这三句话：

1. LangChain supports short-term memory
2. Memory is associated with thread identifiers
3. Persistence is required for multi-turn conversations

读者拿到的信息是「这个 Stage 有出处：LangChain memory 文档 → short-term-memory 段」。
**三句话各自被哪一段支撑，无法回答。**

引用能打开，但不能就地核对。这两件事经常被混为一谈，而 R3 只解决了前一件。

## 2. 证据的最小单位应该是 Claim，不是 Stage

Stage 是**设计产物**：它是「为了让学习者获得某项能力而安排的一步」。
Claim 是**事实单元**：一句可以被单独判真伪的话。

现在把 Evidence 挂在 Stage 上，等于说「整个 Stage 一起有出处」。但 Stage 里
通常混着三类句子：

- 事实断言（需要证据）
- 操作性指令（由 `implementation_details` 承担）
- 组织性说明（"先做这一步再���做那一步"，本身不需要外部来源）

把证据挂在 Stage 上，会让第三类句子看起来也像是有来源的事实。这不是形式问题——
它让读者无法区分「这一步为什么在这个位置」和「这个 API 确实这么用」。

所以：**Claim 是证据的最小单位。**

### 但不要走成论文系统

一个 Stage 可能有五句以上的事实断言，22 个 Stage 加起来是上百条。
逐句提取并标注来源，是 research-assistance 的做法，不是 COP 的做法，而且会引入
两个 COP 已经明确反对的问题：

- **Encyclopedia Failure**——为了覆盖率而堆引用
- **人工成本不可接受**——V1 没有做逐句核对的预算

### 建议的阈值：只标注承重 Claim

一个 Claim 进入证据链，当且仅当满足：

1. **可判真假**。删掉它，Stage 的操作路径仍然成立 → 它是承重的。
2. **会过期或会出错**。API 签名、参数语义、版本差异、默认值。
3. **是「为什么这样设计」而非「怎么做」**。「怎么���」由 implementation detail 承担。

按这个标准，LangChain 的 22 个 Stage 大概只需要 **15–25 条**承重 Claim，
而不是上百条。可核查，且工作量可控。

## 3. 三个证据等级

证据的强度不是一条线，是三件不同的事。混在一起谈会得出错误结论。

### Level 0 — Traceability（已有）

```
Stage → Source
```

回答：**你从哪里来的？**

已实现：15 个引用全部解析，0 orphan，Exa 结果持久化为 Source Snapshot，
发布时报告悬空引用，UI 对无法解析的引用显式标注而不隐藏。

这一层解决的是「不要编造来源」。它成立。

### Level 1 — Claim Evidence（未实现）

```
Claim → Source segment → Quote
```

回答：**为什么这样说？**

需要 `claim` 字段。设计草案（未决，见 §4）：

```json
{
  "claim": "Short-term memory keeps one conversation, scoped by a thread_id",
  "source_ref": { "url": "...", "segment": "short-term-memory" },
  "quote": "Pass a thread_id in the config to invoke so state is scoped to that thread",
  "confidence": "high"
}
```

价值：让读者可以在不打开 Source 的情况下判断这条断言是否被支撑。

**风险**：如果 `quote` 变成必填，模型会开始编造看起来像引文的字符串——比没有引用
更糟，因为它看起来可核查。所以 quote 的可信度取决于它是不是从 Source 原文里
**摘取**的，而不是模型**生成**的。这一条必须由 Gate 2 决定（见 §6）。

### Level 2 — Executable Evidence（形式已存在，从未被验证）

```
Operation → Example → Runnable verification
```

回答：**它真的能用吗？**

这一层**已经存在**，而且形式上相当完整。每个 implementation detail 都有
`command` 和 `expected_result`：

```json
{
  "title": "Install LangChain and a provider integration",
  "command": "python3 -m venv .venv && source .venv/bin/activate && pip install -U langchain langchain-openai",
  "expected_result": "pip ends with 'Successfully installed'. `python -c \"import langchain; print(langchain.__version__)\"` prints a version and exits 0.",
  "caution": "Install into the virtual environment, never the system interpreter."
}
```

**但它从未被执行过。** 22 个 Stage 的命令全部是文本，测试只断言这个字符串**存在**
（`test_content_contract.py` 检查 `command` 字段非空），没有任何一处**运行**它并
比对 `expected_result`。

这是本草案里最重要的一条，理由是：

> COP 的核心主张是「把任意复杂领域压缩成**可执行**能力路径」。
> 如果证据是「可执行断言」而非「已执行记录」，那这个主张目前是**未经验证的**。

对一个以可执行性为卖点的产品，这是比缺 `claim` 字段严重得多的问题。

## 4. Level 1 的未决设计问题

以下**没有**决定，因为它们应该由实测决定：

1. **`claim` 挂在哪？** 挂在 Stage 上作为 `claims[]` 数组，还是提升为 artifact
   的一等集合（新增 `claims` collection）？前者改动小；后者更干净但改动 schema
   的 required 列表，会影响所有旧 Published Version。
2. **`quote` 是否必填？** 必填则可核查性最强，也最容易诱发编造。可选则可能
   永远为空，等于没有。
3. **quote 如何保证是摘取而非生成？** 可选方案：把 Source 原文按 segment 切好
   塞进 prompt，强制模型只能引用给定文本；或后端做一次字符串包含校验。
   后者是确定性的，但会拒绝掉大量「转述式」引用。
4. **`confidence` 要不要？** 主观分数。除非有校准过程，否则只是装饰。
5. **URL 存不存进 ref？** 现在是 ref → Source 行 → `uri` 两跳。artifact 是可移植
   文档（要能导出后独立阅读），把 URL 冗余进 ref 更符合它的定位。

## 5. 与现有结构的兼容性

设计约束：**v1.1 必须是纯增量**。

- `EvidenceRef` 的现有字段一个都不删不改。旧 Published Version 必须继续可读
  （这是 spec 的硬要求，不是偏好）。
- v1.1 的新字段全部可选。缺失时行为与今天完全一致。
- `completeness_summary` 已经能同时报「能否打开」和「能否就地核对」两个数；
  新增 Level 1 之后应再加一个数，而不是替换。

## 6. Gate 1 和 Gate 2 分别回答什么

不要两个变量一起动。

**Gate 1（LangChain 使用闭环）回答 §3 的 Level 2。**
一个真实学习者按 Main Process 走一遍，记录三件事：

- 哪个 Stage 不够具体
- 哪个 Operation 不知道怎么执行
- 哪个 Concept 需要前置解释

如果 22 个命令里有关键的几个跑不通，那么 Level 2 当前的
`command` / `expected_result` 是**装饰**而不是证据。第一优先级是让它们变成记录，
而不是去设计 `claim` 字段。

**Gate 2（真实 Provider + Exa）回答 §3 的 Level 1 和 §4 的第 2、3 点。**
真实 provider 能否稳定产出可摘取的 quote？如果不能，那问题出在检索层
（Source 粒度太粗、segment 切分不对），而不是证据模型——先修检索再谈证据模型。

## 7. 本文档明确不做的事

- 不改 `schemas/cop-artifact.schema.json`
- 不改 H20 / H50 的产出约束
- 不加 `claims` collection
- 不加执行验证流程

在 Gate 1 和 Gate 2 给出结果之前，这些都是设计偏好而不是改进。
