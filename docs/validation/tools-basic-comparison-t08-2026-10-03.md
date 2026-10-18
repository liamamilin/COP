# T08：Basic 与 Tools 对照及最小共享契约

日期：2026-10-03。

目的：逐项比较两个子样板的实现，提炼真正共有的最小契约，为 A2 的数据结构和展示提供输入。不预设"应该统一"，只记录已经一致的部分、必须不同的部分，以及由此推导的 A2 必要字段。

## 1. 文件与目录结构对照

| 维度 | Basic | Tools | 一致？ |
| --- | --- | --- | --- |
| `config.py` | LC_* 显式配置 + Settings + ConfigError | 同 | 几乎一致（仅 DEFAULT_PROMPT 不同） |
| `agent.py` | build → invoke → inspect 同进程 | 同 | 结构一致，细节不同 |
| `.env.example` | LC_API_KEY / LC_BASE_URL / LC_MODEL / LC_SYSTEM_PROMPT | 同 | 一致 |
| `requirements.txt` | 7 个固定版本 | 同 | 一致 |
| 离线 mock | `FakeMessagesListChatModel`（单轮固定回复） | `_ToolCallMockModel`（多轮脚本化序列） | 不同 |
| 独立验证器 | `inspect_result.py`（结构检查） | `verify_run.py` + `evidence.py`（结构 + re-execution + hash） | 不同 |
| 领域数据 | 无 | `products.json` + `tool.py` | Tools 独有 |
| 备选初始化 | `--model-init identifier`（init_chat_model） | 无 | Basic 独有 |
| 测试 | `test_basic.py`（13 项） | `test_tool.py`（23）+ `test_agent.py`（20）+ `test_evidence.py`（23）= 66 | 规模不同 |

## 2. 完全一致的部分（共享契约候选）

### 2.1 配置层

`config.py` 在两个样板中几乎逐字相同。唯一差异是 `DEFAULT_PROMPT` 常量：

- Basic: `"Answer in one short sentence."`
- Tools: 面向产品目录的多行 prompt

共享契约：

| 要素 | 约定 |
| --- | --- |
| 变量名 | `LC_API_KEY`, `LC_BASE_URL`, `LC_MODEL`, `LC_SYSTEM_PROMPT` |
| 优先级 | 进程环境变量 > 同目录 `.env` 文件 |
| 空值行为 | 空进程值也覆盖文件值并报错 |
| 文件读取 | `dotenv_values(env_file, interpolate=False)`；不搜索父目录、不展开 `${NAME}` |
| URL 验证 | 不含凭据/query/fragment；远程必须 HTTPS；localhost 允许 HTTP；不能是完整请求路径 |
| Settings | `frozen=True` dataclass；`api_key` 的 `repr=False`；`public_summary()` 返回脱敏摘要 |
| ConfigError | `ValueError` 子类；错误信息不包含凭据值 |
| CLI 独立运行 | `python config.py` 打印脱敏 JSON 摘要 |

### 2.2 模型构造

两个 `build_agent` 使用完全相同的 ChatOpenAI 参数：

```python
ChatOpenAI(
    model=settings.model,
    api_key=settings.api_key,
    base_url=settings.base_url,
    timeout=30,
    max_retries=0,
    use_responses_api=False,
)
```

共享契约：同一组显式参数，不依赖 SDK 隐式默认值。`create_agent(model=..., tools=..., system_prompt=...)` 是统一的装配入口。

### 2.3 调用与追踪

```python
with tracing_context(enabled=False):
    return agent.invoke({"messages": [{"role": "user", "content": message}]})
```

共享契约：同一进程内 build → invoke → inspect；显式关闭 LangSmith tracing；输入为 user role 消息字典。

### 2.4 JSON 报告外壳

两个样板的 `main()` 产出相同的外壳字段：

| 字段 | 含义 |
| --- | --- |
| `mode` | `construction-only` / `offline-{fixture,mock}` / `provider-response` |
| `configuration` | `Settings.public_summary()` 或 `null` |
| `note` | 范围说明，不冒充能力证明 |
| `input` | 本次发送的用户消息 |
| `answer` | 最终 AI 回复文本 |
| `messages` | 本次运行的消息序列 |

