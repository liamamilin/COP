# AI 语音 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `voice-01`｜结果视角｜将文案制作成旁白与朗读音频｜s-tts
2. `voice-02`｜结果视角｜制作多角色有声对话｜s-dialogue
3. `voice-03`｜结果视角｜从文字描述设计角色声音｜s-design
4. `voice-04`｜结果视角｜为自己的声音建立可复用合成版本｜s-clone
5. `voice-05`｜结果视角｜保持表演意图而替换录音音色｜s-changer
6. `voice-06`｜结果视角｜补录或替换现有录音中的局部词句｜s-changer
7. `voice-07`｜结果视角｜从嘈杂音视频中分离人声｜s-isolation
8. `voice-08`｜结果视角｜将已有节目译配为其他语言｜s-dubbing
9. `voice-09`｜结果视角｜把已知稿件与录音对齐到词句时间｜s-align
10. `voice-10`｜结果视角｜将会议、采访或视频语音转成文本｜s-stt
11. `voice-11`｜结果视角｜获得带说话人及词级时间的信息稿｜s-stt
12. `voice-12`｜结果视角｜为实时语音输入持续显示文字｜s-stt
13. `voice-13`｜完整示例视角｜把整部稿件制作成可编辑有声书｜s-books
14. `voice-14`｜完整示例视角｜为网站文章提供嵌入式朗读｜s-native
15. `voice-15`｜结果视角｜构建可以听说并执行任务的语音助手｜s-agent
16. `voice-16`｜结果视角｜统一专名和技术词的播读方式｜s-pronounce
17. `voice-17`｜结果视角｜在自有环境部署轻量语音合成｜s-local
18. `voice-18`｜结果视角｜在本地生成多语种录音的转写或英语译稿｜s-whisper

## 归一化、补漏与停止依据

先从合成、转写和译配可交付结果提取候选，再阅读整书和网页朗读完整流程，补查本地模型与实时代理。
归一化：音频格式、语速、情感等控制并入成品语音；转写、已有文本对齐、说话人标签和实时字幕分别对应不同输入和结果。
补漏区分 voice cloning、speech-to-speech、自动配音和口型视频，后者由视频主题覆盖；不把语音模型称为完整业务代理。

## 保留的未知项

- 未生成音频、上传录音或调用任何克隆、转写和电话服务；没有评测听感、方言准确率或延迟。
- ElevenLabs 文档部分总览与各模型的语言数表述不一致；因此不写统一支持语言数量，按模型页及部署时状态核对。
- 付费等级、声音权利、身份验证和分发条款因功能不同；本轮不作可商用、授权充分或合规保证。
- 官方 Audio Native 与 Audiobooks 提供完整任务流程；没有获取独立用户音频工程的可重复评价。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-agent](https://elevenlabs.io/docs/eleven-agents/overview.md) | 2026-11-05T09:32:36.961430+00:00 | 是 |
| [s-align](https://elevenlabs.io/docs/overview/capabilities/forced-alignment.md) | 2026-11-05T09:32:34.486814+00:00 | 是 |
| [s-books](https://elevenlabs.io/docs/eleven-creative/products/audiobooks.md) | 2026-11-05T09:32:36.834957+00:00 | 是 |
| [s-changer](https://elevenlabs.io/docs/overview/capabilities/voice-changer.md) | 2026-11-05T09:32:33.909756+00:00 | 是 |
| [s-clone](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning.md) | 2026-11-05T09:32:35.858143+00:00 | 是 |
| [s-design](https://elevenlabs.io/docs/eleven-creative/voices/voice-design.md) | 2026-11-05T09:32:35.795869+00:00 | 是 |
| [s-dialogue](https://elevenlabs.io/docs/overview/capabilities/text-to-dialogue.md) | 2026-11-05T09:32:33.070531+00:00 | 是 |
| [s-dubbing](https://elevenlabs.io/docs/overview/capabilities/dubbing.md) | 2026-11-05T09:32:34.857937+00:00 | 是 |
| [s-index](https://elevenlabs.io/docs/llms.txt) | 2026-11-05T09:26:48.333195+00:00 | 否 |
| [s-isolation](https://elevenlabs.io/docs/overview/capabilities/voice-isolator.md) | 2026-11-05T09:32:33.835025+00:00 | 是 |
| [s-local](https://huggingface.co/hexgrad/Kokoro-82M/raw/main/README.md) | 2026-11-05T09:26:48.524334+00:00 | 是 |
| [s-native](https://elevenlabs.io/docs/eleven-creative/audio-tools/audio-native.md) | 2026-11-05T09:32:36.940041+00:00 | 是 |
| [s-pronounce](https://elevenlabs.io/docs/eleven-agents/customization/voice/pronunciation-dictionary.md) | 2026-11-05T09:32:37.392999+00:00 | 是 |
| [s-stt](https://elevenlabs.io/docs/overview/capabilities/speech-to-text.md) | 2026-11-05T09:32:32.652022+00:00 | 是 |
| [s-tts](https://elevenlabs.io/docs/overview/capabilities/text-to-speech.md) | 2026-11-05T09:32:32.898712+00:00 | 是 |
| [s-whisper](https://github.com/openai/whisper/blob/86098128c0b4f24f0e2aa2994de830614b474227/README.md) | 2026-11-05T09:40:28.170650+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`voice-04`、`voice-09`、`voice-17`、`voice-18`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
