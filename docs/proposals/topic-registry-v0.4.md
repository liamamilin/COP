# Topic Registry v0.4 · P Discovery 批量选题系统

> **交付范围：目录与待执行队列，不运行批量 P Discovery、不修改 Skill、不自动发布 P Atlas。**

## 结构

```text
Domain 领域 → Area 子领域 → Topic 独立研究对象
                              ↓ Codex 调用 p-discovery Skill
                         P (可达用户结果)
```

**Domain、Area 只用于组织对象。** Topic 的 `scope_level` 表示研究层级：`bounded_subject` 是具体产品、库、框架、服务、协议或边界清晰的方法；`area_survey` 是较宽的领域概览，当前不进入默认批次；新增加的 181 个种子除少量身份已核验者外，都不得直接入队。对象类型通过 `topic_type` 独立标识。不要把数据应用这个 Area 与 Shiny 这个 Topic、或 Shiny 研究后发现的 P 混淆。

## 四份核心文件

- `catalog/topic-taxonomy.v0.4.json`：11 个 Domain + 85 个 Area（其中一个暂为空） + 官方类别索引入口。
- `catalog/topic-registry.v0.4.json`：291 个 Topics、身份与来源核对、范围摘要、关联主题与研究状态。
- `catalog/coverage.v0.4.md`：各 Area 的候选分布、分类修订、空白子领域及待进行的来源调查，防止将对象数当成覆盖率。
- `catalog/research-queue.v0.4.json`：自动从身份已核实且已批准的候选派生的可执行队列，其他优先候选只保留为 deferred，不负责发布。

可以运行 `python3 scripts/validate_topic_registry.py` 检查父子引用、状态和队列是否同步；运行 `python3 scripts/validate_topic_registry.py --write-queue` 按当前目录重新生成队列。运行 `python3 -m unittest discover -s scripts/tests -p test_topic_registry.py -v` 执行回归测试。批次不自动执行。

## 研究状态及来源来源

- `published`：目前 main 已有并被 Atlas 使用的 20 个主题。
- `researched_in_unmerged_pr`：PR #4 中已完成研究但尚未合并的 18 个主题；这不是生产环境发布状态。
- `candidate`：以前 v0.3 的 72 个候选 + 新种子 181 个；**不是已来源确认的产品或其 P**。

未来应区分 Topic 的 `research_state` 与 P 的 `source_supported/proposed/reviewed`。本次没有给任何 P 授予 reviewed。

## 如何继续做 Topic Discovery

逐 Area 进行一轮研究对象发现：先读官方生态索引、相关官方/维护者产品文档，再读真实应用与相邻开源项目；整理新增候选及拒绝项，明确有无遗漏。种子只是起点，不以数量达标。将资料取回入口、候选身份验证和争议写入覆盖记录。新近更新的产品、模型服务或受限制项目必须核对当前维护状态、版本与条件。

## 如何用 Codex 批量执行 P Discovery

1. 先读四份文件并运行 `python3 scripts/validate_topic_registry.py`。
2. 选 `research-queue.v0.4.json` 的一个 wave；**最多两个研究任务并行**，每个 topic 单独研究、单独目录、单独分支或不冲突工作区。
3. 使用原版 `p-discovery` Skill；先记录范围，检索官方、案例、生态，提取结果、去重、补漏、再分类；不以 P 数为绩效目标。
4. 保存 `outputs/<slug>/possibilities.json`、`possibilities.md`、`validation-report.txt`、`discovery-log.md`、`source-coverage.json`。
5. 使用原 Skill 的验证脚本检查，结合人工或独立 reviewer 检查证据是否足以支持重要结论；失败/证据不足记录返工，不得擅自标记 `reviewed`。
6. 仅通过的主题进入研究 PR；合并后根据实际状态更新 P Atlas catalog，运行阅读器构建及完整浏览器测试，最后发布。

**目录完善与批量 P Discovery 是两个工作流。** 本次队列只是建议执行清单，不启动 Codex、不修改线上 catalog。

## v0.4 审查重点

- 以前的 v0.3 以工具凑目录，现根据活动领域先建立 82 个 Area，随后审查增至 85 个 Area；再将旧的 110 项和 181 项种子映射。新增空子领域不强制补齐。
- 具体方法可以进入目录（例如 A/B 测试、刻意练习），但不能仅凭名称假装它是一款有 API 的软件；证据主要来自研究方法与实际案例。
- 已有的 LLM 推理、微调、AI 视频等概览仍保留但标注 `area_survey`，不与 llama.cpp、LTX Video、Shiny 等具体对象在默认批次里比较数量。
- 此版本解决的是**结构上的系统性**。覆盖报告承认独立来源普查未完成，不声称目录已穷尽。

## P0 修订：分类与执行准入（本分支）

上次审查指出 Qdrant、SearXNG、Graphviz、Tailscale、WireGuard 归属不精确，现已调整各自主要 Area。新增向量检索、图结构可视化、安全网络连接三个子领域；移走网络工具后，个人领域的「本地优先、隐私与家庭数据服务」没有种子，因此保留为 `unseeded_needs_discovery`，不生成假对象。

`openai-agent-harness` 未找到清楚独立于现有 `agent-harness` 的身份，状态设为 `blocked`；若找到有权威来源的独立对象，必须先提供范围和来源再重新解锁。

新增 `identity_status`、`official_url`、`identity_evidence_note`、`selection_status` 及有限的 `related_topics`。仅当一个**具体有界对象**同时满足「状态仍待研究」「身份已核验」「有官方入口」「已明确批准」时，才能出现在 `research-queue.v0.4.json` 的 `executable` 列表。其他优先候选仍可作为 `deferred_preferred`，不能被 Codex 当作已准入任务执行。

当前只有 6 项进入可执行队列：PydanticAI、MLX LM、llama.cpp、Mem0、Langfuse、browser-use。其余并未完成目录调查；此处只把来源明确的对象作为试运行候选，而非认为其他对象不值得研究。

**目录处于修复规划分支，不代表 P Atlas 线上内容已经修改。** 独立来源普查仍未完成；本轮也没有实际运行 P Discovery。