共享契约：`--output` 使用 exclusive create（`open("x")`），不覆盖已有文件；错误只打印异常类型和 HTTP 状态码，不写成功记录、不泄露凭据。

### 2.5 错误处理

```python
except ConfigError as error:
    print(f"Configuration error: {error}", file=sys.stderr)
    return 2
except Exception as error:
    status = getattr(error, "status_code", None)
    ...
    return 3
```

共享契约：ConfigError → exit 2；运行时异常 → exit 3；不在 stderr/JSON 中打印 provider 原始异常文本。

### 2.6 依赖版本

`requirements.txt` 完全一致（7 个包、同一版本号）。这意味着两个样板可在同一 venv 运行。

## 3. 必须不同的部分

### 3.1 消息链结构（profile）

| | Basic | Tools |
| --- | --- | --- |
| 消息数 | 2 | ≥ 4 |
| 类型序列 | `human → ai` | `human → ai(tool_calls) → tool → ai` |
| 核心证据 | input/answer 文本链接 | tool_call_id 链接 + re-execution + evidence_hash |

这不是可选差异。用 Basic 的两条消息规则判 Tools 会误拒正确运行；用 Tools 的规则判 Basic 会误收缺少工具证据的运行。

**A2 推论**：消息链验证规则必须按 profile 参数化，不能写死为一种模式。

### 3.2 离线模拟

| | Basic | Tools |
| --- | --- | --- |
| 实现 | `FakeMessagesListChatModel`（SDK 内置） | `_ToolCallMockModel`（自定义） |
| 行为 | 一次返回固定文本 | 第一次返回 tool_calls，第二次返回最终答案 |
| 证明力 | 管线可用，回复不是 LLM | 工具调用管线可用，工具结果不是 LLM 推理 |

**A2 推论**：离线模式需要声明自己的消息 profile，不能只说"offline"。

### 3.3 独立验证器

| | Basic `inspect_result.py` | Tools `verify_run.py` + `evidence.py` |
| --- | --- | --- |
| 检查项 | mode、消息类型序列、input 一致、answer 非空且一致 | 上述 + tool_call_id 链接、re-execution 匹配、evidence_hash |
| 工具依赖 | 仅标准库 + json | 需要导入 `evidence.py`（进而导入 `tool.py`） |
| 语义判断 | 人工 | 人工 + re-execution 自动验证工具事实 |

**A2 推论**：验证器需要按 profile 选择检查规则集；Tools 的 re-execution 和 evidence_hash 是 Tools 特有的证据层，不应强加给 Basic。

### 3.4 领域层

Tools 有 `products.json` + `tool.py`（`get_product_info` 纯函数）+ `StructuredTool.from_function` 包装。Basic 没有领域数据。

**A2 推论**：工具定义和领域数据是 Tools 的扩展层，不是共享契约的一部分。但工具的名称、参数、返回值的记录格式（`tool_name`, `tool_args`, `tool_result`, `tool_call_id`）是 Tools profile 的标准字段。

## 4. 最小共享契约

从上述对照提炼出的共享契约分为三层：

### 层 1：必须共享（违反即不合格）

| 契约项 | 内容 |
| --- | --- |
| C1 配置接口 | LC_* 四变量、进程优先、`.env` 同目录、`interpolate=False`、ConfigError 不泄露凭据 |
| C2 Settings 形状 | frozen dataclass、`api_key` repr=False、`public_summary()` 返回四字段 dict |
| C3 模型参数 | ChatOpenAI 五参数显式传入（model, api_key, base_url, timeout=30, max_retries=0） |
| C4 装配入口 | `create_agent(model=..., tools=..., system_prompt=...)` |
| C5 调用模式 | 同进程 build → invoke → inspect；`tracing_context(enabled=False)` |
| C6 报告外壳 | JSON 含 mode / configuration / note / input / answer / messages |
| C7 文件安全 | `--output` exclusive create，不覆盖 |
| C8 错误安全 | ConfigError → exit 2；运行时 → exit 3；stderr 不泄露凭据或 provider 原始文本 |
| C9 依赖版本 | 同一组固定版本（requirements.txt 一致） |

