# AI 视频生成 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `video-01`｜结果视角｜从文字或图片生成有声短片｜s-google-md
2. `video-02`｜结果视角｜用首尾画面约束镜头变化｜s-omni
3. `video-03`｜结果视角｜用参考主体引导人物或物体形象｜s-omni
4. `video-04`｜结果视角｜通过对话修订已有视频｜s-omni
5. `video-05`｜结果视角｜延展已有镜头的后续内容｜s-omni
6. `video-06`｜结果视角｜把剧本或创意转成可评审分镜｜s-ltx
7. `video-07`｜结果视角｜交付动态分镜与提案文件｜s-ltx
8. `video-08`｜完整示例视角｜从产品照片制作广告镜头｜s-product
9. `video-09`｜完整示例视角｜把新商品替换进参考视频｜s-swap
10. `video-10`｜完整示例视角｜制作有人物参考的 UGC 风格推广片｜s-ugc
11. `video-11`｜结果视角｜生成相互切换的多镜头叙事素材｜s-multishot
12. `video-12`｜结果视角｜从脚本制作数字人讲解视频｜s-avatar
13. `video-13`｜结果视角｜让单张人像讲述指定内容｜s-photo
14. `video-14`｜结果视角｜把已有录音配到虚拟讲述者上｜s-audio
15. `video-15`｜结果视角｜将视频翻译并同步新语言口型｜s-translate
16. `video-16`｜结果视角｜用新音轨重配已有视频的口型｜s-lipsync
17. `video-17`｜完整示例视角｜只修订成片中指定的场景｜s-edit
18. `video-18`｜结果视角｜批量生产多条脚本和头像视频｜s-batch
19. `video-19`｜结果视角｜获得可合成到其他画面的透明数字人素材｜s-transparent
20. `video-20`｜结果视角｜提升已有片段的输出规格｜s-core
21. `video-21`｜结果视角｜在自己环境中运行有声视频生成｜s-local
22. `video-22`｜结果视角｜制作可实时对话的虚拟人物界面｜s-characters2

## 归一化、补漏与停止依据

从文字、图像和视频输入的结果遍历开始，随后阅读广告配方、数字人讲述与场景修订完整案例，补查本地项目和实时角色。
归一化：把分辨率、帧率、比例等设置合并为交付规格；把照片与分身说话按素材路线保留，未拆每个 API。
补漏发现 Google 预览模型关闭、Runway 旧模型退役及 HeyGen v3 引擎差异；未以旧教程承诺可用。
按候选的制作目的整理导航，而非按厂商或模型名分组；AI 生成服务的效果宣传已收敛为可尝试的具体结果。

## 保留的未知项

- 未调用付费生成接口，未下载模型或评价样片质量；未声称图像、口型、文字、物理或身份一致性可保证。
- Luma 旧 Ray 2 文档提示转向新 Agents API，本轮未完成新路线核对；旧文档的循环和反向延展未当作当前通用能力。
- 未对训练素材、音乐、人像和输出的各法域版权作判断；商业使用需按具体素材、模型和服务条款确认。
- 真实案例以官方产品配方、场景编辑前后示例与 LTX 本地推理项目为主，缺少独立质量对照和完整长片交付评测。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-agent](https://developers.heygen.com/docs/video-agent.md) | 2026-11-05T09:36:00.338622+00:00 | 否 |
| [s-api](https://docs.dev.runwayml.com/api/) | 2026-11-05T09:32:35.951324+00:00 | 否 |
| [s-audio](https://developers.heygen.com/audio-to-video.md) | 2026-11-05T09:35:59.725031+00:00 | 是 |
| [s-avatar](https://developers.heygen.com/generate-avatar-video.md) | 2026-11-05T09:35:59.479059+00:00 | 是 |
| [s-batch](https://developers.heygen.com/batch-videos.md) | 2026-11-05T09:36:00.695622+00:00 | 是 |
| [s-characters2](https://docs.dev.runwayml.com/_llms-txt/characters.txt) | 2026-11-05T09:35:58.639603+00:00 | 是 |
| [s-context](https://docs.dev.runwayml.com/ai-context.md) | 2026-11-05T09:35:59.052724+00:00 | 否 |
| [s-core](https://docs.dev.runwayml.com/_llms-txt/core-api.txt) | 2026-11-05T09:40:27.839142+00:00 | 是 |
| [s-edit](https://developers.heygen.com/docs/edit-scenes.md) | 2026-11-05T09:36:00.903316+00:00 | 是 |
| [s-google-md](https://aistudio.google.com/docs/video.md) | 2026-11-05T09:36:01.692080+00:00 | 是 |
| [s-google](https://aistudio.google.com/docs/video) | 2026-11-05T09:26:45.550558+00:00 | 否 |
| [s-heygen-index](https://developers.heygen.com/llms.txt) | 2026-11-05T09:26:46.107112+00:00 | 否 |
| [s-lipsync](https://developers.heygen.com/lipsync-precision.md) | 2026-11-05T09:40:49.821958+00:00 | 是 |
| [s-local](https://github.com/Lightricks/LTX-2/blob/4f521619ae0029e8fbb64d555030c2b121a33b4f/README.md) | 2026-11-05T09:40:28.370646+00:00 | 是 |
| [s-ltx](https://ltx.io/studio/platform/ai-storyboard-generator) | 2026-11-05T09:26:45.462659+00:00 | 是 |
| [s-luma](https://docs.lumalabs.ai/docs/video-generation) | 2026-11-05T09:26:44.163788+00:00 | 否 |
| [s-multishot](https://docs.dev.runwayml.com/recipes/multi-shot-video.md) | 2026-11-05T09:40:26.734923+00:00 | 是 |
| [s-omni](https://aistudio.google.com/docs/omni.md) | 2026-11-05T09:36:02.179015+00:00 | 是 |
| [s-photo](https://developers.heygen.com/photo-avatar.md) | 2026-11-05T09:35:59.715954+00:00 | 是 |
| [s-product](https://docs.dev.runwayml.com/recipes/product-ad.md) | 2026-11-05T09:40:26.729647+00:00 | 是 |
| [s-recipes](https://docs.dev.runwayml.com/_llms-txt/recipes.txt) | 2026-11-05T09:35:58.646119+00:00 | 否 |
| [s-runway-index](https://docs.dev.runwayml.com/llms.txt) | 2026-11-05T09:26:43.463040+00:00 | 否 |
| [s-swap](https://docs.dev.runwayml.com/recipes/product-swap.md) | 2026-11-05T09:40:26.733373+00:00 | 是 |
| [s-translate](https://developers.heygen.com/docs/video-translate.md) | 2026-11-05T09:40:49.858774+00:00 | 是 |
| [s-transparent](https://developers.heygen.com/transparent-background-videos.md) | 2026-11-05T09:36:01.380839+00:00 | 是 |
| [s-ugc](https://docs.dev.runwayml.com/recipes/product-ugc.md) | 2026-11-05T09:40:26.668160+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`video-06`、`video-09`、`video-10`、`video-11`、`video-22`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
