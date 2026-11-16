# PostHog：个人开发者与经营者能做什么？

研究范围：面向个人开发者和经营者，梳理 PostHog 核心产品及明确标注的扩展/外部数据依赖，可实现的数据观察、用户反馈、实验和产品改进任务；以 2026-11-05 实际抓取的官方产品文档、教程、定价和一则客户案例为证据。重点区分观察数据与因果证据，不承诺营收或增长。

PostHog 能把事件分析、会话回放、用户反馈、旗标和实验放在一处查看。先正确接入数据，才能观察实际行为。普通分析描述发生了什么；随机对照实验可以估计特定设计下的差异，但仍取决于样本和实验执行。

## 观察网站流量

- **查看网站流量来源与关键指标**（核心）——查看主要流量来源，并同时掌握会话、跳出率和热门页面。 条件：需要网站 SDK 页面事件；入口来源/UTM 用于渠道归因，广告成本与点击曝光需连接广告平台。归因数据不能证明渠道带来增量。 来源：[Web analytics](https://posthog.com/docs/web-analytics)。

## 理解产品行为

- **观察产品采用、转化与留存**（核心）——用采集的产品事件观察用户是否采用功能、完成关键转化并持续回来。 条件：需要采集并正确命名相关事件，且身份关联和属性完整性会影响分析。观察指标本身不证明产品改动造成变化。 来源：[Product analytics](https://posthog.com/docs/product-analytics)、[Events](https://posthog.com/docs/data/events)。
- **检查用户在哪些转化步骤停滞**（核心）——从漏斗完成或流失用户进入关联会话回放，查看具体交互并形成待验证的改进假设。 条件：需要应用 SDK 安装并启用 Session Replay 录制；按录制规则采集会话并设置隐私遮罩。回放样本不代表全部用户。 来源：[How to use session replays to get a deeper understanding of user behavior](https://posthog.com/tutorials/explore-insights-session-recordings)、[Session Replay](https://posthog.com/docs/session-replay)。

## 收集用户意见

- **向目标用户收集定性反馈**（核心）——向选定用户展示调查并收集定性回答，之后可结合其行为上下文理解意见。 条件：在产品内显示调查需要 SDK；受众定向可依据事件、属性、cohort 或旗标；回答会作为事件记录。样本可能有自选偏差。 来源：[Surveys](https://posthog.com/docs/surveys)。

## 发布与检验改动

- **按条件逐步发布或关闭功能**（核心）——用旗标按百分比、用户属性、cohort 或群组控制功能发布；发现异常时可关闭旗标。 条件：需要把旗标评估接入应用运行时。定向取决于已有身份和属性；旗标不能替代上线监控和回滚计划。 来源：[Feature flags](https://posthog.com/docs/feature-flags)。
- **通过随机对照实验比较改动**（核心）——为改动定义变体和指标，通过旗标随机分配用户、记录曝光，并比较实验组与控制组。 条件：依赖 Feature Flags、曝光和预定义指标；可使用已有产品事件或已同步仓库表。实验结论只针对具体设计，仍受样本量、实验污染和统计不确定性影响。不能保证普遍因果或增长。 来源：[Experiments](https://posthog.com/docs/experiments)、[How Y Combinator used PostHog experiments to boost engagement by 40%](https://posthog.com/customers/ycombinator)。

## 定位可靠性问题

- **把应用异常整理成可处理的问题**（核心）——把应用异常聚合为可指派和解决的问题，并查看受影响用户的事件及会话。 条件：需要应用 SDK 上报异常；上传 source maps/符号以还原压缩堆栈，并标记版本或提交来关联发布。 来源：[Error tracking](https://posthog.com/docs/error-tracking)。

## 关联业务与 AI 数据

- **把产品行为与业务数据联查**（扩展）——同步外部业务数据，与产品事件、用户和会话放在同一 SQL 查询中分析。 条件：需要授权并同步外部系统或文件数据源；连接器按计划刷新。按产品用量计费，额度与连接器细节需以实际定价为准。 来源：[Data warehouse](https://posthog.com/docs/data-warehouse)、[PostHog pricing](https://posthog.com/pricing)。
- **查看 AI 请求的输入输出、成本和延迟**（核心）——把模型提示、回答、token 成本、延迟和工具调用作为 trace 检查，并与触发用户和异常关联。 条件：AI Observability 是 PostHog 产品。应用需发送 LLM 事件，通常通过供应商 SDK 包装采集；也可转发 Helicone、Langfuse、Traceloop 或 Keywords AI traces。按 AI 产品用量适用对应额度。 来源：[AI Observability](https://posthog.com/docs/ai-observability)。

## 实际案例

[Y Combinator 客户案例](https://posthog.com/customers/ycombinator)描述了共同创始人匹配产品的一次旗标随机实验：客户报告 6 周组的消息发送量比控制组高 40%。案例页没有提供可供独立审计的原始数据和完整设计；此数字只描述该客户报告的结果，不表示 PostHog 一般会带来增长。

## 计费与接入边界

浏览器事件需经 SDK 或 API 接入；回放需启用录制并设置隐私遮罩；旗标要接入应用运行时；实验依赖旗标和曝光/指标数据。数据仓库需要授权外部来源并同步；AI 观测可以用 SDK 包装模型调用，也可以转发其他观测工具数据。PostHog 按产品用量计量，免费额度和超额费用可能按产品不同而不同，应以实际使用时的定价页为准。

本次没有安装 SDK、连接账户或读取真实业务数据，因此结果说明的是来源支持的可实现任务，不是某个项目的性能或商业效果。

## 待验证

- 官方产品目录提到更多工作流、目的地、营销分析等产品方向；本轮没有足够的个人经营结果证据支撑单独列为已确认能力。
- 自托管运行的维护成本、不同移动端 SDK 的回放覆盖与隐私/法规要求需按具体版本和部署另行验证。

## 资料覆盖与缺口

- 实际取回官方产品文档、教程、定价页、产品索引和 YC 客户故事；没有把统计术语或产品/API 名称本身当成 P。
- 案例为 PostHog 自述；指标相关变化、漏斗关联和单一回放不能自动证明原因。
- 所有条目保持 `source_supported`，尚未经过人工审查，不标为 `reviewed`。

## 原研究保留的未解决问题

- 证据主要来自官方文档、官方教程和一则厂商发布的客户案例；独立开发者项目的深入记录和独立评测不足。
- 没有安装 SDK、连接账户或读取真实用户数据；没有执行实际分析或实验。
- 未逐项审计不同 SDK 版本、移动端实现、隐私/合规要求、地区和所有数据源连接器。
- 客户案例报告的 40% 是单一客户自述，未拿到原始数据或实验设计，无法独立核验。
- 观察到的行为指标不证明改动的因果效果；实验结论受样本、设计和执行影响，不能保证收入或增长。
