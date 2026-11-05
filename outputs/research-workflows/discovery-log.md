# 研究工作流 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `research-01`｜结果视角｜把研究问题整理为可执行的综述方案｜s-elicit
2. `research-02`｜结果视角｜找到使用不同表达的相关论文｜s-paper-search
3. `research-03`｜结果视角｜沿前向与后向引文扩展文献集合｜s-citations
4. `research-04`｜结果视角｜迁移其他数据库的检索策略并核查差异｜s-search-translate
5. `research-05`｜结果视角｜寻找领域研究者、机构与潜在合作者｜s-experts
6. `research-06`｜结果视角｜保存与共享有明确成员的研究集合｜s-collections
7. `research-07`｜结果视角｜批量补齐可追踪的出版物元数据｜s-crossref
8. `research-08`｜结果视角｜建立可整理和查找的来源资料库｜s-zotero
9. `research-09`｜结果视角｜合并重复文献而保留有效资料｜s-zotero-duplicate
10. `research-10`｜结果视角｜把阅读标注变成可继续写作的笔记｜s-zotero-pdf
11. `research-11`｜结果视角｜让团队共享并接续整理文献｜s-zotero
12. `research-12`｜结果视角｜从 PDF 等材料提取可处理的结构化内容｜s-docling
13. `research-13`｜结果视角｜统一资料表中的名称和变体｜s-refine-cluster
14. `research-14`｜结果视角｜让文献筛选优先呈现更可能相关的记录｜s-asreview
15. `research-15`｜结果视角｜在已标注文献集上评估筛选策略｜s-asreview
16. `research-16`｜结果视角｜协调多人的标题摘要与全文筛选｜s-rayyan
17. `research-17`｜结果视角｜从研究材料提取可对照的数据表｜s-elicit
18. `research-18`｜结果视角｜形成带逐句引用的证据综述草稿｜s-elicit
19. `research-19`｜完整项目视角｜构建可配置的自动化深度研究流程｜s-deep
20. `research-20`｜完整案例视角｜从出版与合作关系绘制研究领域地图｜s-vos-case
21. `research-21`｜结果视角｜检查研究主题的密度与时间变化｜s-vos
22. `research-22`｜结果视角｜让写作中的引文与参考文献表同步｜s-zotero-cite
23. `research-23`｜结果视角｜记录系统综述各阶段文献去向｜s-prisma
24. `research-24`｜结果视角｜为研究计划留下可引用的事先记录｜s-osf
25. `research-25`｜结果视角｜使分析在输入变化后按依赖重算｜s-targets
26. `research-26`｜结果视角｜交付代码、计算和叙述相连的研究报告｜s-quarto

## 归一化、补漏与停止依据

先从研究者能取得的资料与报告发现，再读 OpenAlex 引文／跨库检索配方、VOSviewer 实际网络示例和 Open Deep Research 项目，补查筛选、元数据与复现记录。
归一化：同一工具多个 API 合并为检索或资料库结果；文本抽取与研究数据提取分开，引用格式与证据综合分开。
补漏发现近似名称清洗、已有标签上的筛选评估、预注册和可重算报告；按实际问题追加候选后才建立导航。
没有沿用前几轮研究地图的用途分类；从检索到证据交付的分组只用于阅读，不声称唯一线性研究流程。

## 保留的未知项

