# Tools 原型内容审核记录

审核日期：2026-10-03（Asia/Shanghai）。审核范围：`examples/langchain-tools/` 全部文件。审核依据：COP_GOAL_PLAN_TASK_METHOD.md §3（S1–S9）与 §6.5（五视角）。

状态：**审核完成，无阻塞性问题；记录若干改进点供实施。** 工程/离线/真实验证均已通过（66/66 测试 + 4/4 真实调用）。

---

## 1. 按 S1–S9 逐条评估

### S1 范围与起点明确 — 通过（有改进空间）

- README 开头「适用起点」明确：与 Basic 相同，能编辑文件、终端运行 Python、Python 3.10+。
- 「不适合」反向声明存在：没有 Python 3.10+、Windows、需要 GUI。
- 「与 Basic 的关键区别」明确：消息结构从 2 条变 4+ 条，验收重点从输入/回复链接变为因果链。
- 任务定义链接到 `tools-task-definition-v1.md`。

**改进点**：
1. `requirements.txt` 不包含 `pytest`，README 第 22 行要求单独安装。这是隐藏依赖。建议将 pytest 加入 requirements.txt，或在 README 明确说明「测试需要额外安装 pytest，不在主线依赖中」。非阻塞。

### S2 Goal 是能力成果 — 通过

- Goal 声明：独立完成「明确配置 → 创建带工具的 Agent → 调用 → 检查同一次工具调用因果链」。
- 成功可观察：offline-run.json 或 first-run.json 存在 + verify_run.py PASS + 人工语义判断。
- 失败可观察：construction-only 不算、结构 PASS 但语义不相关不算。
- Practice 的 checkpoint 问题覆盖因果链理解。

无问题。

### S3 默认主线连续 — 通过

- 主线：Install → Tool → Config → Create → Invoke → Inspect → Practice，每一步产物是下一步输入。
- Tool 章节先建立工具的确定性行为，为后续 Agent 调用打基础。
- Invoke 先离线后真实，两条路径都回接 Inspect。
- README 的七节与主线顺序一致。

无断裂点。

### S4 Stage 是闭合局部任务 — 通过

每节有明确目标和预期输出：

- §1 Tool：产物 `get_product_info` 函数；验收 `python -c` 显示正确字典 + 23 项测试通过。
- §2 Config：产物 `.env` + `config.py`；验收 `key_configured=true`。
- §3 Create：产物 `agent.py --create-only`；验收构造成功。
- §4 Invoke：产物 `offline-run.json` 或 `first-run.json`；验收消息链结构。
- §5 Inspect：产物 `verify_run.py` 验证；验收 PASS + 人工语义判断。
- §6 Practice：交付物和练习。
- §7 对比：与 Basic 的差异总结。

每节的 input/output 明确，失败恢复在常见失败段落有说明。

### S5 Concept × Operation 有因果关系 — 通过

- Tool 概念（确定性查询）→ Operation（`get_product_info` 调用）→ 结果（字典返回）。
- Config 概念（显式配置）→ Operation（`ChatOpenAI` 初始化）→ 结果（模型可用）。
- Message chain 概念（human→ai→tool→ai）→ Operation（`invoke_agent`）→ 结果（完整消息链）。
- Evidence 概念（tool_call_id 链接 + re-execution）→ Operation（`verify_run.py`）→ 结果（证据完整性）。

每个概念的因果在 README 和代码中都有说明。

### S6 没有承重隐藏知识 — 通过（有改进空间）

已明确的关键条件：
- LC_* 配置规则（与 Basic 一致）。
- .env 文件格式（简单 key=value，不加引号）。
- tool_call_id 链接 AI 的工具调用和 Tool 的结果。
- evidence_hash 绑定证据内容。
- verify_run.py 的 re-execution 证明工具确实被执行。

**改进点**：
1. README §4.3 先展示 Python API（`from evidence import verify_single_call_evidence`），再展示命令行（`python verify_run.py`）。对学习者来说，命令行更直观。建议先展示命令行用法，再说明 Python API 供扩展使用。非阻塞。
2. README §5 的「验证器不证明」段落很好，但可以更明确区分「离线 mock 不证明模型能力」和「真实调用不证明语义正确性」。当前两段混在一起。非阻塞。

### S7 备选可选择且能回接 — 通过

