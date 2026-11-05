# AI 音乐制作 可能性地图

范围：从作曲草稿、旋律与歌词、编曲和演唱到分轨、MIDI、母带和 DAW 交付；按 Suno、Lyria、Synthesizer V、MusicGen、Basic Pitch、Demucs 与 LANDR 的具名路线确认。

资料截点：2026-11-05。本图有 22 项来源支持的结果，来自 19 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

这是多个软件和模型共同组成的领域地图，所有条目标 extension 并明确路线。服务账户、软件／声音库、权重、硬件、素材权利和导出条件分别适用。

## 地图导航

- [从创意和素材发展音乐](#creation)
- [延展与重构既有作品](#revision)
- [制作演唱和声音编排](#vocals)
- [分离、转写和母带交付](#post)
- [制作采样与交互演出](#interactive)

<a id="creation"></a>
## 从创意和素材发展音乐

### `music-01` 把音乐想法变成歌曲草稿

用风格、主题、乐器等文字描述，让 Suno 生成可试听歌曲。

**扩展／具名实现路线 · 有来源支持。** 需要服务账户及额度；生成时长、下载权和模型依当前计划，不保证按提示精确作曲。

来源：[s-simple：Make a song in Simple Mode · Make a song in Simple Mode；本次 HTML 提取正文第 16–16 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/2462273)。

### `music-02` 给自己的歌词谱成歌

把已有歌词输入 Custom 模式，生成包含这些文字的音乐版本。

**扩展／具名实现路线 · 有来源支持。** Suno；需拥有歌词权利并核对漏词、改词、发音和段落结构。

来源：[s-lyrics：Can I use my own lyrics? · 页面正文；本次 HTML 提取正文第 16–16 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/2415873)。

### `music-03` 生成无主唱的伴奏音乐

使用 Lyria 的器乐生成路线，为内容或创作提供纯器乐素材。

**扩展／具名实现路线 · 有来源支持。** 需要兼容模型、账户和 API；不是自动获得任意商用许可。

来源：[s-lyria-md：Generate music with Lyria 3.5 · Generate instrumental tracks  {% id="instrumental" %}；取回 Markdown第 1248–1248 行](https://aistudio.google.com/docs/music-generation.md)。

### `music-04` 以图片引导音乐氛围

向 Lyria 提供图像作为音乐创意输入，生成与场景气氛相关的音频。

**扩展／具名实现路线 · 有来源支持。** 图像与声响的关系由模型解释，不保证精确同步视觉事件。

来源：[s-lyria-md：Generate music with Lyria 3.5 · Generate music from images  {% id="image-to-music" %}；取回 Markdown第 760–760 行](https://aistudio.google.com/docs/music-generation.md)。

### `music-05` 让音乐围绕段落和时间要求展开

以 Lyria 支持的歌词时间和结构描述约束生成，制作更符合编排意图的版本。

**扩展／具名实现路线 · 有来源支持。** 需要当前模型支持；节拍、时长与结构仍需试听核查。

来源：[s-lyria-md：Generate music with Lyria 3.5 · Control timing and structure  {% id="timing" %}；取回 Markdown第 1116–1116 行](https://aistudio.google.com/docs/music-generation.md)。

### `music-07` 把录下的旋律或节奏发展成完整素材

上传原创录音或鼓循环，以它为起点生成新伴奏或歌曲。

**扩展／具名实现路线 · 有来源支持。** Suno 官方示例使用鼓循环续写；需要拥有录音权利和符合当前上传限制。

来源：[s-upload：What does Upload Audio do? · What does Upload Audio do?；本次 HTML 提取正文第 16–16 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/2477633)。

### `music-12` 把已有 MIDI 想法发展成配器音乐

将 MIDI 乐段上传 Suno Create，听取更完整的乐器编排或歌曲方案。

**扩展／具名实现路线 · 有来源支持。** 官方当前文档限桌面网页及 Pro / Premier；不能保证每个音符严格照谱演奏。

来源：[s-midi-in：Using MIDI files in Create · 页面正文；本次 HTML 提取正文第 11–11 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/14594177)。

### `music-20` 在自有环境尝试旋律条件音乐生成

使用 MusicGen 代码和对应权重，从文字或旋律条件生成器乐素材。

**扩展／具名实现路线 · 有来源支持。** 需要匹配模型、音频预处理与硬件；代码和权重许可证不同，应核对非商用等限制，不保证当前依赖可直接安装。

来源：[s-musicgen：AudioCraft · MusicGen · API；取回 Markdown第 53–53 行](https://github.com/facebookresearch/audiocraft/blob/896ec7c47f5e5d1e5aa1e4b260c4405328bf009d/docs/MUSICGEN.md#L53-L53)。

<a id="revision"></a>
## 延展与重构既有作品

### `music-06` 延长歌曲或重做结尾

选择保留的片段和续写起点，生成并拼接新段落。

**扩展／具名实现路线 · 有来源支持。** Suno Extend；拼接、和声和声音延续效果需核查，不保证无缝。

来源：[s-extend：How do I make my song longer? · 页面正文；本次 HTML 提取正文第 15–15 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/2409601)。

### `music-08` 保持旋律方向而尝试另一种风格

使用 Covers 为自己的既有作品生成不同风格的版本。

**扩展／具名实现路线 · 有来源支持。** Suno 文档标为 Beta，限自身创建作品及相应付费计划；可能需要多次尝试。

来源：[s-cover：What is a Cover? · 页面正文；本次 HTML 提取正文第 17–17 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/2872257)。

### `music-09` 替换歌曲中间的歌词或音乐段落

通过 Replace Section 对选定区间重生成，再形成更新的整曲。

**扩展／具名实现路线 · 有来源支持。** 需要支持该功能的付费计划；交界、演唱和歌词应对照检查。

来源：[s-replace：Can I replace a section of a song? · 页面正文；本次 HTML 提取正文第 15–15 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/3271873)。

### `music-16` 以自有歌曲建立风格模型

上传拥有权利的歌曲，在 Suno 建立私有 Custom Model 用于后续创作。

**扩展／具名实现路线 · 有来源支持。** 当前官方说明有歌曲数量、模型数量与付费限制；不是导出通用可下载模型的保证。

来源：[s-custom：Using Custom Models · 页面正文；本次 HTML 提取正文第 15–15 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/11362497)。

<a id="vocals"></a>
## 制作演唱和声音编排

### `music-13` 按谱制作可精细控制的合成人声

用 Synthesizer V Studio 2 Pro 控制音高、音色、表情和音素，制作演唱或参考 demo。

**扩展／具名实现路线 · 有来源支持。** 需要软件、歌声数据库与相应授权；可在本机运行，实际硬件表现和发音需试听。

来源：[s-singing-full：Synthesizer V Studio 2 Pro - Professional AI Vocal Synthesizer · 页面正文；本次 HTML 提取正文第 13–13 行（不是 HTML 源码行号）](https://dreamtonics.com/synthesizerv/)。

### `music-14` 为歌曲制作和声与背景人声编排

以 Synthesizer V 制作多层和声、伴唱及不同演唱风格，供混音使用。

**扩展／具名实现路线 · 有来源支持。** 需要编写旋律与声部、调整混合及音色；不等于自动完成整首歌曲编曲。

来源：[s-singing-full：Synthesizer V Studio 2 Pro - Professional AI Vocal Synthesizer · 页面正文；本次 HTML 提取正文第 36–36 行（不是 HTML 源码行号）](https://dreamtonics.com/synthesizerv/)。

### `music-15` 让自己的声音用于生成的歌曲

先建立个人声音档案，再在 Suno 生成作品时选择该声音。

**扩展／具名实现路线 · 有来源支持。** 需要自己的录音、服务验证和功能可用性；不代表可以未经许可复制他人声音。

来源：[s-voice：Voices: Use Your Voice in Suno · Voices: Use Your Voice in Suno；本次 HTML 提取正文第 15–15 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/11362369)。

<a id="post"></a>
## 分离、转写和母带交付

### `music-10` 把混音拆成可独立处理的声部

使用 Suno Stem Separation 分离人声、鼓、贝斯等，供重混与后期。

**扩展／具名实现路线 · 有来源支持。** 不同分离模式与计划限制适用；残留串音和分离伪影无法排除。

来源：[s-stems：Advanced Stem Separation · 页面正文；本次 HTML 提取正文第 16–16 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/12702337)。

### `music-11` 把录音旋律转成可编辑 MIDI

用 Basic Pitch 从音频估计音高和音符，生成含弯音信息的 MIDI。

**扩展／具名实现路线 · 有来源支持。** 需安装公开项目；一件乐器效果通常更合适，多声部混音和复杂音色可能出错。

来源：[s-midi：Basic Pitch — Spotify 音频转 MIDI 项目 · 页面概述；取回 Markdown第 14–14 行](https://github.com/spotify/basic-pitch/blob/fa5997af0a8210982619003269994a1be25eddf3/README.md#L14-L14)。

### `music-17` 为已完成混音制作母带版本

使用 LANDR 分析上传混音并调整均衡、压缩、响度等，试听后导出母带。

**扩展／具名实现路线 · 有来源支持。** 商业母带服务；需比较不同播放设备，不保证满足所有平台规范或优于人工处理。

来源：[s-mastering：AI Mastering | Online Audio Mastering - Try Free | LANDR · 页面正文；本次 HTML 提取正文第 102–102 行（不是 HTML 源码行号）](https://www.landr.com/online-audio-mastering)。

### `music-21` 将生成项目带回 DAW 继续制作

从 Suno Studio 导出整曲、指定时段、分轨或可用的 MIDI，进入现有混音和配器流程。

**扩展／具名实现路线 · 有来源支持。** 相应 Studio 权限、导出额度和转 MIDI 费用适用；MIDI 是估计结果，须检查。

来源：[s-export：Exporting from Studio · 页面正文；本次 HTML 提取正文第 20–20 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/13925249)。

### `music-22` 在本地从已有歌曲分离伴奏与人声

运行 Demucs 公开实现，将音频拆分为鼓、贝斯、人声等分轨。

**扩展／具名实现路线 · 有来源支持。** 需要安装和计算资源；原 Meta 仓库明确已停止维护，新 fork 仅处理重要修复；当前 Python / 模型兼容性未实测，不保证分离无伪影。

来源：[s-demucs：Demucs v4 — 项目说明与维护状态 · Demucs Music Source Separation；取回 Markdown第 18–19 行](https://github.com/facebookresearch/demucs/blob/e976d93ecc3865e5757426930257e200846a520a/README.md#L18-L19)。

<a id="interactive"></a>
## 制作采样与交互演出

### `music-18` 生成独立乐器采样和环境声音素材

使用 Suno Sounds 生成短采样、声效或氛围素材，供音乐制作使用。

**扩展／具名实现路线 · 有来源支持。** 官方标为实验功能；计划、长度与导出条件适用，版权和听感需核查。

来源：[s-sounds：Suno Sounds: Generate Custom Audio Samples · Overview；本次 HTML 提取正文第 17–17 行（不是 HTML 源码行号）](https://help.suno.com/en/articles/10625537)。

### `music-19` 以实时交互持续引导器乐演出

用 Lyria RealTime 在流式会话中调整音乐方向，构建 Prompt DJ 或 MIDI DJ 类应用。

**扩展／具名实现路线 · 有来源支持。** 实验模型，需要持久连接、客户端及额度，不保证低延迟或适合现场演出的稳定性。

来源：[s-realtime：Real-time music generation using Lyria RealTime · Real-time music generation using Lyria RealTime；取回 Markdown第 17–17 行](https://aistudio.google.com/docs/realtime-music-generation.md)。

## 资料覆盖与发现过程

先发现完整歌曲、歌词、录音和 MIDI 等输入可得到的结果，再阅读鼓循环扩展、实时 DJ 和 DAW 导出的完整流程。
归一化：将风格与乐器提示归入歌曲生成，分离、转写、模型训练与母带保留为不同交付结果；本地与托管分轨路线因部署条件差异分别说明。
补漏检索发现新的 MIDI 输入、声音档案与 Custom Model；以当前文章的账户、版本和权利限制收敛结果，不把宣传百分比当作质量保证。
按实际发现的创作、修订、演唱和后期目的整理，不按模型名预先分类。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未生成或上传音频，未安装 DAW 插件与本地模型，未评价旋律、音乐性、音高和分轨质量。
- 未核实所有生成音频的商用、训练素材、表演者和样本权利；需依输入、模型和当前服务条款判断。
- Suno 部分旧文章仍标 Beta，当前页面也出现新模型与下载规则；未假设旧版权益永久有效。
- Eleven Music 当前文档提示 music_v1 将于 2027-01-31 移除；其相似结果在去重时归入已有音乐生成／编辑用途，没有扩写成重复条目。
- Demucs 原仓库明确不再维护，fork 也仅处理重要修复；MusicGen 依赖兼容及真实工作站性能未做安装验证。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
