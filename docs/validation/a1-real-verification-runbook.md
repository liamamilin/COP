# A1 真实验证准备清单

日期：2026-10-03。状态：**准备完成，等待用户授权。** 本文档列出执行 A1-B07（Basic 真实验证）和 A1-T07（Tools 真实验证）所需的全部信息、命令和判据。用户授权后方可执行。

---

## 1. 用户需要提供的信息

执行真实验证前，需要明确以下五项：

| 项目 | 说明 | 示例 |
| --- | --- | --- |
| **Provider** | OpenAI-compatible Chat Completions 服务 | OpenAI / Azure / 本地 Ollama / 其他 |
| **Base URL** | API 端点（不带 `/chat/completions`） | `https://api.openai.com/v1` |
| **Model** | 模型名称 | `gpt-4o-mini` / `gpt-4o` / `llama3` |
| **API Key** | 凭据（将写入 `.env`，不提交 git） | `sk-...` |
| **预算上限** | 最大请求数和/或费用 | 「最多 10 次请求」或「不超过 $1」 |

**安全约束**：
- API Key 只写入课件目录的 `.env` 文件（已被 `.gitignore`），不提交 git
- 不读取项目根目录的 `.env` 或其他位置的凭据
- 每次真实调用前打印将要使用的 base URL 和 model（脱敏 key）
- 达到预算上限立即停止，不无限重试

---

## 2. Basic 真实验证（A1-B07）

### 2.1 准备

```sh
cd examples/langchain-basic
cp -n .env.example .env
chmod 600 .env
# 编辑 .env 填写 LC_API_KEY / LC_BASE_URL / LC_MODEL
python config.py  # 应显示 key_configured: true
```

### 2.2 执行

```sh
python agent.py --message "What does a system prompt control?" --output first-run.json
```

预期：
- 发送 1 次 API 请求
- 保存 `first-run.json`，包含 mode=`provider-response`、messages（human→ai）、input/answer
- 打印脱敏配置摘要和消息结构

### 2.3 验证

```sh
python inspect_result.py first-run.json
```

预期输出：
- mode: provider-response
- message types: human → ai
- input 一致
- answer 非空且与 messages 最后一条一致
- `LIVE PROVIDER VERIFIED`（不再是 `NOT VERIFIED`）

### 2.4 人工语义判定

打开 `first-run.json`，检查：
- answer 是否实际回答了 "What does a system prompt control?"
- answer 是否使用了 system prompt 的约束（如「一句话回答」）
- 如果 answer 是无关文本或重复问题，记录语义失败

### 2.5 近邻迁移

```sh
python agent.py --message "What does a system prompt control?" --output transfer-run.json
# 或换一个问题：
python agent.py --message "Explain what base_url does" --output transfer-run.json
```

检查新输入/回复是否同样通过结构检查和语义判定。

### 2.6 成功判据

- [ ] `first-run.json` 存在且通过 `inspect_result.py`
- [ ] 人工判定 answer 语义相关
- [ ] 近邻迁移同样通过
- [ ] 请求数在预算内
- [ ] 无凭据泄露（检查 JSON 和 stderr）

---

## 3. Tools 真实验证（A1-T07）

### 3.1 准备

```sh
cd examples/langchain-tools
cp -n .env.example .env
chmod 600 .env
# 编辑 .env 填写 LC_API_KEY / LC_BASE_URL / LC_MODEL
python config.py  # 应显示 key_configured: true
```

### 3.2 执行

```sh
python agent.py --message "P001 的价格是多少？" --output first-run.json
```

预期：
- 发送 1–2 次 API 请求（模型决定调用工具，然后基于结果回答）
- 保存 `first-run.json`，包含 mode=`provider-response`、messages（human→ai(tool_calls)→tool→ai）、tool_name/tool_args/tool_call_id/tool_result、evidence_hash
- 打印消息链结构和证据摘要

### 3.3 验证

```sh
python verify_run.py first-run.json
```