两个备选：
1. **离线模式**（`--offline`）：选用条件是「没有凭据或暂不愿产生费用」；改动是加 `--offline`；回接是 Inspect 同一文件，但要达成 Goal 需回到真实路径。
2. **仅构造**（`--create-only`）：选用条件是「只检查配置和工具绑定」；改动是加 `--create-only`；不 invoke，不证明能力。

两个备选都有明确的选择条件和回接位置。

### S8 Example / Practice / 迁移衔接 — 通过

- Practice 使用同一任务与资源：从 Tool 开始，配置，创建，调用，验证。
- 近邻迁移：换产品（P003、P005），检查 `in_stock: false` 是否被正确反映。
- 诊断迁移：换不存在的 P999，检查错误处理。
- 诊断任务（不联网）：篡改 JSON，验证器应拒绝。

Practice 覆盖了理解、迁移和诊断三个维度。

### S9 事实与验证状态诚实 — 通过

- 验证记录明确区分：工程/离线通过、真实 Provider 通过（4/4）、目标用户验收待验。
- README 明确说明离线 mock 不证明模型能力。
- README 明确说明 verify_run.py 不证明语义正确性。
- 不虚假达标。

无问题。

---

## 2. 五视角审核

### 开发者视角 — 通过

- API/版本正确：与 Basic 同一组依赖。
- 脚本连续执行：`python tool.py` → `python config.py` → `python agent.py --create-only` → `python agent.py --offline` → `python verify_run.py`，已在测试中验证。
- 测试覆盖：66/66 通过，包括工具行为、Agent 装配、证据验证、负例集成。

### 目标用户视角 — 通过（有改进空间）

- 第一步从哪开始：README 「适用起点」→ §1 Tool，明确。
- 能否不靠额外搜索完成：主线命令完整，失败恢复在常见失败段落有说明。
- 错了如何恢复：常见失败段落列出了 venv、导入、401/404/429 等问题。

**改进点**：
1. 常见失败段落在 §6 Practice 末尾，不够显眼。建议单独成节或在每节末尾加 caution。非阻塞。
2. README 没有说明 pytest 不在 requirements.txt 中，用户运行 `python -m pytest` 可能失败。非阻塞。

### 教学/内容视角 — 通过

- Goal 有价值：完成一次有工具 Agent 调用并理解因果链，为更复杂场景打基础。
- 概念解释了因果：为什么需要 tool_call_id（链接因果）、为什么需要 re-execution（证明工具确实执行）、为什么需要 evidence_hash（防篡改）。
- Practice 和迁移有效：换产品、错误处理、篡改检测。
- 信息负担合理：代码摘录关键部分，完整文件在仓库中。

### 产品/UI 视角 — 通过

- 默认主线可达：Tool → Config → Create → Invoke → Inspect，七节。
- 当前位置可见：章节顺序清晰。
- 与 Basic 对比：§7 有对照表，帮助理解差异。
- 代码可复制：命令行和代码片段都可复制。

### 安全/运维视角 — 通过

- 凭据不泄露：ConfigError 不包含 key 值；异常处理不打印 provider 原始异常。
- 费用有界：真实调用需用户明确许可；max_retries=0；timeout=30 秒。
- 测试隔离：test_agent.py 禁止网络；不读真实 .env；不使用用户密钥。
- 历史数据保护：--output 文件已存在时阻止运行。

---

## 3. 总结与建议

### 结论

Tools 原型在 S1–S9 标准和五视角审核下**均通过**，无阻塞性问题。工程/离线/真实验证均已通过，教学流程清晰，安全边界明确，验证状态诚实。

### 改进建议（非阻塞，供用户决定）

1. **S1 pytest 依赖**：将 pytest 加入 requirements.txt，或在 README 明确说明「测试需要额外安装 pytest」。
2. **S6 验证顺序**：在 §4.3 先展示命令行 `verify_run.py`，再展示 Python API。
3. **S6 验证器限制**：在 §5 更明确区分「离线 mock 不证明模型能力」和「真实调用不证明语义正确性」。
4. **目标用户视角**：将常见失败段落单独成节或在每节末尾加 caution；说明 pytest 不在 requirements.txt 中。
5. **底部声明**：更新「维护与离线回归」段落，反映真实验证已通过。

以上均为信息负担和表达清晰度改进，不影响主线完成或验收判据。

---

审核人：AI assistant（基于代码和文档阅读）。
审核依据版本：COP_GOAL_PLAN_TASK_METHOD.md 2026-10-03 版本。
审核范围：Tools 原型内容，工程/离线/真实验证已在其他文档记录。
