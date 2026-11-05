# LangGraph 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `p-hybrid`｜结果视角｜把规则步骤与模型判断串成可执行业务流程｜s-overview
2. `p-conversation`｜结果视角｜接续同一用户的多轮对话｜s-memory
3. `p-remember`｜结果视角｜跨对话记住用户偏好和已知事实｜s-store
4. `p-resume`｜结果视角｜从保存的任务进度继续中断工作｜s-persistence
5. `p-approval`｜结果视角｜在执行关键动作前等待人工审阅｜s-interrupts
6. `p-time-travel`｜结果视角｜回到历史进度比较另一条执行路线｜s-time
7. `p-live-progress`｜结果视角｜向用户实时呈现回答和执行进展｜s-streaming
8. `p-failure-recovery`｜结果视角｜为暂时失败的任务配置自动重试与恢复路线｜s-faults
9. `p-parallel`｜结果视角｜并行完成互不依赖的子任务｜s-patterns
10. `p-route`｜结果视角｜按问题内容分流到不同处理专长｜s-patterns
11. `p-revise`｜结果视角｜依据评价反馈反复改进一份结果｜s-patterns
12. `p-tool-loop`｜结果视角｜让 Agent 在任务中选择工具并继续决策｜s-patterns
13. `p-modular-team`｜扩展视角｜把流程模块复用于不同 Agent｜s-subgraphs
14. `p-targeted-tests`｜扩展视角｜独立检查复杂流程中指定的一段行为｜s-test
15. `p-sql`｜示例视角｜用自然语言向数据库提问并得到查询结果｜s-sql
16. `p-rag`｜示例视角｜根据问题决定是否检索私有或选定资料后回答｜s-rag
17. `p-retrieve-again`｜示例视角｜在检索资料不相关时改写问题继续查找｜s-rag
18. `p-support-email`｜示例视角｜建立能分类、查资料并提交人工审阅的客服邮件流程｜s-email
19. `p-research`｜示例视角｜改造开放深度研究项目来交付研究结果｜s-research
20. `p-chat-interface`｜扩展视角｜给 Agent 提供可查看工具动作的对话界面｜s-ui
21. `p-managed-service`｜扩展视角｜把状态化 Agent 发布为可管理的生产服务｜s-deploy

## 归一化、补漏与停止依据

结果视角先提取状态接续、人工介入、容错、流式反馈和控制流结果，没有先套用其他主题的分类。
示例视角补读邮件客服、自定义 SQL、Agentic RAG 和 Open Deep Research，保留“开发示例”与“已部署产品”的区别。
扩展视角检查子图、局部测试、独立 Chat UI 与 LangSmith 部署。把多种 checkpointer/数据库适配器合并进结果及条件，没有按包名拆分 P。
补漏复查 Graph API、Stores 与运行时概述后，新增资料主要落在已识别的状态、控制流和记忆结果；将数据库、UI 和托管服务边界补入条件后停止本轮。

## 保留的未知项

- 未安装运行全部例子，也未对模型正确率、生产吞吐、故障恢复的外部副作用做实测。
- 官方当前文档含 1.1、1.2 新接口；不能推定旧版本支持所有条目，升级需按项目依赖与迁移说明核对。
- 未把任意外部 API 的 exactly-once 执行、无限任务时长或自动消除幻觉列为已确认能力。
- 生产部署、跨租户权限、各数据库适配器兼容性与费用需在目标环境验证；LangSmith 不能归入开源包内置。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-deploy](https://docs.langchain.com/langsmith/deployment.md) | 2026-11-05T08:36:34.334727+00:00 | 是 |
| [s-email](https://docs.langchain.com/oss/python/langgraph/thinking-in-graph-api.md) | 2026-11-05T08:36:34.394415+00:00 | 是 |
| [s-faults](https://docs.langchain.com/oss/python/langgraph/fault-tolerance.md) | 2026-11-05T08:36:31.371026+00:00 | 是 |
| [s-graph](https://docs.langchain.com/oss/python/langgraph/graph-api.md) | 2026-11-05T08:39:06.761707+00:00 | 否 |
| [s-interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts.md) | 2026-11-05T08:36:31.422469+00:00 | 是 |
| [s-memory](https://docs.langchain.com/oss/python/langgraph/add-memory.md) | 2026-11-05T08:36:31.564355+00:00 | 是 |
| [s-overview](https://docs.langchain.com/oss/python/langgraph/overview.md) | 2026-11-05T08:35:11.237386+00:00 | 是 |
| [s-patterns](https://docs.langchain.com/oss/python/langgraph/workflows-agents.md) | 2026-11-05T08:36:32.822133+00:00 | 是 |
| [s-persistence](https://docs.langchain.com/oss/python/langgraph/persistence.md) | 2026-11-05T08:36:30.993535+00:00 | 是 |
| [s-rag](https://docs.langchain.com/oss/python/langgraph/agentic-rag.md) | 2026-11-05T08:36:33.030974+00:00 | 是 |
| [s-research](https://github.com/langchain-ai/open_deep_research/blob/1b7d2e80db9faa586165c60e09096dbbfd483a64/README.md) | 2026-11-05T08:39:06.363055+00:00 | 是 |
| [s-sql](https://docs.langchain.com/oss/python/langgraph/sql-agent.md) | 2026-11-05T08:36:33.228551+00:00 | 是 |
| [s-store](https://docs.langchain.com/oss/python/langgraph/stores.md) | 2026-11-05T08:39:07.188014+00:00 | 是 |
| [s-streaming](https://docs.langchain.com/oss/python/langgraph/streaming.md) | 2026-11-05T08:36:31.489682+00:00 | 是 |
| [s-subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs.md) | 2026-11-05T08:36:32.657537+00:00 | 是 |
| [s-test](https://docs.langchain.com/oss/python/langgraph/test.md) | 2026-11-05T08:36:32.840420+00:00 | 是 |
| [s-time](https://docs.langchain.com/oss/python/langgraph/use-time-travel.md) | 2026-11-05T08:36:31.198123+00:00 | 是 |
| [s-ui](https://docs.langchain.com/oss/python/langgraph/ui.md) | 2026-11-05T08:36:34.079182+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：无额外措辞修订。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
