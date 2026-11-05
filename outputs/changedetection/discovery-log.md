# changedetection.io 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `change-01`｜结果视角｜持续比较网页内容并查看具体改动｜s-readme
2. `change-02`｜结果视角｜收到商品降价或补货提示｜s-home
3. `change-03`｜结果视角｜跟进公告、软件发布和规则更新｜s-readme
4. `change-04`｜结果视角｜发现招聘页面的新机会｜s-readme
5. `change-05`｜结果视角｜检查在线 PDF 的内容变化｜s-readme
6. `change-06`｜结果视角｜减少无关区域变化造成的噪声｜s-selectors
7. `change-07`｜完整示例视角｜在目标词出现时获得提示｜s-keywords
8. `change-08`｜完整示例视角｜只在数值或逻辑条件满足时通知｜s-conditions
9. `change-09`｜结果视角｜监控登录或交互之后才出现的内容｜s-steps
10. `change-10`｜结果视角｜只监测 JSON 接口中相关字段｜s-json
11. `change-11`｜完整示例视角｜发现藏在 HTML 源码中的库存或元数据变化｜s-html
12. `change-12`｜结果视角｜在页面引用另一张图片时提醒｜s-images
13. `change-13`｜结果视角｜把变化通知发送到常用消息渠道｜s-notifications
14. `change-14`｜结果视角｜在发现变化后触发自定义系统｜s-notifications
15. `change-15`｜结果视角｜把原始差异变成简明变化摘要｜s-ai
16. `change-16`｜结果视角｜让变化提醒匹配自然语言关注意图｜s-ai
17. `change-17`｜结果视角｜与他人复用已经调好的监控规则｜s-sharing
18. `change-18`｜结果视角｜从程序批量管理监控与读取历史｜s-api
19. `change-19`｜结果视角｜把网页更新转成订阅源｜s-readme

## 归一化、补漏与停止依据

先从维护者实际列出的监控结果发现，再读关键词、极端温度、HTML 商品数量等完整教程，补查 JSON、通知和 AI。
归一化：将各平台的通知渠道合为一个结果，价格和库存合并为购物监控；源码数据与图片引用保留清楚边界。
补漏发现当前新增的自带模型 Key 的 AI 摘要与意图筛选；不把宣传的零噪声和即时检测当作保证。
观察到 Case Studies 页为空、旧教程网址失效；改沿官方 Wiki 和当前教程导航追溯，不以首页列举的用途冒充独立用户验证。

## 保留的未知项

- 官方 docs 入口部分返回 403，改读维护者 README、Wiki、API 和教程；Case Studies Wiki 只有 Coming soon，未作为真实成功案例。
- 未部署监控或运行定时、登录、通知和模型；没有通知时延、准确率或反爬兼容的实测。
- 图片 Wiki 只支持以源码引用变化实现特定监测，不能泛化为像素视觉回归。
- Twitter、网页商店及第三方代理示例年代不同，当前网站规则、凭据和服务维护状态未验证。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-ai](https://changedetection.io/tutorial/ai-summary-and-change-detection-bring-your-own-key) | 2026-11-05T09:48:31.964687+00:00 | 是 |
| [s-api](https://changedetection.io/docs/api_v1/index.html) | 2026-11-05T09:39:51.766240+00:00 | 是 |
| [s-cases](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Case-Studies.md) | 2026-11-05T09:48:29.852845+00:00 | 否 |
| [s-conditions](https://changedetection.io/tutorial/conditional-actions-web-page-changes) | 2026-11-05T09:48:31.877933+00:00 | 是 |
| [s-home](https://changedetection.io/) | 2026-11-05T09:47:15.076823+00:00 | 是 |
| [s-html](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Detecting-changes-in-HTML-page-sources.md) | 2026-11-05T09:48:31.365795+00:00 | 是 |
| [s-images](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Detecting-changes-in-images.md) | 2026-11-05T09:48:29.839520+00:00 | 是 |
| [s-javascript](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Run-JavaScript-before-change-detection.md) | 2026-11-05T09:48:31.360047+00:00 | 否 |
| [s-json](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/JSON-Selector-Filter-help.md) | 2026-11-05T09:48:29.866505+00:00 | 是 |
| [s-keywords](https://changedetection.io/tutorial/how-monitor-keywords-any-website) | 2026-11-05T09:48:33.263899+00:00 | 是 |
| [s-notifications](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Notification-configuration-notes.md) | 2026-11-05T09:48:29.975005+00:00 | 是 |
| [s-readme](https://github.com/dgtlmoon/changedetection.io/blob/38e0668c1cd6b773b9f9efb50c17281974d0ba21/README.md) | 2026-11-05T09:39:49.418200+00:00 | 是 |
| [s-recipes](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Recipes.md) | 2026-11-05T09:48:29.974112+00:00 | 否 |
| [s-selectors](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/CSS-Selector-help.md) | 2026-11-05T09:48:31.368005+00:00 | 是 |
| [s-sharing](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Sharing-a-Watch.md) | 2026-11-05T09:48:31.754190+00:00 | 是 |
| [s-steps](https://raw.githubusercontent.com/wiki/dgtlmoon/changedetection.io/Browser-Steps.md) | 2026-11-05T09:48:29.845944+00:00 | 是 |
| [s-wiki](https://github.com/dgtlmoon/changedetection.io/wiki) | 2026-11-05T09:39:50.638740+00:00 | 否 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`change-06`、`change-07`、`change-11`、`change-12`、`change-15`、`change-16`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
