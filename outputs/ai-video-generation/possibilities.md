# AI 视频生成 可能性地图

范围：跨产品的生成、编辑、讲述、翻译、后期和制作交付可能性；每项只确认具名厂商或公开项目支持的路线。

资料截点：2026-11-05。本图有 22 项来源支持的结果，来自 18 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

这是技术领域地图，没有统一“内置”平台，所有确认结果均标为 extension 并指明路线。账户、额度、地区、模型、输入权利及后期审核条件分别适用。

## 地图导航

- [构思与生成镜头](#shots)
- [编辑、配音和规格调整](#revision)
- [制作商业叙事素材](#marketing)
- [制作讲述与角色体验](#presenter)
- [批量、本地与合成交付](#delivery)

<a id="shots"></a>
## 构思与生成镜头

### `video-01` 从文字或图片生成有声短片

以 Gemini Omni Flash 等具名模型，将场景描述或图像发展为短视频素材。

**扩展／具名实现路线 · 有来源支持。** 需要当前支持的模型、账户和 API；Veo 3.1 Preview 已于 2026-10-22 在 Gemini API 关闭，不能沿用旧示例。

来源：[s-google-md：Video generation in the Gemini API · Gemini Omni Flash  {% id="omni-flash" %}；取回 Markdown第 19–20 行](https://aistudio.google.com/docs/video.md)。

### `video-02` 用首尾画面约束镜头变化

提供开始与结束画面，让模型生成中间视频过渡。

**扩展／具名实现路线 · 有来源支持。** Gemini Omni 的输入限制和生成时长适用；两帧之间的动作和细节需人工核查。

来源：[s-omni：Generate and edit videos with Gemini Omni Flash · First and last frame interpolation  {% id="first-and-last-frame-interpolation" %}；取回 Markdown第 734–734 行](https://aistudio.google.com/docs/omni.md)。

### `video-03` 用参考主体引导人物或物体形象

向模型提供主体参考，使新镜头向指定外观靠拢。

**扩展／具名实现路线 · 有来源支持。** 参考图、模型和提示共同影响结果，不保证跨镜头身份或商品细节完全一致。

来源：[s-omni：Generate and edit videos with Gemini Omni Flash · Subject reference  {% id="subject-reference" %}；取回 Markdown第 945–945 行](https://aistudio.google.com/docs/omni.md)。

### `video-05` 延展已有镜头的后续内容

让模型为已有片段继续生成后续画面和声音。

**扩展／具名实现路线 · 有来源支持。** 受原视频来源、长度和扩展次数等当前约束限制，不等于任意长片无缝续写。

来源：[s-omni：Generate and edit videos with Gemini Omni Flash · Video extension  {% id="video-extension" %}；取回 Markdown第 2153–2153 行](https://aistudio.google.com/docs/omni.md)。

### `video-06` 把剧本或创意转成可评审分镜

通过 LTX Studio 将简报或剧本拆成场景、镜头和参考画面，形成团队讨论材料。

**扩展／具名实现路线 · 有来源支持。** LTX Studio 商业服务；镜头和角色提取是辅助结果，需要人工修改。

来源：[s-ltx：AI Storyboard Generator: Create Storyboards With AI | LTX Studio · Transform concepts into visuals with AI storyboarding；本次 HTML 提取正文第 105–105 行（不是 HTML 源码行号）](https://ltx.io/studio/platform/ai-storyboard-generator)。

### `video-07` 交付动态分镜与提案文件

把 LTX 分镜预览导出为视频或 PDF pitch deck，用于项目沟通。

**扩展／具名实现路线 · 有来源支持。** 需要对应导出权限；分镜交付不等于成片制作完成。

来源：[s-ltx：AI Storyboard Generator: Create Storyboards With AI | LTX Studio · 页面正文；本次 HTML 提取正文第 116–116 行（不是 HTML 源码行号）](https://ltx.io/studio/platform/ai-storyboard-generator)。

<a id="revision"></a>
## 编辑、配音和规格调整

### `video-04` 通过对话修订已有视频

在多轮上下文中描述需要改变的元素或视角，迭代编辑视频。

**扩展／具名实现路线 · 有来源支持。** 需要 Interactions API 的状态和正确视频输入；保留区域与动作的效果须审核。

来源：[s-omni：Generate and edit videos with Gemini Omni Flash · Stateful video editing  {% id="stateful-video-editing" %}；取回 Markdown第 1386–1386 行](https://aistudio.google.com/docs/omni.md)。

### `video-15` 将视频翻译并同步新语言口型

使用视频翻译服务生成目标语言声音及相应唇形，面向不同语言受众。

**扩展／具名实现路线 · 有来源支持。** HeyGen Video Translation；目标语言、说话人和翻译模式有条件，必须核对译文、名字和口型。

来源：[s-translate：Video Translation - Speed · Video Translation - Speed；取回 Markdown第 7–7 行](https://developers.heygen.com/docs/video-translate.md)。

### `video-16` 用新音轨重配已有视频的口型

用 Lipsync Precision 将已有画面的嘴部动作与替换音频对齐。

**扩展／具名实现路线 · 有来源支持。** 需要兼容的人脸视频和音频；身份、画面和时序质量不保证，对应服务可能另计额度。

来源：[s-lipsync：Lipsync - Precision · Lipsync - Precision；取回 Markdown第 12–12 行](https://developers.heygen.com/lipsync-precision.md)。

### `video-17` 只修订成片中指定的场景

读取 Video Agent 场景清单后针对选定场景发出编辑要求，生成新的草稿。

**扩展／具名实现路线 · 有来源支持。** 仅适用于 Video Agent 会话流程；官方示例展示两处修改，不保证各种素材都保持未编辑区域完全相同。

来源：[s-edit：Edit Scenes · Edit Scenes；取回 Markdown第 15–15 行](https://developers.heygen.com/docs/edit-scenes.md)。

### `video-20` 提升已有片段的输出规格

通过 Runway 对应模型提升分辨率或重定帧率，以适配后期时间线。

**扩展／具名实现路线 · 有来源支持。** 具体模型的输入长度、容器和额外费用适用；不能恢复真实缺失细节或保证广播级质量。

来源：[s-core：Runway Dev · Core API 与专业输出文档合集 · Upscale resolution and frame rate；取回 Markdown第 1800–1800 行](https://docs.dev.runwayml.com/_llms-txt/core-api.txt)。

<a id="marketing"></a>
## 制作商业叙事素材

### `video-08` 从产品照片制作广告镜头

使用 Runway Product Ad 完整配方，把参考商品图转成广告式视频。

**扩展／具名实现路线 · 有来源支持。** 需要 Runway Dev、参考图和额度；商品文字和结构应对照原图。

来源：[s-product：Runway · Product Ad Recipe · 页面概述；取回 Markdown第 3–3 行](https://docs.dev.runwayml.com/recipes/product-ad.md)。

### `video-09` 把新商品替换进参考视频

使用 Product Swap 配方以新商品图替换原视频中的商品。

**扩展／具名实现路线 · 有来源支持。** 需要兼容参考媒体；遮挡、接触与外观不一定精确，不能代替成品审核。

来源：[s-swap：Runway · Product Swap Recipe · 页面概述；取回 Markdown第 6–6 行](https://docs.dev.runwayml.com/recipes/product-swap.md)。

### `video-10` 制作有人物参考的 UGC 风格推广片

使用 Product UGC 配方结合人物与商品参考生成推广素材。

**扩展／具名实现路线 · 有来源支持。** 需要有权使用的参考图和服务权限；生成表演不构成真实使用体验或用户证言。

来源：[s-ugc：Runway · Product UGC Recipe · 页面概述；取回 Markdown第 3–3 行](https://docs.dev.runwayml.com/recipes/product-ugc.md)。

### `video-11` 生成相互切换的多镜头叙事素材

使用 Multi-Shot Video 配方在多个场景间切换，表达产品或品牌故事。

**扩展／具名实现路线 · 有来源支持。** 镜头顺序、角色连续性和商品准确性仍需检查；需要参考媒体和付费服务。

来源：[s-multishot：Runway · Multi-Shot Video Recipe · 页面概述；取回 Markdown第 6–6 行](https://docs.dev.runwayml.com/recipes/multi-shot-video.md)。

<a id="presenter"></a>
## 制作讲述与角色体验

### `video-12` 从脚本制作数字人讲解视频

选择现有 Digital Twin、声音与背景，将脚本渲染为带字幕的讲解片。

**扩展／具名实现路线 · 有来源支持。** HeyGen v3 API；需要已创建并可用的头像与声音及相应授权，创建数字分身另有素材和同意要求。

来源：[s-avatar：Digital Twin · Digital Twin；取回 Markdown第 7–7 行](https://developers.heygen.com/generate-avatar-video.md)。

### `video-13` 让单张人像讲述指定内容

使用 Photo Avatar 将人像照片和脚本变成口型同步的说话视频。

**扩展／具名实现路线 · 有来源支持。** 需要清晰人像、声音、服务权限和素材使用权；不保证任意照片或姿态效果。

来源：[s-photo：Photo Avatar · Photo Avatar；取回 Markdown第 7–7 行](https://developers.heygen.com/photo-avatar.md)。

### `video-14` 把已有录音配到虚拟讲述者上

提供语音、播客片段或配音轨，让头像或单人图像演绎已有音频。

**扩展／具名实现路线 · 有来源支持。** HeyGen Audio to Video；需要合适主体和可访问音频，遵守当前时长与格式限制。

来源：[s-audio：Audio to Video · Overview；取回 Markdown第 13–13 行](https://developers.heygen.com/audio-to-video.md)。

### `video-22` 制作可实时对话的虚拟人物界面

使用 Runway Characters 的头像、声音、资料与工具调用，构建可交互的视频角色。

**扩展／具名实现路线 · 有来源支持。** 这是实时 Characters 与客户端集成路线，需开发、运行会话和配置资料；不是离线视频自动变成交互应用。

来源：[s-characters2：Runway Characters · Runway Characters；取回 Markdown第 7–7 行](https://docs.dev.runwayml.com/_llms-txt/characters.txt)。

<a id="delivery"></a>
## 批量、本地与合成交付

### `video-18` 批量生产多条脚本和头像视频

将多个视频请求作为一批提交，追踪每个素材的成功或失败结果。

**扩展／具名实现路线 · 有来源支持。** HeyGen 批处理是异步任务；额度、并发和每条素材的依赖仍适用，不保证整批成功。

来源：[s-batch：HeyGen · Batch Videos · Overview；取回 Markdown第 13–13 行](https://developers.heygen.com/batch-videos.md)。

### `video-19` 获得可合成到其他画面的透明数字人素材

输出带 alpha 的 WebM 头像视频，供后续视频编辑和网页播放器使用。

**扩展／具名实现路线 · 有来源支持。** 头像必须支持 matting；默认 MP4 不含透明度，输出格式和后期工具需匹配。

来源：[s-transparent：Transparent Background Videos · Transparent Background Videos；取回 Markdown第 7–7 行](https://developers.heygen.com/transparent-background-videos.md)。

### `video-21` 在自己环境中运行有声视频生成

下载 LTX-2 系列权重和实现，使用本地推理管线或 ComfyUI 集成生产视频素材。

**扩展／具名实现路线 · 有来源支持。** 需要满足模型许可证、下载权重和足够硬件；仓库当前指向 LTX-2.5，不保证普通电脑可流畅运行。

来源：[s-local：LTX-2 · LTX-2；取回 Markdown第 9–9 行](https://github.com/Lightricks/LTX-2/blob/4f521619ae0029e8fbb64d555030c2b121a33b4f/README.md#L9-L9)。

## 资料覆盖与发现过程

从文字、图像和视频输入的结果遍历开始，随后阅读广告配方、数字人讲述与场景修订完整案例，补查本地项目和实时角色。
归一化：把分辨率、帧率、比例等设置合并为交付规格；把照片与分身说话按素材路线保留，未拆每个 API。
补漏发现 Google 预览模型关闭、Runway 旧模型退役及 HeyGen v3 引擎差异；未以旧教程承诺可用。
按候选的制作目的整理导航，而非按厂商或模型名分组；AI 生成服务的效果宣传已收敛为可尝试的具体结果。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未调用付费生成接口，未下载模型或评价样片质量；未声称图像、口型、文字、物理或身份一致性可保证。
- Luma 旧 Ray 2 文档提示转向新 Agents API，本轮未完成新路线核对；旧文档的循环和反向延展未当作当前通用能力。
- 未对训练素材、音乐、人像和输出的各法域版权作判断；商业使用需按具体素材、模型和服务条款确认。
- 真实案例以官方产品配方、场景编辑前后示例与 LTX 本地推理项目为主，缺少独立质量对照和完整长片交付评测。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
