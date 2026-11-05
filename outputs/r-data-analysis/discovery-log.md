# R 数据分析 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `r-01`｜结果视角｜把文本表格读成可分析数据｜s-import
2. `r-02`｜结果视角｜分析 Excel 工作表中的表格｜s-excel
3. `r-03`｜结果视角｜与其他统计软件交换数据｜s-haven
4. `r-04`｜结果视角｜清洗记录并计算分组汇总｜s-transform
5. `r-05`｜结果视角｜把宽表、嵌套数据和混合字段整理成规则表｜s-reshape
6. `r-06`｜结果视角｜直接分析数据库中的数据｜s-database
7. `r-07`｜结果视角｜处理多文件或超出内存的数据集｜s-arrow
8. `r-08`｜结果视角｜比较样本均值及其不确定性｜s-test
9. `r-09`｜结果视角｜用回归解释连续结果与变量关系｜s-lm
10. `r-10`｜结果视角｜对不同分布的结果建立统计模型｜s-glm
11. `r-11`｜结果视角｜从对象相似性中寻找层次结构｜s-cluster
12. `r-12`｜完整案例视角｜开发并评估可用于新数据的预测模型｜s-model-case
13. `r-13`｜结果视角｜对时间序列形成未来预测｜s-fable
14. `r-14`｜结果视角｜分析地理空间对象与几何关系｜s-spatial
15. `r-15`｜结果视角｜探索和展示网络关系｜s-network
16. `r-16`｜完整案例视角｜比较文本语料的词汇、情绪和主题特征｜s-text-case
17. `r-17`｜结果视角｜分析事件发生时间及删失数据｜s-survival
18. `r-18`｜结果视角｜根据复杂抽样设计估计总体指标｜s-survey
19. `r-19`｜完整案例视角｜完成基因表达探索与差异分析｜s-rnaseq
20. `r-20`｜结果视角｜制作可交互的数据探索应用｜s-shiny
21. `r-21`｜结果视角｜把计算、图表和说明交付为研究报告｜s-quarto
22. `r-22`｜结果视角｜在数据变化后更新必要分析结果｜s-targets
23. `r-23`｜结果视角｜在另一环境恢复分析所用包版本｜s-renv
24. `r-24`｜结果视角｜用随机模拟研究假设与不确定性｜s-simulate
25. `r-25`｜结果视角｜用散点图检查变量关系｜s-graphics
26. `r-26`｜补漏视角｜将多个来源的数据按键关联或比较｜s-joins

## 归一化、补漏与停止依据

先从输入、处理和可交付分析结果发现，再读酒店预测、Twitter 语料和 RNA-seq 的完整案例，最后补查部署、流水线与依赖复现。
归一化：把筛选、变量计算、排序和聚合合并为分析表整理；将统计模型按实际问题保留，而非罗列函数参数。
补漏发现 Excel、统计软件格式、复杂抽样与删失数据；最终挑战又补查航班与航空公司关联的完整示例，追加多来源表关联后再更新导航。
原三个主题的数据与分类未被读取作为本次候选来源；这里只引用当前取回的 R 官方及包作者资料。

## 保留的未知项

- 未安装执行这些 R 项目；包版本、操作系统、编译器和数据规模的实际适配仍需验证。
- 部分官方站点显示开发版或较旧示例；R-devel 参考、survey 作者主页与旧生物信息流程不等于当前稳定环境测试。
- 未穷尽 CRAN / Bioconductor；贝叶斯、因果推断、优化、金融和并行计算等专门主题仍需独立证据研究。
- readr / haven 的读写格式边界与 Arrow / sf 的外部依赖均不能从“R 能分析”推导为无条件支持。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-arrow](https://arrow.apache.org/docs/r/) | 2026-11-05T09:39:40.694149+00:00 | 是 |
| [s-bioc](https://bioconductor.org/help/workflows/) | 2026-11-05T09:39:45.829083+00:00 | 否 |
| [s-cluster](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/hclust.html) | 2026-11-05T09:47:10.276044+00:00 | 是 |
| [s-database](https://dbplyr.tidyverse.org/) | 2026-11-05T09:39:40.162826+00:00 | 是 |
| [s-excel](https://readxl.tidyverse.org/) | 2026-11-05T09:47:11.798622+00:00 | 是 |
| [s-fable](https://fable.tidyverts.org/) | 2026-11-05T09:40:51.463529+00:00 | 是 |
| [s-glm](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/glm.html) | 2026-11-05T09:47:10.741029+00:00 | 是 |
| [s-graphics](https://stat.ethz.ch/R-manual/R-devel/library/graphics/html/plot.default.html) | 2026-11-05T09:47:10.028195+00:00 | 是 |
| [s-haven](https://haven.tidyverse.org/) | 2026-11-05T09:47:11.681844+00:00 | 是 |
| [s-import](https://readr.tidyverse.org/) | 2026-11-05T09:39:40.206806+00:00 | 是 |
| [s-intro](https://cran.r-project.org/doc/manuals/r-release/R-intro.html) | 2026-11-05T09:39:53.407489+00:00 | 否 |
| [s-joins](https://dplyr.tidyverse.org/articles/two-table.html) | 2026-11-05T10:01:26.534258+00:00 | 是 |
| [s-lm](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/lm.html) | 2026-11-05T09:47:10.488382+00:00 | 是 |
| [s-model-case](https://www.tidymodels.org/start/case-study/) | 2026-11-05T09:40:51.972966+00:00 | 是 |
| [s-models](https://www.tidymodels.org/start/) | 2026-11-05T09:39:41.865847+00:00 | 否 |
| [s-network](https://r.igraph.org/) | 2026-11-05T09:39:42.586643+00:00 | 是 |
| [s-quarto](https://quarto.org/docs/computations/r.html) | 2026-11-05T09:39:44.317306+00:00 | 是 |
| [s-renv](https://rstudio.github.io/renv/) | 2026-11-05T09:39:44.265832+00:00 | 是 |
| [s-reshape](https://tidyr.tidyverse.org/) | 2026-11-05T09:39:40.115575+00:00 | 是 |
| [s-rnaseq](https://bioconductor.org/packages/release/workflows/vignettes/rnaseqGene/inst/doc/rnaseqGene.html) | 2026-11-05T09:48:34.646513+00:00 | 是 |
| [s-shiny](https://shiny.posit.co/r/gallery/) | 2026-11-05T09:39:44.058393+00:00 | 是 |
| [s-simulate](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/Distributions.html) | 2026-11-05T09:47:10.021763+00:00 | 是 |
| [s-spatial](https://r-spatial.github.io/sf/) | 2026-11-05T09:39:42.041153+00:00 | 是 |
| [s-survey](https://r-survey.r-forge.r-project.org/survey/) | 2026-11-05T09:39:46.618380+00:00 | 是 |
| [s-survival](https://cran.r-project.org/web/packages/survival/index.html) | 2026-11-05T09:39:52.816468+00:00 | 是 |
| [s-targets](https://docs.ropensci.org/targets/) | 2026-11-05T09:39:44.323347+00:00 | 是 |
| [s-test](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/t.test.html) | 2026-11-05T09:47:10.015598+00:00 | 是 |
| [s-text-case](https://www.tidytextmining.com/twitter) | 2026-11-05T09:40:52.454124+00:00 | 是 |
| [s-text](https://www.tidytextmining.com/) | 2026-11-05T09:39:42.546968+00:00 | 否 |
| [s-transform](https://dplyr.tidyverse.org/) | 2026-11-05T09:39:40.123754+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`r-01`、`r-20`、`r-24`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
