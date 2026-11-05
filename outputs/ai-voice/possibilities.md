# AI 语音 可能性地图

范围：文本合成、音色与表演、转写对齐、译配、长内容和语音应用；以 ElevenLabs 当前官方文档及 Kokoro、Whisper 公开实现确认具体路线。

资料截点：2026-11-05。本图有 18 项来源支持的结果，来自 15 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

本主题没有统一平台原生能力，所有结果均标 extension 并指明服务或项目。声音使用权、模型、账户和部署条件分别适用；内容与时序需要试听和校对。

## 地图导航

- [制作朗读、对话和有声书](#production)
- [设计和调整声音表演](#performance)
- [转写与对齐语音资料](#understanding)
- [清理和译配已有内容](#adaptation)
- [把语音带入网站和自有应用](#applications)

<a id="production"></a>
## 制作朗读、对话和有声书

### `voice-01` 将文案制作成旁白与朗读音频

通过 ElevenLabs TTS 将文本转为可导出的语音，用于说明、广告或学习资料。

**扩展／具名实现路线 · 有来源支持。** 需要服务账户、额度与适用声音；支持语言和音质随模型而异，不能保证情感、读音与事实正确。

来源：[s-tts：Text to Speech · Overview；取回 Markdown第 7–7 行](https://elevenlabs.io/docs/overview/capabilities/text-to-speech.md)。

### `voice-02` 制作多角色有声对话

根据带角色的文本生成不同声音的游戏、播客或故事对话。

**扩展／具名实现路线 · 有来源支持。** Eleven Text to Dialogue；需要选定兼容模型和声音，通常需多次生成挑选，不能假定自然节奏一次成功。

来源：[s-dialogue：Text to Dialogue · Overview；取回 Markdown第 7–7 行](https://elevenlabs.io/docs/overview/capabilities/text-to-dialogue.md)。

### `voice-13` 把整部稿件制作成可编辑有声书

上传稿件、组织章节与角色声音、编辑旁白并导出或使用支持的发布路线。

**扩展／具名实现路线 · 有来源支持。** Eleven Audiobooks 项目工作流；需要内容权利、额度和完整质量审核，平台分发条件另计。

来源：[s-books：Audiobooks · Overview；取回 Markdown第 11–11 行](https://elevenlabs.io/docs/eleven-creative/products/audiobooks.md)。

<a id="performance"></a>
## 设计和调整声音表演

### `voice-03` 从文字描述设计角色声音

当现有音库不合适时，用年龄、口音和风格等描述探索并保存新声音。

**扩展／具名实现路线 · 有来源支持。** Eleven Voice Design；预览和声音槽有账户限制，生成结果可能偏离描述。

来源：[s-design：Voice Design · Overview；取回 Markdown第 13–13 行](https://elevenlabs.io/docs/eleven-creative/voices/voice-design.md)。

### `voice-04` 为自己的声音建立可复用合成版本

利用录音制作即时克隆或训练专业克隆，再用于授权内容的配音。

**扩展／具名实现路线 · 有来源支持。** 需要自己或有权使用的声音和相应验证；IVC 与 PVC 的样本、训练和付费条件不同，不保证完全复现。

来源：[s-clone：Voice Cloning · Overview；取回 Markdown第 7–7 行](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning.md)。

### `voice-05` 保持表演意图而替换录音音色

用 Voice Changer 将现有录音转成另一个声音，尝试保留情感和表达细节。

**扩展／具名实现路线 · 有来源支持。** 需要兼容语言、录音与已获授权声音；转换效果应试听。

来源：[s-changer：Voice changer · Overview；取回 Markdown第 9–9 行](https://elevenlabs.io/docs/overview/capabilities/voice-changer.md)。

### `voice-06` 补录或替换现有录音中的局部词句

通过 Voice Changer 等流程制作替换的词句，用于后期修订录音。

**扩展／具名实现路线 · 有来源支持。** 需剪辑和时序匹配，不能据此认为服务会自动无缝修复整段音频。

来源：[s-changer：Voice changer · Overview；取回 Markdown第 11–11 行](https://elevenlabs.io/docs/overview/capabilities/voice-changer.md)。

### `voice-16` 统一专名和技术词的播读方式

使用发音字典让语音代理按指定读法表达名字、地点或技术术语。

**扩展／具名实现路线 · 有来源支持。** ElevenAgents 模型支持有差异；部分模型忽略 phoneme 标签，须用别名或兼容模型并试听。

来源：[s-pronounce：Pronunciation dictionaries · Overview；取回 Markdown第 9–9 行](https://elevenlabs.io/docs/eleven-agents/customization/voice/pronunciation-dictionary.md)。

<a id="understanding"></a>
## 转写与对齐语音资料

### `voice-09` 把已知稿件与录音对齐到词句时间

在已有文本和音频时生成时间对齐稿，用于字幕或电子书有声同步。

**扩展／具名实现路线 · 有来源支持。** Forced Alignment 不是从无文本转写；需要稿件与实际录音基本对应，时间戳仍需检查。

来源：[s-align：Forced Alignment · Overview；取回 Markdown第 7–7 行](https://elevenlabs.io/docs/overview/capabilities/forced-alignment.md)。

### `voice-10` 将会议、采访或视频语音转成文本

通过语音识别生成可搜索和编辑的文字稿。

**扩展／具名实现路线 · 有来源支持。** Eleven Scribe；支持格式、语言和时长有条件，噪声、专名和口音会影响准确率。

来源：[s-stt：Transcription · Overview；取回 Markdown第 7–7 行](https://elevenlabs.io/docs/overview/capabilities/speech-to-text.md)。

### `voice-11` 获得带说话人及词级时间的信息稿

为多人录音添加说话人区分和时间标记，辅助编辑与检索。

**扩展／具名实现路线 · 有来源支持。** Scribe 对人数和模型有上限；speaker 标签不等于可靠的实名身份识别。

来源：[s-stt：Transcription · [Scribe v2](/docs/overview/models#scribe-v2)；取回 Markdown第 47–47 行](https://elevenlabs.io/docs/overview/capabilities/speech-to-text.md)。

### `voice-12` 为实时语音输入持续显示文字

通过实时 STT 连接在说话过程中返回转写，用于实时界面。

**扩展／具名实现路线 · 有来源支持。** 需要实时模型与 WebSocket 等接入；延迟和准确率不能据宣传值保证。

来源：[s-stt：Transcription · [Scribe v2 Realtime](/docs/overview/models#scribe-v2-realtime)；取回 Markdown第 59–59 行](https://elevenlabs.io/docs/overview/capabilities/speech-to-text.md)。

### `voice-18` 在本地生成多语种录音的转写或英语译稿

使用 Whisper 公开项目识别语音、做语言识别或按支持方向翻译为英文。

**扩展／具名实现路线 · 有来源支持。** 需 Python、ffmpeg 和模型资源；语言质量不同，翻译为英文不等于任意语言双向翻译。

来源：[s-whisper：OpenAI Whisper — 项目说明 · Whisper；取回 Markdown第 8–8 行](https://github.com/openai/whisper/blob/86098128c0b4f24f0e2aa2994de830614b474227/README.md#L8-L8)。

<a id="adaptation"></a>
## 清理和译配已有内容

### `voice-07` 从嘈杂音视频中分离人声

使用 Voice Isolator 提取语音，减少背景音乐、环境声等干扰。

**扩展／具名实现路线 · 有来源支持。** 服务支持特定音视频格式；失真、串音或缺失语音仍可能存在，不保证恢复不可辨识内容。

来源：[s-isolation：Voice isolator · Usage；取回 Markdown第 17–17 行](https://elevenlabs.io/docs/overview/capabilities/voice-isolator.md)。

### `voice-08` 将已有节目译配为其他语言

使用 ElevenLabs Dubbing 翻译音视频，生成目标语言配音并尽量保留说话人特征。

**扩展／具名实现路线 · 有来源支持。** 不同语言、v2 Alpha 自动配音与 v1 Dubbing Studio 的可编辑能力有差别；需审核译文和声音。

来源：[s-dubbing：Dubbing · Overview；取回 Markdown第 7–7 行](https://elevenlabs.io/docs/overview/capabilities/dubbing.md)。

<a id="applications"></a>
## 把语音带入网站和自有应用

### `voice-14` 为网站文章提供嵌入式朗读

通过 Audio Native 在自己的网页加入播放器，让读者收听正文或预生成音频。

**扩展／具名实现路线 · 有来源支持。** 需服务、HTML 接入和域名白名单；不代表所有网页访问者或浏览器均兼容。

来源：[s-native：Audio Native · Overview；取回 Markdown第 9–9 行](https://elevenlabs.io/docs/eleven-creative/audio-tools/audio-native.md)。

### `voice-15` 构建可以听说并执行任务的语音助手

结合 ElevenAgents 的模型、工具、知识和会话连接，制作电话、网页或移动语音交互。

**扩展／具名实现路线 · 有来源支持。** 独立代理产品与外部工具／电话服务共同实现；需开发与评估，语音生成本身没有业务执行能力。

来源：[s-agent：ElevenAgents · Deploy；取回 Markdown第 17–17 行](https://elevenlabs.io/docs/eleven-agents/overview.md)。

### `voice-17` 在自有环境部署轻量语音合成

使用 Kokoro 开放权重和代码制作自己的朗读服务或本地项目。

**扩展／具名实现路线 · 有来源支持。** 需要安装运行栈、权重和适用语言／声音；许可需核对具体组件，本轮不承诺资源消耗或实时速度。

来源：[s-local：Kokoro-82M — 模型卡 · 页面概述；取回 Markdown第 9–9 行](https://huggingface.co/hexgrad/Kokoro-82M/raw/main/README.md)。

## 资料覆盖与发现过程

先从合成、转写和译配可交付结果提取候选，再阅读整书和网页朗读完整流程，补查本地模型与实时代理。
归一化：音频格式、语速、情感等控制并入成品语音；转写、已有文本对齐、说话人标签和实时字幕分别对应不同输入和结果。
补漏区分 voice cloning、speech-to-speech、自动配音和口型视频，后者由视频主题覆盖；不把语音模型称为完整业务代理。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未生成音频、上传录音或调用任何克隆、转写和电话服务；没有评测听感、方言准确率或延迟。
- ElevenLabs 文档部分总览与各模型的语言数表述不一致；因此不写统一支持语言数量，按模型页及部署时状态核对。
- 付费等级、声音权利、身份验证和分发条款因功能不同；本轮不作可商用、授权充分或合规保证。
- 官方 Audio Native 与 Audiobooks 提供完整任务流程；没有获取独立用户音频工程的可重复评价。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