### 层 2：按 profile 参数化（共享框架，不同规则）

| 契约项 | Basic profile | Tools profile |
| --- | --- | --- |
| P1 消息链 | `["human", "ai"]` | `["human", "ai", "tool", "ai"]`（≥ 4 条，含 tool_calls） |
| P2 离线模式 | `offline-fixture`（FakeMessagesListChatModel） | `offline-mock`（_ToolCallMockModel） |
| P3 验证规则 | 消息类型 + input/answer 链接 | P3 基本 + tool_call_id 链接 + re-execution + evidence_hash |
| P4 note 含义 | "not evidence of real LLM quality" | "not evidence of real LLM tool-calling quality" |

### 层 3：profile 独有（不共享）

| Basic 独有 | Tools 独有 |
| --- | --- |
| `--model-init identifier` 备选 | `products.json` 领域数据 |
| 无工具/领域层 | `tool.py` 纯函数 + `StructuredTool` 包装 |
| `inspect_result.py` 独立验证 | `evidence.py` + `verify_run.py` 独立验证 |
| — | `build_agent` 中的 `model.bind_tools([TOOL])` |

## 5. 对 A2 的输入

A2 的任务是"从样板提炼必要字段，打通保存、编辑、展示、导出"。T08 的对照结果提供以下具体输入：

### 5.1 Schema 必要字段

从层 1 的共享契约推导：

```
configuration: {
  key_configured: bool,
  base_url: string,
  model: string,
  system_prompt: string
}
mode: "construction-only" | "offline-fixture" | "offline-mock" | "provider-response"
input: string
answer: string
messages: [{type, content, tool_calls?, tool_call_id?}]
note: string
```

从层 2 的 Tools profile 推导（可选字段）：

```
tool_name: string
tool_args: object
tool_call_id: string
tool_result: object
evidence_hash: string
```

### 5.2 Profile 机制

A2 的 Schema 或 COP 结构需要支持 profile 参数化：

- 每个 COP 声明自己的 message profile（Basic 或 Tools 或未来扩展）
- 验证规则按 profile 选择，不写死
- 离线模式按 profile 有不同的模拟策略，但都声明"不证明真实能力"

### 5.3 验证分层

A2 的质量检查需要区分：

| 层 | Basic 能验 | Tools 能验 |
| --- | --- | --- |
| 结构（L1） | 消息类型序列、input/answer 链接 | 消息类型序列 + tool_call_id 链接 |
| 工程（L2 部分） | 配置脱敏、文件不覆盖 | + re-execution 匹配、evidence_hash |
| 能力（L2） | 待真实验证 | 待真实验证 |
| 学习（L3） | 待用户验收 | 待用户验收 |

### 5.4 不应统一的部分

- 消息链验证规则：不同 profile 有不同规则，强行统一会误收或误拒
- 离线模拟实现：Basic 用 SDK 内置 Fake，Tools 用自定义多轮 mock，各自匹配其 profile
- 领域数据和工具定义：是 Tools 的扩展，不是共享层
- 备选初始化方式：Basic 有 `--model-init identifier`，Tools 没有；这是 Basic 的教学选择，不是契约差异

## 6. 总结

两个样板在配置、模型构造、调用模式、报告外壳、错误处理和依赖版本上高度一致——这些构成了可提取的最小共享契约（层 1，9 项）。消息链结构、离线模拟和验证规则必须按 profile 参数化（层 2，4 项）。领域数据、工具定义和备选初始化是各自的教学选择，不构成共享层（层 3）。

A2 的设计应当：
1. 把层 1 作为所有 COP 的必要字段和行为规范
2. 把层 2 作为 profile 机制的实现基础
3. 不强行统一层 3 的差异

这为 A2-01（提炼必要字段）和 A2-02（决定版本与验证记录）提供了来自实际实现的经验依据，而不是从 Schema 推测。
