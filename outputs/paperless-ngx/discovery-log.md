# Paperless-ngx 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `paper-01`｜结果视角｜把扫描件变成能搜索和选中文字的文档｜s-index
2. `paper-02`｜结果视角｜保留原件并建立长期归档副本｜s-index
3. `paper-03`｜结果视角｜按来源和文档用途建立个人档案库｜s-index
4. `paper-04`｜结果视角｜在文档内容中检索所需信息｜s-index
5. `paper-05`｜结果视角｜在单一条目下管理文件的多个版本｜s-index
6. `paper-06`｜结果视角｜自动从邮件收集附件文档｜s-usage
7. `paper-07`｜结果视角｜按事件自动分配元数据和后续动作｜s-usage
8. `paper-08`｜结果视角｜通过有期限的链接分享文件｜s-usage
9. `paper-09`｜结果视角｜为不同用户控制文档可见性和编辑权｜s-usage
10. `paper-10`｜结果视角｜记录发票号、付款日期等业务字段｜s-usage
11. `paper-11`｜结果视角｜在文档界面整理 PDF 页面｜s-usage
12. `paper-12`｜结果视角｜从既有标注学习自动归类文档｜s-advanced
13. `paper-13`｜结果视角｜利用模型辅助填写文档元数据｜s-advanced
14. `paper-14`｜结果视角｜找到与当前文档相关的既有档案｜s-advanced
15. `paper-15`｜结果视角｜对单份或一组档案提问并查看引用文档｜s-advanced
16. `paper-16`｜结果视角｜批量扫描时自动按分隔条码拆件｜s-advanced
17. `paper-17`｜完整示例视角｜用单面扫描器整理双面文件｜s-advanced
18. `paper-18`｜结果视角｜由外部程序导入和管理档案｜s-api
19. `paper-19`｜结果视角｜导出可用于恢复或迁移的档案资料｜s-admin
20. `paper-20`｜结果视角｜将指定文档送交远程 OCR 服务｜s-configuration
21. `paper-21`｜结果视角｜把电子档案关联到纸质原件编号｜s-configuration
22. `paper-22`｜结果视角｜按元数据组织可识别的文件路径｜s-configuration
23. `paper-23`｜结果视角｜将办公文档纳入同一检索档案库｜s-faq
24. `paper-24`｜结果视角｜在消费后识别和处理重复文件｜s-faq
25. `paper-25`｜补漏视角｜从回收站恢复尚未清除的误删文档｜s-usage

## 归一化、补漏与停止依据

从官方功能总览发现纸张到可检索档案的结果，接着读取推荐扫描流程、双面扫描例子和 API，再核对新 AI 与 v3 行为。
归一化：多个入口合并为收集结果；PDF 页面动作合并为整理，标签和字段按实际档案用途解释。
补漏发现文件版本、嵌套标签、远程 OCR、向量检索和重复文档默认行为变化；版本未验证处保留条件；最终挑战另补入误删文件的回收站恢复。
先保留无分类候选，再按收集、查找、整理、协作和维护的实际结果建立导航。

## 保留的未知项

- 官网文档请求返回 403，改从官方 GitHub 同源 Markdown 取回；main 包含 v3 描述，不保证你的已安装稳定版／2.x 具备全部功能。
- 未部署系统、扫描实物或运行邮件、OCR、备份恢复、API 与模型；OCR 和问答准确性未实测。
- 没有把旧社区 AI 插件当成当前必需组件；当前主干自带 AI 功能入口，但本地／远程模型依赖仍要配置。
- 第三方手机应用、parser 插件和身份服务生态未逐一验证维护与兼容性，未列为无条件支持。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-admin](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/administration.md) | 2026-11-05T09:40:51.443893+00:00 | 是 |
| [s-advanced](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/advanced_usage.md) | 2026-11-05T09:40:49.918785+00:00 | 是 |
| [s-api](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/api.md) | 2026-11-05T09:40:49.665194+00:00 | 是 |
| [s-configuration](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/configuration.md) | 2026-11-05T09:40:51.569098+00:00 | 是 |
| [s-faq](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/faq.md) | 2026-11-05T09:40:51.456285+00:00 | 是 |
| [s-index](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/index.md) | 2026-11-05T09:40:49.477115+00:00 | 是 |
| [s-readme](https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/main/README.md) | 2026-11-05T09:39:48.833398+00:00 | 否 |
| [s-usage](https://github.com/paperless-ngx/paperless-ngx/blob/fc29f3511f427e365a7d6fe19b232c13445b9343/docs/usage.md) | 2026-11-05T09:40:49.941972+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`paper-01`、`paper-02`、`paper-05`、`paper-07`、`paper-10`、`paper-22`、`paper-24`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。

为工作流事件与动作、文件版本管理补查两个已合入的维护者功能 PR，当前元数据归属仍以固定文档为准；不以 PR 的未来计划确认通知或 webhook。

- [s-workflows-pr](https://github.com/paperless-ngx/paperless-ngx/pull/5121)，取回时间 2026-11-05T10:44:04.887Z；哈希针对 PR body UTF-8，合入实现提交另记于 JSON。
- [s-versions-pr](https://github.com/paperless-ngx/paperless-ngx/pull/12061)，取回时间 2026-11-05T10:44:04.929Z；哈希针对 PR body UTF-8，合入实现提交另记于 JSON。
