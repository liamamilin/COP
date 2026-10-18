# LangChain Tools Agent：标准 COP 的第二个原型

目标不是打印 `created`，而是独立完成「明确配置 → 创建带工具的 Agent → 调用 → 检查同一次工具调用因果链」，并解释、验证和迁移这条路径。

这是 A1 的 Tools 子样板，不是完整 LangChain COP。在 Basic 的「无工具 human → ai」之上，增加一次 tool call / tool result 的因果链：用户提问 → 模型决定调用工具 → 工具返回结果 → 模型基于结果回答。任务定义见 [tools-task-definition-v1.md](/Users/milin/2026/软件开发/COP/docs/proposals/tools-task-definition-v1.md)。

## 适用起点

与 Basic 相同：你能编辑文件、在终端运行 Python；已有 Python 3.10+。主线命令面向 macOS/Linux，下面每条 `python` 命令都在本目录且已激活 venv。版本见 `requirements.txt`。

**不适合**：还没有 Python 3.10+ 或无法使用终端的环境（本课件不覆盖安装指导）；Windows 用户（激活命令不同，不在本次已验 profile 内）；需要图形界面或 IDE 集成的场景。

**与 Basic 的关键区别**：消息结构不再是 `human → ai` 两条，而是至少 `human → ai(tool_calls) → tool → ai` 四条。验收重点从「输入/回复链接」变为「工具调用/结果/最终回答的因果链」。

从仓库根目录进入并建立独立环境：

```sh
cd examples/langchain-tools
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import sys; from langchain.agents import create_agent; from langchain_openai import ChatOpenAI; from tool import get_product_info; print(sys.executable); print('imports ok')"
```

应看到本目录 `.venv` 的解释器路径和 `imports ok`。`tool.py` 不依赖 LangChain，只读同目录的 `products.json`。

## 1. 工具：本地确定性查询

本课使用一个固定产品目录（`products.json`，5 个产品 P001–P005）和一个纯 Python 查询函数（`tool.py`）：

```sh
python -c "from tool import get_product_info; print(get_product_info('P001'))"
```

应显示 `{'name': 'LangChain 入门教程', 'price': 99.0, 'category': '教程', 'in_stock': True}`。

这个函数不依赖 LangChain、不联网、不调用模型。它做三件事：
- **有效 ID**：返回 `{name, price, category, in_stock}` 字典。
- **未知 ID**：返回 `{"error": "Product not found", "product_id": "<input>"}`。
- **错误类型**：返回 `{"error": "Invalid product_id type", "product_id": "<input>"}`，不抛异常。

错误处理统一为返回字典，不抛异常。这保证 Agent 管线不会因工具报错而崩溃，也让验收可以精确比对返回值。

运行工具单元测试（23 项）确认行为：

```sh
python -m pytest test_tool.py -v
```

## 2. 显式配置（与 Basic 同一模式）

```sh
cp -n .env.example .env
chmod 600 .env
```

填写 `LC_API_KEY`、`LC_BASE_URL`、`LC_MODEL`。`config.py` 的规则与 Basic 完全一致：进程 `LC_*` 优先于同目录 `.env`；不找父目录、不展开 `${NAME}`、不读取 `OPENAI_*`。

**.env 文件格式**：只使用简单 `key=value`，不加引号（如 `LC_API_KEY=sk-xxx` 而非 `LC_API_KEY="sk-xxx"`）；行首 `#` 是注释；不支持多行值或变量插值（`${NAME}` 会被拒绝）。

唯一区别是 `LC_SYSTEM_PROMPT` 的默认值：本课默认 prompt 指示模型使用 `get_product_info` 工具查询产品信息。

```sh
python config.py
```

应显示 `key_configured: true` 和正确的配置值。没有凭据可以跳到第 5 节做离线自检。

## 3. 创建带工具的 Agent

`agent.py` 的 `build_agent` 比 Basic 多两步：

