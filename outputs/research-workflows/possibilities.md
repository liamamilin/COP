# 研究工作流 可能性地图

范围：文献与资料研究的可追踪任务：检索、收集、阅读、筛选、提取、综合、计量、写作与可复现记录；每项由具名工具、标准或公开项目实现。

资料截点：2026-11-05。本图有 26 项来源支持的结果，来自 22 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

这是方法与工具组合的地图，没有单一产品内置能力，所有 P 标 extension 并给出具体路线。研究者负责问题定义、来源质量、纳排、推断、权利和最终核验。

## 地图导航

- [形成问题与发现材料](#discovery)
- [积累和整理来源资料](#library)
- [筛选与提取研究证据](#evidence)
- [综合与探索研究全貌](#synthesis)
- [写作与交付研究报告](#writing)
- [保留可重查的研究记录](#transparency)

<a id="discovery"></a>
## 形成问题与发现材料

### `research-01` 把研究问题整理为可执行的综述方案

借助 Elicit 对问题、检索策略和筛选标准提出建议，形成待研究者确认的方案。

**扩展／具名实现路线 · 有来源支持。** 需要服务权限、领域知识与人工确认；工具建议不自动构成方法学合格方案。

来源：[s-elicit：Systematic Literature Reviews | Elicit: AI for research & decision-making · 页面正文；本次 HTML 提取正文第 66–66 行（不是 HTML 源码行号）](https://elicit.com/solutions/systematic-review)。

### `research-02` 找到使用不同表达的相关论文

用 OpenAlex 的标题、摘要和关键词联合检索，拓展单一字面词检索遗漏的材料。

**扩展／具名实现路线 · 有来源支持。** 需要适合的检索词和数据库访问；覆盖、排序和关键词不保证完整相关性。

来源：[s-paper-search：Finding papers with keywords · Finding papers with keywords；取回 Markdown第 3–3 行](https://help.openalex.org/how-to/finding-papers-with-keywords.md)。

### `research-03` 沿前向与后向引文扩展文献集合

追踪一篇或一组文章引用及被引用的研究，发现相关工作。

**扩展／具名实现路线 · 有来源支持。** OpenAlex OQL / API 或界面；引文缺失与数据库覆盖会影响结果，引用关系不代表赞同。

来源：[s-citations：Following citations · Following citations；取回 Markdown第 3–3 行](https://help.openalex.org/how-to/following-citations.md)。

### `research-04` 迁移其他数据库的检索策略并核查差异

将受支持的 PubMed、Scopus 等检索式转成 OpenAlex 查询，检查系统列出的语义差别。

**扩展／具名实现路线 · 有来源支持。** 数据库字段和词表并不等价，例如文档提示 MeSH 限制；需用已知文章验证召回。

来源：[s-search-translate：Searching with a strategy from another database · Searching with a strategy from another database；取回 Markdown第 3–3 行](https://help.openalex.org/how-to/search-strategies-from-other-databases.md)。

### `research-05` 寻找领域研究者、机构与潜在合作者

从主题发表和合作关系筛选专家或机构，辅助后续联系和审稿人调查。

**扩展／具名实现路线 · 有来源支持。** OpenAlex 机构、作者消歧和记录可能有误；无共同署名不等于没有利益冲突。

来源：[s-experts：Finding experts and partners · Finding experts and partners；取回 Markdown第 1–1 行](https://help.openalex.org/how-to/finding-experts.md)。

### `research-06` 保存与共享有明确成员的研究集合

把 DOI、作者或检索结果整理为可共享集合，用于后续统计或复用。

**扩展／具名实现路线 · 有来源支持。** 需要账户／API key 及相应访问权；集合是成员清单，动态追踪需单独保存搜索，不能混为自动更新。

来源：[s-collections：Working with collections · Working with collections；取回 Markdown第 3–3 行](https://help.openalex.org/how-to/collections.md)。

### `research-07` 批量补齐可追踪的出版物元数据

使用 Crossref 查询 DOI、出版信息和相关标识，辅助规范参考文献与来源核对。

**扩展／具名实现路线 · 有来源支持。** 需处理登记质量、缺字段与重复记录；元数据不等于全文或内容可靠性认证。

来源：[s-crossref：REST API - Crossref · Endpoints；本次 HTML 提取正文第 310–310 行（不是 HTML 源码行号）](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)。

<a id="library"></a>
## 积累和整理来源资料

### `research-08` 建立可整理和查找的来源资料库

用 Zotero 保存文献条目与附件，按项目或标签整理研究资料。

**扩展／具名实现路线 · 有来源支持。** 需要 Connector 或导入数据和合法附件；PDF 获取、识别与站点访问有条件。

来源：[s-zotero：The Basics | Zotero Documentation · 页面正文；本次 HTML 提取正文第 60–60 行（不是 HTML 源码行号）](https://www.zotero.org/support/quick_start_guide)。

### `research-09` 合并重复文献而保留有效资料

利用 Zotero 的重复检测识别可能相同的条目，人工选择并合并。

**扩展／具名实现路线 · 有来源支持。** 按标题、DOI、ISBN 等启发式判断；跨库和不完整元数据可能漏报或误报，合并前需确认。

来源：[s-zotero-duplicate：Duplicate Detection | Zotero Documentation · 页面正文；本次 HTML 提取正文第 61–61 行（不是 HTML 源码行号）](https://www.zotero.org/support/duplicate_detection)。

### `research-10` 把阅读标注变成可继续写作的笔记

在 Zotero PDF 阅读器标注并将引文相关材料加入笔记，连接阅读与写作。

**扩展／具名实现路线 · 有来源支持。** 需要可阅读附件；笔记中的材料与原文解释仍需研究者核对。

来源：[s-zotero-pdf：Zotero PDF Reader and Note Editor | Zotero Documentation · Adding Annotations to Notes；本次 HTML 提取正文第 67–67 行（不是 HTML 源码行号）](https://www.zotero.org/support/pdf_reader)。

### `research-11` 让团队共享并接续整理文献

利用 Zotero 群组与同步在成员和设备间共享条目和适用附件。

**扩展／具名实现路线 · 有来源支持。** 需要账户、组权限和文件存储；个人 WebDAV 与群组附件的支持范围不同，不能保证无限附件空间。

来源：[s-zotero：The Basics | Zotero Documentation · 页面正文；本次 HTML 提取正文第 118–118 行（不是 HTML 源码行号）](https://www.zotero.org/support/quick_start_guide)。

### `research-13` 统一资料表中的名称和变体

使用 OpenRefine 聚类发现近似但不完全相同的文本，确认后合并规范值。

**扩展／具名实现路线 · 有来源支持。** 需人工批准建议；同名、缩写和不同实体不能盲目合并。

来源：[s-refine-cluster：OpenRefine · Cell Editing and Clustering · 页面正文；本次 HTML 提取正文第 47–47 行（不是 HTML 源码行号）](https://openrefine.org/docs/manual/cellediting#clustering)。

<a id="evidence"></a>
## 筛选与提取研究证据

### `research-12` 从 PDF 等材料提取可处理的结构化内容

用 Docling 识别版面、阅读顺序和表格，导出 Markdown 或 JSON 进入资料整理流程。

**扩展／具名实现路线 · 有来源支持。** 需要安装代码和模型，扫描件可能需 OCR；复杂表格、公式和阅读顺序必须抽查。

来源：[s-docling：Docling · Features；取回 Markdown第 36–36 行](https://github.com/docling-project/docling/blob/d59ca4a97fe0c86cdeadb2a17dd86b98461d2517/README.md#L36-L36)。

### `research-14` 让文献筛选优先呈现更可能相关的记录

使用 ASReview 主动学习，从研究者标签持续调整待筛记录顺序。

**扩展／具名实现路线 · 有来源支持。** 需要种子与持续人工标注；排序不等于自动纳入／排除正确，不保证找齐所有相关研究。

来源：[s-asreview：ASReview LAB v3 — 项目说明 · ASReview LAB: Active Learning for Systematic Reviews；取回 Markdown第 33–33 行](https://github.com/asreview/asreview/blob/79d568212b2b0a78f9fd7be3c5117dfb890489f9/README.md#L33-L33)。

### `research-15` 在已标注文献集上评估筛选策略

用 ASReview 模拟工具衡量筛选方法表现，比较停止和排序策略。

**扩展／具名实现路线 · 有来源支持。** 需要可靠全量标签和适合的评估设计；模拟召回不能直接保证新题目效果。

来源：[s-asreview：ASReview LAB v3 — 项目说明 · ASReview LAB: Active Learning for Systematic Reviews；取回 Markdown第 40–40 行](https://github.com/asreview/asreview/blob/79d568212b2b0a78f9fd7be3c5117dfb890489f9/README.md#L40-L40)。

### `research-16` 协调多人的标题摘要与全文筛选

用 Rayyan 邀请协作者、分工，记录纳排和冲突处理，形成可导出的筛选结果。

**扩展／具名实现路线 · 有来源支持。** 需要账户、团队权限和相应功能等级；自动建议不能代替方案和人工一致性检查。

来源：[s-rayyan：AI-Powered Systematic Review & Literature Review Platform · Full-Text Screening；本次 HTML 提取正文第 123–125 行（不是 HTML 源码行号）](https://www.rayyan.ai/)。

### `research-17` 从研究材料提取可对照的数据表

用 Elicit 的提取模板整理定量或定性信息，并回看支持的引文或图表。

**扩展／具名实现路线 · 有来源支持。** 需要对应服务与资料访问；必须核对单位、群体、时间点和缺失信息，不采信宣传准确率作为本次验证。

来源：[s-elicit：Systematic Literature Reviews | Elicit: AI for research & decision-making · 页面正文；本次 HTML 提取正文第 80–80 行（不是 HTML 源码行号）](https://elicit.com/solutions/systematic-review)。

<a id="synthesis"></a>
## 综合与探索研究全貌

### `research-18` 形成带逐句引用的证据综述草稿

由 Elicit 将已选研究汇总为报告，保留方法、来源引用与材料摘要供核查。

**扩展／具名实现路线 · 有来源支持。** 需适用计划及选定文献范围；有引用不等于推断成立，不能自动替代系统综述质量评估。

来源：[s-elicit：Systematic Literature Reviews | Elicit: AI for research & decision-making · 页面正文；本次 HTML 提取正文第 84–84 行（不是 HTML 源码行号）](https://elicit.com/solutions/systematic-review)。

### `research-19` 构建可配置的自动化深度研究流程

运行 Open Deep Research 公开项目，组合搜索、研究、压缩和报告模型生成调研报告。

**扩展／具名实现路线 · 有来源支持。** 需要 LangGraph / LangChain 相关环境、模型与搜索凭据，可选 MCP；示例默认模型及性能榜单不保证当前兼容与事实质量。

来源：[s-deep：🔬 Open Deep Research · 🔬 Open Deep Research；取回 Markdown第 5–5 行](https://github.com/langchain-ai/open_deep_research/blob/1b7d2e80db9faa586165c60e09096dbbfd483a64/README.md#L5-L5)。

证据说明：README 开篇描述可配置研究 Agent，并明确可组合模型提供方、搜索工具和 MCP；不再以单个模型角色名作为整条流程的证据。

### `research-20` 从出版与合作关系绘制研究领域地图

用 VOSviewer 将引文、共同署名或术语数据组织为可探索的网络。

**扩展／具名实现路线 · 有来源支持。** 官方示例包含大学和期刊地图；需数据授权和合理计数，网络位置不直接代表质量或因果。

来源：[s-vos-case：VOSviewer - Features - Examples · 页面正文；本次 HTML 提取正文第 76–76 行（不是 HTML 源码行号）](https://www.vosviewer.com/examples)。

### `research-21` 检查研究主题的密度与时间变化

使用 VOSviewer 密度和叠加图查看领域聚集以及随时间的分布。

**扩展／具名实现路线 · 有来源支持。** 受样本和年份字段质量影响；视觉聚类不是领域演化的确定解释。

来源：[s-vos：VOSviewer - Features - Highlights · 页面正文；本次 HTML 提取正文第 61–61 行（不是 HTML 源码行号）](https://www.vosviewer.com/features)。

<a id="writing"></a>
## 写作与交付研究报告

### `research-22` 让写作中的引文与参考文献表同步

通过 Zotero Word / LibreOffice / Google Docs 集成插入引用，并按选择样式更新书目。

**扩展／具名实现路线 · 有来源支持。** 需要受支持编辑器和插件；作者、标题、页码与引文适配仍须核查。

来源：[s-zotero-cite：Word Processor Plugins | Zotero Documentation · 页面正文；本次 HTML 提取正文第 61–61 行（不是 HTML 源码行号）](https://www.zotero.org/support/word_processor_integration)。

### `research-23` 记录系统综述各阶段文献去向

用 PRISMA 流程图模板呈现检索、筛选、排除和纳入数量及理由。

**扩展／具名实现路线 · 有来源支持。** 需要真实筛选记录和正确模板；图表本身不证明研究遵循全部 PRISMA 要求。

来源：[s-prisma：PRISMA flow diagram · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://www.prisma-statement.org/prisma-2020-flow-diagram)。

### `research-26` 交付代码、计算和叙述相连的研究报告

用 Quarto 执行 R 代码并渲染文档，使分析过程和呈现结果共同保存。

**扩展／具名实现路线 · 有来源支持。** 需要运行环境、数据和输出格式依赖；可渲染不等于任何机器均可复现。

来源：[s-quarto：Quarto · Using R · Overview；本次 HTML 提取正文第 246–246 行（不是 HTML 源码行号）](https://quarto.org/docs/computations/r.html)。

证据说明：Quarto 的 Using R 概述直接说明执行 R 代码；Code Blocks 章节提供把说明、代码与图表一起渲染的完整示例。

<a id="transparency"></a>
## 保留可重查的研究记录

### `research-24` 为研究计划留下可引用的事先记录

在 OSF 注册研究计划，并连接相关材料、代码、数据或成果。

**扩展／具名实现路线 · 有来源支持。** 需要账户及适用注册规则；注册不是研究质量审查或对结果的背书。

来源：[s-osf：The Open Science Framework · 页面正文；本次 HTML 提取正文第 44–44 行（不是 HTML 源码行号）](https://www.cos.io/products/osf)。

### `research-25` 使分析在输入变化后按依赖重算

用 targets 将数据准备、分析和结果组织为可更新研究流水线。

**扩展／具名实现路线 · 有来源支持。** 需要把依赖写入可追踪任务；外部状态、数据版本和随机性仍要自行管理。

来源：[s-targets：Dynamic Function-Oriented Make-Like Declarative Pipelines • targets · 页面正文；本次 HTML 提取正文第 13–13 行（不是 HTML 源码行号）](https://docs.ropensci.org/targets/)。

## 资料覆盖与发现过程

先从研究者能取得的资料与报告发现，再读 OpenAlex 引文／跨库检索配方、VOSviewer 实际网络示例和 Open Deep Research 项目，补查筛选、元数据与复现记录。
归一化：同一工具多个 API 合并为检索或资料库结果；文本抽取与研究数据提取分开，引用格式与证据综合分开。
补漏发现近似名称清洗、已有标签上的筛选评估、预注册和可重算报告；按实际问题追加候选后才建立导航。
没有沿用前几轮研究地图的用途分类；从检索到证据交付的分组只用于阅读，不声称唯一线性研究流程。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 本轮没有执行完整系统综述、真实双人筛选或安装模型，所有内容是来源支持的流程可能性。
- OpenAlex 官方旧文档重定向到新 Help Center，当前 OQL、搜索翻译与集合按新资料描述；账户、收费及 API 限制需实际使用时核实。
- Unpaywall 当前抓取仅取得壳页，scite 返回 403；未把这两条路线的具体效果加入确认清单。
- 没有以自动引用、AI 摘要、筛选排序或厂商宣传准确率证明研究结论正确；独立复现和人工方法学评估仍待进行。
- 数据库覆盖、付费全文与出版偏倚无法由这些工具消除；本图不包括实验室、现场调查等所有研究方法。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
