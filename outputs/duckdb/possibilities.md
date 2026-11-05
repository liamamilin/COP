# DuckDB：个人开发者可完成的成果

范围：本地分析、文件格式、嵌入式客户端及可分享计算结果。资料基于 DuckDB 2.0 LTS 文档与部分真实应用案例，取回于 2026-11-05；未安装或实测，所有性能与效果需在实际数据上验证。

## 查询与整理手边的数据

### 直接用 SQL 查询本地 CSV

在 CLI 中读取本地 CSV，并让 DuckDB 自动推断读取选项以便开始分析。 **核心**。

条件与边界：面向 DuckDB 2.0 LTS 文档；需安装 DuckDB CLI。CSV reader 的自动推断对异常/非标准文件仍需检查或手动配置。

来源：[DuckDB Documentation — 2.0 LTS](https://duckdb.org/docs/2.0/)、[CSV Import — DuckDB 2.0](https://duckdb.org/docs/2.0/data/csv/overview)。

### 把多份 Parquet 文件作为一张表查询

把多份结构兼容的 Parquet 文件一次读入同一个查询，便于汇总分散在多个文件里的数据。 **核心**。

条件与边界：Parquet 扩展在绝大多数 DuckDB clients 中随附；精简嵌入发行版可能需单独安装。不同 schema 的文件需另外选择 schema 合并策略。

来源：[Reading Multiple Files — DuckDB 2.0](https://duckdb.org/docs/2.0/data/multiple_files/overview)。

## 导出可交换的成果

### 把分析查询结果导出为 Parquet

将 SQL 查询的结果写成压缩列式 Parquet 文件，交给其他分析工具或流程继续使用。 **核心**。

条件与边界：需要可写的目标路径与磁盘空间。目标客户端须包含 Parquet 支持；不同压缩/行组参数会影响文件和性能。

来源：[Reading and Writing Parquet Files — DuckDB 2.0](https://duckdb.org/docs/2.0/data/parquet/overview)。

## 连接外部数据源

### 查询 S3 对象存储中的数据文件

使用 S3 API 读取或写入对象存储中的分析文件，并用 DuckDB 的文件查询能力整理结果。 **扩展**。

条件与边界：依赖官方 httpfs 扩展；需 S3-compatible endpoint、凭据/权限和网络访问。Plain HTTP(S) 只支持读取；不同对象存储实现兼容性需验证。

来源：[httpfs Extension for HTTP and S3 Support — DuckDB 2.0](https://duckdb.org/docs/2.0/core_extensions/httpfs/overview)。

### 把 PostgreSQL 表接入本地 SQL 分析

在 DuckDB 中附加 PostgreSQL 数据库，并在查询时直接读取其表。 **扩展**。

条件与边界：需要安装/加载 PostgreSQL extension、可访问的 PostgreSQL 数据库与适当权限/凭据；该扩展也可执行写入，应显式使用 READ_ONLY 以避免修改源库。

来源：[PostgreSQL Extension — DuckDB 2.0](https://duckdb.org/docs/2.0/core_extensions/postgres/overview)。

## 嵌入开发工作流

### 在 Python 中直接分析 Pandas 数据

在 Python 脚本或应用里把 Pandas DataFrame 作为 SQL 查询的数据源。 **核心**。

条件与边界：需安装 DuckDB 的 Python client（如 pip install duckdb）与 Pandas。Python 包版本和 pandas 版本应按项目锁定；未测试兼容性。

来源：[Python API — DuckDB 2.0](https://duckdb.org/docs/2.0/clients/python/overview)。

## 构建面向用户的应用

### 制作可交互的铁路数据地图

用铁路公开数据做交互式地图：展示 2024 铁路网络流量，并查询地图选点附近的车站。 **扩展**。

条件与边界：此完整示例使用第三方 Streamlit、Plotly、Streamlit Folium 组件和 DuckDB Python API；需这些依赖及铁路数据访问，地图可视化不是 DuckDB 内建 UI。

来源：[Using DuckDB in Streamlit](https://duckdb.org/2025/03/28/using-duckdb-in-streamlit)。

### 复用已保存的分析结果继续查询

在桌面分析工具里对先前保存的查询结果继续执行 SQL，而不必重跑原始远端工作负载。 **扩展**。

条件与边界：这是 QStudio 的真实集成案例，使用 DuckDB Java client 和 Parquet 文件；QStudio/Java 应用是额外环境，文章的性能/适用性观察不构成保证。

来源：[Bringing Local Analytics to the Quant's Desktop](https://duckdb.org/2026/11/03/bringing-local-analytics-to-the-quants-desktop)。

### 在浏览器里运行 SQL 查询

把 DuckDB-Wasm 集成进网页，在浏览器交互式运行 SQL。 **核心**。

条件与边界：DuckDB 官方 WebAssembly client 2.0.0（JavaScript/WebAssembly）可作为 DuckDB 官方客户端用于网页；需在网页应用中集成。默认单线程，内存上限 4 GB 且浏览器可能更低，多线程仍为实验性。此条是官方 client 形态，不表示浏览器无限资源或本次运行验证。

来源：[DuckDB Wasm Client — DuckDB 2.0](https://duckdb.org/docs/2.0/clients/wasm/overview)。

## 处理地理空间数据

### 分析空间几何并连接地理数据

使用空间扩展处理地理数据，支持空间变换与连接，适用于位置或区域类数据分析。 **扩展**。

条件与边界：需要安装并显式加载 DuckDB Spatial extension；DuckDB 2.0 官方文档仍列出该扩展并说明其不可自动加载。这里关于 transform/join 的具体结果来自 2023 历史案例；2.0 下相同函数、格式及兼容性未逐一核实或运行测试。

来源：[Introducing the DuckDB Spatial Extension](https://duckdb.org/2023/04/28/spatial)、[Spatial Extension — DuckDB 2.0](https://duckdb.org/docs/2.0/core_extensions/spatial/overview)。

## 资料覆盖与缺口

- 研究重点为本地及嵌入式分析、文件型数据和开发者集成；未调查大型并发多写 OLTP 服务、企业级数据仓库替换或多租户在线 SaaS 的生产适用性。
- Spatial、HTTPFS、PostgreSQL extension 的版本/二进制兼容性需按 DuckDB client、平台架构、权限和远端服务逐一测试；文档有讲述其能力，不代表本次部署实测。
- 财务/业务决策结果仍取决于输入数据质量、查询逻辑和可视化表达；未校验样例数据、业务结论或性能声明。