- 本轮没有执行完整系统综述、真实双人筛选或安装模型，所有内容是来源支持的流程可能性。
- OpenAlex 官方旧文档重定向到新 Help Center，当前 OQL、搜索翻译与集合按新资料描述；账户、收费及 API 限制需实际使用时核实。
- Unpaywall 当前抓取仅取得壳页，scite 返回 403；未把这两条路线的具体效果加入确认清单。
- 没有以自动引用、AI 摘要、筛选排序或厂商宣传准确率证明研究结论正确；独立复现和人工方法学评估仍待进行。
- 数据库覆盖、付费全文与出版偏倚无法由这些工具消除；本图不包括实验室、现场调查等所有研究方法。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-api-recipes](https://help.openalex.org/how-to/api-recipes.md) | 2026-11-05T09:49:05.654498+00:00 | 否 |
| [s-asreview](https://github.com/asreview/asreview/blob/79d568212b2b0a78f9fd7be3c5117dfb890489f9/README.md) | 2026-11-05T09:39:55.707102+00:00 | 是 |
| [s-citations](https://help.openalex.org/how-to/following-citations.md) | 2026-11-05T09:49:05.656198+00:00 | 是 |
| [s-collections](https://help.openalex.org/how-to/collections.md) | 2026-11-05T09:49:05.409296+00:00 | 是 |
| [s-crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | 2026-11-05T09:39:53.815884+00:00 | 是 |
| [s-deep](https://github.com/langchain-ai/open_deep_research/blob/1b7d2e80db9faa586165c60e09096dbbfd483a64/README.md) | 2026-11-05T09:39:55.196232+00:00 | 是 |
| [s-docling](https://github.com/docling-project/docling/blob/d59ca4a97fe0c86cdeadb2a17dd86b98461d2517/README.md) | 2026-11-05T09:39:54.861416+00:00 | 是 |
| [s-elicit-case](https://elicit.com/customer-stories) | 2026-11-05T09:47:16.145052+00:00 | 否 |
| [s-elicit](https://elicit.com/solutions/systematic-review) | 2026-11-05T09:39:56.846072+00:00 | 是 |
| [s-experts](https://help.openalex.org/how-to/finding-experts.md) | 2026-11-05T09:49:05.303058+00:00 | 是 |
| [s-openalex-api](https://help.openalex.org/) | 2026-11-05T09:40:54.475142+00:00 | 否 |
| [s-openalex-index](https://help.openalex.org/llms.txt) | 2026-11-05T09:47:11.865059+00:00 | 否 |
| [s-openalex](https://help.openalex.org/) | 2026-11-05T09:39:53.779871+00:00 | 否 |
| [s-openrefine](https://openrefine.org/docs) | 2026-11-05T09:39:57.797414+00:00 | 否 |
| [s-osf](https://www.cos.io/products/osf) | 2026-11-05T09:40:53.845494+00:00 | 是 |
| [s-paper-search](https://help.openalex.org/how-to/finding-papers-with-keywords.md) | 2026-11-05T09:49:05.768367+00:00 | 是 |
| [s-prisma](https://www.prisma-statement.org/prisma-2020-flow-diagram) | 2026-11-05T09:39:58.282569+00:00 | 是 |
| [s-quarto](https://quarto.org/docs/computations/r.html) | 2026-11-05T09:49:07.968749+00:00 | 是 |
| [s-rayyan](https://www.rayyan.ai/) | 2026-11-05T09:39:56.992384+00:00 | 是 |
| [s-refine-cluster](https://openrefine.org/docs/manual/cellediting#clustering) | 2026-11-05T09:49:07.549936+00:00 | 是 |
| [s-search-translate](https://help.openalex.org/how-to/search-strategies-from-other-databases.md) | 2026-11-05T09:49:05.351080+00:00 | 是 |
| [s-semantic](https://www.semanticscholar.org/product/api) | 2026-11-05T09:39:54.156369+00:00 | 否 |
| [s-targets](https://docs.ropensci.org/targets/) | 2026-11-05T09:49:07.139709+00:00 | 是 |
| [s-unpaywall-api](https://unpaywall.org/products/api/v2) | 2026-11-05T09:40:53.160421+00:00 | 否 |
| [s-unpaywall](https://unpaywall.org/products/api) | 2026-11-05T09:39:57.354938+00:00 | 否 |
| [s-vos-case](https://www.vosviewer.com/examples) | 2026-11-05T09:47:12.778645+00:00 | 是 |
| [s-vos](https://www.vosviewer.com/features) | 2026-11-05T09:40:54.103331+00:00 | 是 |
| [s-zotero-cite](https://www.zotero.org/support/word_processor_integration) | 2026-11-05T09:47:12.257342+00:00 | 是 |
| [s-zotero-duplicate](https://www.zotero.org/support/duplicate_detection) | 2026-11-05T09:47:12.826582+00:00 | 是 |
| [s-zotero-pdf](https://www.zotero.org/support/pdf_reader) | 2026-11-05T09:49:07.313904+00:00 | 是 |
| [s-zotero](https://www.zotero.org/support/quick_start_guide) | 2026-11-05T09:39:55.126381+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`research-07`、`research-10`、`research-14`、`research-15`、`research-16`、`research-19`、`research-26`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
