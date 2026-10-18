# LangChain Tools 标准 COP 原型：验证记录

验证日期：2026-10-03（Asia/Shanghai）。状态：**A1 / Tools 工程原型及离线验收通过；真实 provider、能力语义、目标用户验收待完成。** Tools 是 A1 的第二个子样板，在 Basic 的无工具 human→ai 之上增加 tool call / tool result 因果链。不能因此宣称 A1、完整 LangChain case 或稳定自动生产已完成。

## 交付与边界

- 独立可运行课件：`examples/langchain-tools/`。12 个文件：`agent.py`、`config.py`、`tool.py`、`evidence.py`、`verify_run.py`、`products.json`、`requirements.txt`、`.env.example`、`README.md`，加三个测试文件。
- 无独立 COP fixture：Tools 样板目前不附带 `fixtures/langchain-tools-cop.json`。COP 结构（Goal、Stage、Practice）在 README 中定义，尚未通过 builder 生成独立 JSON。这是与 Basic 的差异点，后续如需前端预览或 Schema 验证需补充。
- 对照总结：`docs/validation/tools-basic-comparison-t08-2026-10-03.md`，层 1 共享契约 9 项、层 2 profile 参数化 4 项、层 3 独有差异。
- 已保存的实际离线结果：`docs/validation/tools-tools-offline-run-2026-10-03.json`。

本次不修改 Schema、不创建 COP fixture、不接入新 Harness 生成门禁、不覆盖原五目标 fixture、不修改已发布版本或开发数据库内容。不读取项目真实 `.env`，不使用用户密钥，不发真实 LLM/Exa 请求。依赖安装使用 PyPI；费用步骤在课件中明确由学习者决定。

## 教学契约

默认路径：独立 venv / 固定依赖 → 命名 `.env` / 显式配置 → 同进程创建带工具 Agent / invoke → 保存本次 JSON → 独立 Inspect（结构 + re-execution + evidence_hash）→ 真实能力与近邻迁移验收。

- 配置层与 Basic 完全一致（`config.py` 仅 `DEFAULT_PROMPT` 不同）：`LC_API_KEY / LC_BASE_URL / LC_MODEL / LC_SYSTEM_PROMPT`，进程值覆盖同目录 `.env`，空覆盖值也报错，不搜索父目录、不读 `OPENAI_*`、不展开 `${NAME}`。
- `build_agent` 比 Basic 多两步：`StructuredTool.from_function` 包装纯函数 → `model.bind_tools([TOOL])` 绑定到模型 → `create_agent(model=model_with_tools, tools=[TOOL], system_prompt=...)` 装配。
- 消息链结构从 Basic 的 2 条（human→ai）变为 ≥4 条（human→ai(tool_calls)→tool→ai）。验收重点从「输入/回复链接」变为「工具调用/结果/最终回答的因果链」。
- `created` 只表示构造，Agent 对象不会跨进程保留；实际运行脚本在同一进程中创建、调用、检查。
- 离线 `_ToolCallMockModel` 模拟工具调用序列：第一次 invoke 返回 `AIMessage(tool_calls=[...])`，Agent 执行工具，第二次 invoke 返回最终回答。仍经过真实 LangChain 图，但不是 LLM 推理或 provider 兼容性证据。
- `verify_run.py` 独立验证：消息链结构、tool_call_id 链接、re-execution 匹配（重新执行 `get_product_info(args)` 比对记录结果）、evidence_hash 完整性。不再次 invoke，不读 key。
- Practice 使用同一成果，要求真实运行/检查、语义判定、近邻换产品迁移与结构错误诊断；离线文件不能充作真实能力通过。

## 已执行的检查

### 1. 工具单元测试

在课件目录使用 venv（Python 3.10.13 / macOS arm64）执行：

```sh
.venv/bin/python -m pytest test_tool.py -v
```

结果：**23/23 通过**。覆盖：

- 5 个有效产品 ID（P001–P005）返回完整 `{name, price, category, in_stock}` 字典。
- 5 个未知 ID（P999、数字字符串、空字符串、小写、近似 ID）返回 `{"error": "Product not found", "product_id": "..."}`.
- 6 个错误类型（None、int、float、list、dict、bool）返回 `{"error": "Invalid product_id type", "product_id": "..."}`，不抛异常。
- 返回值形状：成功恰好 4 键、错误恰好 2 键、类型错误恰好 2 键、price 为 float、in_stock 为 bool。

