# Zotero 可能性地图

范围：资料收集、阅读标注、引用和协作；区分原生、第三方插件、出版物访问与存储服务。

## 按用户结果浏览

### 收集与建库

- **把网页收进可检索的文献库**（扩展）——用浏览器 Zotero Connector 保存当前网页为资料库条目，后续可整理、检索并关联附件。 条件：需要安装浏览器 Zotero Connector 和桌面端 Zotero；网页识别/可保存字段因站点而异。Connector 不授予出版物全文权限，全文访问仍取决于出版商和机构授权。 来源：[Zotero Connector | Zotero Documentation](https://www.zotero.org/support/connector)。

### 整理与查重

- **按主题整理文献并让动态清单自动更新**（核心）——用 collections、tags 和 saved searches 建立主题/项目清单；一个条目可出现在多个集合而不复制，匹配搜索条件的新增资料会自动进入保存搜索结果。 条件：集合/标签适合人工分类与过滤；保存搜索按当前条件刷新。集合在个人库与组库之间复制时不保留位置，标签会保留。 来源：[Collections and Tags | Zotero Documentation](https://www.zotero.org/support/collections_and_tags)。
- **合并重复文献并保住分类与引用关联**（核心）——检查 Zotero 标出的疑似重复项，合并为一条资料记录并保留集合、标签；官方说明文字处理器插件会识别合并，自动生成的引用和书目不会因此失效。 条件：检测只在单个资料库内运行，使用标题、DOI、ISBN 等字段；可能有误报，目前不能把误报标记为非重复，需人工检查合并字段。 来源：[Duplicate Detection | Zotero Documentation](https://www.zotero.org/support/duplicate_detection)。

### 阅读与笔记

- **把 PDF 标注整理成可回到原文的研究笔记**（核心）——在内置 PDF 阅读器标注并将选中内容汇入笔记；笔记保留回到 PDF 页面的链接和引文，便于复核上下文。 条件：使用 Zotero 内置 PDF 阅读器和笔记编辑器。注释保存在 Zotero 数据中；外部 PDF 查看器不一定会同步显示这些注释，向外分享需导出带注释副本。 来源：[Zotero PDF Reader and Note Editor | Zotero Documentation](https://www.zotero.org/support/pdf_reader)。

### 写作与引用

- **在 Word、LibreOffice 或 Google Docs 中维护引用和书目**（扩展）——从 Zotero 文献库插入文内引文或脚注，生成动态参考书目；修正文献条目后可更新文档中的书目信息。 条件：官方桌面端文字处理插件与 Zotero 捆绑并通常自动安装；Google Docs 路线还涉及浏览器 Connector 与文档授权。各文字处理器支持方式不同，未实测当前客户端兼容性。 来源：[Word Processor Plugins | Zotero Documentation](https://www.zotero.org/support/word_processor_integration)。
- **让 LaTeX/Markdown 文献文件随 Zotero 集合变化自动导出**（扩展）——使用 Better BibTeX 维护引用键，并在 Zotero 集合变化时自动导出 BibTeX/BibLaTeX 文件，供文本化写作流程使用。 条件：这是第三方 Better BibTeX 作者文档描述的扩展工作流，不是 Zotero 核心导出承诺。文档注明 Zotero 8 已有原生引用键，Better BibTeX 的 Zotero 7 支持不再更新；须按当前 Zotero/扩展版本核对迁移和兼容性。未实装验证。 来源：[Better BibTeX for Zotero](https://retorque.re/zotero-better-bibtex/)。

### 导入与迁移

- **从其他文献管理器迁移资料库**（核心）——将已有文献库导入 Zotero，尽量延续条目和文件夹/集合结构，继续在同一库中检索与引用。 条件：Mendeley 可从在线库直接导入资料与文件夹结构，但需先同步到其服务器；群组库不能直接导入，Mendeley Cite 引用不可读。EndNote 需先导出 XML，附件目录位置影响附件导入；其他工具可尝试 RIS、BibTeX 或 CSL JSON，字段保留情况因格式而异。迁移前备份并抽查结果。 来源：[How do I import a Mendeley library into Zotero? | Zotero Documentation](https://www.zotero.org/support/kb/mendeley_import)、[How do I import from EndNote? | Zotero Documentation](https://www.zotero.org/support/kb/endnote_import)、[Importing from Other Reference Managers | Zotero Documentation](https://www.zotero.org/support/moving_to_zotero)。

### 协作与共享

- **与同学或同事共建共享资料库**（核心）——在 Zotero Group Library 中共同维护项目资料，让成员访问共享条目并按组设置查看、编辑和附件权限。 条件：需要 Zotero.org 账户和组成员权限。组库与个人库分开；组类型和管理员设置决定成员权限。组附件共享使用组所有者的存储配额，公开开放组不能启用文件存储。 来源：[Zotero Groups | Zotero Documentation](https://www.zotero.org/support/groups)。

### 同步与存储

- **在个人电脑间同步文献记录、笔记和附件**（扩展）——在 Zotero 安装的设备间同步个人库条目、笔记、链接、标签及配置的附件文件；需要时通过 Zotero 在线资料库访问记录。 条件：这是数据同步与附件同步组合后的用户结果：官方明确两者分别处理。条目/笔记需启用 Zotero 账户数据同步；PDF、快照等附件需 Zotero Storage 或 WebDAV。WebDAV 不支持组库；当前配额、价格和地区付款未核实。 来源：[Syncing | Zotero Documentation](https://www.zotero.org/support/sync)、[Zotero Storage FAQ | Zotero Documentation](https://www.zotero.org/support/storage_faq)。

## 能力边界与待验证方向

Zotero 的网页收集依赖浏览器 Connector；引用集成依赖官方文字处理插件；Better BibTeX 是第三方扩展。Connector 不提供出版物全文授权。

条目、笔记、链接与标签的数据同步和附件同步是两条配置路线；附件可使用 Zotero Storage 或 WebDAV，后者不支持组库。没有核实当前价格、配额或地区限制。

迁移能力因来源工具而异：Mendeley 在线导入、EndNote XML 导出和标准格式导入均有不同的文件与字段边界；关键库应先备份并抽样检查。

未实装任何客户端或扩展，以上是文档支持的可行结果，不是本地运行或客户成效认证。逐站点抓取质量、地区/付费条件、插件安全性及新版本兼容性仍待核验。

## 原研究保留的未解决问题

- 未安装或运行 Zotero、Connector、Word/LibreOffice/Google Docs 插件及 Better BibTeX；兼容性与具体授权流程未验证。
- 未核实 Zotero Storage 当前价格/配额、各地区付款方式及第三方 WebDAV 服务条件。
- 未验证特定出版商 translator 的准确率和字段修复路径，也未核验第三方扩展的安全审查。
- 未验证迁移后附件、非标准字段、引用键和 PDF 标注逐项完整；建议对关键库先备份并抽样核对。
