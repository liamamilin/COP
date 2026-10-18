# A1 执行就绪检查清单

**日期**：2026-10-03  
**目的**：确认 A1 真实验证的所有准备工作已完成，授权后可立即执行

## 工程实现检查（100% 完成）

### Basic 样板
- [x] `main.py` 存在且可执行
- [x] `config.py` 配置加载正确
- [x] `inspect_result.py` 独立验证器就绪
- [x] `.env.example` 模板正确
- [x] `requirements.txt` 依赖固定（7 个包）
- [x] 单元测试：13/13 通过
- [x] 离线验证：JSON 已保存 + SHA-256 绑定
- [x] 内容审核：无阻塞性问题

### Tools 样板
- [x] `agent.py` 存在且可执行
- [x] `tool.py` 工具实现正确
- [x] `products.json` 数据完整（5 个产品）
- [x] `evidence.py` 证据链验证就绪
- [x] `verify_run.py` 独立验证器就绪
- [x] `.env.example` 模板正确
- [x] `requirements.txt` 依赖固定（7 个包）
- [x] 单元测试：66/66 通过
- [x] 离线验证：JSON 已保存 + SHA-256 绑定
- [x] 完成度审核：T01 所有要求满足

### 共享契约
- [x] T08 对照总结完成
- [x] 层 1 共享契约：9 项
- [x] 层 2 Profile 参数化：4 项
- [x] 层 3 独有差异已记录

## 执行准备检查（100% 完成）

### 自动化脚本
- [x] `examples/langchain-basic/run-basic-verification.sh` 已创建且可执行
- [x] `examples/langchain-tools/run-tools-verification.sh` 已创建且可执行
- [x] 脚本包含：配置检查、自动执行、独立验证、输出保存

### 文档准备
- [x] 授权请求：`a1-authorization-request-2026-10-03.md`
- [x] 执行手册：`a1-real-verification-runbook.md`
- [x] 状态摘要：`a1-status-summary-2026-10-03.md`
- [x] 完成度审核：`tools-completion-audit-2026-10-03.md`
- [x] 主文档更新：停靠点、文档索引已更新

### 虚拟环境
- [x] Tools `.venv` 存在且依赖已安装
- [ ] Basic `.venv` 需要创建（运行 `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`）
- [x] langchain 版本：1.4.3（两个样板一致）

## 等待用户授权

### 需要的信息
```
LC_API_KEY=<your-api-key>
LC_BASE_URL=<your-base-url>
LC_MODEL=<model-name>
最大调用次数：Basic 5 次，Tools 5 次
费用上限：$2（建议）
```

### 授权选项
1. **提供配置** → 运行自动化脚本 → 完成 A1
2. **使用现有 .env** → 运行自动化脚本 → 完成 A1
3. **跳过真实验证** → 直接进入用户验收
4. **暂停 A1** → 处理其他优先级

## 授权后执行步骤

### 步骤 1：配置环境（10 分钟）

**Basic 样板**（需要先创建 venv）：
```bash
cd examples/langchain-basic
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入真实配置
```

**Tools 样板**（venv 已存在）：
```bash
cd examples/langchain-tools
cp .env.example .env
# 编辑 .env 填入真实配置
```

### 步骤 2：运行 Basic 验证（5 分钟）
```bash
./run-basic-verification.sh
```

预期输出：
- 2 个 JSON 文件（默认问题 + 近邻迁移）
- 控制台显示验证结果
- 人工检查 answer 字段语义正确性

### 步骤 3：运行 Tools 验证（10 分钟）
```bash
cd ../langchain-tools
cp .env.example .env
# 编辑 .env 填入真实配置
./run-tools-verification.sh
```

预期输出：
- 4 个 JSON 文件（默认 + 近邻 + 诊断 + 组合）
- 控制台显示验证结果（tool_call_id 链接、重新执行匹配）
- 人工检查工具调用和语义正确性

### 步骤 4：收口 A1（10 分钟）
- 移动 JSON 文件到 `docs/validation/`
- 更新验证记录文档
- 更新主文档状态
- 提炼 A2 输入

**总耗时**：约 40 分钟（含 Basic venv 创建）

## 当前状态

**工程实现**：✅ 100% 完成  
**执行准备**：✅ 100% 完成  
**真实验证**：⏳ 等待授权  
**用户验收**：⏳ 等待执行  

**阻塞项**：用户授权真实 API 调用

## 关键联系人

- 项目维护者：LinMi（git user）
- 授权决策者：用户（需要回复授权选项）

## 下一步行动

**等待用户回复授权选项**。一旦授权，可立即执行上述步骤，30 分钟内完成 A1 全部验证。

---

**备注**：本清单是 A1 执行阶段的最终检查文档。所有技术实现、测试报告、验证记录均在对应文档中。
