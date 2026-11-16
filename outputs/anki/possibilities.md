# Anki 可能性地图

范围：学习材料、检索练习、复习调度和同步；区分桌面、移动、AnkiWeb 与插件，不承诺学习成效。

## 按用户结果浏览

### 制作与获取学习卡片

- **从图像制作遮挡检索卡**（核心）——把图像中需要记忆的区域遮住，制作基于图片的回忆卡，适用于依赖图形信息的材料。 条件：内置 Image Occlusion 自 Anki 23.10 起提供；需要图像素材。官方说明其用于测试被遮挡信息的回忆，不代表学习成效。 来源：[Adding/Editing - Anki Docs](https://docs.ankiweb.net/manual/editing)。
- **把笔记内容编成可复习卡片**（核心）——把正面和背面等内容录入笔记，Anki 根据笔记类型生成可复习卡片。 条件：使用内置笔记编辑器和卡片模板；同一笔记类型可以按模板生成卡片。 来源：[Adding/Editing - Anki Docs](https://docs.ankiweb.net/manual/editing)。
- **导入共享牌组作为学习起点**（核心）——下载其他人分享的牌组并导入到本地 Anki 集合。 条件：需要 Anki Desktop、AnkiMobile 或 AnkiDroid 先完成导入；官方手册说明不能直接把共享牌组加入 AnkiWeb。复杂主题的共享卡片可能缺少背景讲解，应补充教材或其他学习材料。 来源：[Getting Started - Anki Docs](https://docs.ankiweb.net/manual/getting-started)。

### 调度与集中复习

- **按遗忘风险安排间隔复习**（核心）——使用 FSRS 根据目标保留率安排卡片复习间隔，并可查看目标保留率变化对每日工作量的影响。 条件：FSRS 是调度算法，不是学习成效保证；官方手册列出的最低客户端版本为 Anki 23.10、AnkiMobile 23.10、AnkiDroid 2.17，AnkiWeb 支持。更高目标保留率会增加复习量。 来源：[Deck Options - Anki Docs](https://docs.ankiweb.net/manual/deck-options)。
- **临时筛选卡片进行考前或积压复习**（核心）——建立筛选牌组，集中预览新卡、考前突击、复习某些标签或处理漏复习卡片。 条件：筛选牌组按搜索条件临时挑卡；卡片学习后通常回到原牌组，是否改变排期取决于重排设置。 来源：[Filtered Decks & Cramming - Anki Docs](https://docs.ankiweb.net/manual/filtered-decks)。
- **查看复习统计并导出可分享报告**（核心）——按牌组或整个集合查看历史复习统计，并将统计窗口保存为 PDF 以便分享。 条件：官方提示单日答题正确率不宜作为总体学习进度判断；FSRS true retention 更适合看月度数据。结果记录的是 Anki 复习历史，不证明掌握或考试成绩。 来源：[Card Info, Graphs and Statistics - Anki Docs](https://docs.ankiweb.net/manual/stats)。
- **为假期或忙碌时段提前重新分配到期复习**（扩展）——使用 FSRS Helper 的 Schedule a Break，将假期期间到期的卡片分配到之后的日期。 条件：这是 open-spaced-repetition 作者维护的 Anki add-on，不是核心功能；README 要求 Anki 23.10+ 启用内置 FSRS，旧 2.1.55–2.1.66 支持已不再维护，且作者称它仅是附加工具、不建议大量使用。未运行验证。 作者明确提醒：假期重排会降低未来记忆保持率，算法只能尽量减小下降；可通过 Edit → Undo 撤销重排。 来源：[# FSRS Helper](https://github.com/open-spaced-repetition/fsrs4anki-helper/blob/29208f220f21ff994c199712a6aaac47636773bf/README.md#L43-L43)。

### 跨设备学习

- **在多个设备间同步个人卡片集合**（核心）——通过 AnkiWeb 在不同设备间同步自己的卡片集合，并可在线学习。 条件：需要免费 AnkiWeb 账户并在受支持客户端登录；首次同步要选择上传或下载，双端已有不同数据时需要谨慎处理以免丢失。音频和图片可随集合同步，但文件编辑检测有边界。 来源：[Syncing with AnkiWeb - Anki Docs](https://docs.ankiweb.net/manual/syncing)。

### 导入、备份与迁移

- **从文本表格批量更新已有笔记**（核心）——将文本或 CSV 表格导入 Anki，并按首字段匹配已有笔记；选择更新时可批量改写现有字段。 条件：字段顺序、笔记类型和匹配范围需正确；导入设置可改为忽略重复或另建新笔记。导入更新可能保留现有排期。 来源：[Text Files - Anki Docs](https://docs.ankiweb.net/manual/importing/text-files)。
- **从备份中恢复误改的卡片与排期**（核心）——打开本机自动备份或导入手动集合备份，恢复误删/误改前的卡片文本与复习排期。 条件：自动备份在本地，默认不含声音/图像，因此不能单独保护设备损坏或失窃；恢复会丢失备份后更改。含媒体的完整备份需导出 collection package 并启用媒体。 来源：[Backups - Anki Docs](https://docs.ankiweb.net/manual/backups)。
- **导出牌组或集合用于迁移和分享**（核心）——把单个牌组导出为可导入的牌组包，或将完整集合打包备份，用于转移给他人或其他配置文件。 条件：桌面版导出支持 .apkg 牌组包与 .colpkg 集合包；排期信息和媒体可按导出选项决定是否包含。导入牌组会合并内容而不是覆盖整个集合。 来源：[Exporting - Anki Docs](https://docs.ankiweb.net/manual/exporting)。

## 待验证方向

- 具体 add-on 能否在当前 Anki 桌面版本工作、是否能跨设备同步，以及具体带来的用户结果，本轮未验证。
- 自动从电子书/网页摘录生成卡片需要外部流程或特定 add-on；未找到足以证明完整稳定结果的直接来源。

## 资料覆盖与缺口

本轮覆盖官方手册的卡片编辑、FSRS/排期、筛选牌组、文本导入、同步、共享牌组、备份/恢复、导出、统计，以及一个 FSRS Helper 作者项目。FSRS 的目标保留率会影响工作量；统计数字不代表掌握或考试成绩。

没有安装或运行 Anki；所有结果按文档描述界定。AnkiWeb 账户用于同步；第三方插件不是核心功能，移动端客户端和插件支持情况可能不同。未核实价格、云存储限额、地区限制或各客户端最新版本。

## 原研究保留的未解决问题

- 未安装 Anki 或实际测试桌面、AnkiMobile、AnkiDroid、AnkiWeb 同步；不作学习结果保证。
- 未核实当前移动应用商店价格、AnkiWeb 存储限额或不同平台的收费条款。
- FSRS Helper 是单个作者 add-on 案例；未安装运行，其他 add-on 的维护、兼容和安全性未评估。
- 共享牌组内容质量、教材/出版物版权和适用地区均未逐项检查。
