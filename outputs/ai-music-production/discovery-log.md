# AI 音乐制作 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `music-01`｜结果视角｜把音乐想法变成歌曲草稿｜s-simple
2. `music-02`｜结果视角｜给自己的歌词谱成歌｜s-lyrics
3. `music-03`｜结果视角｜生成无主唱的伴奏音乐｜s-lyria-md
4. `music-04`｜结果视角｜以图片引导音乐氛围｜s-lyria-md
5. `music-05`｜结果视角｜让音乐围绕段落和时间要求展开｜s-lyria-md
6. `music-06`｜结果视角｜延长歌曲或重做结尾｜s-extend
7. `music-07`｜完整示例视角｜把录下的旋律或节奏发展成完整素材｜s-upload
8. `music-08`｜结果视角｜保持旋律方向而尝试另一种风格｜s-cover
9. `music-09`｜结果视角｜替换歌曲中间的歌词或音乐段落｜s-replace
10. `music-10`｜结果视角｜把混音拆成可独立处理的声部｜s-stems
11. `music-11`｜结果视角｜把录音旋律转成可编辑 MIDI｜s-midi
12. `music-12`｜结果视角｜把已有 MIDI 想法发展成配器音乐｜s-midi-in
13. `music-13`｜结果视角｜按谱制作可精细控制的合成人声｜s-singing-full
14. `music-14`｜结果视角｜为歌曲制作和声与背景人声编排｜s-singing-full
15. `music-15`｜结果视角｜让自己的声音用于生成的歌曲｜s-voice
16. `music-16`｜结果视角｜以自有歌曲建立风格模型｜s-custom
17. `music-17`｜结果视角｜为已完成混音制作母带版本｜s-mastering
18. `music-18`｜结果视角｜生成独立乐器采样和环境声音素材｜s-sounds
19. `music-19`｜完整示例视角｜以实时交互持续引导器乐演出｜s-realtime
20. `music-20`｜结果视角｜在自有环境尝试旋律条件音乐生成｜s-musicgen
21. `music-21`｜结果视角｜将生成项目带回 DAW 继续制作｜s-export
22. `music-22`｜结果视角｜在本地从已有歌曲分离伴奏与人声｜s-demucs

## 归一化、补漏与停止依据

先发现完整歌曲、歌词、录音和 MIDI 等输入可得到的结果，再阅读鼓循环扩展、实时 DJ 和 DAW 导出的完整流程。
归一化：将风格与乐器提示归入歌曲生成，分离、转写、模型训练与母带保留为不同交付结果；本地与托管分轨路线因部署条件差异分别说明。
补漏检索发现新的 MIDI 输入、声音档案与 Custom Model；以当前文章的账户、版本和权利限制收敛结果，不把宣传百分比当作质量保证。
按实际发现的创作、修订、演唱和后期目的整理，不按模型名预先分类。

## 保留的未知项

- 未生成或上传音频，未安装 DAW 插件与本地模型，未评价旋律、音乐性、音高和分轨质量。
- 未核实所有生成音频的商用、训练素材、表演者和样本权利；需依输入、模型和当前服务条款判断。
- Suno 部分旧文章仍标 Beta，当前页面也出现新模型与下载规则；未假设旧版权益永久有效。
- Eleven Music 当前文档提示 music_v1 将于 2027-01-31 移除；其相似结果在去重时归入已有音乐生成／编辑用途，没有扩写成重复条目。
- Demucs 原仓库明确不再维护，fork 也仅处理重要修复；MusicGen 依赖兼容及真实工作站性能未做安装验证。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-cover](https://help.suno.com/en/articles/2872257) | 2026-11-05T09:40:23.217744+00:00 | 是 |
| [s-custom](https://help.suno.com/en/articles/11362497) | 2026-11-05T09:40:25.020961+00:00 | 是 |
| [s-demucs](https://github.com/facebookresearch/demucs/blob/e976d93ecc3865e5757426930257e200846a520a/README.md) | 2026-11-05T09:26:47.400694+00:00 | 是 |
| [s-export](https://help.suno.com/en/articles/13925249) | 2026-11-05T09:40:25.158135+00:00 | 是 |
| [s-extend](https://help.suno.com/en/articles/2409601) | 2026-11-05T09:40:23.236143+00:00 | 是 |
| [s-lyria-md](https://aistudio.google.com/docs/music-generation.md) | 2026-11-05T09:36:02.640122+00:00 | 是 |
| [s-lyria](https://aistudio.google.com/docs/music-generation) | 2026-11-05T09:26:47.440345+00:00 | 否 |
| [s-lyrics](https://help.suno.com/en/articles/2415873) | 2026-11-05T09:40:23.214910+00:00 | 是 |
| [s-mastering](https://www.landr.com/online-audio-mastering) | 2026-11-05T09:26:47.506122+00:00 | 是 |
| [s-midi-in](https://help.suno.com/en/articles/14594177) | 2026-11-05T09:40:25.300091+00:00 | 是 |
| [s-midi](https://github.com/spotify/basic-pitch/blob/fa5997af0a8210982619003269994a1be25eddf3/README.md) | 2026-11-05T09:26:47.013065+00:00 | 是 |
| [s-music](https://elevenlabs.io/docs/overview/capabilities/music.md) | 2026-11-05T09:32:37.389127+00:00 | 否 |
| [s-musicgen](https://github.com/facebookresearch/audiocraft/blob/896ec7c47f5e5d1e5aa1e4b260c4405328bf009d/docs/MUSICGEN.md) | 2026-11-05T09:26:45.725643+00:00 | 是 |
| [s-realtime](https://aistudio.google.com/docs/realtime-music-generation.md) | 2026-11-05T09:40:28.424461+00:00 | 是 |
| [s-replace](https://help.suno.com/en/articles/3271873) | 2026-11-05T09:40:23.126855+00:00 | 是 |
| [s-simple](https://help.suno.com/en/articles/2462273) | 2026-11-05T09:40:23.120653+00:00 | 是 |
| [s-singing-full](https://dreamtonics.com/synthesizerv/) | 2026-11-05T09:36:03.875082+00:00 | 是 |
| [s-singing](https://dreamtonics.com/synthesizerv/) | 2026-11-05T09:26:47.674371+00:00 | 是 |
| [s-sounds](https://help.suno.com/en/articles/10625537) | 2026-11-05T09:40:26.838540+00:00 | 是 |
| [s-stems](https://help.suno.com/en/articles/12702337) | 2026-11-05T09:40:24.967057+00:00 | 是 |
| [s-suno-index](https://help.suno.com/en) | 2026-11-05T09:26:45.208383+00:00 | 否 |
| [s-upload](https://help.suno.com/en/articles/2477633) | 2026-11-05T09:40:23.162243+00:00 | 是 |
| [s-vocals](https://help.suno.com/en/articles/6882817) | 2026-11-05T09:40:25.154226+00:00 | 否 |
| [s-voice](https://help.suno.com/en/articles/11362369) | 2026-11-05T09:40:25.185902+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`music-01`、`music-07`、`music-15`、`music-18`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
