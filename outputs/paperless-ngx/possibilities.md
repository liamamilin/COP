# Paperless-ngx 可能性地图

范围：以研究时实际取回的官方主干文档的固定提交快照及已合入功能 PR为范围；涵盖个人文档收集、OCR、归档、检索与自动化，区分内置非 LLM、可选模型和外部解析服务。

资料截点：2026-11-05。本图有 25 项来源支持的结果，来自 9 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

资料来自当前官方主干而非已安装版本。一般流程可自托管；AI 和远程 OCR 是可选能力，启用远程后内容不再只留本机。Office 解析、身份服务和客户端有独立依赖。

## 地图导航

- [收集和识别文档](#capture)
- [整理和保存档案](#archive)
- [查找和理解内容](#retrieval)
- [减少重复整理工作](#automation)
- [共享与访问协作](#collaboration)
- [集成与迁移维护](#maintenance)

<a id="capture"></a>
## 收集和识别文档

### `paper-01` 把扫描件变成能搜索和选中文字的文档

使用 OCR 提取扫描图像中的文字，为检索和后续处理提供文本。

**内置／核心能力 · 有来源支持。** 需要 Tesseract 与相应语言数据，清晰度和版面影响结果；识别后仍需检查。

来源：[s-index：Paperless-ngx · 官方 主干快照（固定提交）功能总览 · Features；取回 Markdown第 33–33 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/index.md#L33-L33)。

### `paper-06` 自动从邮件收集附件文档

根据邮件账户和规则把附件送入文档消费流程。

**内置／核心能力 · 有来源支持。** 需要邮件访问、规则和可用认证；邮箱副作用如标记或删除需明确配置。

来源：[s-usage：Paperless-ngx · Usage（固定提交） · Incoming Email；取回 Markdown第 195–195 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/usage.md#L195-L195)。

### `paper-16` 批量扫描时自动按分隔条码拆件

使用适用条码分隔页把扫描批次拆成独立文档。

**内置／核心能力 · 有来源支持。** 需要启用条码检测和支持的 PDF / TIFF；分隔页保留与起始页语义依配置，不保证识别所有打印条码。

来源：[s-advanced：Paperless-ngx · Advanced Topics（固定提交） · Document Splitting；取回 Markdown第 959–959 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/advanced_usage.md#L959-L959)。

### `paper-17` 用单面扫描器整理双面文件

先分别扫描奇偶页，再由自动 collation 合并并调整页序。

**内置／核心能力 · 有来源支持。** 功能默认关闭；需要按官方扫描顺序和目录流程操作，并核对缺页与颠倒。

来源：[s-advanced：Paperless-ngx · Advanced Topics（固定提交） · Automatic collation of double-sided documents；取回 Markdown第 1026–1026 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/advanced_usage.md#L1026-L1026)。

### `paper-20` 将指定文档送交远程 OCR 服务

配置 Azure AI 后，通过全局策略或工作流选择适合的文件远程识别。

**扩展／具名实现路线 · 有来源支持。** 主干内置入口，但需要外部 Azure AI、凭据及费用；文档离开本地服务器，格式不支持时可回退本地。

来源：[s-configuration：Paperless-ngx · Configuration（固定提交） · [`PAPERLESS_REMOTE_OCR_ENGINE=<str>`](#PAPERLESS_REMOTE_OCR_ENGINE)；取回 Markdown第 2096–2096 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/configuration.md#L2096-L2096)。

### `paper-23` 将办公文档纳入同一检索档案库

对支持的 Word、表格和幻灯片等文件使用相应解析路线归档与提取内容。

**扩展／具名实现路线 · 有来源支持。** 需要 Apache Tika、Gotenberg 等额外解析组件及支持格式；不是完整 Office 在线编辑器。

来源：[s-faq：Paperless-ngx · FAQ（固定提交） · _What file types does paperless-ngx support?_；取回 Markdown第 67–67 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/faq.md#L67-L67)。

<a id="archive"></a>
## 整理和保存档案

### `paper-02` 保留原件并建立长期归档副本

保留原始文件，同时生成适合归档的 PDF/A 副本。

**内置／核心能力 · 有来源支持。** 受输入格式、解析和归档配置影响；不等于法律效力或无限期保存保证。

来源：[s-index：Paperless-ngx · 官方 主干快照（固定提交）功能总览 · Features；取回 Markdown第 36–36 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/index.md#L36-L36)；[s-faq：Paperless-ngx · FAQ（固定提交） · Let's say I want to switch tools in a year. Can I easily move to other systems?；取回 Markdown第 47–47 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/faq.md#L47-L47)。

### `paper-03` 按来源和文档用途建立个人档案库

用标签、往来方和文档类型整理文件，便于按真实业务线索定位。

**内置／核心能力 · 有来源支持。** 需要设计适合自己的元数据；自动建议不能代替校对。

来源：[s-index：Paperless-ngx · 官方 主干快照（固定提交）功能总览 · Features；取回 Markdown第 31–31 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/index.md#L31-L31)。

### `paper-05` 在单一条目下管理文件的多个版本

把文件修订保留为同一文档的版本历史，共享根条目的元数据。

**内置／核心能力 · 有来源支持。** 主干文档包含该能力；版本主要跟踪文件及文本，不是每一项元数据的完整版本控制。

来源：[s-versions-pr：Paperless-ngx · Feature: document file versions（已合入 PR） · Proposed change；取回 Markdown第 11–11 行](https://github.com/paperless-ngx/paperless-ngx/pull/12061)；[s-versions-pr：Paperless-ngx · Feature: document file versions（已合入 PR） · Proposed change；取回 Markdown第 14–14 行](https://github.com/paperless-ngx/paperless-ngx/pull/12061)。

证据说明：合入的功能 PR 说明版本保存独立内容并允许新增版本；当前固定文档说明元数据仍属于根文档。

### `paper-10` 记录发票号、付款日期等业务字段

为文档附加自定义类型字段，保存软件默认元数据之外的信息。

**内置／核心能力 · 有来源支持。** 需定义字段类型和录入／导入规则，系统不会自动保证金额和日期准确。

来源：[s-usage：Paperless-ngx · Usage（固定提交） · Custom Fields；取回 Markdown第 765–765 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/usage.md#L765-L765)；[s-api：Paperless-ngx · REST API（固定提交） · Documents；取回 Markdown第 327–327 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/api.md#L327-L327)。

证据说明：Usage 的自定义字段章节举例发票号和付款日期；API 的 bulk_edit 说明将字段 ID 与值添加到文档的操作。

### `paper-11` 在文档界面整理 PDF 页面

合并或拆分 PDF、旋转、删除和重新排列页面，得到合适归档文件。

**内置／核心能力 · 有来源支持。** 仅适用支持的 PDF 操作；部分修改会改变归档文件，需保留原件并检查页序。

来源：[s-usage：Paperless-ngx · Usage（固定提交） · PDF Actions；取回 Markdown第 798–798 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/usage.md#L798-L798)。

### `paper-21` 把电子档案关联到纸质原件编号

使用 ASN 条码或档案序号，将电子记录关联到物理文件。

**内置／核心能力 · 有来源支持。** 需要编号规则和可识别条码；编号不自动确保实物存放正确。

来源：[s-configuration：Paperless-ngx · Configuration（固定提交） · [`PAPERLESS_CONSUMER_ENABLE_ASN_BARCODE=<bool>`](#PAPERLESS_CONSUMER_ENABLE_ASN_BARCODE)；取回 Markdown第 1691–1691 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/configuration.md#L1691-L1691)。

### `paper-22` 按元数据组织可识别的文件路径

配置文件名与存储路径模板，让磁盘档案反映日期、来源或类型。

**内置／核心能力 · 有来源支持。** 文件由系统管理；需校验模板和字符替换，不能绕过系统直接随意重命名。

来源：[s-configuration：Paperless-ngx · Configuration（固定提交） · [`PAPERLESS_FILENAME_FORMAT=<format>`](#PAPERLESS_FILENAME_FORMAT)；取回 Markdown第 404–404 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/configuration.md#L404-L404)。

### `paper-24` 在消费后识别和处理重复文件

利用重复标记检查内容相同的文件，人工决定保留、合并或删除。

**内置／核心能力 · 有来源支持。** 主干 FAQ 指明 v3 默认仍消费并标记重复；不能沿用旧说法声称所有重复上传必然拒绝。

来源：[s-faq：Paperless-ngx · FAQ（固定提交） · _Are duplicate documents rejected?_；取回 Markdown第 78–78 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/faq.md#L78-L78)。

### `paper-25` 从回收站恢复尚未清除的误删文档

在文件最终清除前恢复文档及其数据库内容，纠正近期误删。

**内置／核心能力 · 有来源支持。** 仅限尚未手动或按保留期限彻底清除的文件；回收站不替代独立备份。

来源：[s-usage：Paperless-ngx · Usage（固定提交） · Document Trash；取回 Markdown第 819–819 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/usage.md#L819-L819)。

<a id="retrieval"></a>
## 查找和理解内容

### `paper-04` 在文档内容中检索所需信息

用全文查询、相关度、匹配高亮等找到归档资料。

**内置／核心能力 · 有来源支持。** 文本必须成功提取并索引；检索结果取决于 OCR、语言与查询。

来源：[s-index：Paperless-ngx · 官方 主干快照（固定提交）功能总览 · Features；取回 Markdown第 50–50 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/index.md#L50-L50)。

### `paper-14` 找到与当前文档相关的既有档案

启用嵌入与 LLM 索引，用相似文档检索为阅读和建议补充背景。

**扩展／具名实现路线 · 有来源支持。** 需要向量索引及本地或远程 embedding 后端；不是无需配置的普通全文搜索。

来源：[s-advanced：Paperless-ngx · Advanced Topics（固定提交） · The LLM index (RAG) and similar documents；取回 Markdown第 150–150 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/advanced_usage.md#L150-L150)。

### `paper-15` 对单份或一组档案提问并查看引用文档

使用文档聊天检索相关上下文，获得附有来源文档链接的回答。

**扩展／具名实现路线 · 有来源支持。** 需要 LLM 索引和生成后端；引用链接不证明回答正确，必须对照文件。

来源：[s-advanced：Paperless-ngx · Advanced Topics（固定提交） · Document chat；取回 Markdown第 175–175 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/advanced_usage.md#L175-L175)。

<a id="automation"></a>
## 减少重复整理工作

### `paper-07` 按事件自动分配元数据和后续动作

在文档消费、添加或更新时，按规则触发标签、类型或权限等整理动作，减少重复处理。

**内置／核心能力 · 有来源支持。** 需要匹配触发条件与权限；外部 webhook、邮件或模型调用还需要各自服务。

来源：[s-workflows-pr：Paperless-ngx · Feature: Workflows（已合入 PR） · Proposed change；取回 Markdown第 16–16 行](https://github.com/paperless-ngx/paperless-ngx/pull/5121)；[s-workflows-pr：Paperless-ngx · Feature: Workflows（已合入 PR） · Proposed change；取回 Markdown第 19–19 行](https://github.com/paperless-ngx/paperless-ngx/pull/5121)。

证据说明：引用已合入的功能 PR 说明事件与动作机制；外部通知与 webhook 不是本条结果的确认范围。

### `paper-12` 从既有标注学习自动归类文档

利用 Auto 匹配从已标注资料学习标签、往来方、类型和存储路径建议。

**内置／核心能力 · 有来源支持。** 这是内置非 LLM 分类路线；需要足够正确样本和更新训练，建议并不总正确。

来源：[s-advanced：Paperless-ngx · Advanced Topics（固定提交） · Automatic matching；取回 Markdown第 55–55 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/advanced_usage.md#L55-L55)。

### `paper-13` 利用模型辅助填写文档元数据

启用 AI 后请求标题、标签、日期等建议，再确认或通过已配置流程应用。

**扩展／具名实现路线 · 有来源支持。** 入口在主干内置；需启用并配置本地或远程 LLM，远程路线会发送文档内容并可能计费。

来源：[s-advanced：Paperless-ngx · Advanced Topics（固定提交） · AI features；取回 Markdown第 103–103 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/advanced_usage.md#L103-L103)。

<a id="collaboration"></a>
## 共享与访问协作

### `paper-08` 通过有期限的链接分享文件

创建单文档或多文档分享链接，让有链接的人访问相应下载内容。

**内置／核心能力 · 有来源支持。** 链接持有者可访问；需设置合适期限和撤销策略，不能把公开链接当成身份权限隔离。

来源：[s-usage：Paperless-ngx · Usage（固定提交） · Share Links；取回 Markdown第 353–353 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/usage.md#L353-L353)。

### `paper-09` 为不同用户控制文档可见性和编辑权

结合全局与对象权限安排用户、组和文档的访问。

**内置／核心能力 · 有来源支持。** 需正确设置 owner、view / edit 与默认权限；超级用户等特殊角色需单独理解。

来源：[s-usage：Paperless-ngx · Usage（固定提交） · Default permissions；取回 Markdown第 391–391 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/usage.md#L391-L391)。

<a id="maintenance"></a>
## 集成与迁移维护

### `paper-18` 由外部程序导入和管理档案

通过 REST API 上传、查询或处理受支持文档数据，连接扫描和业务流程。

**扩展／具名实现路线 · 有来源支持。** 需要自行开发调用方并配置认证；使用当前 schema 和版本，不保证旧客户端兼容。

来源：[s-api：Paperless-ngx · REST API（固定提交） · REST API；取回 Markdown第 3–3 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/api.md#L3-L3)。

### `paper-19` 导出可用于恢复或迁移的档案资料

导出文档、缩略图、元数据和数据库内容，形成可另存或导入的资料集。

**内置／核心能力 · 有来源支持。** 需按官方版本限制恢复并重新生成 API token；异版本数据库导出不能直接导入，备份须实际演练。

来源：[s-admin：Paperless-ngx · Administration（固定提交） · Making backups；取回 Markdown第 13–14 行](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/administration.md#L13-L14)。

## 资料覆盖与发现过程

从官方功能总览发现纸张到可检索档案的结果，接着读取推荐扫描流程、双面扫描例子和 API，再核对新 AI 与 v3 行为。
归一化：多个入口合并为收集结果；PDF 页面动作合并为整理，标签和字段按实际档案用途解释。
补漏发现文件版本、嵌套标签、远程 OCR、向量检索和重复文档默认行为变化；版本未验证处保留条件；最终挑战另补入误删文件的回收站恢复。
先保留无分类候选，再按收集、查找、整理、协作和维护的实际结果建立导航。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 官网文档请求返回 403，改从官方 GitHub 同源 Markdown 取回；main 包含 v3 描述，不保证你的已安装稳定版／2.x 具备全部功能。
- 未部署系统、扫描实物或运行邮件、OCR、备份恢复、API 与模型；OCR 和问答准确性未实测。
- 没有把旧社区 AI 插件当成当前必需组件；当前主干自带 AI 功能入口，但本地／远程模型依赖仍要配置。
- 第三方手机应用、parser 插件和身份服务生态未逐一验证维护与兼容性，未列为无条件支持。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