预期输出：
- mode: provider-response
- message types: human → ai → tool → ai（4 条）
- tool_call_id linkage: OK
- re-execution match: OK（重新执行 `get_product_info("P001")` 与记录结果一致）
- final answer present: OK
- evidence_hash: MATCH
- `LIVE PROVIDER VERIFIED`

### 3.4 人工语义判定

打开 `first-run.json`，检查：
- answer 是否包含 P001 的价格（99.00 元）
- answer 是否使用了 tool_result 中的事实（不是模型编造）
- tool_result 是否与 `get_product_info("P001")` 的实际返回值一致
- 如果 answer 编造价格或未使用工具事实，记录语义失败

### 3.5 近邻迁移

```sh
# 换产品（P003 库存为 false）
python agent.py --message "Prompt 工程指南还有货吗？" --output transfer-run.json

# 换问题（未知产品 P999）
python agent.py --message "P999 的价格是多少？" --output error-run.json
```

检查：
- P003：answer 是否反映 `in_stock: false`
- P999：tool_result 是否返回错误，answer 是否说明产品不存在

### 3.6 成功判据

- [ ] `first-run.json` 存在且通过 `verify_run.py`
- [ ] tool_call_id 链接正确
- [ ] re-execution 匹配（工具确实被执行）
- [ ] 人工判定 answer 使用了工具事实
- [ ] 近邻迁移同样通过
- [ ] 请求数在预算内
- [ ] 无凭据泄露

---

## 4. 失败处理

### 4.1 常见错误

| 错误 | 原因 | 修复 |
| --- | --- | --- |
| 401 Unauthorized | API Key 无效或过期 | 检查 `.env` 中的 `LC_API_KEY` |
| 404 Not Found | Base URL 或 Model 错误 | 检查 `LC_BASE_URL` 和 `LC_MODEL` |
| 429 Too Many Requests | 达到速率限制或预算 | 等待或降低请求频率 |
| 500 Internal Server Error | Provider 服务端问题 | 重试或换 provider |
| answer 语义不相关 | 模型能力不足或 prompt 不当 | 记录语义失败，调整 prompt 或换模型 |

### 4.2 停止条件

遇到以下情况立即停止，不继续重试：
- 达到预算上限
- 连续 3 次相同错误
- 凭据疑似泄露（检查 stderr 和 JSON）
- 模型返回明显无关或有害内容

### 4.3 失败记录

如果验证失败，保存：
- 错误信息和 stderr 输出
- 已生成的 JSON 文件（如有）
- 请求次数和费用（如可查）
- 失败原因分析

不为了通过而降低验收标准。

---

## 5. 验证后步骤

### 5.1 如果 Basic 和 Tools 都通过

1. 更新验证记录，添加真实运行结果和 SHA-256
2. 标记 A1-B07 和 A1-T07 为通过
3. 进入 A1-B08（目标用户验收）
4. 用户或目标用户从声明起点独立完成 Practice
5. 记录卡点、外部帮助需求、迁移表现
6. 通过后标记 A1-B09 收口
7. 提炼最小 Schema 契约（基于 T08 三层模型），进入 A2

### 5.2 如果有失败

1. 分析失败原因（配置/模型能力/prompt/工具逻辑）
2. 修复问题（不改验收标准）
3. 重验受影响路径
4. 重新绑定内容版本（SHA-256）
5. 通过后才收口

---

## 6. 授权确认模板

用户授权时，应明确以下信息（可复制填写）：

```
Provider: [填写]
Base URL: [填写]
Model: [填写]
API Key: [将写入 .env，不在此处填写]
预算上限: [最多 N 次请求 / 不超过 $X]

授权范围:
- [ ] Basic 真实验证（A1-B07）
- [ ] Tools 真实验证（A1-T07）
- [ ] 近邻迁移
- [ ] 不自动进入目标用户验收（B08 需单独授权）

确认:
- [ ] 我理解这将产生真实 API 调用和费用
- [ ] 我理解 API Key 将写入课件目录的 .env 文件
- [ ] 我理解达到预算上限会立即停止
```

---

准备完成。等待用户授权后执行。
