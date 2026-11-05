# Playwright 可能性地图

范围：Playwright 浏览器自动化和 Playwright Test 的可交付结果；官方 Node.js 测试文档为主，另标 axe 与 AI Test Agents 的扩展依赖。

资料截点：2026-11-05。本图有 18 项来源支持的结果，来自 18 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

核心浏览器自动化不依赖 AI 服务。AI Test Agents 和 axe 是额外路线；测试能否发现错误取决于用例、断言、环境与数据。

## 地图导航

- [验证用户与接口行为](#behavior)
- [覆盖浏览器、环境与可访问性](#coverage)
- [发现与调查回归](#debugging)
- [生产和运行测试集](#production)
- [提取页面内容与交付文档](#artifacts)

<a id="behavior"></a>
## 验证用户与接口行为

### `pw-01` 自动验证用户的网页操作流程

将导航、点击、填写和页面断言组织成可重复的端到端测试。

**内置／核心能力 · 有来源支持。** 需要测试数据和明确断言；自动等待减少时序问题，不保证没有不稳定测试。

来源：[s-writing-tests：Playwright · Writing tests · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/writing-tests)。

### `pw-04` 在已登录状态下稳定验证业务流程

保存与复用认证状态，配合隔离上下文测试用户身份相关功能。

**内置／核心能力 · 有来源支持。** 状态文件含敏感凭据；会修改服务端共享数据的并行测试应使用不同账户。

来源：[s-auth：Playwright · Authentication · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/auth)。

### `pw-05` 脱离真实后端测试前端异常和边界

拦截请求、返回预设响应或重放 HAR，构造慢响应、错误与特定数据场景。

**内置／核心能力 · 有来源支持。** 需要自定义模拟数据；Service Worker 等场景需参考文档限制，不证明真实后端可用。

来源：[s-network：Playwright · Network · 页面正文；本次 HTML 提取正文第 11–11 行（不是 HTML 源码行号）](https://playwright.dev/docs/network)。

### `pw-06` 验证 REST API 并准备端到端测试数据

直接发送 HTTP 请求验证接口，建立前置状态并检查 UI 操作后的服务端结果。

**内置／核心能力 · 有来源支持。** APIRequestContext 与浏览器 UI 分层使用；需要可访问接口和授权。

来源：[s-api-testing：Playwright · API testing · 页面正文；本次 HTML 提取正文第 8–8 行（不是 HTML 源码行号）](https://playwright.dev/docs/api-testing)。

### `pw-14` 验证文件下载并保存生成的交付物

监听网页下载，将文件保存后检查其内容或用于后续处理。

**内置／核心能力 · 有来源支持。** 需等待下载完成并明确保存路径；默认临时下载随上下文关闭删除。

来源：[s-downloads：Playwright · Downloads · 页面正文；本次 HTML 提取正文第 7–7 行（不是 HTML 源码行号）](https://playwright.dev/docs/downloads)。

### `pw-15` 验证用户上传与复杂表单输入

自动选择上传文件、填写控件并测试相关交互结果。

**内置／核心能力 · 有来源支持。** 需要受支持 DOM 控件、测试文件和后续断言。

来源：[s-input：Playwright · Actions · Upload files；本次 HTML 提取正文第 91–91 行（不是 HTML 源码行号）](https://playwright.dev/docs/input)。

<a id="coverage"></a>
## 覆盖浏览器、环境与可访问性

### `pw-02` 检查同一应用在不同浏览器中的表现

在 Chromium、WebKit、Firefox 上重复运行流程，发现引擎兼容问题。

**内置／核心能力 · 有来源支持。** 需要安装相应浏览器和系统依赖；WebKit 不等于所有真实 Safari 设备。

来源：[s-intro：Playwright · Installation · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/intro)。

### `pw-03` 验证移动布局与地区环境差异

模拟视口、触摸、位置、语言、时区等条件，检查响应式和本地化行为。

**内置／核心能力 · 有来源支持。** 模拟设备参数不是完整真机认证；需选取与产品目标相符的配置。

来源：[s-emulation：Playwright · Emulation · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/emulation)。

### `pw-09` 把常见无障碍问题纳入自动回归

用 axe 扩展扫描页面，把缺少标签、颜色对比等可自动检测问题变成测试结果。

**扩展／具名实现路线 · 有来源支持。** 依赖额外 axe 包；自动检测不能替代人工无障碍评估和用户测试。

来源：[s-accessibility-testing：Playwright · Accessibility testing · Introduction；本次 HTML 提取正文第 11–11 行（不是 HTML 源码行号）](https://playwright.dev/docs/accessibility-testing)。

### `pw-10` 检查多环境与多身份的同一业务行为

以测试项目矩阵对已登录／未登录、staging／production 等运行同组用例。

**内置／核心能力 · 有来源支持。** 需要隔离账号、数据和有副作用的生产测试；项目配置本身不提供环境。

来源：[s-test-projects：Playwright · Projects · Introduction；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/test-projects)。

<a id="debugging"></a>
## 发现与调查回归

### `pw-07` 从 CI 失败记录还原网页操作过程

打开记录的 Trace，沿操作、页面状态和相关信息排查失败。

**内置／核心能力 · 有来源支持。** 必须在运行中启用并保留 trace；查看器不自动提供根因。

来源：[s-trace-viewer：Playwright · Trace viewer · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/trace-viewer)。

### `pw-08` 发现界面截图的视觉回归

建立基准图并比较后续截图，检测布局、样式和渲染改变。

**内置／核心能力 · 有来源支持。** 基准和测试环境应一致；系统、字体和浏览器差异可能造成噪声。

来源：[s-test-snapshots：Playwright · Visual comparisons · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/test-snapshots)。

<a id="production"></a>
## 生产和运行测试集

### `pw-11` 缩短大型测试集的执行等待

在可用 CPU 上并行测试，并按需要将测试分片到多台机器。

**内置／核心能力 · 有来源支持。** 需要 CI 资源、隔离数据及适当分片策略；不保证线性加速。

来源：[s-test-sharding：Playwright · Sharding · Introduction；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/test-sharding)。

### `pw-12` 生成适合人工和 CI 消费的测试报告

将测试结果输出为 HTML、JSON 或其他报告，供排查和流水线处理。

**内置／核心能力 · 有来源支持。** 需要保留构建产物；报告格式与自定义集成依具体版本而定。

来源：[s-test-reporters：Playwright · Reporters · HTML reporter；本次 HTML 提取正文第 130–130 行（不是 HTML 源码行号）](https://playwright.dev/docs/test-reporters)。

### `pw-13` 把手工操作记录为可维护测试起点

通过 Codegen 在真实网页交互中生成脚本与定位器，再补充断言和测试设计。

**内置／核心能力 · 有来源支持。** 录制结果需要审查和维护，不自动成为完整覆盖。

来源：[s-codegen-intro：Playwright · Generating tests · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/codegen-intro)。

### `pw-17` 借助 AI 工具形成并维护网页测试

使用官方 planner、generator、healer 工作流，从探索计划到生成和修复测试。

**扩展／具名实现路线 · 有来源支持。** 需要相应 AI 代理环境、初始化和模型；应核实修复没有掩盖产品错误，不是确定性测试库自动保证正确。

来源：[s-test-agents：Playwright · Playwright Test Agents · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://playwright.dev/docs/test-agents)。

<a id="artifacts"></a>
## 提取页面内容与交付文档

### `pw-16` 从已渲染页面提取任务所需数据

在页面环境运行 JavaScript，读取 DOM 或应用状态并把可序列化结果带回程序。

**内置／核心能力 · 有来源支持。** 这是浏览器自动化路线，需自行实现页面选择、访问和数据校验；不是开箱即用全站爬虫。

来源：[s-evaluating：Playwright · Evaluating JavaScript · Introduction；本次 HTML 提取正文第 7–7 行（不是 HTML 源码行号）](https://playwright.dev/docs/evaluating)。

### `pw-18` 把网页输出为可分享的 PDF

使用页面打印布局生成 PDF，供报告、归档或文档交付。

**内置／核心能力 · 有来源支持。** 需支持该方法的浏览器环境；打印 CSS、字体、分页与颜色需另检查。

来源：[s-page：Playwright · Page · 页面正文；本次 HTML 提取正文第 893–893 行（不是 HTML 源码行号）](https://playwright.dev/docs/api/class-page)。

## 资料覆盖与发现过程

先遍历实际测试结果，再阅读认证、网络、文件、报告与完整示例，最后补查可选 AI 和无障碍扩展。
归一化：将定位、等待和具体输入动作并入端到端结果；并行和分片合并为缩短大型测试等待。
发现后才按验证对象、失败调查和测试生产维护整理；跨浏览器、仿真与真实设备的边界独立记录。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 没有在本次研究中实测全部浏览器、设备参数和第三方测试集成。
- 无障碍、性能与安全的完整审计不能从端到端测试通过推导。
- Electron、真实手机和通用全站采集没有足够的本轮证据，未作为确认能力扩写；PDF 仅依据已取回的 Page API，不代表所有浏览器均支持。
- 真实任务证据以官方 API 测试、认证、网络与 Codegen 完整示例为主，未以项目流行度代替任务效果证据。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
