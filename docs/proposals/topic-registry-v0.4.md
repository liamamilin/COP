# Topic Registry v0.4 · P Discovery 批量选题系统

> **交付范围：目录与待执行队列，不运行批量 P Discovery、不修改 Skill、不自动发布 P Atlas。**

## 结构

```text
Domain 领域 → Area 子领域 → Topic 独立研究对象
                              ↓ Codex 调用 p-discovery Skill
                         P (可达用户结果)
```

**Domain、Area 只用于组织对象。** Topic 的 `scope_level` 表示研究层级：`bounded_subject` 是具体产品、库、框架、服务、协议或边界清晰的方法；`area_survey` 是较宽的领域概览，当前不进入默认批次。对象类型通过 `topic_type` 独立标识。不要把数据应用这个 Area 与 Shiny 这个 Topic、或 Shiny 研究后发现的 P 混淆。

## 四份核心文件

- `catalog/topic-taxonomy.v0.4.json`：11 个 Domain + 82 个 Area + 官方类别索引入口。
- `catalog/topic-registry.v0.4.json`：291 个 Topics、身份类型、范围摘要、来源批次与研究状态。
- `catalog/coverage.v0.4.md`：各 Area 的种子覆盖及仍待进行的来源调查，防止将对象数当成覆盖率。
- `catalog/research-queue.v0.4.json`：研究工作流建议，不包含已研究主题，不负责发布。

可以运行 `python3 scripts/validate_topic_registry.py` 检查父子引用、去重、来源批次状态和队列是否引用尚未研究的具体对象。

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

- 以前的 v0.3 以工具凑目录，现根据活动领域先建立 82 个 Area，再将旧的 110 项和 181 项种子映射。
- 具体方法可以进入目录（例如 A/B 测试、刻意练习），但不能仅凭名称假装它是一款有 API 的软件；证据主要来自研究方法与实际案例。
- 已有的 LLM 推理、微调、AI 视频等概览仍保留但标注 `area_survey`，不与 llama.cpp、LTX Video、Shiny 等具体对象在默认批次里比较数量。
- 此版本解决的是**结构上的系统性**。覆盖报告承认独立来源普查未完成，不声称目录已穷尽。
