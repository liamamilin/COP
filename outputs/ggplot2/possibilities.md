# ggplot2 能实现哪些事情：有来源的可能性地图

调研日期：2026-11-05（Asia/Shanghai）。输出语言：中文。

R 中以 ggplot2 为基础的数据探索、统计表达、叙事与可复用图形生产；涵盖核心静态图、明确标注的扩展与集成，以及有原始证据的任务案例。

本轮保留 **74 项结果：39 项核心能力、35 项扩展或集成实现**，使用 75 个来源页面，整理为 11 个用途分组。数字只描述本轮交付，不是完整性或质量评分。

**如何读这份地图：** 每项是可以提出的结果需求，而非 API 名称。核心表示 ggplot2 提供相应图层或机制，仍可能调用 R 的统计或空间依赖；扩展表示本文所依据的实现需另装包或集成环境。同一结果可能还有其他实现路径。

**证据状态：** 所有条目均为 `source_supported`，没有自行标为 `reviewed`。逐字短摘录和原文位置保存在 [possibilities.json](possibilities.json) 的 `sources` 与逐项 `evidence_refs` 中；下文每项均直接链接原始出处。本文已阅读来源上下文，但未在本机运行 R 示例，也未接受独立人工评审。

**版本边界：** [ggplot2 官方站点](https://ggplot2.tidyverse.org/)当前标示 4.0.3。扩展文档可能对应开发版；版本记录见 JSON。核心不支持真正三维曲面，网页交互、动画和三维场景分别依靠额外工具。

## 可提出的需求示例

- “比较各组分布，并同时展示样本点、分布形状与摘要。” → 雨云式图，需 ggdist。
- “保留完整趋势计算，只把图放大到某段范围。” → 核心坐标缩放；需要同时保留总览则考虑 ggforce。
- “把几十个地区图分成多页，并自动更新同样风格的报告图片。” → 分面分页、参数化绘图与导出组合；文档编译和调度另行完成。
- “让网页读者悬浮看详情，选择图中对象。” → ggiraph 及相应 HTML / Shiny 环境。

## 用途导航

- [发现关系与追踪变化](#grp-relationships)（7 项）
- [比较类别与组成](#grp-comparison)（7 项）
- [理解分布与样本结构](#grp-distributions)（12 项）
- [表达统计摘要、趋势与不确定性](#grp-statistics)（7 项）
- [理解空间、网格与数值表面](#grp-spatial)（5 项）
- [探索多变量、网络与树](#grp-structure)（4 项）
- [解释分析与模型结果](#grp-models)（5 项）
- [解释、强调与改善可读性](#grp-communication)（13 项）
- [组织多图与总览细节](#grp-layout)（5 项）
- [制作动画、交互与日历成品](#grp-dynamic)（5 项）
- [导出、复用与定制生产](#grp-production)（4 项）

<a id="grp-relationships"></a>

## 发现关系与追踪变化

### 观察两个变量之间的关系、分组与异常点

**核心 · p-scatter · 来源支持**

得到散点图，用位置和分组颜色观察关联、聚集及偏离常见模式的观测。

**条件与边界：** 需要可比较的变量和观测行；相关图形不能自行证明因果关系，重叠严重时应聚合或改用密度表达。

**来源：** [Points and bubble charts](https://ggplot2.tidyverse.org/reference/geom_point.html)（Description / introductory paragraph）。

### 在二维关系图中同时展示第三个数量变量

**核心 · p-bubble · 来源支持**

得到气泡图，以点面积补充第三个变量，例如同时对比收入、寿命和人口。

**条件与边界：** 第三个变量需适合大小编码；面积比不易精确读取，不能把半径误当面积。

**来源：** [Points and bubble charts](https://ggplot2.tidyverse.org/reference/geom_point.html)（Description / introductory paragraph）。

### 追踪指标随时间或观测顺序的发展

**核心 · p-trend · 来源支持**

得到折线、阶梯或路径图，展示趋势、跳变发生的位置及按顺序经过的轨迹。

**条件与边界：** 时间值和分组必须正确；折线按 x 排序，路径按数据顺序连接，二者不可混用。

**来源：** [Connect observations](https://ggplot2.tidyverse.org/reference/geom_path.html)（Description / introductory paragraph）。

### 表达位置上的方向与距离或强度

**核心 · p-direction · 来源支持**

得到方向线段或向量场式图，展示每个位置的方向和长度信息。

**条件与边界：** 需提供起点、方向和长度；角度从东起逆时针，风向等领域惯例须先转换。

**来源：** [Direction and distance vectors](https://ggplot2.tidyverse.org/reference/geom_spoke.html)（Description / introductory paragraph）。

### 突出同一对象两次测量的差距

**扩展 / 集成 · p-paired · 来源支持**

得到哑铃式比较图，突出多个对象在起点和终点之间的变化幅度。

**条件与边界：** 所引 BBC 实现使用 ggalt 和 bbplot，并整理两次测量为同一行；2019 示例未在当前环境复现。该结果也可用核心点线自行组合，本文按证据中的实现标注。

**实际案例：** BBC 用 Gapminder 比较各国 1967 与 2007 年预期寿命差距。

**来源：** [BBC Visual and Data Journalism cookbook](https://bbc.github.io/rcookbook/)（Make a dumbbell chart / Gapminder 1967 and 2007）。

### 用端点和细线制作紧凑的成绩或排名比较图

**核心 · p-lollipop · 来源支持**

得到棒棒糖式图形，比较每个项目的数值，并可在相邻区域安排文字和记录说明。

**条件与边界：** 主体可由核心点和线段组合；所引 Mario Kart 成品另外使用 ggtext、自定义字体和 ragg 等美化或输出工具，完整成品不全是核心能力。

**实际案例：** Cédric Scherer 的 TidyTuesday Mario Kart 64 世界纪录图，附作者原始 R Markdown。

**来源：** [Cédric Scherer Mario Kart visualisation, authorised walkthrough](https://r-graph-gallery.com/web-lollipop-plot-with-r-mario-kart-64-world-records.html)（Introduction; About; complete R code）；[Original Mario Kart visualisation source by Cédric Scherer](https://github.com/z3tt/TidyTuesday/blob/main/R/2021_22_MarioKart.Rmd)（R Markdown YAML title; plot-building code）。

### 跟踪对象排名随时间的升降

**扩展 / 集成 · p-ranking · 来源支持**

得到排名变化图，突出各对象相对名次的上升、下降与交叉。

**条件与边界：** 需 ggbump，名次和并列规则需先确定；平滑连接不是两个时点之间的实际测量。

**来源：** [ggbump: rankings over time](https://github.com/davidsjoberg/ggbump)（README introduction; Bump chart examples）。


<a id="grp-comparison"></a>

## 比较类别与组成

### 比较不同类别的频数、数量或汇总值

**核心 · p-bars · 来源支持**

得到类别条形图，可比较原始观测计数，也可显示已经计算好的业务或实验指标。

**条件与边界：** 计数与已汇总数值采用不同统计方式；排序、缺失类别和零基线应有明确含义。

**来源：** [Bar charts](https://ggplot2.tidyverse.org/reference/geom_bar.html)（Description / introductory paragraph）。

### 比较不同群体的组成与占比

**核心 · p-composition · 来源支持**

得到堆叠或标准化的百分比条形图，查看整体由哪些部分构成及比例如何不同。

**条件与边界：** 需要类别及其分组或权重；百分比图隐藏总量差异，应另给分母或总量。

**来源：** [Stack and standardise bars](https://ggplot2.tidyverse.org/reference/position_stack.html)（Description / introductory paragraph）。

### 展示数量随连续横轴的变化及累积组成

**核心 · p-area · 来源支持**

得到面积图或堆叠面积图，呈现总量与组成随时间等连续变量的变化。

**条件与边界：** 通常以零为基线；需统一分组、顺序和横轴对齐方式，面积形状不适合精确比较中间系列。

**来源：** [Ribbons and area plots](https://ggplot2.tidyverse.org/reference/geom_ribbon.html)（Description / introductory paragraph）。

### 把组成数据表达为极坐标图

**核心 · p-polar · 来源支持**

把堆叠条形等图形转换为饼图或其他极坐标表达，用于圆周上的组成展示。

**条件与边界：** 极坐标图的角度和面积较难比较；精确比较通常优先条形图，不把装饰性当作准确性。

**来源：** [Polar coordinate graphics](https://ggplot2.tidyverse.org/reference/coord_polar.html)（Description / introductory paragraph）。

### 展示人群或对象在多个类别之间的组成流向

**扩展 / 集成 · p-alluvial · 来源支持**

得到冲积图，展示类别之间对应的人数、频数或群体构成。

**条件与边界：** 需 ggalluvial 和适合的数据框；流带表示给定群体的对应或频数，不会自动推断真实因果或个体转移。

**实际案例：** 包作者用 Titanic 乘客数据展示多维人口类别的组成。

**来源：** [ggalluvial: design and Titanic example](https://corybrunson.github.io/ggalluvial/)（Design; Usage / Titanic example）。

### 用嵌套面积展示层级组成与第二个指标

**扩展 / 集成 · p-treemap · 来源支持**

得到矩形树图，以矩形面积表示数量，以颜色或嵌套分组补充另一维信息。

**条件与边界：** 需 treemapify，面积值应适合非负的部分与整体比较；面积编码不适合精确读取。

**实际案例：** 包作者用 G20 数据把 GDP 映射为面积、HDI 映射为颜色，并演示区域分组。

**来源：** [treemapify: G20 treemap example](https://wilkox.org/treemapify/)（Drawing a simple treemap; Subgrouping）。

### 用等面积小格表达整体中的份额

**扩展 / 集成 · p-waffle · 来源支持**

得到华夫图，以固定单位的小格数量表现各部分占整体的比例或数量。

**条件与边界：** 所引实现需 waffle::geom_waffle；必须说明每格单位和舍入方式，核心也能手动排格但不自动完成此布局。

**来源：** [waffle: square-pie graphics](https://github.com/hrbrmstr/waffle)（README / geom_waffle; faceted examples）。


<a id="grp-distributions"></a>

## 理解分布与样本结构

### 查看数值数据的分布形状与集中区间

**核心 · p-histogram · 来源支持**

得到直方图或频率多边形，发现偏斜、多峰、稀疏区以及不同组分布的差异。

**条件与边界：** 需要连续或近似连续数值；分箱宽度会改变外观，不能只采用任意默认分箱作结论。

**来源：** [Histograms and frequency polygons](https://ggplot2.tidyverse.org/reference/geom_histogram.html)（Description / introductory paragraph）。

### 比较连续变量的平滑分布形状

**核心 · p-density · 来源支持**

得到核密度曲线，观察不同群体在哪些取值范围集中及尾部如何变化。

**条件与边界：** 带宽影响结果；密度不是逐点观测频数，小样本、离散值和边界需特别处理。

**来源：** [Smoothed density estimates](https://ggplot2.tidyverse.org/reference/geom_density.html)（Description / introductory paragraph）。

### 紧凑比较多组数据的中位数、离散程度与异常值

**核心 · p-boxplot · 来源支持**

得到并列箱线图，在有限空间内比较各组分布摘要及按规则识别的离群观测。

**条件与边界：** 箱线摘要会隐藏多峰与样本量；图中离群规则不等于证明记录有错。

**来源：** [Box and whiskers plots](https://ggplot2.tidyverse.org/reference/geom_boxplot.html)（Description / introductory paragraph）。

### 比较多组分布的形状而不只比较均值

**核心 · p-violin · 来源支持**

得到小提琴图，以对称密度形状展示每组数据在不同取值处的集中程度。

**条件与边界：** 分组样本量和带宽会影响形状；宜同时给样本量或原始点。

**来源：** [Violin plots](https://ggplot2.tidyverse.org/reference/geom_violin.html)（Description / introductory paragraph）。

### 读取达到某个阈值的样本比例

**核心 · p-ecdf · 来源支持**

得到经验累积分布图，可比较多少观测低于某值，以及各组整体分布如何移动。

**条件与边界：** 纵轴是累计比例，读者需理解其含义；无需选择直方图分箱或密度带宽。

**来源：** [Empirical cumulative distribution](https://ggplot2.tidyverse.org/reference/stat_ecdf.html)（Description / introductory paragraph）。

### 检查样本分布与理论分布的偏离

**核心 · p-qq · 来源支持**

得到分位数对比分布图和参考线，观察尾部、偏斜等对分布假设的偏离。

**条件与边界：** 必须选择适当的理论分布；视觉近似不能证明模型正确或代替其他诊断。

**来源：** [Quantile-quantile plots](https://ggplot2.tidyverse.org/reference/geom_qq.html)（Description / introductory paragraph）。

### 揭示离散或重复取值下被遮挡的观测

**核心 · p-overlap · 来源支持**

用轻微抖动分开小样本重叠点，或用点面积表示相同位置的观测数量。

**条件与边界：** 抖动位置不是实际测量值；需固定随机性以便复现，计数图则保留重复位置的计数。

**来源：** [Jittered observations](https://ggplot2.tidyverse.org/reference/geom_jitter.html)（Description / introductory paragraph）；[Count overlapping observations](https://ggplot2.tidyverse.org/reference/geom_count.html)（Description / introductory paragraph）。

### 辨认大量二维样本在哪些区域集中

**核心 · p-hexbin · 来源支持**

得到六边形分箱计数图，用颜色展示密集散点的位置与局部数量。

**条件与边界：** geom_hex 属于 ggplot2，但需要可用的 hexbin 依赖；分箱大小会改变局部结构。

**来源：** [Hexagonal bin counts](https://ggplot2.tidyverse.org/reference/geom_hex.html)（Description / introductory paragraph）。

亦可用于：发现关系与追踪变化。

### 比较二维数据的密集区域和分布轮廓

**核心 · p-density2d · 来源支持**

得到二维核密度等高线或填色密度带，以轮廓呈现聚集模式。

**条件与边界：** 使用 MASS::kde2d 等统计依赖；密度带宽和样本分布影响轮廓，不是地理边界。

**来源：** [Contours of two-dimensional density](https://ggplot2.tidyverse.org/reference/geom_density_2d.html)（Description / introductory paragraph）。

亦可用于：发现关系与追踪变化。

### 用数据椭圆比较二维分组的集中范围

**核心 · p-ellipse · 来源支持**

在散点图上叠加分组椭圆，观察各组二维分布的方向、尺度与重叠。

**条件与边界：** t、正态和欧氏类型的含义不同；数据椭圆不应被误读为均值的置信区域。

**来源：** [Data ellipses](https://ggplot2.tidyverse.org/reference/stat_ellipse.html)（Page heading; type and level arguments）。

亦可用于：发现关系与追踪变化。

### 比较很多组分布随时间或空间的变化

**扩展 / 集成 · p-ridge · 来源支持**

得到山脊图，以错层密度或曲线形状紧凑比较多组分布。

**条件与边界：** 需 ggridges；应明确带宽、归一化和重叠比例，避免把高度或面积误当样本量。

**来源：** [ggridges](https://wilkelab.org/ggridges/)（Description / introductory paragraph）。

### 同时比较样本点、分布形状与区间摘要

**扩展 / 集成 · p-raincloud · 来源支持**

得到雨云式组合图，在同一画面中同时展示个体观测、半密度和摘要。

**条件与边界：** 需 ggdist 及相应组合图层；各部分应基于相同数据和清楚的统计口径。

**来源：** [ggdist: uncertainty and distributions](https://mjskay.github.io/ggdist/)（Overview: dotsinterval and lineribbon families）。


<a id="grp-statistics"></a>

## 表达统计摘要、趋势与不确定性

### 比较估计值及其区间范围

**核心 · p-interval · 来源支持**

得到点区间、误差棒或线范围图，让读者同时看到中心值和不确定范围。

**条件与边界：** 需提供或计算上下限，并说明它是置信区间、标准差、标准误还是取值范围；绘制不会自动验证其含义。

**来源：** [Intervals, point ranges and error bars](https://ggplot2.tidyverse.org/reference/geom_linerange.html)（Description / introductory paragraph）。

### 沿连续横轴展示上下界与不确定范围

**核心 · p-band · 来源支持**

得到围绕曲线或时序的带状区域，展示测量范围、预测区间或上下限。

**条件与边界：** 需提供每个横轴位置的上下界；预测模型和区间计算可以来自其他工具。

**来源：** [Ribbons and area plots](https://ggplot2.tidyverse.org/reference/geom_ribbon.html)（Description / introductory paragraph）。

### 在噪声样本中显示趋势与拟合置信带

**核心 · p-smooth · 来源支持**

在原始样本上叠加平滑或回归曲线及置信带，便于观察整体变化模式。

**条件与边界：** 需选择合适的方法、公式和分组；置信带不是所有未来观测的预测区间，也不证明因果。

**来源：** [Smooth trends with confidence bands](https://ggplot2.tidyverse.org/reference/geom_smooth.html)（Page heading; se argument）。

### 观察变量关系在不同分位数上的差异

**核心 · p-quantile · 来源支持**

得到多条分位数回归曲线，比较下尾、中位数和上尾随解释变量如何变化。

**条件与边界：** 需 quantreg 等依赖并指定分位数和拟合方法；结果依赖模型假设。

**来源：** [Quantile regression](https://ggplot2.tidyverse.org/reference/geom_quantile.html)（Description / introductory paragraph）。

### 按分组或区间展示自定义统计摘要

**核心 · p-aggregate · 来源支持**

直接在图层中汇总均值、中位数或其他函数结果，并可返回中心值和上下界。

**条件与边界：** 需明确汇总函数和有效样本；默认摘要不能代替研究设计或错误数据清理。

**来源：** [Summary statistics by category or bins](https://ggplot2.tidyverse.org/reference/stat_summary.html)（Description / introductory paragraph）。

### 把数学函数或理论分布叠加到数据上

**核心 · p-theory · 来源支持**

得到函数曲线，可用于比较观测数据与理论形状，或讲解模型参数的影响。

**条件与边界：** 提供可在数值网格上求值的函数及参数；这只是绘制，不自动拟合或检验理论。

**来源：** [Draw a mathematical function](https://ggplot2.tidyverse.org/reference/geom_function.html)（Description / introductory paragraph）。

### 展示拟合曲线的多层不确定带

**扩展 / 集成 · p-multiband · 来源支持**

沿拟合线显示多种覆盖水平的区间带，表达不确定性的层次而不只给单一误差带。

**条件与边界：** 需 ggdist；需要抽样、分布对象或合法的区间数据，并说明是置信还是后验等不确定性。

**来源：** [ggdist: uncertainty and distributions](https://mjskay.github.io/ggdist/)（Overview: dotsinterval and lineribbon families）。

亦可用于：解释分析与模型结果。


<a id="grp-spatial"></a>

## 理解空间、网格与数值表面

### 把三变量形成的数值表面表达为二维等高图

**核心 · p-surface · 来源支持**

得到等值线或填色等值带，例如展示空间位置上的高度、温度或响应值变化。

**条件与边界：** 需要规则的 x-y 网格和 z 值；不规则数据须先外部插值，核心包不绘制真正三维曲面。

**来源：** [Display a surface in two dimensions](https://ggplot2.tidyverse.org/reference/geom_contour.html)（Description / introductory paragraph）。

### 把矩阵或二维网格数值转换为颜色热图

**核心 · p-heatmap · 来源支持**

得到按行列或空间格点排布的色块图，用颜色辨认高低值、周期与局部模式。

**条件与边界：** 矩阵需整理成坐标和值；相关系数、聚类、标准化或缺失值判定需另行计算。

**来源：** [Tile and raster heatmaps](https://ggplot2.tidyverse.org/reference/geom_tile.html)（Examples: df grid with fill = z）。

### 绘制带数据编码的点、线和区域地图

**核心 · p-map · 来源支持**

将 sf 空间对象及其属性绘制成地图，可叠加观测点、道路或区域填色。

**条件与边界：** 需要 sf 及空间数据依赖，并确保坐标参考系、区域关联和统计口径正确；绘图不自动取得地图数据。

**来源：** [Visualise simple-feature geographic objects](https://ggplot2.tidyverse.org/reference/ggsf.html)（Description / introductory paragraph）。

### 为专题地图补充底图、比例尺与指北信息

**扩展 / 集成 · p-cartography · 来源支持**

在数据地图上加入背景瓦片、空间比例尺和指北针，提供地理阅读背景。

**条件与边界：** 需 ggspatial 和 sf 等依赖；在线瓦片需要网络并遵守提供方的使用及署名要求，投影须匹配。

**实际案例：** ggspatial 的 Long Lake 示例叠加道路、水深、底图、比例尺与指北针。

**来源：** [ggspatial: cartographic additions](https://paleolimbot.github.io/ggspatial/)（Introduction / Long Lake example code comments）；[ggspatial: background map tiles](https://paleolimbot.github.io/ggspatial/reference/annotation_map_tile.html)（Description; attribution requirement）。

亦可用于：解释、强调与改善可读性。

### 把二维图中的颜色或填充值转换为三维高度

**扩展 / 集成 · p-3d · 来源支持**

通过 rayshader 把兼容的 ggplot 图形挤出为三维场景，例如把密度颜色转换为高度。

**条件与边界：** 需 rayshader、rgl 等三维渲染依赖；不是 ggplot2 原生三维，也不是任意三维数据绘制；文档明确不支持把映射为颜色的线条转换为三维。

**来源：** [rayshader: transform ggplots into 3D](https://www.rayshader.com/reference/plot_gg.html)（Description; restrictions; density examples）。

亦可用于：解释、强调与改善可读性。


<a id="grp-structure"></a>

## 探索多变量、网络与树

### 一次检查多个变量之间的两两关系

**扩展 / 集成 · p-pairs · 来源支持**

得到包含散点、分布和相关摘要的图形矩阵，用来筛查多变量的关系结构。

**条件与边界：** 需 GGally::ggpairs；变量数过多会产生过大的矩阵，相关摘要仍需核对变量类型。

**来源：** [GGally pairwise plot matrix](https://ggobi.github.io/ggally/reference/ggpairs.html)（Description / introductory paragraph）。

### 比较每个对象跨多个指标的整体轮廓

**扩展 / 集成 · p-parallel · 来源支持**

得到平行坐标图，以每条线连接同一个对象在多个变量轴上的取值。

**条件与边界：** 需 GGally；变量尺度、排序、缺失处理和标准化会显著影响模式。

**来源：** [GGally parallel coordinates](https://ggobi.github.io/ggally/reference/ggparcoord.html)（Description / introductory paragraph）。

### 绘制关系网络与层级结构

**扩展 / 集成 · p-network · 来源支持**

得到节点和连接边组成的网络图，或按树状、圆形等布局显示关系结构。

**条件与边界：** 需 ggraph，通常配合 tidygraph 或 igraph；节点位置依赖布局算法，不天然等于距离或因果强度。

**实际案例：** ggraph 官方示例绘制高中友谊网络，并把入度作为节点大小。

**来源：** [ggraph: high-school friendship network](https://ggraph.data-imaginist.com/)（Introduction; An example）。

### 绘制可整合关联数据的系统发育树

**扩展 / 集成 · p-phylogeny · 来源支持**

得到系统发育树视图，可选择布局，并继续使用配套工具加入分支或外部数据注释。

**条件与边界：** 需 Bioconductor 的 ggtree 及兼容的树数据、R 和包版本；构建或估计系统发育树是前置分析。

**来源：** [ggtree author book: phylogenetic tree visualisation](https://yulab-smu.top/treedata-book/chapter4.html)（4.1 Introduction; tree layouts）。


<a id="grp-models"></a>

## 解释分析与模型结果

### 把主成分分析结果转换为可解释的样本图

**扩展 / 集成 · p-pca · 来源支持**

展示 PCA 得分、类别差异和可选的载荷向量，以观察降维后的结构。

**条件与边界：** 需 ggfortify 和预先计算的 prcomp 或 princomp 对象；所引作者论文为 2016 年，当前组合需复现确认。

**实际案例：** ggfortify 作者在 The R Journal 用 iris 展示按物种着色及带载荷的 PCA。

**来源：** [ggfortify author paper in The R Journal](https://journal.r-project.org/articles/RJ-2016-060/)（3.1 Principal components analysis / Figure 1）。

### 把模型假设检查结果转换为诊断图

**扩展 / 集成 · p-model-diagnostics · 来源支持**

展示残差等模型诊断结果，帮助检查正态性和其他适用的模型假设。

**条件与边界：** 需 see 和 easystats 中相应分析包，如 performance；支持的诊断依模型类型而异，图形不自动判定模型可用。

**来源：** [see: model visualisation toolbox](https://easystats.github.io/see/)（Introduction; parameters; performance）。

### 把模型参数与预测摘要整理为可比较图形

**扩展 / 集成 · p-model-results · 来源支持**

把模型参数、预测或不确定区间变成点须等图形，便于比较效应方向与大小。

**条件与边界：** 需 see 及 parameters、modelbased 等对应的 easystats 包；必须解释估计对象、变换和区间口径。

**来源：** [see: model visualisation toolbox](https://easystats.github.io/see/)（Introduction; parameters; performance）。

### 把生存分析结果与风险人数同时展示

**扩展 / 集成 · p-survival · 来源支持**

得到生存曲线及风险人数表，也可显示事件和删失数量等辅助信息。

**条件与边界：** 需 survminer 与适当的 survival 拟合结果；删失规则、组间可比性和检验选择属于分析前提。

**来源：** [survminer: survival curves](https://rpkgs.datanovia.com/survminer/)（Survival Curves / ggsurvplot）。

### 把统计检验和效应量放进对应图表

**扩展 / 集成 · p-statistical-report · 来源支持**

得到同时包含数据分布、检验结果以及支持的效应量或区间的统计图。

**条件与边界：** 需 ggstatsplot 及统计依赖；检验类型、研究设计、样本假设和多重比较仍需人工选择与核对。

**来源：** [ggstatsplot: graphics with statistical details](https://cran.r-project.org/web/packages/ggstatsplot/readme/README.html)（Introduction; Statistical reporting）。


<a id="grp-communication"></a>

## 解释、强调与改善可读性

### 在跨数量级或逆序的数据中保留可读的轴

**核心 · p-transformed · 来源支持**

得到对数、平方根或反向坐标轴，以合适尺度显示跨度很大或方向有特定含义的数据。

**条件与边界：** 对数变换要求适用的值域；坐标变换会影响统计及视觉解释，不应隐藏变换。

**来源：** [Transformed numeric axes](https://ggplot2.tidyverse.org/reference/scale_continuous.html)（Description / introductory paragraph）。

### 放大局部图形而保留完整数据的统计结果

**核心 · p-zoom · 来源支持**

得到局部放大的静态视图，同时避免因为删去轴范围外数据而重新改变平滑或汇总。

**条件与边界：** 使用坐标范围作视觉缩放；它与改变 scale limits 导致数据被排除的行为不同。

**来源：** [Zoom without discarding observations](https://ggplot2.tidyverse.org/reference/coord_cartesian.html)（Examples: coordinate limits versus scale limits）。

### 直接在图内解释关键发现、阈值与事件

**核心 · p-annotate · 来源支持**

把文字、连线或几何注释放到相关位置，使图表能够说明关键点和背景。

**条件与边界：** 注释内容及定位由作者提供；多面板、裁剪和文本碰撞需要检查。

**来源：** [Add plot annotations](https://ggplot2.tidyverse.org/reference/annotate.html)（Description / introductory paragraph）；[Line segments and curves](https://ggplot2.tidyverse.org/reference/geom_segment.html)（Description / introductory paragraph）；[Plot metadata and alternative text](https://ggplot2.tidyverse.org/reference/labs.html)（Description; alt / alt_insight arguments）。

### 为一组图表建立一致的出版或品牌风格

**核心 · p-style · 来源支持**

统一字体、背景、网格、图例和间距，使不同图表呈现一致的视觉规范。

**条件与边界：** 主题控制非数据元素；数据配色和字体安装仍需单独配置，组织规范也需作者制定。

**来源：** [Consistent graphical style](https://ggplot2.tidyverse.org/reference/theme.html)（Description / introductory paragraph）。

### 使用兼顾常见色觉差异的颜色编码

**核心 · p-accessible · 来源支持**

用 viridis 系列颜色表达分类或连续数值，减少常见色觉差异造成的阅读障碍。

**条件与边界：** 配色不能保证整图可访问性；仍要检查对比、文字、形状和导出效果。

**来源：** [Colour scales for colour-vision accessibility](https://ggplot2.tidyverse.org/reference/scale_viridis.html)（Description / introductory paragraph）。

### 为图表保存可被报告系统读取的替代文字

**核心 · p-alt · 来源支持**

在图对象中提供替代描述与要点，供支持的输出或报告系统读取使用。

**条件与边界：** 需要作者编写或审核描述；并非所有图片格式或宿主都会自动嵌入和展示这些文字。

**来源：** [Plot metadata and alternative text](https://ggplot2.tidyverse.org/reference/labs.html)（Description; alt / alt_insight arguments）。

### 在同一数值轴上同时显示可换算的两套单位

**核心 · p-units · 来源支持**

在主轴对面增加对应的第二套单位或刻度，例如摄氏与华氏温度。

**条件与边界：** 副轴必须是主轴的一一变换；不能直接借此绘制两套无关、任意缩放的数据轴。

**来源：** [Secondary axes for transformed units](https://ggplot2.tidyverse.org/reference/sec_axis.html)（Description / introductory paragraph）。

### 自动减少数据标签之间的遮挡

**扩展 / 集成 · p-repel · 来源支持**

在点或其他对象附近放置相互避让的标签，并可用连线保留对应关系。

**条件与边界：** 需 ggrepel；非常拥挤时可能无法显示全部标签，应检查迭代、随机种子与标签省略。

**来源：** [ggrepel: label placement](https://ggrepel.slowkow.com/)（Overview）。

### 用富文本标题和说明表达重点

**扩展 / 集成 · p-richtext · 来源支持**

在标题、轴、图例或文本框中混合强调、颜色、上下标和可换行文字。

**条件与边界：** 需 ggtext 与 gridtext；只支持有限的 Markdown/HTML/CSS 子集，不是完整网页排版引擎。

**来源：** [ggtext: Markdown and HTML text](https://wilkelab.org/ggtext/)（Introduction; limited supported subset）。

### 在许多系列中突出满足条件的对象

**扩展 / 集成 · p-highlight · 来源支持**

在保留背景系列的同时强调达到阈值或规则的曲线和观测。

**条件与边界：** 需 gghighlight；强调条件由作者指定，不能把突出显示解释为统计显著。

**来源：** [gghighlight: focus on selected series](https://yutannihilation.github.io/gghighlight/)（Example）。

### 用纹理或图案区分图中的填充区域

**扩展 / 集成 · p-patterns · 来源支持**

为条形、区域、地图等图形增加条纹、几何或图像图案，补充颜色编码。

**条件与边界：** 需 ggpattern 及其图形依赖；密集纹理、设备和缩小印刷后的可读性需要检查。

**来源：** [ggpattern: pattern-filled graphics](https://coolbutuseless.github.io/package/ggpattern/)（Introduction; Quickstart）。

### 在不同图层中独立编码不同含义的颜色

**扩展 / 集成 · p-multiple-scales · 来源支持**

使一张图的不同图层使用独立的颜色或填充尺度与图例，而非被迫共享同一映射。

**条件与边界：** 需 ggnewscale；多个图例要清楚说明各自含义，过多尺度会增加阅读负担。

**来源：** [ggnewscale: multiple scales](https://eliocamp.github.io/ggnewscale/)（Introduction）。

### 用文字大小展示词项的频数或权重

**扩展 / 集成 · p-wordcloud · 来源支持**

得到可旋转、分面或按形状布局的词云，以文字大小表达给定的词项权重。

**条件与边界：** 需 ggwordcloud；分词、清洗和权重计算另行完成，布局可能省略放不下的词，不适合精确比较。

**来源：** [ggwordcloud](https://lepennec.github.io/ggwordcloud/)（Introduction; love_words examples）。


<a id="grp-layout"></a>

## 组织多图与总览细节

### 用同一规则并列比较不同群体或条件

**核心 · p-facets · 来源支持**

得到一组小多图，可按单一分组换行，也可按两个分类变量构成行列矩阵。

**条件与边界：** 各面板共享图层结构；需明确固定还是自由坐标尺度，分面不是任意独立图的拼版。

**来源：** [Facets by two grouping variables](https://ggplot2.tidyverse.org/reference/facet_grid.html)（Description / introductory paragraph）；[Wrap small multiples](https://ggplot2.tidyverse.org/reference/facet_wrap.html)（Description / introductory paragraph）。

亦可用于：探索多变量、网络与树。

### 把多幅独立图组合成同一叙事版面

**扩展 / 集成 · p-compose · 来源支持**

得到对齐、嵌套的多图组合，可把不同图形用于解释同一个问题。

**条件与边界：** 需 patchwork；不同于核心分面，子图可以拥有各自的数据、图层和坐标。

**来源：** [patchwork: assemble separate plots](https://patchwork.data-imaginist.com/)（Description / introductory paragraph）。

### 在主图中嵌入补充图或局部图

**扩展 / 集成 · p-inset · 来源支持**

把另一幅图放入主图的指定区域，展示补充背景、总览或局部细节。

**条件与边界：** 需 patchwork 的 inset 布局；插图位置、裁剪、比例和图例遮挡须检查。

**来源：** [patchwork: controlling layouts / Insets](https://patchwork.data-imaginist.com/articles/guides/layout.html)（Insets）。

### 在展示局部放大的同时保留整体背景

**扩展 / 集成 · p-contextzoom · 来源支持**

得到总览与局部放大并列的图形，并在总览中标明放大的范围。

**条件与边界：** 需 ggforce::facet_zoom；这是静态的总览与细节布局，不是鼠标交互缩放。

**来源：** [ggforce: zoom with context](https://ggforce.data-imaginist.com/reference/facet_zoom.html)（Description / introductory paragraph）。

### 把大量分面分成可阅读的多页图

**扩展 / 集成 · p-paginate · 来源支持**

按设定的行列数把分组图拆成多页，适合逐地区、逐对象的审阅或报告。

**条件与边界：** 需 ggforce；页码和输出循环由调用者控制，合成报告另需文档工具。

**来源：** [ggforce: paginate facets](https://ggforce.data-imaginist.com/reference/facet_wrap_paginate.html)（Description / introductory paragraph）。


<a id="grp-dynamic"></a>

## 制作动画、交互与日历成品

### 把图形随时间或状态的变化制作成动画

**扩展 / 集成 · p-animation · 来源支持**

得到随时间或状态过渡的动画图，可呈现各阶段变化并保持对象之间的对应。

**条件与边界：** 需 gganimate；输出 GIF 或视频还需要合适渲染器，插帧是表现方式而非新增观测。

**实际案例：** gganimate 官方示例让汽车油耗箱线图随变速挡位状态切换。

**来源：** [gganimate: animated graphics](https://gganimate.com/)（Introduction; boxplot transition example）。

### 让读者悬浮查看详情并点击图中对象

**扩展 / 集成 · p-svg-interaction · 来源支持**

得到带提示、悬浮效果和点击动作的 SVG 网页图；配合 Shiny 可把选中元素回传应用。

**条件与边界：** 需 ggiraph 的交互图层和支持 HTML/JavaScript 的输出环境；Shiny 联动另需应用逻辑，静态图片不会保留这些交互。

**来源：** [ggiraph: interactive SVG graphics](https://davidgohel.github.io/ggiraph/)（Overview; Why use ggiraph; Usage）。

亦可用于：导出、复用与定制生产。

### 把支持的静态图转换成可缩放的网页图

**扩展 / 集成 · p-plotly · 来源支持**

通过 ggplotly 转换为可缩放、平移和切换系列显示的浏览器图形。

**条件与边界：** 需 plotly 及 HTML/JavaScript 环境；转换并不保证所有 ggplot2 或扩展图层完整还原，应对目标图逐项检查。

**来源：** [Plotly official ggplot2 integration guide](https://plotly.com/ggplot2/getting-started/)（Initialization; ggplotly conversion explanation）。

### 在日历上寻找日度数值的周期与异常

**扩展 / 集成 · p-calendar-heat · 来源支持**

把每天的数值映射到月历或年历中的颜色，从星期和月份位置观察日度模式。

**条件与边界：** 所引实现需 calendR；需正确日期序列、缺失值及本地化设置，部分双颜色功能在文档中限定 GitHub 版。

**来源：** [calendR: printable calendars and daily heatmaps](https://github.com/R-CoderDotCom/calendR)（README introduction; Calendar heatmap (Gradient)）。

亦可用于：理解空间、网格与数值表面。

### 生成可打印并标注日期事件的月历或年历

**扩展 / 集成 · p-calendar-print · 来源支持**

生成按月或按年排列的日历，可用于规划、标记指定日期与呈现活动安排。

**条件与边界：** 需 calendR；文字、事件与语言环境由调用者提供，具体字体和打印尺寸需要检查。

**来源：** [calendR: printable calendars and daily heatmaps](https://github.com/R-CoderDotCom/calendR)（README introduction; Calendar heatmap (Gradient)）。


<a id="grp-production"></a>

## 导出、复用与定制生产

### 导出用于论文、印刷或网页的图形文件

**核心 · p-export · 来源支持**

保存 PDF、SVG、PNG、TIFF 等文件，并控制版面尺寸与位图分辨率。

**条件与边界：** 具体格式依赖可用的图形设备和字体；部分设备需额外包，保存后仍应检查渲染。

**来源：** [Export graphic files](https://ggplot2.tidyverse.org/reference/ggsave.html)（device argument; width, height, units and dpi arguments）。

### 用同一个图形模板批量生成可更新的图表

**核心 · p-automate · 来源支持**

把绘图逻辑封装为 R 函数，数据或参数变化后可重复生成一组一致的图表。

**条件与边界：** 需要编写 R 函数并提供数据；数据获取、调度、报告编译和自动部署由外部工作流负责。

**来源：** [Programming with ggplot2](https://ggplot2-book.org/programming.html)（Introduction; 18.4 Plot functions）。

### 为特殊数据设计可复用的新图层或统计图形

**核心 · p-extend · 来源支持**

编写自己的几何图层、统计变换或主题，使团队能重复绘制领域特定图形。

**条件与边界：** 这里指核心包提供的扩展机制；需要开发 R 代码、理解 ggproto 并测试，不是现成的一键图表。

**来源：** [Official ggplot2 extension mechanism](https://ggplot2.tidyverse.org/articles/extending-ggplot2.html)（Introduction）。

### 缩小密集图形文件而保留清晰的矢量文字

**扩展 / 集成 · p-rasterize · 来源支持**

只把大量点等指定图层转成栅格，同时保留标签和其他元素为矢量。

**条件与边界：** 需 ggrastr 和相应输出设备；被栅格化层的质量取决于分辨率，不保证任意大数据都能快速绘制。

**来源：** [ggrastr: rasterise dense plot layers](https://github.com/VPetukhov/ggrastr)（README introduction）。

## 资料覆盖与缺口

来源包括官方概览与参考页、作者书籍及指南、扩展作者维护的文档 / 仓库、作者论文、BBC 数据新闻食谱和经作者授权的案例及其原始代码。扩展目录用于发现线索，具体能力回到原作者文档核对。

官方作者书籍第三版仍在编写；带有草稿提示的章节仅作补充，不据此保证所有旧代码兼容当前版本。

- 这是一次尽量广泛的来源调研，不是穷举，也没有建立独立人工关键能力基准，因此不报告覆盖率或宣称完整。
- 没有在本机安装 R、ggplot2 或扩展包并执行示例；source_supported 表示原始来源明确支持该结果，不表示已在本机实测。
- ggplot2 官网当前显示 4.0.3。扩展站点可能展示开发版；未统一锁定全部包版本、操作系统、字体和设备。较旧 BBC / ggfortify 案例应在实际采用时复现。
- 未系统调查全部领域生态：基因组轨道、单细胞、临床专用图、空间统计、金融 K 线、复杂时间序列、体育场地和工程专用图仍有未覆盖扩展。
- 研究发现的扩展并非互斥实现或推荐排行榜；同一结果可能由核心图层手工实现或由多个不同扩展完成。availability 按本文有证据的实现路径标注，条件中指出已知替代路径。
- 没有把数据采集、清洗、任意模型训练、GIS 分析、文本挖掘、因果推断、网站开发或任务调度归给 ggplot2。图形可接收这些过程的结果。
- HTML 交互、三维、动画和地图瓦片都有额外环境或服务要求；兼容性、可访问性、性能和设备渲染需要在真实交付中复核。
- 官方扩展目录部分条目有陈旧接口；本文回到扩展作者文档核对，没有直接采用目录中的旧 gganimate frame / gg_animate 用法。
- 人工独立评审、实际用户新增选择价值和对学习效果的验证尚未进行；没有任何条目标为 reviewed。

## 先发现、后分类的过程记录

1. 先读取官方概览、参考索引、作者书籍和扩展目录，确定研究边界。
2. 结果视角：从官方说明提取可观察的用户结果，先不分类。
3. 案例视角：核对 BBC、作者代码、R Journal 和各扩展官方案例的成品与数据任务。
4. 扩展视角：回到扩展作者文档，确认可新增的结果和额外依赖。
5. 缺口复查：检查地图、模型、动画、交互、三维、日历、生产输出等未充分覆盖的意图。
6. 规范化和合并重复：抖动与重复计数合为遮挡处理；分面两种布局合为小多图；没有把每个参数独立当能力。
7. 候选稳定后按用户目的建立分类，允许交叉标签，最后核对证据和扩展边界。

**停止依据：** 后续查阅主要重复已有结果或提供不同实现；保留可明确说明的数据结果，未将缺少直接证据的想法扩充为已确认条目。

## 校验方式与实际结果

**实际结果：通过。** 结构与逐项证据引用校验通过；技能测试 **14 / 14** 通过；另外只读抓取 **75 / 75** 个来源页面，全部摘录与其文本匹配（解码 HTML 并规范化 Unicode / 空白后）。详情见 [validation-report.txt](validation-report.txt)。校验只检查结构、唯一 ID、分类与来源引用、逐项摘录匹配及来源抓取核对；它不会证明任何统计结论正确，也不替代独立人工审核。

```sh
python3 .agents/skills/p-discovery/scripts/validate.py outputs/ggplot2/possibilities.json
python3 -m unittest discover -s .agents/skills/p-discovery/tests -v
```
