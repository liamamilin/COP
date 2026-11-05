# Obsidian 可能性地图

范围：面向个人、研究者、作者和小团队，发现 Obsidian 能帮助完成的知识工作、生活记录和资料交付结果；包含桌面与移动端，以及明确标注的插件、服务和外部工具。不是 API 清单、教程或新的 Skill 规则。

研究截点：**2026-11-05**。本图整理 **63 项有来源支持的可能性、10 个导航分组、76 个来源记录**。这里的“有来源支持”表示取回的原始资料直接描述或展示该结果，**不等于已安装实测或独立人工评审**。没有任何条目被标为 `reviewed`。

版本参照：官方 [1.15 桌面正式版](https://obsidian.md/changelog/2026-11-02-desktop-v1.15.0/) 与 [1.15 移动正式版](https://obsidian.md/changelog/2026-11-02-mobile-v1.15.0/)。1.15.1 早期访问功能没有被当作所有用户都已具备的能力。旧案例仍保留其年代与依赖边界。

证据短摘录、具体位置、来源类型、实际取回入口和正文核对哈希见 [possibilities.json](possibilities.json) 的 `sources` 与各 P 的 `evidence_refs`；下文每项给出直接来源链接。摘录的精确匹配只能证明文本存在，还需读其上下文。

## 如何阅读边界

- **内置**：随应用提供的功能或无需社区插件的基本工作流；部分核心插件须手动启用。
- **扩展**：另装官方组件、社区插件，或依赖服务/工具。官方维护的 Maps、Importer、Web Clipper 也不因此成为已内置功能。
- 应用可免费使用，商业许可证当前为可选支持；Sync、Publish 是可选付费服务。插件是否免费与其模型、API、托管服务是否收费是两回事。[价格与授权说明](https://obsidian.md/pricing)
- 以下是可选择的路径，不是建议把全部插件装入同一个库。插件继承应用访问能力，目录收录不代表版本兼容或权限隔离。[插件边界](https://obsidian.md/help/plugin-security)

## 地图导航

- [收集外部资料与即时想法](#g-capture)
- [连接、找回与重用已有知识](#g-connect)
- [阅读、学习与开展研究](#g-study)
- [形成文稿并交付给读者](#g-write)
- [以空间和图解组织解释](#g-visual)
- [管理项目、记录和行动](#g-work)
- [安排生活并保存个人世界](#g-life)
- [保有、保护和共同维护资料](#g-steward)
- [发布和管理知识网站](#g-publish)
- [把知识库接入工作流与计算实验](#g-integrate)

<a id="g-capture"></a>
## 收集外部资料与即时想法

### `p-audio-evidence` 把讲座或会议录音附在记录中

把现场声音录成库内音频附件并嵌入当前笔记，作为之后重听的资料。

**内置 · 有来源支持。** 启用 Audio recorder，配置麦克风与系统权限；这项不包含转写、说话人识别或会议摘要。

来源：[s-audio：Obsidian Help — Audio recorder](https://obsidian.md/help/plugins/audio-recorder)。

### `p-mobile-capture` 在 iPhone 锁屏入口快速记录灵感

从系统入口直接采集文字到新笔记、日记或选定笔记，无需等待整个库载入。

**内置 · 有来源支持。** Quick Capture 需要 Obsidian 1.14+ 与 iOS/iPadOS 26+；先配置入口和保存位置。其他移动系统不能按此项推定支持。

来源：[s-ios：Obsidian Help — Obsidian for iOS and iPadOS](https://obsidian.md/help/ios)。

### `p-voice-transcript` 把口述灵感保存成文字笔记

在 iOS Quick Capture 说话时生成转写文字，并可选择把录音一同保存。

**内置 · 有来源支持。** 正式版 Obsidian 1.15 移动端，要求 iOS 26；转写语言、设备支持及准确率未实测。不等同于导入任意长音频或多人会议分析。

来源：[s-mobile-release：Obsidian 1.15 Mobile (Public)](https://obsidian.md/changelog/2026-11-02-mobile-v1.15.0/)。

### `p-migrate-notes` 把旧笔记系统迁成库内可编辑资料

借助官方 Importer 把支持的笔记应用或文件格式转成 Obsidian 资料。

**扩展｜官方另装插件 · 有来源支持。** Importer 是官方另装的社区插件；Notion、Evernote、Apple Notes、OneNote 等需依各导入指南准备导出文件与平台环境。不要推定所有字段、附件和链接都能无损迁移。

来源：[s-importer：Obsidian Help — Importer](https://obsidian.md/help/plugins/importer)；[s-import-formats：Obsidian Help — Import notes](https://obsidian.md/help/import)。

### `p-capture-web` 把网页内容和出处保存为笔记资料

从网页正文、所选文字或高亮采集内容，并用站点模板保存标题等元数据。

**扩展｜官方浏览器扩展 · 有来源支持。** 另装免费的官方 Web Clipper；浏览器与网站结构有影响，模板需配置。图片默认只保留远程 URL，完整离线归档需另下载附件；不承诺绕过登录或付费墙。

来源：[s-clipper：Obsidian Help — Clip web pages](https://obsidian.md/help/web-clipper/capture)；[s-clipper-templates：Obsidian Help — Web Clipper Templates](https://obsidian.md/help/web-clipper/templates)。

### `p-interpret-web` 在保存网页前生成摘要或译文

让语言模型把网页信息压缩、解释或翻译，再把结果写入采集笔记。

**扩展｜第三方服务／本地模型路线 · 有来源支持。** 需要 Web Clipper Interpreter、模型提供方或本地模型及相应设置；云端可能需要 API 凭据和费用。模型结果需人工核对，发送内容的隐私取决于所选模型路线。

来源：[s-interpreter：Obsidian Help — Interpreter](https://obsidian.md/help/web-clipper/interpreter)。

### `p-reading-highlights` 把跨阅读来源的划线汇入知识库

把 Readwise 账户中的阅读划线和相关信息持续导入 Obsidian，纳入自己的阅读资料。

**扩展｜第三方服务／本地模型路线 · 有来源支持。** 需要 Readwise 团队的插件、账户、付费订阅和网络；导入源以 Readwise 当前支持为准。旧 README 列出的 Pocket/Twitter 等名称不能证明对应外部连接器今天仍有效。

来源：[s-readwise：Readwiseio/obsidian-readwise — README.md](https://github.com/readwiseio/obsidian-readwise/blob/master/README.md)。


<a id="g-connect"></a>
## 连接、找回与重用已有知识

### `p-knowledge-network` 建立能双向追溯的知识网络

把概念、人物和资料相互链接，并从当前笔记回查引用它的其他笔记及未链接的提及。

**内置 · 有来源支持。** 启用 Backlinks；引用与未链接提及依赖笔记内容和名称。链接主要在同一 vault 内生效，关联不代表事实正确。

来源：[s-links：Obsidian Help — Internal links](https://obsidian.md/help/links)；[s-backlinks：Obsidian Help — Backlinks](https://obsidian.md/help/plugins/backlinks)。

### `p-visual-network` 可视化浏览知识关联与孤立笔记

在全库或局部关系图里查看链接结构，筛选要浏览的笔记与未连接节点。

**内置 · 有来源支持。** 启用 Graph view 并有笔记链接；孤立节点筛选可辅助人工补链，图形本身不证明概念间因果。

来源：[s-graph：Obsidian Help — Graph view](https://obsidian.md/help/plugins/graph)。

### `p-retrieve-notes` 从大量笔记中找回指定信息

用词句、路径、标签、属性条件和正则表达式缩小检索范围，找回相关笔记内容。

**内置 · 有来源支持。** 启用 Search；正文搜索范围是笔记与 Canvas，不是所有 PDF、扫描件或 Office 附件；被排除的文件不参与搜索。

来源：[s-search：Obsidian Help — Search](https://obsidian.md/help/plugins/search)。

### `p-reuse-content` 在多份文档里复用同一份资料

嵌入原笔记、标题段落、块或媒体，使引用位置随源文件更新。

**内置 · 有来源支持。** 使用内部嵌入链接；源文件必须仍可访问。远程图片或网页仍依赖网络，导出和发布的呈现需单独检查。

来源：[s-embeds：Obsidian Help — Embed files](https://obsidian.md/help/embeds)。

### `p-refactor-notes` 把零散记录整理成可复用的主题笔记

合并重复记录，或从长文抽出独立笔记，逐步调整知识库的粒度。

**内置 · 有来源支持。** 启用 Note composer；合并会改动和移除源笔记，应保留独立备份。官方明确合并时更新指向合并笔记的链接。

来源：[s-refactor：Obsidian Help — Note composer](https://obsidian.md/help/plugins/note-composer)。

### `p-semantic-rediscovery` 按含义重新发现没有手工链接的旧笔记

用向量相似性在当前工作附近找回语义相关资料，减少只能依靠相同关键词检索的限制。

**扩展｜社区插件 · 有来源支持。** 安装 Smart Connections、建立索引并配置嵌入模型；当前作者说明默认本地嵌入，部分 Pro 界面另付费。是否上传内容取决于具体模型设置，未验证召回率或大库性能。

来源：[s-semantic：brianpetro/obsidian-smart-connections — README.md](https://github.com/brianpetro/obsidian-smart-connections/blob/main/README.md)。

### `p-attachment-search` 把部分图片与附件文字纳入检索

用文字提取插件获取图片或文档内容，再由 Omnisearch 等工具检索。

**扩展｜社区插件 · 有来源支持。** Text Extractor README 明示 Unmaintained，PDF 常失败，移动端不执行提取；OCR 语言资源需联网下载，已生成缓存可同步。须另装 Omnisearch 才得到该检索界面；不承诺全格式或当前版本可用。

来源：[s-ocr：scambier/obsidian-text-extractor — README.md](https://github.com/scambier/obsidian-text-extractor/blob/master/README.md)；[s-omnisearch：scambier/obsidian-omnisearch — README.md](https://github.com/scambier/obsidian-omnisearch/blob/master/README.md)。


<a id="g-study"></a>
## 阅读、学习与开展研究

### `p-pdf-reading` 阅读 PDF 并把证据位置链接到笔记

在内置阅读器查阅 PDF，把页码或具体选区链接纳入自己的阅读笔记。

**内置 · 有来源支持。** 具体选区引用、复制引文和 PDF 内搜索按帮助页限桌面端；内置阅读器未宣称可添加 PDF 高亮批注。移动端 PDF 导出另见正式版更新证据。

来源：[s-pdf：Obsidian Help — PDFs](https://obsidian.md/help/pdf)。

### `p-read-alongside` 在笔记旁对照阅读网页资料

在应用内打开外部网页并与笔记分栏，减少研究时来回切换窗口。

**内置 · 有来源支持。** 本文仅确认文档中的桌面端 Web viewer；1.15.1 移动端仍属早期访问。本功能访问网页需网络，不是完整浏览器替代品。

来源：[s-web-viewer：Obsidian Help — Web viewer](https://obsidian.md/help/plugins/web-viewer)。

### `p-academic-network` 建立可以反复检索的文献与研究想法网络

把论文、主题、概念和研究设想分别建档并关联，在研究工作中重新找到相关文献。

**扩展｜社区插件 · 有来源支持。** 作者案例含自定义 Notebook Navigator 分支、Supercharged Links 和改造的 Citations；使用其完整界面和导入流程需相应版本与配置。不能把其个人规模或效率当通用性能保证。

来源：[s-academic-case：Emile van Krieken — How I use Obsidian for academic work](https://www.emilevankrieken.com/blog/2025/academic-obsidian/)。

### `p-experiment-record` 把实验过程和分析背景放在同一研究档案里

围绕研究项目记录实验协议、结果及分析笔记，减少相关记录分散。

**扩展｜社区插件 · 有来源支持。** 来源为生物医学博士生自报使用的案例库，附模板、插件和 CSS/JavaScript；同帖后续仍记录运行问题。本轮只确认这种记录结果有案例，不确认整包目前即装即用或具备合规电子实验记录系统能力。 基础文字记录本身也可用内置编辑器完成，此项扩展标签指作者完整案例库路线。

来源：[s-research-case：Science Research Vault — author showcase](https://forum.obsidian.md/t/science-research-vault-a-structured-workflow-for-academics/95589)。

### `p-archive-prototype` 用本地资料库试作社区档案的关联描述

在可离线访问的原型中链接、解释和查找档案材料，并保留社区自己的描述术语。

**内置 · 有来源支持。** 案例为 Rematriation 项目；事先数字化、整理和导入文件由研究团队完成。此项是档案描述原型，不承诺原生扫描、OCR、标准档案导出或自动实现数据主权。

来源：[s-archive-teaching：Long & Yunes — From Notes to Networks](https://journal.code4lib.org/articles/18535)。

### `p-teach-relations` 用真实资料向团队讲清元数据关系

把人物、事件和来源变成可浏览的链接笔记，帮助非专业参与者讨论和检查数据建模。

**内置 · 有来源支持。** 案例还使用外部表格准备资料，并在后续迁往 Wikibase；本项限可视化讨论和原型验证，不等同于自动生成合规 RDF/LOD 数据。

来源：[s-archive-teaching：Long & Yunes — From Notes to Networks](https://journal.code4lib.org/articles/18535)。

### `p-spaced-study` 按间隔复习笔记和自制记忆卡

把学习内容制成卡片或复习笔记，由插件安排后续复习。

**扩展｜社区插件 · 有来源支持。** 安装 Spaced Repetition 并按其格式制作学习材料；算法安排不是记忆效果保证，也不意味着已与 Anki 双向同步。

来源：[s-spaced：st3v3nmw/obsidian-spaced-repetition — README.md](https://github.com/st3v3nmw/obsidian-spaced-repetition/blob/main/README.md)。

### `p-zotero-material` 把文献管理器中的引文和批注接入阅读笔记

从 Zotero 引入书目信息、引文、笔记和 PDF 批注，供写作与文献阅读使用。

**扩展｜社区插件 · 有来源支持。** 依赖 Zotero Integration、Zotero、Better BibTeX，以及导入模板/引用样式设置。仓库已转至 community-archive（取回时 archived=false）；不保证当前 Zotero/Better BibTeX/Obsidian 组合兼容。

来源：[s-zotero：community-archive/obsidian-zotero-integration — README.md](https://github.com/community-archive/obsidian-zotero-integration/blob/main/README.md)。

### `p-pdf-annotation` 把 PDF 高亮和自己的旁注互相连通

通过链接选区形成高亮关联，把自己的 Markdown 解释与 PDF 证据放在一起。

**扩展｜社区插件 · 有来源支持。** 安装 PDF++；反向链接高亮与直接写入 PDF 的批注有不同保存方式。作者说明依赖私有 API，升级可能破坏功能；直接写回 PDF 也有限制，不能把全部高亮当可移植原文件批注。

来源：[s-pdf-plus：RyotaUshio/obsidian-pdf-plus — README.md](https://github.com/RyotaUshio/obsidian-pdf-plus/blob/main/README.md)。

### `p-ai-reading` 围绕正在阅读的内容向 AI 提问

对选中的文字发问，并把回答插入、替换或复制到自己的写作中。

**扩展｜社区插件 · 有来源支持。** 需要 Copilot 和可用模型路线：已有代理账户、模型 API 或本地模型；托管模型可能需要付费。插件本身与模型/服务费用需区分，答案不自带正确性保证。

来源：[s-copilot：logancyang/obsidian-copilot — README.md](https://github.com/logancyang/obsidian-copilot/blob/master/README.md)。


<a id="g-write"></a>
## 形成文稿并交付给读者

### `p-consistent-records` 按统一结构建立会议、读书和项目记录

复用预设文字及标题、日期、时间变量，减少重复输入并保持记录结构一致。

**内置 · 有来源支持。** 启用 Templates 并自行准备模板；例中的会议、读书和项目是模板内容的应用，内置模板不会自动抓取外部资料或执行复杂逻辑。

来源：[s-templates：Obsidian Help — Templates](https://obsidian.md/help/plugins/templates)。

### `p-technical-documents` 撰写包含图解和数学表达的技术文档

在笔记中呈现 Mermaid 流程或时序图，以及用 MathJax 渲染的数学表达式。

**内置 · 有来源支持。** 需编写相应文本语法；不是完整 LaTeX 排版或公式求解器。具体语法支持跟随 Obsidian 捆绑的渲染版本。

来源：[s-technical-writing：Obsidian Help — Advanced formatting syntax](https://obsidian.md/help/advanced-syntax)。

### `p-present-notes` 直接把笔记作为幻灯演示

用一份分段的 Markdown 笔记向听众逐页展示内容。

**内置 · 有来源支持。** 启用 Slides 并用分隔线组织页面；不据此保证 PowerPoint 文件导出或完整演讲者工具。

来源：[s-slides：Obsidian Help — Slides](https://obsidian.md/help/plugins/slides)。

### `p-share-pdf` 把笔记导出为可直接分发的 PDF

将当前记录或文章转成 PDF，发给没有 Obsidian 的读者。

**内置 · 有来源支持。** 桌面端 PDF 导出见 PDF 帮助页；移动端需 Obsidian 1.15+。旧 PDF 帮助页关于移动端不可导出的文字与此新正式版日志冲突，以新日志为准；排版未实测。

来源：[s-mobile-release：Obsidian 1.15 Mobile (Public)](https://obsidian.md/changelog/2026-11-02-mobile-v1.15.0/)；[s-pdf：Obsidian Help — PDFs](https://obsidian.md/help/pdf)。

### `p-story-draft` 从故事卡片发展到分场景长篇初稿

先在视觉板梳理故事，再把场景发展为章节，保留结构与素材之间的联系。

**内置 · 有来源支持。** 作者展示基础工作流并另谈 Longform；文章把卡片界面称作 Graph View，与官方文档的 Canvas 不符，此处按官方 Canvas 解释，不沿用其界面命名。编译成连贯稿件另见 Longform 扩展项。

来源：[s-novel-case：Iain F Macleod — How to Write a Novel in Obsidian](https://www.iainfmacleod.com/how-to-write-a-novel-in-obsidian/)；[s-canvas：Obsidian Help — Canvas](https://obsidian.md/help/plugins/canvas)。

### `p-compile-manuscript` 把分场景草稿编成顺序连贯的稿件

按场景顺序组织长篇创作，并通过编译流程输出合并的手稿。

**扩展｜社区插件 · 有来源支持。** 安装 Longform 并配置项目、场景顺序和编译流程；它不自动承诺 Word/ePub 交付格式、在线协作或出版级排版。

来源：[s-longform：kevboh/longform — README.md](https://github.com/kevboh/longform/blob/main/README.md)。

### `p-ai-vault-work` 结合库资料撰写和整理笔记

让配置好的代理读取相关笔记、使用工具，并在权限控制下创建或修改知识库文件。

**扩展｜社区插件 · 有来源支持。** Copilot 桌面 Agent Chat 依赖所选外部代理/适配器、账户或 API/本地模型；移动端聊天不能推定具备同等多步改文件能力。需审核修改；不保证完整引用、正确推理或任意自动化成功。

来源：[s-copilot-agent：logancyang/obsidian-copilot — docs/agent-mode-and-tools.md](https://github.com/logancyang/obsidian-copilot/blob/master/docs/agent-mode-and-tools.md)。

### `p-deliver-manuscript` 把 Markdown 稿件交付为 Word 或电子书等格式

借助转换器把笔记内容导成 DOCX、ePub 等对方需要的文档格式。

**扩展｜第三方工具 · 有来源支持。** 需要桌面 Pandoc 插件、另装 Pandoc 及正确路径；部分目标格式还需排版引擎或模板。作者标明 beta 且可能有格式问题，必须检查输出；不承诺复杂嵌入和插件块无损转换。

来源：[s-pandoc：OliverBalfour/obsidian-pandoc — README.md](https://github.com/OliverBalfour/obsidian-pandoc/blob/master/README.md)。


<a id="g-visual"></a>
## 以空间和图解组织解释

### `p-visual-synthesis` 把多种资料整理成可浏览的视觉思考板

在二维画布上并置笔记、图片、附件和网页，以连线和分组梳理结构。

**内置 · 有来源支持。** 启用 Canvas；数据为 .canvas / JSON Canvas。纯文本卡片和笔记不是同一种对象，画布连线也不等于自动生成笔记内部链接。

来源：[s-canvas：Obsidian Help — Canvas](https://obsidian.md/help/plugins/canvas)。

### `p-sketch-knowledge` 把手绘图解和文字知识相互连接

在库中绘制和编辑草图，再嵌入笔记并与相关文档或其他图解建立链接。

**扩展｜社区插件 · 有来源支持。** 安装 Obsidian Excalidraw；图解格式、导出和跨设备编辑需按所用版本核对。手写识别或 AI 生成不是本项承诺。

来源：[s-excalidraw：zsviczian/obsidian-excalidraw-plugin — README.md](https://github.com/zsviczian/obsidian-excalidraw-plugin/blob/master/README.md)。

### `p-data-charts` 在知识笔记中展示可交互的数据图表

把自己提供的数据绘为图表，供笔记阅读时查看。

**扩展｜社区插件 · 有来源支持。** 安装 Charts 并遵循其图表数据格式及选项；与 Tracker 从日志提取记录不同，本项为通用笔记内图表呈现。具体交互和导出效果未实测。

来源：[s-charts：Phibr0/obsidian-charts — README.md](https://github.com/phibr0/obsidian-charts/blob/master/README.md)。

### `p-guided-canvas` 沿设定路径讲解画布上的资料结构

把同一画布组织成可切换的演示步骤，向观众逐段讲解复杂主题。

**扩展｜社区插件 · 有来源支持。** 需要 Advanced Canvas 及 Canvas；与 Slides 的线性 Markdown 演示不同，此项保留空间资料板。增强格式与功能在其他 JSON Canvas 工具或 Publish 中是否保留需另核对。

来源：[s-canvas-presentation：Developer-Mike/obsidian-advanced-canvas — README.md](https://github.com/Developer-Mike/obsidian-advanced-canvas/blob/main/README.md)。


<a id="g-work"></a>
## 管理项目、记录和行动

### `p-collections` 把项目、书单或收藏整理成动态目录

把一条记录对应一篇笔记，用表格、卡片等视图统一查看、编辑、排序和筛选属性。

**内置 · 有来源支持。** 启用 Bases 并维护笔记属性；数据仍在文件与属性内。不能据此等同于关系数据库的事务、权限或任意跨表联接。

来源：[s-bases：Obsidian Help — Introduction to Bases](https://obsidian.md/help/bases)。

### `p-derived-information` 从记录属性计算费用、时间和优先级

用 Bases 计算字段把已有属性转成总成本、日期差或排序所需的评分。

**内置 · 有来源支持。** 需自行设置公式及输入字段；结果依赖数据质量，公式字段并不意味着自动把计算结果写回 Markdown 属性。

来源：[s-formulas：Obsidian Help — Formulas](https://obsidian.md/help/formulas)。

### `p-progress-board` 用看板推进项目或内容的状态

把项目或稿件笔记按状态分列，拖动卡片更新笔记的分组属性。

**内置 · 有来源支持。** Bases Kanban 需要 Obsidian 1.14+；要有分组属性。按公式或多数 file 属性分组时不能拖动写回；不能把所有旧版看板教程直接视为现行内置能力。

来源：[s-kanban：Obsidian Help — Kanban view](https://obsidian.md/help/bases/views/kanban)。

### `p-client-context` 把客户、联系人、商机和沟通汇成客户全貌

从客户页面集中查看相关会议、机会、联系人、待办及其他提及。

**扩展｜社区插件 · 有来源支持。** 作者明确需要 Templater、Dataview、模板和持续一致的记录习惯；动态汇总需要配置。此个人销售案例不证明多人 CRM、自动邮件同步或可靠提醒。

来源：[s-crm-case：Muted-Temperature212 — My take on using Obsidian as a CRM](https://www.reddit.com/r/ObsidianMD/comments/1clswlh/my_take_on_using_obsidian_as_a_crm/)。

### `p-computed-dashboard` 把分散在笔记里的结构化信息汇成看板

按字段、条件和分组生成动态列表、表格或任务汇总，作为项目或阅读仪表板。

**扩展｜社区插件 · 有来源支持。** 需要 Dataview、适当的 frontmatter/行内字段及查询；不同于 Bases 的文件属性编辑视图，此处强调可写入笔记正文的计算查询结果。动态块依赖插件，不能假设 Publish 会执行。

来源：[s-dataview：blacksmithgu/obsidian-dataview — README.md](https://github.com/blacksmithgu/obsidian-dataview/blob/master/README.md)。

### `p-task-workflow` 集中处理散落各处的到期与重复待办

跨笔记查询任务，按日期等条件组织，并在汇总处完成任务、更新原记录。

**扩展｜社区插件 · 有来源支持。** 安装 Tasks 并按其任务格式和过滤设置使用；该结果不自动等于系统推送提醒、外部日历双向同步或多人任务调度。

来源：[s-tasks：obsidian-tasks-group/obsidian-tasks — README.md](https://github.com/obsidian-tasks-group/obsidian-tasks/blob/main/README.md)。

### `p-calendar-context` 把日程事件和上下文笔记连在一起

在日历中查看事件，为每个事件保留一篇可链接的说明或会议笔记。

**扩展｜社区插件 · 有来源支持。** Full Calendar 可读笔记属性、日记事件及只读 ICS/CalDAV 日历；远程日历需服务地址与可能的凭据。仓库取回时 archived=true，未验证当前 Obsidian 兼容性；不能据此声称可靠双向同步。

来源：[s-calendar：community-archive/obsidian-full-calendar — README.md](https://github.com/community-archive/obsidian-full-calendar/blob/main/README.md)。


<a id="g-life"></a>
## 安排生活并保存个人世界

### `p-daily-log` 按日期积累日记、工作日志与随手发现

每天在固定日期笔记中连续记录当天的想法、事项和经历，供之后回顾。

**内置 · 有来源支持。** 启用 Daily notes；可选择模板和存放路径。周月汇总与提醒不是此项自动提供的结果。

来源：[s-daily：Obsidian Help — Daily notes](https://obsidian.md/help/plugins/daily-notes)。

### `p-campaign-wiki` 把桌游战役的世界和跑团记录组织成可查资料

把战役纲要、人物、地点和场次记录存为相互链接的主持人或玩家资料库。

**内置 · 有来源支持。** 公开案例以笔记、属性、标签、模板及 Bases 组织战役；本项基础记录不要求某个特定社区插件。套用作者库前仍需查看库内配置；未运行样例，不保证第三方游戏资料可再分发。

来源：[s-rpg-case：dclasair/ttrpg-campaign-vault — README.md](https://github.com/dclasair/ttrpg-campaign-vault/blob/main/README.md)。

### `p-family-archive` 把家谱导成可读的人物档案和家族图

从 GEDCOM 生成每人一篇的 Markdown、媒体链接及 Canvas 家族图，保留可读的家族资料。

**扩展｜第三方工具 · 有来源支持。** 依赖作者单独编写的 GEDCOM 转换脚本，不是原生导入格式；作者称为一次性个人用途，Canvas 导出不完美。未验证它兼容其他 GEDCOM 数据或维护状态。

来源：[s-genealogy-case：Alexander Kucera — Genealogy in Obsidian](https://alexanderkucera.com/2025/11/03/genealogy-in-obsidian.html)。

### `p-travel-dossier` 建立随身可查的旅行行程资料包

把地点、行程、事件和准备事项集中在旅行库，出行时查阅已保存的资料。

**扩展｜社区插件 · 有来源支持。** 作者案例需 Dataview、Map View、Meta Bind、Tasks、List Callouts 及同步方案。文本可本地查阅不等于地图瓦片、路线服务或远程图片也可离线使用；同行共享需另配同步。

来源：[s-travel-case：wallaburton45 — Obsidian Travel Planner](https://forum.obsidian.md/t/obsidian-travel-planner-your-offline-trip-planner/100934)。

### `p-geographic-notes` 按地理位置浏览地点和相关笔记

把带坐标的笔记显示为地图标记，从地点进入相应资料。

**扩展｜官方另装插件 · 有来源支持。** 需 Obsidian 1.10+、Bases 和另装官方 Maps 插件，并填入坐标属性；地图图层与地理服务的网络、费用和可用性需检查。

来源：[s-maps：Obsidian Help — Map view](https://obsidian.md/help/bases/views/map)。

### `p-journal-trends` 把日志里的习惯和数值变成趋势记录

从日期笔记提取习惯、心情或收支等已有字段，用图表回看变化。

**扩展｜社区插件 · 有来源支持。** 安装 Tracker、统一日志字段并编写查询图表配置；它不会自动获取银行或健康设备数据，也不提供医学或财务判断。

来源：[s-tracker：pyrochlore/obsidian-tracker — README.md](https://github.com/pyrochlore/obsidian-tracker/blob/master/README.md)；[s-tracker-examples：pyrochlore/obsidian-tracker — docs/Examples.md](https://github.com/pyrochlore/obsidian-tracker/blob/master/docs/Examples.md)。

### `p-meal-planning` 从菜谱安排餐食并汇总采购清单

把菜谱笔记排入周计划，按所需食材合并购物清单。

**扩展｜社区插件 · 有来源支持。** 安装 Recipe Box 并提供结构化食材和份量；站点导入与分享可能依赖外部服务，应另核对。此项只确认作者文档中的本地计划与清单功能，未实测单位换算或移动端表现。

来源：[s-recipe：Adam Tommasi — Recipe Box](https://community.obsidian.md/plugins/recipe-box)。


<a id="g-steward"></a>
## 保有、保护和共同维护资料

### `p-local-knowledge` 保有可离线使用、可迁出的个人知识库

把笔记保存在本机文件夹，以普通文本继续编辑，并在需要时迁移到其他工具。

**内置 · 有来源支持。** 本地 Markdown 文件；附件也需存于本地。链接、Canvas、Bases 和插件专用语法在其他工具中的表现需另行核对；本地文件不自动获得加密或备份。

来源：[s-local：Obsidian Help — How Obsidian stores data](https://obsidian.md/help/data-storage)；[s-offline：Obsidian Help — Import notes](https://obsidian.md/help/import)。

### `p-local-recovery` 找回误删或误改的笔记内容

从设备保存的定期笔记快照中恢复旧内容，减少意外编辑造成的损失。

**内置 · 有来源支持。** 启用 File recovery；快照有保留期限，位于 vault 外且依设备与原路径关联，不会随 Sync 同步，也不是完整备份。

来源：[s-recovery：Obsidian Help — File recovery](https://obsidian.md/help/plugins/file-recovery)。

### `p-git-history` 为知识库保留可比较的版本记录和远程副本

在 Obsidian 内提交变更、比较差异并把库推到自己的 Git 远程仓库。

**扩展｜社区插件 · 有来源支持。** 需要 Git 插件、仓库、远程凭据与相应环境；作者明确移动端高度不稳定。冲突、忽略规则和备份策略需自行管理，不能把自动 push 等同于完整备份。

来源：[s-git：Vinzent03/obsidian-git — README.md](https://github.com/Vinzent03/obsidian-git/blob/master/README.md)。

### `p-multi-device` 在自己的多台设备间延续笔记工作

通过 Obsidian Sync 同步笔记和所选文件，在桌面与移动设备间接续使用。

**扩展｜官方付费服务 · 有来源支持。** 需要付费 Sync 订阅、账户和网络，按计划有空间/文件等限制；端到端加密设置及密码管理需核对。同步不是独立备份，不建议同目录叠加多个同步器。

来源：[s-sync：Obsidian Help — Introduction to Obsidian Sync](https://obsidian.md/help/sync)。

### `p-team-vault` 与团队共同维护同一组知识文件

邀请协作者接入共享远程库，各自本地编辑并同步团队资料。

**扩展｜官方付费服务 · 有来源支持。** 所有协作者都需要有效 Sync 订阅；不支持细粒度权限，也不支持同一文件的实时协同光标编辑。并发修改可能产生合并或冲突，不等同于网页协作文档。

来源：[s-shared-vault：Obsidian Help — Collaborate on a shared vault](https://obsidian.md/help/sync/collaborate)。

### `p-restore-history` 从同步历史恢复旧笔记或附件

查看文件以前的版本，找回误改内容或已删除的已同步资料。

**扩展｜官方付费服务 · 有来源支持。** 需要 Sync 且文件曾被同步；保留期限依订阅计划，不能保证永久版本历史；本地 File recovery 与该服务分开。

来源：[s-sync-versions：Obsidian Help — Version history](https://obsidian.md/help/sync/version-history)。


<a id="g-publish"></a>
## 发布和管理知识网站

### `p-publish-site` 把选定笔记发布为可浏览的知识网站

把选定的知识资料变成读者可在浏览器访问的维基、文档或数字花园。

**扩展｜官方付费服务或第三方工具 · 有来源支持。** 两条有证据的路线：①付费 Obsidian Publish：需要订阅、账户与网络，由服务托管；②第三方 Quartz 5：需要 Node 22+、npm 10.9.2+，自行配置构建和静态托管，托管可能另收费。二者均不能假设运行所有社区插件；按平台检查格式、附件和交互。

来源：[s-publish：Obsidian Help — Introduction to Obsidian Publish](https://obsidian.md/help/publish)；[s-quartz：Quartz 5 — Welcome](https://quartz.jzhao.xyz/)。

### `p-limited-readers` 用站点密码向有限读者分享已发布知识

在 Publish 网站设置访问密码，让知道密码的人读取站点内容。

**扩展｜官方付费服务 · 有来源支持。** 需要 Publish 订阅；是全站密码，不支持给单篇笔记设置独立密码，也不等同于按人按页授权或端到端加密发布。

来源：[s-publish-password：Obsidian Help — Publish Security and privacy](https://obsidian.md/help/publish/security)。

### `p-publish-pipeline` 把知识网站更新接入定时或构建流程

在无桌面环境通过 Headless Publish 发布最新文件，使知识网站更新成为流水线的一步。

**扩展｜官方付费服务 · 有来源支持。** Obsidian Headless 仍为开放测试，需 Node 22+、Publish 订阅、认证和外部调度/CI；本轮未执行发布，也不承诺服务稳定性或自动审核内容。

来源：[s-headless-publish：Obsidian Help — Headless Publish](https://obsidian.md/help/publish/headless)。


<a id="g-integrate"></a>
## 把知识库接入工作流与计算实验

### `p-cross-app-workflow` 让其他应用和脚本向知识库采集或检索资料

用应用链接或桌面命令，把建笔记、追加内容和搜索串入既有工作流。

**内置 · 有来源支持。** URI 需正确编码和本机 Obsidian；CLI 需桌面应用运行并注册命令，官方要求 1.12 安装器，安装指引建议 1.12.7+。定时器及外部应用需自行配置。

来源：[s-cli：Obsidian Help — Obsidian CLI](https://obsidian.md/help/cli)；[s-uri：Obsidian Help — Obsidian URI](https://obsidian.md/help/uri)。

### `p-capture-workflow` 把重复采集和建档串成一次工作流

把收集输入、按模板建笔记、追加日志等动作组合起来，重复处理同类记录。

**扩展｜社区插件 · 有来源支持。** 需要 QuickAdd 并配置 choice、宏或表单；查书籍数据、运行脚本、调用 AI 等步骤有各自外部依赖。此项不保证任意工作流无需编程。

来源：[s-quickadd：chhoumann/quickadd — README.md](https://github.com/chhoumann/quickadd/blob/master/README.md)。

### `p-server-vault` 让服务器工作流取得持续更新的知识库副本

在不运行桌面应用的环境同步库文件，供自建 CI、备份或代理工具读取。

**扩展｜官方付费服务 · 有来源支持。** 使用 Obsidian Headless 开放测试版，需 Node 22+、Sync 订阅和认证；同一设备不要并用桌面 Sync 与 Headless Sync。下游工具、调度和处理逻辑需自行搭建。

来源：[s-headless-sync：Obsidian Help — Headless Sync](https://obsidian.md/help/sync/headless)。

### `p-executable-notes` 在技术笔记中运行实验代码并查看结果

执行笔记中的代码块，把运行输出留在学习或计算过程的上下文中。

**扩展｜社区插件 · 有来源支持。** Execute Code manifest 声明仅桌面，minAppVersion 1.7.2；需对应解释器/编译器和配置路径。Python/R 等图形依运行库；不是所有环境都可用，也不是原生代码高亮即能执行。

来源：[s-execute：twibiral/obsidian-execute-code — README.md](https://github.com/twibiral/obsidian-execute-code/blob/master/README.md)。

## 待验证与未计入的诉求

以下没有被混入确认的 P 数量；现有来源不足以支撑完整承诺：

- **从任意已有长会议录音自动形成带说话人与回跳时间戳的纪要**：现有 iOS 实时口述转写证据不足以证明完整流程，未完成相关插件/模型组合的专门验证。
- **可靠双向维护任意远程日历**：选取的 Full Calendar 文档仅确认只读 ICS/CalDAV；其他插件或服务组合未核验。
- **在完全无网环境持续进行地图与路线导航**：本地地点笔记不等于离线地图瓦片、地理编码或路线服务。

## 资料覆盖、发现过程与缺口

### 从哪里发现

- 官方产品、价格、正式版更新日志与帮助文档；另从官方英文仓库取回 45 篇正文，用来核对核心功能、移动端和服务边界。
- 插件作者文档、官方社区目录、服务说明、示例及少量 manifest/仓库元数据。没有把搜索摘要、下载量或最佳软件榜单当作能力证明。
- 作者实际案例包括学术文献网络、生物医学实验档案、两项图书馆/数字人文项目、小说创作、跑团、家谱、客户关系与旅行规划。案例是作者陈述或公开成品，不是本轮复现。

### 怎样形成这张地图

先按结果、真实示例和扩展三个视角提取无分类候选，再归一化名称、比较同义结果与边界，最后才建立分组。临时记录先保存 64 个无分组候选；把 Publish 与 Quartz 合并为同一“发布知识网站”结果，保留两条路线。书单、项目目录和收藏清单没有各拆一个 P，单个插件选项、图表样式也没有计数。

补漏时另查了生活记录、档案教学、技术笔记执行及文稿交付，随后发现的资料大多对应已有结果。停止检索不表示穷尽所有插件或用途。JSON 中保留查询词、三轮发现记录、候选归一化决策、失败/重定向说明和未解决问题。

### 必须保留的冲突与限制

- **版本冲突**：PDF 帮助页仍称移动端不能导出；1.15 正式版日志已明确可导出。因此导出项采用新日志，但不顺带推断移动端已获得 PDF 内搜索或选区引用。
- **维护风险**：Full Calendar 的 GitHub 元数据取回时为归档状态；Text Extractor README 明示停止维护；Zotero Integration 已转至 community-archive，其 API 字段取回时仍为未归档。组织名、最近提交时间和可下载均不能代替维护承诺。[日历仓库状态](https://api.github.com/repos/community-archive/obsidian-full-calendar)；[Text Extractor 作者说明](https://github.com/scambier/obsidian-text-extractor/blob/master/README.md)
- **共享边界**：Sync 共享库要求各方订阅，缺少细粒度权限及同文件实时协同；Publish 密码作用于整个站点。不要据此推为企业逐页权限系统。
- **保存边界**：本地文件、同步、副本和完整备份有区别；File recovery 也不是完整备份。[官方备份说明](https://obsidian.md/help/backup)
- **发布边界**：网站不会自动执行本机全部社区插件；特别是依赖代码块运行的动态渲染需要单独检查。[Publish 限制](https://obsidian.md/help/publish/limitations)

- source_supported 只表示具体结果有实际取回的来源支撑；没有任何 P 被本模型授予 reviewed。尚无独立人工评审。
- 未安装或运行 Obsidian、插件、转换脚本、云服务、地图图层、模型或案例库；不能保证当前平台兼容、性能、维护响应或无故障。
- 以 2026-11-05 资料快照为准；已确认 2026-11-02 桌面和移动端 1.15 正式版日志，1.15.1 的移动 Web viewer、搜索相关性排序等早期访问功能未推广为普遍能力。
- 帮助页可能滞后：PDF 帮助页仍写移动端不可导出，已用 1.15 正式版日志纠正导出项；没有据此推断其他 PDF 移动端限制也已消失。
- 插件 README 可能描述开发分支或旧版本；没有逐个核对稳定版发布包、minAppVersion、所有系统与移动端实际兼容。少量 manifest 与仓库状态只能提供观察点。
- Full Calendar 仓库归档、Text Extractor 作者声明停止维护、Zotero Integration 的仓库转移，以及 PDF++ 的私有 API 依赖均已保留；下载量或目录收录不代表维护承诺。
- 未确认任意长音频的说话人分离与时间戳会议纪要；iOS 实时口述转写不证明此目标。未确认所有远程日历的可靠双向同步。
- 未确认离线地图瓦片、离线路线计算、跨境网络可达性、模型答案引用完整性、超大库速度、历史数据无损迁移或复杂导出排版。
- 自报案例不是效果实验；不把作者个人效率或规模推为一般结论。案例的 CSS/JavaScript、模板和外部脚本未做代码或安全审计。
- 没有遍历全部社区插件，也未为每个行业单独调研法规要求或组织部署；中文排版、无障碍、输入法和地区服务情况仅零散涉及。
- 服务价格、额度、授权条款与连接器支持会变化；本图主要保留是否需要付费与配置，使用前应重新核对。

## 校验说明

结构校验使用仓库中现有的 P Discovery 校验器，另运行其测试套件及本轮来源、文档一致性和保护文件检查。实际命令、退出码与未验证项见 [validation-report.txt](validation-report.txt)。本轮没有修改 Skill 或既有实验结果，也没有安装插件、运行服务、提交或发布资料。
