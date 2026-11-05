# DuckDB Discovery Log

## 范围与版本

针对个人开发者如何从本地和可访问数据文件做分析、导出结果或将 SQL 嵌入应用。官方入口和文档显示 DuckDB 2.0 LTS；Python 与 Wasm client 页标注 2.0.0。扩展兼容性按客户端和平台另行判断。本次资料于 2026-11-05 抓取。

## 结果视角：先记录的无分类候选

- 在 CLI 直接读 CSV 并推断读取参数。
- 同一查询读取多份 Parquet 文件。
- 导出分析结果供其他工具消费。
- 读取云对象存储中的文件。
- 用 Python 直接查询 DataFrame。
- 连接 PostgreSQL 表查询/交换数据。
- 用 GIS 几何和位置关系做空间分析。
- 把分析引擎放到浏览器端。
- 开发交互式铁路交通地图。
- 缓存远端昂贵查询结果，以后再分析。
- 将本地数据库文件供不同客户端重连。

## 案例视角

官方 Streamlit 示例使用荷兰铁路真实数据建应用：包含 2024 铁路网络流量地图，以及在地图任一点查看附近五个车站。文章还说明它用 Python relational API、Plotly 和 Streamlit Folium，并讨论内存/持久化/外部数据库的连接方式及服务器内存要求。该地图前端依赖 Streamlit 等第三方组件。

DuckDB 官方案例介绍 QStudio 桌面分析工具：分析者先从远端数据库运行重查询并将结果保存成 Parquet；之后直接查询保存结果，继续计算交易符号平均价格与交易量汇总。它需要 QStudio 与 DuckDB Java client，文章观察不等同于性能保证。

DuckDB-Wasm 2.0 client 文档还提供浏览器中的 SQL shell；浏览器限制和 Wasm 内存/线程注意事项保留在条件中。

## 扩展与客户端视角

SQL、CLI 和 Python client 属于 DuckDB 官方客户端/基础功能。CSV/Parquet 的实际打包情况因 client 而异，Parquet 文档说明大多数客户端随附。httpfs 可让核心查询逻辑访问远程 HTTP/S3 文件；PostgreSQL connector 使远端表可在查询时读取；Spatial 作为需显式安装/加载的扩展；DuckDB 2.0 文档确认其仍提供空间处理但不自动加载，详细 transform/join 案例来自 2023 年文章，未验证在 2.0 的同等 API/格式兼容性。httpfs、PostgreSQL connector 均按 extension 标记并说明依赖/账户条件。Wasm、Java、Python 是官方 client API；DuckDB-Wasm 作为官方 WebAssembly client 归 core，同时保留浏览器内存/线程限制；Streamlit、Plotly、Folium、QStudio 是不同的外部应用/框架集成。

## 归一化与最终分类

将“查询 Parquet 文件”和“多文件 glob”合并为多文件查询一项；把 query-result 文件导出单列为可交换结果；Python 数据对象、浏览器和 Streamlit/QStudio 各保留不同使用环境的结果；扩展能力依其用户成果分组。最终 10 项，按数据查询、导出、外部连接、嵌入开发、面向用户应用、空间分析归类，没有把安装命令或 SQL 函数拆成 P。

## 未知项与停止依据

已查看 2.0 官方文档入口、SQL/CSV/Parquet/多文件、CLI/Python/Wasm 客户端、扩展机制、httpfs/PostgreSQL/Spatial 资料和两篇实际应用案例。新材料主要验证并细化已有候选，没有产生新类别；未深入检查每种扩展版本与全部 OS/运行时，也没有针对OLTP、多用户在线 SaaS、云托管数据库或企业数据仓库替代做生产评估。此前若干猜测的 blog/guides URL 404，保留在 source-coverage.json，不作证据。

## 主 agent 来源复核

主 agent 已逐项阅读结果、条件和摘录的周边原文；按实际响应类型区分 Markdown、HTML 提取正文和源文本，并核对 GitHub 固定引用。类型标签累计修正 0 处；引文与原始缓存行号仍逐条匹配。这不授予 reviewed，不是独立人工审核或工具运行认证。

## 交付后复查（2026-11-05）

逐项将 Markdown 的结果、条件、能力标签与证据链接和 JSON 对齐，保留原有用途分组、覆盖说明及发现过程。报告采用条目级证据 URL；固定提交不退回移动分支。新增批次校验会拒绝报告与 JSON 的结果、限制或标签不一致。
