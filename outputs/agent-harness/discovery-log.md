# Agent Harness 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `p-long-work`｜结果视角｜跨上下文窗口逐步推进长时工程任务｜s-long
2. `p-rollback`｜示例视角｜从代理引入的坏改动恢复可用工程状态｜s-long
3. `p-context`｜结果视角｜在长任务中压缩历史并卸载大型中间结果｜s-deep
4. `p-planning`｜结果视角｜跟踪多步任务的计划和执行进度｜s-deep
5. `p-just-in-time`｜结果视角｜让代理按当前任务查找所需文件上下文｜s-context
6. `p-compaction`｜结果视角｜在会话接近上下文上限时保留关键摘要继续工作｜s-context
7. `p-specialists`｜结果视角｜把复杂子任务交给隔离上下文的专长代理｜s-subagents
8. `p-model-mix`｜扩展视角｜为不同子任务配置各自的说明和模型｜s-subagents
9. `p-background`｜扩展视角｜保持前台交互并调整后台执行的任务｜s-async
10. `p-skills`｜扩展视角｜把领域流程作为可复用技能交给不同代理｜s-skills
11. `p-memory`｜结果视角｜在不同对话中沿用可更新的经验文件｜s-memory
12. `p-storage`｜结果视角｜把临时资料与长期记忆分配到不同存储｜s-backends
13. `p-file-policy`｜结果视角｜限制代理可读写的目录和文件范围｜s-backends
14. `p-sandbox`｜扩展视角｜让代理在隔离环境执行代码并产出文件｜s-sandbox
15. `p-approval`｜结果视角｜在外部动作执行前让人批准或修改参数｜s-human
16. `p-tools`｜扩展视角｜把外部系统的工具接入代理执行循环｜s-mcp
17. `p-build-evaluate`｜示例视角｜用规划、生成和评价循环迭代完整应用｜s-harness-design
18. `p-browser-evaluation`｜示例视角｜让代理在真实网页中操作并给出实现评价｜s-harness-design

## 归一化、补漏与停止依据

先从执行、上下文、状态、工具与人类控制中提取可观察结果；不以内部模块名作为 P。
示例视角补读 Anthropic 长任务接续和完整应用迭代实验，把跨会话继续、git 回退与真实浏览器评价保留为不同结果。
扩展视角调查 Deep Agents 的 backend、沙箱、记忆、技能、同步与异步子代理、HITL 和 MCP 连接；依赖全部明确写进条目。
归一化时把工具列表和多个沙箱供应商合并进对应结果；未将供应商名、API 参数或任意“自动化所有工作”拆成 P。
复查上下文工程与长期应用实验后，更多材料主要重复已发现的接续、委派和反馈机制；未证实的运行保证保留为缺口。

## 保留的未知项

- 未对不同 Harness、模型和任务做统一基准或长时可靠性测量；实验中的成功案例不能外推到所有工程。
- 未把无限执行、无损记忆、自动正确、绝对沙箱安全或无人监督上线列为已确认能力。
- 长期任务预算、可观测性、外部副作用补偿、租户隔离和特定部署产品尚需按选用实现深入验证。
- 部分当前接口有明确版本门槛，如 Deep Agents v0.7 的可选 planning，以及 LangChain 1.4 的 beta MCP 接口；未承诺与旧示例兼容。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-async](https://docs.langchain.com/oss/python/deepagents/async-subagents.md) | 2026-11-05T08:39:06.600727+00:00 | 是 |
| [s-backends](https://docs.langchain.com/oss/python/deepagents/backends.md) | 2026-11-05T08:36:35.847104+00:00 | 是 |
| [s-context](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) | 2026-11-05T08:39:04.861027+00:00 | 是 |
| [s-deep](https://docs.langchain.com/oss/python/deepagents/overview.md) | 2026-11-05T08:36:34.853800+00:00 | 是 |
| [s-harness-design](https://www.anthropic.com/research/harness-design-long-running-apps) | 2026-11-05T08:39:06.144927+00:00 | 是 |
| [s-human](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop.md) | 2026-11-05T08:36:35.874856+00:00 | 是 |
| [s-long](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | 2026-11-05T08:39:05.275447+00:00 | 是 |
| [s-mcp](https://docs.langchain.com/oss/python/langchain/mcp.md) | 2026-11-05T08:39:05.670170+00:00 | 是 |
| [s-memory](https://docs.langchain.com/oss/python/deepagents/memory.md) | 2026-11-05T08:39:05.674102+00:00 | 是 |
| [s-sandbox](https://docs.langchain.com/oss/python/deepagents/sandboxes.md) | 2026-11-05T08:36:36.187113+00:00 | 是 |
| [s-skills](https://docs.langchain.com/oss/python/deepagents/skills.md) | 2026-11-05T08:39:04.766007+00:00 | 是 |
| [s-subagents](https://docs.langchain.com/oss/python/deepagents/subagents.md) | 2026-11-05T08:36:36.232496+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`p-context`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。

`p-context` 仅负责工具大结果的外部化与回读；会话历史摘要和接续统一由 `p-compaction` 表达，消除原先交叉。
