# 验证记录索引

> 更新日期：2026-10-04  
> **先读这份再读别的。** 14 份记录分四组，覆盖范围有重叠，没有这份索引就会读到过期结论。

## 怎么用这份索引

| 你想知道 | 读哪份 |
| --- | --- |
| 当前做到哪、下一步做什么 | [`../COP_GOAL_PLAN_TASK_METHOD.md`](../COP_GOAL_PLAN_TASK_METHOD.md) §8 |
| LangChain 这批 COPs 有什么质量问题 | 本文件 §2（**10-03 结论优先**） |
| 真实 provider 到底验了什么 | `a1-real-verification-results-2026-10-03.md` |
| A1 的待办与授权边界 | `a1-status-summary-2026-10-03.md` + `a1-authorization-request-2026-10-03.md` |
| 执行真实验证前要准备什么 | `a1-real-verification-runbook.md` |

---

## 1. 当前有效结论（A1 / 2026-10-03）

这组是**最新的**，关于真实 provider 与用户验收。

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| `a1-real-verification-results-2026-10-03.md` | 真实 provider 6 项全 PASS（Basic 2 + Tools 4），含 P999 错误处理与多次调用 | **有效** |
| `langchain-basic-prototype-2026-10-03.md` | Basic 样板验证范围：13 测试、内容摘要、离线结果 | **有效** |
| `tools-tools-prototype-2026-10-03.md` | Tools 样板验证范围：66 测试、端到端管线、SHA-256 绑定 | **有效** |
| `tools-basic-comparison-t08-2026-10-03.md` | 两样板对照：层1 共享契约 9 项、层 2 profile 参数化 4 项、层 3 独有差异 | **有效**，A2 的输入 |
| `langchain-basic-content-review-2026-10-03.md` | Basic 内容审核：无阻塞，4 项信息负担改进已应用 | **有效** |
| `langchain-tools-content-review-2026-10-03.md` | Tools 内容审核 | **有效** |
| `tools-completion-audit-2026-10-03.md` | Tools 完成度审核 | **有效** |
| `a1-status-summary-2026-10-03.md` | 标题写「等待用户授权」 | **部分过期**：授权与真实验证已完成，仅B08 未完成 |
| `a1-authorization-request-2026-10-03.md` | 授权请求 | **已执行完**（见 results），保留作授权边界记录 |
| `a1-execution-readiness-checklist-2026-10-03.md` | 执行就绪检查 | 已用过 |
| `a1-real-verification-runbook.md` | 准备清单 | 仍有效，**后续新真实调用需重新授权** |
| `a1-completion-summary.md` | A1 完成总结 | 见下方冲突提示 |

## 2. LangChain 案例审查（两条线索，结论不同）

**这两份审查的对象不同，不是同一件事的两次复核。**

| 文档 | 对象 | 结论 |
| --- | --- | --- |
| `gate1-langchain-report.md`（09-30） | `reference-langchain-cop.json`（5 goals / 22 stages） | 结构成立、可执行性部分成立；**9 个阻塞项 B1–B9**，含 Practice 无产出物、`get_tools()` 不存在、端点缺失 |
| `langchain-case-audit-2026-10-02.md` | 同上 | 全面审查，Gap 清单 |

**`gate1-langchain-report.md` 仍然有效**，因为它记录的 B1/B7/B9 在 `enrich_langchain_fixture.py` 里已修，而 B2/B3/B4（Practice 产物契约）与 B8（证据定位）**至今未实施**。

> ⚠️ **已知冲突**：`a1-completion-summary.md` 声称 A1 已完成，但总纲的 B08（目标用户独立完成 Practice）仍未做。**以总纲为准**：A1 的工程与真实 provider 部分完成，用户验收未完成。

## 3. 提案（非验证记录）

| 文档 | 状态 |
| --- | --- |
| `../proposals/cop-quality-standard-and-production-v1.md` | S1–S9 质量标准与生产方案，随样板验证修订中 |
| `../proposals/tools-task-definition-v1.md` | Tools T01 任务定义（产品目录查询），已通过实现验证 |
| `../proposals/evidence-v1.1.md` | Evidence 三级设计草案，**已推迟**，Gate 2 后再定 |

---

## 4. 待办提醒（来自本文档各条记录）

- **B08** 是当前唯一阻塞项：目标用户独立完成 Basic Practice，入口 `http://localhost:3000/prototypes/langchain-basic`
- **B2/B3/B4**（Practice 产物契约）需要 schema 决策，见总纲 §8.2
- **B8**（证据定位）分A/B/C 三档，A 档不碰 schema 可立即做
- 两份 LangChain COP 并存且无权威标记：`reference-langchain-cop.json`（seed 指向，5 goals）与 `langchain-basic-cop.json`（prototype 指向，1 goal）——见总纲 §8.2待决策项