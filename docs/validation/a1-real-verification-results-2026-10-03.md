# A1 真实 Provider 验证记录

日期：2026-10-03
Provider：deepseek/deepseek-v4-flash via https://api.commandcode.ai/provider/v1
授权：使用项目 .env 现有配置

## 验证范围

| 原型 | 测试 | 输入 | 预期消息链 | 结果 |
|---|---|---|---|---|
| Basic | 默认问题 | "Name one benefit of using an agent harness." | human → ai (2) | PASS |
| Basic | 近邻迁移 | "Explain quantum computing in one sentence." | human → ai (2) | PASS |
| Tools | 单次调用 (P001) | "P001 的价格是多少？" | human → ai(tool_calls) → tool → ai (4) | PASS |
| Tools | 近邻迁移 (P005) | "P005 是什么产品？" | human → ai(tool_calls) → tool → ai (4) | PASS |
| Tools | 错误处理 (P999) | "P999 的价格是多少？" | human → ai(tool_calls) → tool → ai (4) | PASS |
| Tools | 多次调用 | "所有教程的价格是多少？" | human → ai(5 tool_calls) → 5×tool → ai (8) | PASS |

## Basic 结果

### 测试 1：默认问题
- 文件：`basic-real-run-20261003-160839.json`
- mode: provider-response
- 消息链：human → ai
- 回答："It provides a standardized loop for managing tool calls, memory, and safety, making agents easier to build and debug."
- inspect_result.py：PASS

### 测试 2：近邻迁移
- 文件：`basic-real-transfer-20261003-160845.json`
- mode: provider-response
- 消息链：human → ai
- 回答："Quantum computing uses qubits that can exist in superpositions and become entangled to solve certain complex problems exponentially faster than classical computers."
- inspect_result.py：PASS

## Tools 结果

### 测试 1：单次调用 P001
- 文件：`tools-real-run-20261003-160501.json`
- mode: provider-response
- 消息链：human → ai(tool_calls=1) → tool → ai (4 messages)
- tool_call_id linkage: OK
- re-execution match: OK
- evidence_hash: MATCH (8200c1afbcc86ed2...)
- 回答正确引用工具返回数据

### 测试 2：近邻迁移 P005
- 文件：`tools-real-transfer-20261003-160510.json`
- mode: provider-response
- 消息链：human → ai(tool_calls=1) → tool → ai (4 messages)
- tool_call_id linkage: OK
- re-execution match: OK
- evidence_hash: MATCH (455698a4998d0a68...)
- 回答正确引用工具返回数据

### 测试 3：错误处理 P999
- 文件：`tools-real-diagnostic-20261003-160515.json`
- mode: provider-response
- 消息链：human → ai(tool_calls=1) → tool → ai (4 messages)
- tool_call_id linkage: OK
- re-execution match: OK
- evidence_hash: MATCH (e401e563d4f2974e...)
- 工具返回 `{"error": "Product not found", "product_id": "P999"}`
- 回答正确说明产品不存在

### 测试 4：多次调用
- 文件：`tools-real-combo-20261003-160521.json`
- mode: provider-response
- 消息链：human → ai(5 tool_calls) → 5×tool → ai (8 messages)
- 5 个 tool_call pairs 全部 re-execution match
- evidence_hash: MATCH (cdb307f9228ecc55...)
- 回答正确汇总 3 个教程类产品价格（¥377.0），并区分电子书分类

## 修复记录

### verify_run.py 多调用支持
原始 verify_run.py 仅支持单次调用验证（`verify_single_call_evidence`）。测试 4 的 5 个 tool_call 导致 "Expected 1 tool_call pair, got 5" 错误。

修复：
1. 导入 `extract_tool_call_chain` 和 `verify_multi_call_evidence`
2. 先调用 `extract_tool_call_chain` 计算 pair 数量
3. 1 pair → `verify_single_call_evidence`；>1 pair → `verify_multi_call_evidence`
4. 修复参数传递：`extract_tool_call_chain(data.get("messages", []))` 而非 `extract_tool_call_chain(data)`

### run-basic-verification.sh bash 兼容性
原始脚本用 `source .env` 加载配置，但 `LC_SYSTEM_PROMPT=Answer in one short sentence.` 含空格导致 bash 执行错误。

修复：改用 grep + cut 提取值，不 source .env 文件。

## 未验证项

- 语义正确性：需人工判断回答是否正确使用了工具返回的事实
- B08 用户验收：需用户独立完成 Practice 练习
- 不同 provider/model 的迁移性：仅测试了 deepseek-v4-flash
