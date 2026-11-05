# changedetection.io 可能性地图

范围：开源 changedetection.io 及官方托管路线的网页、文件和 JSON 变化监控；区分核心比较、浏览器取回、消息服务与可选 LLM。

资料截点：2026-11-05。本图有 19 项来源支持的结果，来自 13 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

基础监控可自托管或使用官方托管服务。JavaScript 与交互页需浏览器取回，消息渠道和 LLM 需额外依赖；抓取权限、页面可达性和轮询间隔决定覆盖。

## 地图导航

- [跟进关键内容更新](#updates)
- [筛选真正关心的变化](#relevance)
- [处理不同页面和数据来源](#access)
- [协作、通知和后续处理](#integration)

<a id="updates"></a>
## 跟进关键内容更新

### `change-01` 持续比较网页内容并查看具体改动

定期取回网页，保留变化并按词、行或字符检查前后差异。

**内置／核心能力 · 有来源支持。** 需要可取回网页和适当检查间隔；轮询可能遗漏两次检查之间的短暂变化。

来源：[s-readme：Detect Website Changes Automatically — Monitor Web Page Changes in Real Time · Easily see what changed, examine by word, line, or individual character.；取回 Markdown第 45–45 行](https://github.com/dgtlmoon/changedetection.io/blob/38e0668c1cd6b773b9f9efb50c17281974d0ba21/README.md#L45-L45)。

### `change-02` 收到商品降价或补货提示

监控商品价格与库存状态，在满足条件时获取通知并查看价格趋势。

**内置／核心能力 · 有来源支持。** 网页结构、地区、登录和抓取方式影响结果；不能保证及时通知、成功购买或始终识别价格。

来源：[s-home：Web Page Change Detection & Monitoring – Instant Alerts | changedetection.io · 页面正文；本次 HTML 提取正文第 42–42 行（不是 HTML 源码行号）](https://changedetection.io/)。

### `change-03` 跟进公告、软件发布和规则更新

监控相关发布页、机构网站或文件，发现新的公告与内容变化。

**内置／核心能力 · 有来源支持。** 需要自行选择可靠页面；监控通知不能代替订阅官方紧急通报或法律信息核验。

来源：[s-readme：Detect Website Changes Automatically — Monitor Web Page Changes in Real Time · Example use cases；取回 Markdown第 87–87 行](https://github.com/dgtlmoon/changedetection.io/blob/38e0668c1cd6b773b9f9efb50c17281974d0ba21/README.md#L87-L87)。

### `change-04` 发现招聘页面的新机会

监控公司职位页或职位列表，在目标内容出现或更新时提醒。

**内置／核心能力 · 有来源支持。** 需要页面可访问、正确筛选和合适关键词；不能保证覆盖所有职位。

来源：[s-readme：Detect Website Changes Automatically — Monitor Web Page Changes in Real Time · Example use cases；取回 Markdown第 103–103 行](https://github.com/dgtlmoon/changedetection.io/blob/38e0668c1cd6b773b9f9efb50c17281974d0ba21/README.md#L103-L103)。

### `change-05` 检查在线 PDF 的内容变化

跟踪 PDF 的文字或文件特征，判断发布文件是否更新。

**内置／核心能力 · 有来源支持。** 文本变化、大小或校验和监测各有边界；不是所有扫描 PDF 的视觉差异检测。

来源：[s-readme：Detect Website Changes Automatically — Monitor Web Page Changes in Real Time · Example use cases；取回 Markdown第 85–85 行](https://github.com/dgtlmoon/changedetection.io/blob/38e0668c1cd6b773b9f9efb50c17281974d0ba21/README.md#L85-L85)。

### `change-19` 把网页更新转成订阅源

根据监控产生的内容变化创建 RSS，以订阅工具跟进。

**内置／核心能力 · 有来源支持。** 需要实例和订阅客户端；RSS 内容受监控范围、访问与更新节奏限制。

来源：[s-readme：Detect Website Changes Automatically — Monitor Web Page Changes in Real Time · Example use cases；取回 Markdown第 99–99 行](https://github.com/dgtlmoon/changedetection.io/blob/38e0668c1cd6b773b9f9efb50c17281974d0ba21/README.md#L99-L99)。

<a id="relevance"></a>
## 筛选真正关心的变化

### `change-06` 减少无关区域变化造成的噪声

使用 CSS / XPath 或可视选择器只监控目标区域。

**内置／核心能力 · 有来源支持。** 依赖网页结构与选择器维护；元素消失、动态布局或空选择结果需排查。

来源：[s-selectors：changedetection.io Wiki · CSS Selector help · Select/extract just the HREF from `<A>` tag using xpath；取回 Markdown第 30–30 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/CSS-Selector-help.md)。

### `change-07` 在目标词出现时获得提示

为新闻、报告等页面设置关键词触发，关注指定实体或事件。

**内置／核心能力 · 有来源支持。** 需要页面发生变化且命中相应规则；旧有词或未取回内容不一定触发。

来源：[s-keywords：How To Monitor Keywords On Any Website | changedetection.io · How to Use Changedetection.io to Monitor Specific Keywords；本次 HTML 提取正文第 18–18 行（不是 HTML 源码行号）](https://changedetection.io/tutorial/how-monitor-keywords-any-website)。

### `change-08` 只在数值或逻辑条件满足时通知

将抽取值与上下界或包含条件比较，过滤普通变化，例如官方极端温度示例。

**内置／核心能力 · 有来源支持。** 需要正确抽取目标数字和配置逻辑；这是规则判断，不是预测或安全预警系统。

来源：[s-conditions：Conditional actions on web page changes! | changedetection.io · 页面正文；本次 HTML 提取正文第 20–20 行（不是 HTML 源码行号）](https://changedetection.io/tutorial/conditional-actions-web-page-changes)。

### `change-15` 把原始差异变成简明变化摘要

连接自己的模型服务，让通知附上自然语言变化说明。

**扩展／具名实现路线 · 有来源支持。** 功能入口在软件中，但需要 LLM 后端和可能的费用；摘要可能遗漏或误解，应可回看原始差异。

来源：[s-ai：AI Summary and Change Detection - Bring your own key! | changedetection.io · AI Change Summary；本次 HTML 提取正文第 19–19 行（不是 HTML 源码行号）](https://changedetection.io/tutorial/ai-summary-and-change-detection-bring-your-own-key)。

### `change-16` 让变化提醒匹配自然语言关注意图

描述自己关心的变化，由模型对检测到的差异作通知筛选。

**扩展／具名实现路线 · 有来源支持。** 需要独立模型与 API 配置；模型筛选可能误报或漏报，不把“zero noise”宣传当成保证。

来源：[s-ai：AI Summary and Change Detection - Bring your own key! | changedetection.io · AI Intent；本次 HTML 提取正文第 20–20 行（不是 HTML 源码行号）](https://changedetection.io/tutorial/ai-summary-and-change-detection-bring-your-own-key)。

<a id="access"></a>
## 处理不同页面和数据来源

### `change-09` 监控登录或交互之后才出现的内容

通过 Browser Steps 重放登录、搜索或接受提示等动作，再取回目标页。

**扩展／具名实现路线 · 有来源支持。** 需要连接 Playwright 和可自动化页面；登录状态、双重验证、CAPTCHA 与网站改版可能中断。

来源：[s-steps：changedetection.io Wiki · Browser Steps · 页面概述；取回 Markdown第 9–9 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Browser-Steps.md)。

### `change-10` 只监测 JSON 接口中相关字段

用 JSONPath 或 jq 抽取需要的数据，对特定字段或记录集变化提醒。

**内置／核心能力 · 有来源支持。** JSONPath 语法与其他库可能不同；复杂 jq 需独立依赖，系统与平台支持要核对。

来源：[s-json：changedetection.io Wiki · JSON Selector Filter help · 页面概述；取回 Markdown第 1–1 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/JSON-Selector-Filter-help.md)。

### `change-11` 发现藏在 HTML 源码中的库存或元数据变化

监测源码内嵌 JSON 或指定字段，例如官方示例中的商品数量。

**内置／核心能力 · 有来源支持。** 需要选择源码取回和提取规则；源码结构变化会影响结果，引用示例不保证商店当前仍适用。

来源：[s-html：changedetection.io Wiki · Detecting changes in HTML page sources · Approach；取回 Markdown第 10–10 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Detecting-changes-in-HTML-page-sources.md)。

### `change-12` 在页面引用另一张图片时提醒

比较 HTML 中图片地址变化，例如月历图片从一个文件名换成另一个。

**内置／核心能力 · 有来源支持。** 这是图片引用的文本变化，不是图片像素相似度检测；同一 URL 图像内容改变未必可见。

来源：[s-images：changedetection.io Wiki · Detecting changes in images · 页面概述；取回 Markdown第 6–6 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Detecting-changes-in-images.md)。

<a id="integration"></a>
## 协作、通知和后续处理

### `change-13` 把变化通知发送到常用消息渠道

配置 Apprise 支持的邮件、聊天等通知目标，收到变化内容和链接。

**扩展／具名实现路线 · 有来源支持。** 需要外部服务凭据与目标配置；长度、设备和服务错误可能导致漏发，不能保证送达。

来源：[s-notifications：changedetection.io Wiki · Notification configuration notes · ARMv7 (RaspberryPi 3 etc)；取回 Markdown第 5–5 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Notification-configuration-notes.md)。

### `change-14` 在发现变化后触发自定义系统

使用 HTTP POST 通知把结果发往 webhook 或后续业务流程。

**扩展／具名实现路线 · 有来源支持。** 需要自建接收端及相应鉴权；外部业务效果与幂等、重试另行实现。

来源：[s-notifications：changedetection.io Wiki · Notification configuration notes · POST/POSTS；取回 Markdown第 37–37 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Notification-configuration-notes.md)。

### `change-17` 与他人复用已经调好的监控规则

生成 shared watch 链接，让另一实例导入 URL、过滤和触发配置。

**内置／核心能力 · 有来源支持。** 需评估链接暴露的信息和实例可访问性，导入后仍需配置私人凭据及通知目标。

来源：[s-sharing：changedetection.io Wiki · Sharing a Watch · 页面概述；取回 Markdown第 3–3 行](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Sharing-a-Watch.md)。

### `change-18` 从程序批量管理监控与读取历史

通过 REST API 创建、更新监控并读取快照或变化，接入自有系统。

**扩展／具名实现路线 · 有来源支持。** 需要开发调用方、正确 URL 和 API key；版本契约与授权需核查。

来源：[s-api：changedetection.io REST API reference · 页面正文；本次 HTML 提取正文第 8–8 行（不是 HTML 源码行号）](https://changedetection.io/docs/api_v1/index.html)。

## 资料覆盖与发现过程

先从维护者实际列出的监控结果发现，再读关键词、极端温度、HTML 商品数量等完整教程，补查 JSON、通知和 AI。
归一化：将各平台的通知渠道合为一个结果，价格和库存合并为购物监控；源码数据与图片引用保留清楚边界。
补漏发现当前新增的自带模型 Key 的 AI 摘要与意图筛选；不把宣传的零噪声和即时检测当作保证。
观察到 Case Studies 页为空、旧教程网址失效；改沿官方 Wiki 和当前教程导航追溯，不以首页列举的用途冒充独立用户验证。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 官方 docs 入口部分返回 403，改读维护者 README、Wiki、API 和教程；Case Studies Wiki 只有 Coming soon，未作为真实成功案例。
- 未部署监控或运行定时、登录、通知和模型；没有通知时延、准确率或反爬兼容的实测。
- 图片 Wiki 只支持以源码引用变化实现特定监测，不能泛化为像素视觉回归。
- Twitter、网页商店及第三方代理示例年代不同，当前网站规则、凭据和服务维护状态未验证。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
