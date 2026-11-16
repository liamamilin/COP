# Quarto 可能性地图

范围：文档、报告、演示、网站、书籍与可执行分析；明确渲染环境、扩展与发布平台。

## 按用户结果浏览

### 研究与可执行分析

- **把可执行分析与说明渲染成可复查的报告**（核心）——在一份 Quarto 文档中组织说明文字、Python 计算和输出，并把代码运行结果渲染成报告。 条件：须安装 Quarto CLI 和所需的 Python/Jupyter 或其他语言执行环境及项目依赖。Jupyter notebook 默认不会在 render 时重新执行，需显式启用。可输出 HTML，也可按目标格式渲染 PDF/DOCX；PDF 可用 Quarto 随附的 Typst 或配置 LaTeX/其他引擎。数据、程序包和引擎版本仍需自行锁定，未在本机运行。 来源：[Using Python – Quarto](https://quarto.org/docs/computations/python.html)、[PDF Basics – Quarto](https://quarto.org/docs/output-formats/pdf-basics.html)。
- **大型项目渲染时跳过未变更文档的重复计算**（核心）——用 Quarto 的 freeze 配置缓存项目级计算结果，只在源文档变化时重新运行对应计算，缩短整个项目的批量渲染时间。 条件：这适用于项目整体渲染；单个文档或子目录的增量 render 仍会执行代码。缓存结果不是验证数据或包版本一致性的替代品；切换数据、环境或计算依赖时应有意识地刷新。 来源：[Managing Execution – Quarto](https://quarto.org/docs/projects/code-execution.html)。

### 长文与公开发布

- **把长篇内容整理成可交叉引用的多章书籍**（核心）——从多个章节文件组装一本书，并输出网站、PDF、Word、EPUB 等格式；章节编号与图表/章节引用可自动贯穿全书。 条件：使用 Quarto Book 项目结构；HTML 书可带全文搜索。PDF 输出依赖所选 PDF 引擎，其他目标格式仍需检查主题、字体和交叉引用兼容。官方文档列举 R for Data Science、Python for Data Analysis 等真实书籍项目作为范例；本研究未重建。 来源：[Creating a Book – Quarto](https://quarto.org/docs/books/)、[Book Structure – Quarto](https://quarto.org/docs/books/book-structure.html)。
- **将研究论文与可查看的计算过程一起发布**（核心）——用 Manuscript 项目发布一篇论文网页，同时提供 LaTeX/Word/PDF 等审稿格式、相关 notebook 和用于生成结果的计算过程。 条件：研究稿项目会产出网站；读者可在浏览器查看 notebook、代码和输出。期刊模板、字体和精确投稿格式需按目标期刊要求自行检查，Quarto 不负责投稿或保证接受。示例页面展示了下载 Word、AGU 模板 PDF 与 notebook 的实际组织方式，但未作为作者客户结果验证。 来源：[Quarto Manuscripts – Quarto](https://quarto.org/docs/manuscripts/)。
- **把多篇文档整理为带导航和搜索的网站**（核心）——把多个报告、文章或博客放进同一个 Quarto Website，共享导航和视觉风格，并启用全文搜索供读者查找内容。 条件：网站通常是渲染后的静态输出，可部署到 GitHub Pages、Netlify、Posit Connect 或其他静态托管服务；若页面嵌入需要后端的交互应用，部署条件会改变。需要管理导航、搜索索引、静态资源和版本更新。 来源：[Creating a Website – Quarto](https://quarto.org/docs/websites/)。
- **每次提交后自动渲染并更新 GitHub Pages 网站**（扩展）——将 Quarto 文档或项目连接 GitHub Pages；通过 GitHub Action 在源代码推送后自动渲染并发布站点。 条件：需要 Git 仓库、GitHub Pages 配置以及正确的工作流权限/发布分支或 Pages Actions 配置。工作流要能安装 Quarto、执行所需语言代码并获得发布权限。Pages 是外部托管服务；公开访问与私有站点功能按 GitHub Pages 规则，未实测本仓库或核价。 来源：[GitHub Pages – Quarto](https://quarto.org/docs/publishing/github-pages.html)。

### 演示与仪表板

- **从一份 Markdown 内容制作演示文稿**（核心）——用 Markdown 标题拆分幻灯片，并选择 Reveal.js 网页演示、PowerPoint 或 Beamer/PDF 输出。 条件：Reveal.js 支持网页端展示和交互样式；PowerPoint 与 Beamer 功能各异。页面版式、字体和媒体需对目标格式逐一预览，不能假定同一内容在三种格式中外观完全一致。 来源：[Presentations – Quarto](https://quarto.org/docs/presentations/)。
- **发布用图表和数据卡片组成的交互仪表板**（核心）——将多个数据可视化放入一个响应式仪表板，例如以 Gapminder 数据展示各洲 GDP/寿命散点图、人口面积图和寿命趋势图。 条件：可用 Python、R、Julia、Observable 等进行计算。静态 dashboard 可作为网页托管且不需要专用服务器；使用 Shiny Python/R 的动态应用则需要服务器或相应托管平台。交互图表与外部资源在离线/静态环境下的能力取决于具体组件。 来源：[Quarto Dashboards – Quarto](https://quarto.org/docs/dashboards/)、[Dashboard Deployment – Quarto](https://quarto.org/docs/dashboards/deployment.html)。

### 交互扩展

- **在文档里嵌入可运行和编辑的 Shiny 小应用**（扩展）——用 Shinylive 扩展在 Quarto 页面中嵌入 Python Shiny 应用，让读者调参数查看输出，也可打开代码编辑器后重新运行。 条件：这是 Quarto 扩展目录中的具名第三方扩展和维护者文档示例，不是 Quarto 核心功能。作者文档示例要求完整的 standalone 应用，并明确不能把此组件用于 self-contained HTML；页面必须保留相应资源。未安装、渲染或实测托管。 来源：[Quarto Extensions – Quarto](https://quarto.org/docs/extensions/)、[Shinylive applications embedded in Quarto documents – Quarto + Shinylive](https://quarto-ext.github.io/shinylive/)。

## 能力边界与覆盖缺口

Quarto 负责从文档/项目渲染标准格式；执行 Python/R/Julia 等代码需要本地运行时和包，PDF 需要合适的引擎。随同 Git 项目提交环境定义、输入数据和锁文件，才能让他人更可靠复现。Notebook 默认可能保留已有执行结果，若要重跑需启用执行。

dashboard 可导出静态网站，也可用 Shiny 服务器加入后端交互。Shinylive 是具名扩展示例，要求完整应用并不能用于自包含 HTML。网站发布到 GitHub Pages、Netlify、Posit Connect 或其他站点需要对应账户/发布凭据与外部服务；本轮没有发布或测试任何站点。

研究覆盖官方计算、文档/书籍/演示/网站/dashboard/发布手册和 Shinylive 维护者示例。扩展目录还包含大量社区插件，但未逐个核验兼容性、安全性和维护状态；费用、地区、目标平台版本和实际渲染质量仍需按项目验证。

## 原研究保留的未解决问题

- 没有本机安装 Quarto/Python/R/Julia/PDF 引擎、Shinylive 或扩展，也没有渲染、部署或访问真实站点。
- 可执行分析的重现性仍取决于用户固定数据、运行时、程序包、网络资源、随机种子和操作系统；Quarto 本身不自动锁定完整环境。
- PDF、PPTX、DOCX、HTML、书籍和交互 widget 的功能并非完全一致；期刊模板/字体、TeX/Typst 依赖和无障碍输出需逐项目核查。
- GitHub Pages、Netlify、Posit Connect、Quarto Pub 等的账户、访问控制、费用、地区和服务限制未核实；Shiny 发布需外部服务器/托管。
- 扩展作者、社区扩展维护与安全状态未逐个审核；Shinylive 是文档充分的具名示例，不代表其他扩展兼容。
