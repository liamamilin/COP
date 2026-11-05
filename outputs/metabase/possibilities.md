# Metabase：个人开发者可交付的分析成果

范围：数据查询、图表、仪表板、报告传递和应用内嵌入。官方文档当前抓取版本为 v0.65；自托管和 Cloud 计划、数据库驱动及权限会影响可用功能。本次未实际安装或连接数据库。

## 查询与理解数据

### 用图形化查询器整理业务问题

用可视化查询器关联表格、分组汇总数据并生成图表；官方电商演示用月度收入和订单数展示这种数据探索。 **核心**。

条件与边界：Metabase v0.65 文档所述功能；需先安装 Metabase 实例并连接有访问权限的受支持数据库。表连接范围受数据库/驱动支持限制。 Learn 教程使用 Examples 演示数据，不代表用户的生产业务数据；示例集合可能由管理员关闭或删除。

来源：[Metabase documentation — v0.65](https://www.metabase.com/docs/latest/)、[Installing Metabase](https://www.metabase.com/docs/latest/installation-and-operation/installing-metabase)、[Adding and managing databases](https://www.metabase.com/docs/latest/databases/connecting)、[The query builder](https://www.metabase.com/docs/latest/questions/query-builder/editor)、[Explore dashboards](https://www.metabase.com/learn/metabase-basics/getting-started/explore-data)。

### 编写 SQL 问题并保存为可复用报告

在 SQL 编辑器中运行数据库原生查询，把结果保存为问题并加入仪表板。 **核心**。

条件与边界：需连接数据库并具有 SQL 编辑权限。查询语法/函数由连接的数据库决定；Metabase 不替代底层数据库。

来源：[SQL editor](https://www.metabase.com/docs/latest/questions/native-editor/writing-sql)。

### 制作可交互的筛选仪表板

让浏览者用仪表板筛选器改变图表显示的数据，避免为每个时间段或类别复制一份报表。 **核心**。

条件与边界：仪表板由已保存的问题构成；筛选器须映射到支持的字段/卡片，权限仍由 Metabase 与数据源的设置决定。

来源：[Introduction to dashboards](https://www.metabase.com/docs/latest/dashboards/introduction)、[Dashboard filters and parameters](https://www.metabase.com/docs/latest/dashboards/filters)。

### 集中运营报告并自动发送每日管理报表

把分散的运营报告集中到共享指标与仪表板，并自动向管理层发送每日摘要。 **核心**。

条件与边界：Metabase 官方案例描述了 Hola Health 的 telehealth 运营实践，属于客户案例而非本次实测；需要连接对应运营系统并配置报告订阅。

来源：[Hola Health case study](https://www.metabase.com/case-studies/hola-health)。

## 统一指标定义

### 定义团队共用的收入指标

把收入算法保存为可复用指标，让后续问题按统一公式计算收入。 **核心**。

条件与边界：需要可建模的数据库字段与创建/管理指标的权限。定义是否业务正确需由团队确认。

来源：[Metrics](https://www.metabase.com/docs/latest/data-modeling/semantic-layer/metrics)。

## 导出与传递结果

### 下载问题或仪表板的结果文件

下载问题/查询结果或仪表板卡片结果为 CSV、XLSX 或 JSON 文件。 **核心**。

条件与边界：问题与仪表板卡片的下载菜单均列出 CSV、XLSX、JSON；用户需要下载结果的权限，实际可下载内容受图表类型、数据库和管理员设置限制。仪表板整体另可导出 PDF（文档说明仅含当时可见图表的截图），本结果不将整体 PDF 与卡片数据文件混为一谈。

来源：[Exporting results](https://www.metabase.com/docs/latest/questions/exporting-results)。

## 自动推送与告警

### 通过邮件或 Slack 收到仪表板更新

将仪表板问题结果发送给收件人或 Slack 频道，按设置的时间安排推送更新。 **核心**。

条件与边界：管理员需先配置 SMTP 邮件或 Slack 集成；外部收件地址可用于邮件订阅。特定订阅筛选和安全选项依版本/计划而异。

来源：[Dashboard subscriptions](https://www.metabase.com/docs/latest/dashboards/subscriptions)。

### 在问题产生结果时接收告警

为已保存的问题订阅邮件或 Slack 告警，及时发现查询返回结果的情况。 **核心**。

条件与边界：管理员需配置通知通道；Webhook 告警需要管理员或具备设置权限者。检查周期可配置，精确选项依问题类型而定。

来源：[Alerts](https://www.metabase.com/docs/latest/questions/alerts)。

## 把分析交付给产品用户

### 把客户自助分析嵌入自己的产品

在应用中展示 Metabase 仪表板或查询界面，让客户围绕自己的业务数据提出问题。 **核心**。

条件与边界：Metabase 提供官方内嵌组件。Guest embeds 在各计划可用；访客无需 Metabase 登录、不计入用户数且不向访客计费，但应使用签名 JWT 和锁定参数隔离客户数据。认证/SSO 嵌入仅 Pro/Enterprise；这些商业版计划的登录/认证用户按其方案口径计费，不能把 Guest viewers 计作付费用户，具体价格以当前方案为准。Synctera 案例展示了金融产品的客户自助分析。

来源：[Embedding overview](https://www.metabase.com/docs/latest/embedding/start)、[Guest embeds](https://www.metabase.com/docs/latest/embedding/guest-embedding)、[Modular embedding](https://www.metabase.com/docs/latest/embedding/modular-embedding)、[Synctera case study](https://www.metabase.com/case-studies/synctera)、[Metabase Pricing](https://www.metabase.com/pricing)。

## 资料覆盖与缺口

- 资料基于 Metabase 官方 v0.65 文档及案例，未安装或部署；自托管生产环境的数据库、备份、SMTP/Slack、安全、升级和容量需单独规划。
- 支持的数据源、驱动、查询能力取决于底层数据库与 Metabase 版本；本次未对任一数据库实际连接或执行查询。
- Embedding/SSO、多租户隔离、行列权限和订阅筛选在 OSS/Starter 与 Pro/Enterprise 的边界不同；版次和价格可能变更，须在采购前核验。
- 客户案例为 Metabase 发布的客户材料，不能视为独立性能评估或普遍结果。未进一步确认的 public link 路径不列为成果。
