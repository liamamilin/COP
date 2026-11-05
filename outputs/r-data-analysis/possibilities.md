# R 数据分析 可能性地图

范围：R 核心统计与图形，以及数据导入、整理、建模、专门领域、交互和可复现交付的具名扩展；不重做 ggplot2 专题清单。

资料截点：2026-11-05。本图有 26 项来源支持的结果，来自 26 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

核心条目标 core，额外包、工具与服务标 extension。统计有效性取决于研究设计、假设、数据质量和诊断；可执行代码不自动产生可靠科学结论。

## 地图导航

- [获取和连接数据](#acquire)
- [整理与探索数据结构](#prepare)
- [估计效应与不确定性](#inference)
- [预测与专门领域研究](#specialist)
- [交互探索与报告交付](#delivery)
- [维护可更新和可恢复的分析](#reproduction)

<a id="acquire"></a>
## 获取和连接数据

### `r-01` 把文本表格读成可分析数据

通过 readr 导入 CSV、TSV 等分隔文件，并获得解析问题提示。

**扩展／具名实现路线 · 有来源支持。** 需要 readr；编码、地区格式、列类型和缺失值需确认。

来源：[s-import：readr · Read Rectangular Text Data · Overview；本次 HTML 提取正文第 22–22 行（不是 HTML 源码行号）](https://readr.tidyverse.org/)。

### `r-02` 分析 Excel 工作表中的表格

通过 readxl 读取 xls / xlsx 工作表，获得 R 中可处理的数据。

**扩展／具名实现路线 · 有来源支持。** 需要 readxl；公式、版式和不规则表头不等于直接可分析表格，需检查范围和类型。

来源：[s-excel：Read Excel Files • readxl · 页面正文；本次 HTML 提取正文第 22–22 行（不是 HTML 源码行号）](https://readxl.tidyverse.org/)。

### `r-03` 与其他统计软件交换数据

用 haven 读写 SAS、SPSS、Stata 的受支持格式，将已有研究数据带入 R 流程。

**扩展／具名实现路线 · 有来源支持。** 需要 haven，具体文件版本有边界；值标签、日期和缺失值语义需核验。

来源：[s-haven：haven · Import and Export SPSS, Stata and SAS Files · 页面正文；本次 HTML 提取正文第 23–23 行（不是 HTML 源码行号）](https://haven.tidyverse.org/)。

### `r-06` 直接分析数据库中的数据

用 dbplyr 将数据处理表达式翻译为 SQL，把计算交给数据库后端。

**扩展／具名实现路线 · 有来源支持。** 需要数据库驱动、连接与权限；不同数据库的函数和类型支持不同。

来源：[s-database：dbplyr · Database Backend · 页面正文；本次 HTML 提取正文第 28–28 行（不是 HTML 源码行号）](https://dbplyr.tidyverse.org/)。

### `r-07` 处理多文件或超出内存的数据集

通过 Arrow 读取列式数据及多文件数据集，按支持的表达式进行分析。

**扩展／具名实现路线 · 有来源支持。** 需要 Arrow 及合适存储布局；并非所有 R 函数都能下推，云后端与系统支持有差异。

来源：[s-arrow：Arrow R Package • Arrow R Package · 页面正文；本次 HTML 提取正文第 46–46 行（不是 HTML 源码行号）](https://arrow.apache.org/docs/r/)。

<a id="prepare"></a>
## 整理与探索数据结构

### `r-04` 清洗记录并计算分组汇总

使用 dplyr 筛选、生成变量、排序和按组汇总，得到问题所需的分析表。

**扩展／具名实现路线 · 有来源支持。** 需要 dplyr；分组、重复值、缺失值和指标定义由分析者负责。

来源：[s-transform：dplyr · A Grammar of Data Manipulation · 页面正文；本次 HTML 提取正文第 37–37 行（不是 HTML 源码行号）](https://dplyr.tidyverse.org/)。

### `r-05` 把宽表、嵌套数据和混合字段整理成规则表

用 tidyr 转换长宽结构、展开嵌套对象和拆合字段，使数据适合建模。

**扩展／具名实现路线 · 有来源支持。** 需要 tidyr；必须保留变量含义、键和观测粒度，不能把重排当作纠错。

来源：[s-reshape：tidyr · Tidy Messy Data · 页面正文；本次 HTML 提取正文第 47–47 行（不是 HTML 源码行号）](https://tidyr.tidyverse.org/)。

### `r-11` 从对象相似性中寻找层次结构

基于距离进行层次聚类，并以树状结果探索样本或变量之间的关系。

**内置／核心能力 · 有来源支持。** stats 核心；距离、标准化与聚类方法会改变结果，不自动证明存在真实类别。

来源：[s-cluster：R: Hierarchical Clustering · 页面正文；本次 HTML 提取正文第 5–5 行（不是 HTML 源码行号）](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/hclust.html)。

### `r-25` 用散点图检查变量关系

调用 R 自带图形系统绘制数据关系，辅助发现结构、异常和模型问题。

**内置／核心能力 · 有来源支持。** graphics 核心；需合适的尺度、坐标和解释，不以图形外观证明统计结论。

来源：[s-graphics：R graphics · Default Scatterplot Function · 页面正文；本次 HTML 提取正文第 1–1 行（不是 HTML 源码行号）](https://stat.ethz.ch/R-manual/R-devel/library/graphics/html/plot.default.html)。

### `r-26` 将多个来源的数据按键关联或比较

通过 dplyr 的连接和集合操作合并补充变量、筛选匹配记录或比较数据集合。

**扩展／具名实现路线 · 有来源支持。** 需要明确关联键、键的唯一性和缺失值语义；多对多关联可能放大记录数，需核对行数。

来源：[s-joins：Drop unimportant variables so it's easier to understand the join results. · 页面正文；本次 HTML 提取正文第 50–50 行（不是 HTML 源码行号）](https://dplyr.tidyverse.org/articles/two-table.html)。

<a id="inference"></a>
## 估计效应与不确定性

### `r-08` 比较样本均值及其不确定性

以合适的 t 检验比较单样本、两样本或配对均值，并报告区间与检验结果。

**内置／核心能力 · 有来源支持。** stats 随 R 提供；设计、分布和独立性等假设需核查，显著性不等于实际意义。

来源：[s-test：R: Student's t-Test · 页面正文；本次 HTML 提取正文第 5–5 行（不是 HTML 源码行号）](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/t.test.html)。

### `r-09` 用回归解释连续结果与变量关系

拟合线性模型，完成回归、方差分析或协方差分析的相应任务。

**内置／核心能力 · 有来源支持。** stats 核心；需检查模型假设、混杂和诊断，相关回归不自动支持因果结论。

来源：[s-lm：R: Fitting Linear Models · 页面正文；本次 HTML 提取正文第 5–5 行（不是 HTML 源码行号）](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/lm.html)。

### `r-10` 对不同分布的结果建立统计模型

使用广义线性模型选择相应误差分布和连接函数，分析二元或计数等结果。

**内置／核心能力 · 有来源支持。** stats 核心；需明确 family、数据分布和模型诊断，不保证拟合或预测可靠。

来源：[s-glm：R stats · Fitting Generalized Linear Models · 页面正文；本次 HTML 提取正文第 5–5 行（不是 HTML 源码行号）](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/glm.html)。

### `r-17` 分析事件发生时间及删失数据

以 survival 包估计生存曲线、Cox 或其他适用事件时间模型。

**扩展／具名实现路线 · 有来源支持。** 推荐包 survival 仍属独立包；设计、删失机制和比例风险等假设必须评估。

来源：[s-survival：CRAN: Package survival · 页面正文；本次 HTML 提取正文第 5–5 行（不是 HTML 源码行号）](https://cran.r-project.org/web/packages/survival/index.html)。

### `r-18` 根据复杂抽样设计估计总体指标

用 survey 的权重、分层和多阶段设计估计统计量及方差。

**扩展／具名实现路线 · 有来源支持。** 需要 survey 和真实设计信息；原作者主页版本信息较旧，当前安装兼容性未验证，不直接套用简单随机抽样方法。

来源：[s-survey：Survey analysis in R · 页面正文；本次 HTML 提取正文第 4–5 行（不是 HTML 源码行号）](https://r-survey.r-forge.r-project.org/survey/)。

### `r-24` 用随机模拟研究假设与不确定性

从统计分布生成随机样本，用于模拟研究或检查方法行为。

**内置／核心能力 · 有来源支持。** stats 核心；需定义生成机制、种子、重复次数和统计指标，模拟结果不能自动推广现实。

来源：[s-simulate：R: Distributions in the 'stats' Package · Details；本次 HTML 提取正文第 10–10 行（不是 HTML 源码行号）](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/Distributions.html)。

<a id="specialist"></a>
## 预测与专门领域研究

### `r-12` 开发并评估可用于新数据的预测模型

按 tidymodels 完整案例切分数据、重采样、比较模型并做最终评估。

**扩展／具名实现路线 · 有来源支持。** 需要 tidymodels 及具体引擎包；酒店案例展示流程，不保证新业务性能；防止数据泄漏。

来源：[s-model-case：tidymodels · A Predictive Modeling Case Study · 页面正文；本次 HTML 提取正文第 37–37 行（不是 HTML 源码行号）](https://www.tidymodels.org/start/case-study/)。

### `r-13` 对时间序列形成未来预测

用 fable 建模、评估和组合预测方法，为未来期间提供估计。

**扩展／具名实现路线 · 有来源支持。** 需要 fable / tsibble 等依赖和合适时间序列；趋势变化会影响准确率，预测不构成保证。

来源：[s-fable：fable · Forecasting Models for Tidy Time Series · 页面正文；本次 HTML 提取正文第 12–12 行（不是 HTML 源码行号）](https://fable.tidyverts.org/)。

### `r-14` 分析地理空间对象与几何关系

用 sf 读写地理对象并调用相应几何运算，将位置数据纳入分析。

**扩展／具名实现路线 · 有来源支持。** 需要 sf、GDAL / GEOS / PROJ 或 s2；坐标系、平面／球面语义及驱动支持需核实。

来源：[s-spatial：Simple Features for R • sf · 页面正文；本次 HTML 提取正文第 22–22 行（不是 HTML 源码行号）](https://r-spatial.github.io/sf/)。

### `r-15` 探索和展示网络关系

用 igraph 将关系数据作为图结构分析和可视化，检查连接组织。

**扩展／具名实现路线 · 有来源支持。** 需要 igraph 和合理的节点／边定义；网页可能展示开发版，安装版本另核查。

来源：[s-network：Network Analysis and Visualization • igraph · 页面正文；本次 HTML 提取正文第 1–1 行（不是 HTML 源码行号）](https://r.igraph.org/)。

### `r-16` 比较文本语料的词汇、情绪和主题特征

按 tidytext 作者的公开案例处理文本、比较词频和表达模式。

**扩展／具名实现路线 · 有来源支持。** 需要 tidytext 及语料清洗、词典和语言适配；该旧 Twitter 案例不保证当前平台数据获取方法可用。

来源：[s-text-case：7 Case study: comparing Twitter archives | Text Mining with R · 页面正文；本次 HTML 提取正文第 21–21 行（不是 HTML 源码行号）](https://www.tidytextmining.com/twitter)。

### `r-19` 完成基因表达探索与差异分析

参考 Bioconductor rnaseqGene 从定量数据准备到探索、质量评估和差异表达结果。

**扩展／具名实现路线 · 有来源支持。** 需要对应 Bioconductor 版本、参考数据和分析包；该流程文档日期较早，命令兼容性未实测，不作为临床判断。

来源：[s-rnaseq：Bioconductor · RNA-seq Gene-level Workflow · 页面正文；本次 HTML 提取正文第 10–10 行（不是 HTML 源码行号）](https://bioconductor.org/packages/release/workflows/vignettes/rnaseqGene/inst/doc/rnaseqGene.html)。

<a id="delivery"></a>
## 交互探索与报告交付

### `r-20` 制作可交互的数据探索应用

用 Shiny 将分析结果与筛选控件、图表或表格组成浏览器应用。

**扩展／具名实现路线 · 有来源支持。** 需要 Shiny、相关前端组件及运行 R 的服务器／本机；不等于可直接脱离 R 运行的纯静态网页。

来源：[s-shiny：Shiny for R Gallery · Interactive visualizations；本次 HTML 提取正文第 31–31 行（不是 HTML 源码行号）](https://shiny.posit.co/r/gallery/)。

### `r-21` 把计算、图表和说明交付为研究报告

在 Quarto 中执行 R 代码，将结果和解释一起渲染为文档。

**扩展／具名实现路线 · 有来源支持。** 需要 Quarto、knitr 和对应输出格式依赖；PDF、Word 等额外工具与排版需检查。

来源：[s-quarto：Quarto · Using R · 页面正文；本次 HTML 提取正文第 246–246 行（不是 HTML 源码行号）](https://quarto.org/docs/computations/r.html)。

<a id="reproduction"></a>
## 维护可更新和可恢复的分析

### `r-22` 在数据变化后更新必要分析结果

用 targets 管理数据准备、模型和汇总依赖，只重算过期任务。

**扩展／具名实现路线 · 有来源支持。** 需要把任务写为 R 函数并正确声明依赖；不能发现所有隐藏外部状态。

来源：[s-targets：Dynamic Function-Oriented Make-Like Declarative Pipelines • targets · 页面正文；本次 HTML 提取正文第 13–13 行（不是 HTML 源码行号）](https://docs.ropensci.org/targets/)。

### `r-23` 在另一环境恢复分析所用包版本

用 renv 记录项目依赖和私有库，帮助复现分析环境。

**扩展／具名实现路线 · 有来源支持。** 需要可获取的软件包与兼容 R／系统依赖；锁文件不是完整操作系统或数据快照。

来源：[s-renv：Project Environments • renv · 页面正文；本次 HTML 提取正文第 27–27 行（不是 HTML 源码行号）](https://rstudio.github.io/renv/)。

## 资料覆盖与发现过程

先从输入、处理和可交付分析结果发现，再读酒店预测、Twitter 语料和 RNA-seq 的完整案例，最后补查部署、流水线与依赖复现。
归一化：把筛选、变量计算、排序和聚合合并为分析表整理；将统计模型按实际问题保留，而非罗列函数参数。
补漏发现 Excel、统计软件格式、复杂抽样与删失数据；最终挑战又补查航班与航空公司关联的完整示例，追加多来源表关联后再更新导航。
原三个主题的数据与分类未被读取作为本次候选来源；这里只引用当前取回的 R 官方及包作者资料。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未安装执行这些 R 项目；包版本、操作系统、编译器和数据规模的实际适配仍需验证。
- 部分官方站点显示开发版或较旧示例；R-devel 参考、survey 作者主页与旧生物信息流程不等于当前稳定环境测试。
- 未穷尽 CRAN / Bioconductor；贝叶斯、因果推断、优化、金融和并行计算等专门主题仍需独立证据研究。
- readr / haven 的读写格式边界与 Arrow / sf 的外部依赖均不能从“R 能分析”推导为无条件支持。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