工具是纯 Python 函数，不依赖 LangChain、不联网、不调用模型。错误处理统一为返回字典，保证 Agent 管线不因工具报错崩溃。

### 2. Agent 装配与消息链测试

```sh
.venv/bin/python -m pytest test_agent.py -v
```

结果：**20/20 通过**。覆盖：

- 工具包装：`StructuredTool` 名称、描述、可调用性。
- 离线 Agent 构造：`build_offline_agent()` 成功、invoke 产生 4 条消息链。
- `inspect_response` 提取：tool_name、tool_args、tool_result、answer、tool_call_id、消息链 4 类型、拒绝错误输入。
- 负例：消息过少、无 tool_calls、错误工具名必须拒绝。
- CLI：offline 模式 exit 0、自定义消息、创建输出文件、拒绝覆盖、无配置 exit 2。

### 3. 证据链验证测试

```sh
.venv/bin/python -m pytest test_evidence.py -v
```

结果：**23/23 通过**。覆盖：

- `re_execute_tool`：有效产品、未知产品、未知工具名抛异常、5 个产品全可重执行。
- `extract_tool_call_chain`：提取单对、拒绝未匹配 tool_call、拒绝无 tool_calls。
- `verify_single_call_evidence`：离线运行通过、拒绝篡改 tool_result、拒绝消息过少、拒绝空 answer、拒绝多对。
- `verify_multi_call_evidence`：单调用通过多调用验证、拒绝多调用中篡改。
- `compute_evidence_hash`：确定性、tool_result 篡改变 hash、answer 篡改变 hash、忽略元数据字段。
- T06 负例集成（5 项）：模型编造答案（无工具调用）、错误参数、工具返回错误但模型声称存在、answer 篡改、多调用中一项篡改。

### 4. 全量回归

```sh
.venv/bin/python -m pytest test_tool.py test_agent.py test_evidence.py -v
```

结果：**66/66 通过**（23 + 20 + 23），0.28 秒。

### 5. 端到端管线

```sh
.venv/bin/python agent.py --offline --message "P001 的价格是多少？" --output /tmp/tools-validation-run.json
.venv/bin/python verify_run.py /tmp/tools-validation-run.json
```

输出消息链：

```
human:  "P001 的价格是多少？"
ai:     tool_calls: [{name: "get_product_info", args: {product_id: "P001"}, id: "call_offline_mock_001"}]
tool:   content: '{"name": "LangChain 入门教程", "price": 99.0, "category": "教程", "in_stock": true}', tool_call_id: "call_offline_mock_001"
ai:     "LangChain 入门教程的价格是 99.00 元。"
```

验证器结果：

- mode: offline-mock
- message types: human → ai → tool → ai（4 条）
- tool_call_id linkage: OK
- re-execution match: OK
- final answer present: OK
- evidence_hash: MATCH
- Summary: PASS

验证器明确打印 `LIVE PROVIDER AND LEARNER ACCEPTANCE: NOT VERIFIED`。

### 6. 后端回归

```sh
cd backend && .venv/bin/python -m pytest tests/test_operational_quality.py -q
```

结果：**21/21 通过**。包含 Schema 验证、Pydantic 引用、课件内容同步检查。Tools 样板的 config.py 与 Basic 共享契约一致性由 T08 对照文档记录，不在后端测试中重复。

曾扩展执行 `test_evidence_chain.py`，其中集成测试因未配置 `TEST_DATABASE_URL` 在 fixture 初始化前停止（与 Basic 验证记录同一情况）。本轮不声称全套数据库集成或 E2E 通过。

## 与 Basic 的关键差异