1. **包装工具**：`StructuredTool.from_function(get_product_info, name=..., description=...)` 将纯函数转为 LangChain 可识别的工具。工具描述是给模型看的，告诉它何时及如何调用。
2. **绑定工具到模型**：`model.bind_tools([TOOL])` 告诉模型有哪些工具可用。
3. **装配 Agent**：`create_agent(model=model_with_tools, tools=[TOOL], system_prompt=...)` 创建可执行图。

```sh
python agent.py --create-only
```

构造成功只证明配置和工具绑定可建立，不证明 key 通过鉴权或模型真的会调用工具。

## 4. 调用：消息链是核心证据

### 4.1 离线模式

```sh
python agent.py --offline --message "P001 的价格是多少？" --output offline-run.json
```

离线模式下，`_ToolCallMockModel` 模拟工具调用序列：第一次 invoke 返回 `AIMessage(tool_calls=[...])`，Agent 执行工具，第二次 invoke 返回最终回答。

查看保存的 JSON：

```sh
cat offline-run.json
```

消息链结构：

```
human:  "P001 的价格是多少？"
ai:     tool_calls: [{name: "get_product_info", args: {product_id: "P001"}, id: "call_offline_mock_001"}]
tool:   content: '{"name": "LangChain 入门教程", "price": 99.0, ...}', tool_call_id: "call_offline_mock_001"
ai:     "LangChain 入门教程的价格是 99.00 元。"
```

**因果链**：AI 的 `tool_calls[0].id` 与 Tool 的 `tool_call_id` 匹配，证明这个工具结果属于这次调用。工具结果的内容与 `get_product_info("P001")` 的实际返回值一致，证明工具确实被执行了。最终回答使用了工具返回的事实。

### 4.2 真实能力路径

有凭据且同意费用后：

```sh
python agent.py --message "P001 的价格是多少？" --output first-run.json
```

真实 provider 的模型会自行决定调用工具。消息链结构相同，但 tool_call_id 由 provider 生成，回答措辞不固定。

### 4.3 证据链验证（T04）

`verify_run.py` 是命令行验证器：

```sh
python verify_run.py offline-run.json
```

它检查消息链结构、tool_call_id 链接、re-execution 匹配和 evidence_hash 完整性。不读 key、不创建 Agent、不再调用 API。

如需在代码中集成，`evidence.py` 也提供 Python API：

```python
from evidence import verify_single_call_evidence, compute_evidence_hash

report = verify_single_call_evidence(run_data)
# report["verified"] == True 表示：
#   1. tool_call_id 链接正确
#   2. 重新执行 get_product_info(args) 的结果与记录一致
#   3. 最终回答非空

hash_value = compute_evidence_hash(run_data)
# hash_value == run_data["evidence_hash"] 表示证据链未被篡改
```

## 5. Inspect 与验收

```sh
python verify_run.py offline-run.json
# 真实调用成功后：
python verify_run.py first-run.json
```

验证器证明：
- 消息链包含 `human → ai(tool_calls) → tool → ai`。
- `tool_call_id` 链接 AI 的工具调用和 Tool 的结果。
- 工具结果与 `get_product_info(args)` 的实际返回值一致（工具确实被执行了）。
- `evidence_hash` 未被篡改。

**验证器不证明（离线模式）**：
- 模型的真实推理能力——`_ToolCallMockModel` 返回固定 mock 回复，不经过真实 LLM。
- 离线 PASS 只证明工具调用管线（bind → call → result → answer）结构正确。

**验证器不证明（真实模式）**：
- 回答的语义正确性——模型可能调用了工具但编造了价格，需要人工判断回答是否正确使用了工具事实。
- JSON 没有被手动修改过——`evidence_hash` 可以检测篡改，但不能阻止篡改。

## 6. 最小 Practice 与验收

交付 `agent.py/config.py/tool.py/products.json/evidence.py/verify_run.py/requirements.txt`、不含 key 的配置摘要、本次运行文件和验证记录。不要交付 `.env`。

- 解释消息链中每条消息的角色：human 是输入，ai(tool_calls) 是模型决定调用工具，tool 是工具执行结果，ai 是最终回答。
- 解释 `tool_call_id` 的作用：它链接 AI 的工具调用意图和 Tool 的执行结果，证明因果关系。
- 解释 `evidence_hash` 的作用：它绑定证据内容，任何字段被篡改都会导致哈希不匹配。
- 解释为什么 `verify_run.py` 的 re-execution 验证比只看消息链更强：它证明工具结果来自实际执行，不是模型编造的。

**近邻迁移**：预测查询 P003（库存为 false）会改变什么；运行 `python agent.py --offline --message "Prompt 工程指南还有货吗？" --output transfer-run.json`，检查工具结果中 `in_stock: false` 是否被正确反映在最终回答中。

**诊断迁移**：预测查询不存在的 P999 会发生什么；运行 `python agent.py --offline --message "P999 的价格是多少？" --output error-run.json`（注意：离线 mock 固定返回 P001 的结果，所以诊断迁移需要真实 provider 才能完整验证）。

**诊断任务（不联网）**：复制已有 JSON 为另一个文件，用编辑器将 `tool_result` 中的 `price` 改为 `0.0`；`verify_run.py` 应报告 re-execution mismatch。解释这与回答语义不正确有何区别。

只有离线输出时，记录「工程自检通过；真实 provider/能力/学习者验收待完成」。

### 常见失败与恢复

- 找不到 `python` 或 `command not found`：先确认 venv 是否激活（提示符应有 `(.venv)` 前缀），运行 `which python` 或 `sys.executable` 检查是否指向本目录 `.venv/bin/python`，未激活则重新 `source .venv/bin/activate`。
- 导入错误：核对 venv 和 Python 版本（需 3.10+）。
- 401：核对 `LC_API_KEY`。
- 404：核对 `LC_BASE_URL` 和 `LC_MODEL`。
- 429：停下确认额度，不要无限重试。
- `--output already exists`：用新文件名。
- 结构 PASS 但回答未使用工具事实（如模型编造价格）：记录语义失败并核对本次 prompt。

## 7. 与 Basic 的对比

| 维度 | Basic | Tools |
| --- | --- | --- |
| 消息结构 | human → ai（2 条） | human → ai(tool_calls) → tool → ai（≥4 条） |
| 验收重点 | 输入/最终回复链接 | 工具调用/结果/最终回答的因果链 |
| 离线模式 | FakeMessagesListChatModel 返回固定文本 | _ToolCallMockModel 模拟工具调用序列 |
| 独立验证 | inspect_result.py 检查消息类型和输入链接 | verify_run.py 检查消息链 + re-execution + evidence_hash |
| 负例 | 结构错配、输入错配 | 工具未调用、结果未使用、错误未处理、证据篡改 |
| 迁移 | 换问题 | 换产品、错误处理、多次调用 |

完整的对照分析和最小共享契约提炼见 [tools-basic-comparison-t08-2026-10-03.md](/Users/milin/2026/软件开发/COP/docs/validation/tools-basic-comparison-t08-2026-10-03.md)。

## 维护与离线回归

```sh
python -m pytest test_tool.py test_agent.py test_evidence.py -v
```

66 项测试覆盖：工具行为（23）、Agent 装配和消息链（20）、证据验证与负例集成（23）。包含 re-execution 匹配、tool_call_id 链接、evidence_hash 完整性、篡改检测和 T06 负例集成（工具未调用、错误参数、错误忽略、答案篡改、多调用部分篡改）。

A1 的两个子样板（Basic + Tools）均已完成工程实现、离线验证和真实 Provider 验证（Tools 4/4 通过）。验证结果见 `docs/validation/a1-real-verification-results-2026-10-03.md`。下一步为目标用户验收（B08），然后收口 A1 并提炼最小 Schema 契约进入 A2；不提前宣称完整 LangChain 或稳定自动生产已完成。Basic 样板见 `../langchain-basic/README.md`。