| 维度 | Basic | Tools |
| --- | --- | --- |
| 消息结构 | human → ai（2 条） | human → ai(tool_calls) → tool → ai（≥4 条） |
| 验收重点 | 输入/最终回复链接 | 工具调用/结果/最终回答的因果链 |
| 离线模式 | FakeMessagesListChatModel 返回固定文本 | _ToolCallMockModel 模拟工具调用序列 |
| 独立验证 | inspect_result.py 检查消息类型和输入链接 | verify_run.py 检查消息链 + re-execution + evidence_hash |
| 领域数据 | 无 | products.json + tool.py |
| 备选初始化 | --model-init identifier | 无 |
| 测试规模 | 13 | 66（23 + 20 + 23） |
| COP fixture | 有 | 无（待后续补充） |

完整对照分析见 `docs/validation/tools-basic-comparison-t08-2026-10-03.md`。

## 内容绑定

以下 SHA-256 绑定本次实际检查内容，改代码/内容后必须重验，不能沿用旧绿灯：

| 文件 | SHA-256 |
| --- | --- |
| examples/langchain-tools/agent.py | e29082f01a952e0e2888e9f98a6eacc19577606039edb3ba00a54ae16bbd4845 |
| examples/langchain-tools/config.py | f2ad2952fa1ef99c0a00eb1345defce99b9516da4efe0523f6f41113468d608c |
| examples/langchain-tools/tool.py | e8d142db4eeff1ae41af10c459647cde83cdf54d1ac23053a6c5adc9ba3b1f32 |
| examples/langchain-tools/evidence.py | d1264c0c737de2b9e5273bed20bde6a98da8c6b41313e2433f1a13b6d021b47c |
| examples/langchain-tools/verify_run.py | a5e6c3b1a21fda33bfd7b5f440dd253c3ed0bae1bf7b441be696094434868447 |
| examples/langchain-tools/products.json | 251b6b22f9f608a510d72c4c97597719fc7a4e498595b75ce0baafef6a912c02 |
| examples/langchain-tools/test_tool.py | 01833cec528980bba2df9db97a351b21828f60aac7254ccb4dcf6605878b82f0 |
| examples/langchain-tools/test_agent.py | 388394e4e04c0191bdb98ef109c6c80cca6b73c294977f132d3d710a28f69356 |
| examples/langchain-tools/test_evidence.py | 1140f911eade34d86f7dfeb660a5ffcf3be2bd2d680caee1f139e89049583d32 |
| examples/langchain-tools/requirements.txt | 8296d0eee583617480ffad40be7a8072a26fe4ee66cc2129f12a0ba17d2911d7 |
| examples/langchain-tools/.env.example | 2eaf6f96678d4edab6c6936979f01671c7974d33a85a104043be61129241e3d7 |
| examples/langchain-tools/README.md | 6c526c48ff83b7ce2c9b443b7fad0a945637eed79f10a22617a175f9ebc286ac |
| docs/validation/tools-tools-offline-run-2026-10-03.json | 9fc7aeb6536cba640e13edb35753455818fcbdc16371bc96a2f8b27d459eb992 |

## 内容改进（2026-10-03 后续）

与 Basic 同步实施了以下非阻塞信息负担改进（详见 Basic 内容审核记录）：

1. **README 适用起点**：增加「不适合」反向声明。
2. **README .env 格式**：明确只使用简单 `key=value`，不加引号。
3. **README 常见失败**：增加「找不到 python」的恢复指导。
4. **README 测试数量**：从 61 更正为 66（实际测试数）。
5. **README 状态行**：更新 T07 需授权、T02–T06/T08 已完成。
6. **README T08 引用**：添加对照文档链接。

改动后 README.md 的 SHA-256 已更新（见上表）。

## 下一停靠点

1. 用户审核 Tools 样板，重点看消息链结构、tool_call_id 因果链、re-execution 验证和证据完整性检查。
2. 在明确 provider / model / 凭据使用范围 / 请求次数和预算后进行受控真实验证（T07）；用户独立从声明起点完成 Practice，记录需要外部帮助的位置与迁移表现。
3. Tools 达到能力/用户验收要求后收口 A1，提炼最小 Schema 契约（基于 T08 三层模型），进入 A2。

相关文档：Basic 验证记录 `docs/validation/langchain-basic-prototype-2026-10-03.md`；对照总结 `docs/validation/tools-basic-comparison-t08-2026-10-03.md`；任务定义 `docs/proposals/tools-task-definition-v1.md`。
