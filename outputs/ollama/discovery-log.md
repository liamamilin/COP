# Ollama 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `p-local`｜结果视角｜在自己机器上运行开放模型回答问题｜s-readme
2. `p-chat`｜结果视角｜把应用接到可多轮交互的聊天模型接口｜s-chat
3. `p-vision`｜结果视角｜围绕图片进行描述、分类和问答｜s-vision
4. `p-fields`｜结果视角｜把文本或图像信息提取为指定字段的 JSON｜s-structured
5. `p-embeddings`｜结果视角｜为语义检索和资料问答生成文本向量｜s-embed
6. `p-tool-work`｜结果视角｜让模型在任务中请求工具并利用执行结果继续回答｜s-tools
7. `p-thinking`｜结果视角｜把思考输出与最终答复分别呈现｜s-thinking
8. `p-presets`｜结果视角｜保存具有固定行为约定的命名模型配置｜s-modelfile
9. `p-import`｜结果视角｜运行自己准备的兼容模型权重｜s-import
10. `p-share-model`｜扩展视角｜把已创建的模型发布给其他用户试用｜s-import
11. `p-compatible-clients`｜扩展视角｜让已有 OpenAI 客户端改连 Ollama 模型｜s-openai
12. `p-concurrency`｜结果视角｜在资源允许时为多个请求或模型提供推理｜s-faq
13. `p-network-service`｜结果视角｜把自己的模型服务提供给网络中的应用｜s-faq
14. `p-local-only`｜结果视角｜选择关闭云功能的纯本地使用路线｜s-faq
15. `p-cloud`｜扩展视角｜在不下载大模型的情况下调用远端模型｜s-cloud
16. `p-web-current`｜扩展视角｜给回答流程补充当前网页搜索结果｜s-websearch
17. `p-code-agent`｜示例视角｜把本地或云模型接入编程代理完成工程任务｜s-integrations
18. `p-desktop`｜示例视角｜在支持的桌面 AI 应用中改用 Ollama 模型｜s-overview
19. `p-document-chat`｜示例视角｜围绕上传的资料进行带检索上下文的问答｜s-webui-rag
20. `p-web-interface`｜示例视角｜为自己的模型提供可在浏览器使用的聊天界面｜s-webui
21. `p-decisions`｜补漏视角｜对文本作分类、是非判断或分级评分｜s-decision
22. `p-speech`｜补漏视角｜把文字或模型回复播放并保存为语音｜s-speech

## 归一化、补漏与停止依据

结果视角读取聊天、视觉、结构化输出、向量、工具调用、thinking 与运行配置，提取可观察结果而不复述 API 参数。
示例视角核对桌面和编程代理集成、Open WebUI 完整部署及资料问答，标明真正交付界面或工程任务的是扩展组件。
扩展视角补读云模型、网络搜索、模型导入与分享；将本地、云端、第三方服务的边界写入条件。
归一化时合并不同品牌模型和多个代码代理入口；保留结构化提取、文档问答、模型发布与远端服务等不同用户结果。
补漏复查 FAQ、CLI、Linux 服务部署与 Modelfile；补漏时发现 decision 与 speech 两项新的用户结果，读取专门指南后纳入；其他下载、列举、复制和停止等步骤不单独拆成 P。相关版本限制保留在条件与缺口。

## 保留的未知项

- 未在各操作系统、GPU、模型家族和文件格式上安装实测；速度、上下文、内存占用与工具准确率不能由功能文档推定。
- 本地与云端接口并不相同。结构化输出、Responses 状态或工具回放等须按具体端点确认。
- 未把权重微调、任意模型兼容、自动量化导入 GGUF、完全替代所有 OpenAI API 或完全离线的外部插件列为内置能力。
- 未审计所列第三方应用的数据外传、认证与多用户隔离；Ollama 本地运行的声明不能外推到整个应用栈。
- CLI 的下载、列举、复制和删除视为模型管理步骤，没有为这些微操作单独增加 P；更多集成生态仍有长尾缺口。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-chat](https://docs.ollama.com/api/chat.md) | 2026-11-05T08:43:28.073083+00:00 | 是 |
| [s-cli](https://docs.ollama.com/cli.md) | 2026-11-05T08:57:08.949588+00:00 | 否 |
| [s-cloud](https://docs.ollama.com/cloud.md) | 2026-11-05T08:43:30.998170+00:00 | 是 |
| [s-decision](https://docs.ollama.com/capabilities/decision.md) | 2026-11-05T09:00:07.158228+00:00 | 是 |
| [s-embed](https://docs.ollama.com/capabilities/embeddings.md) | 2026-11-05T08:43:28.514872+00:00 | 是 |
| [s-faq](https://docs.ollama.com/faq.md) | 2026-11-05T08:43:31.086212+00:00 | 是 |
| [s-import](https://docs.ollama.com/import.md) | 2026-11-05T08:43:29.839909+00:00 | 是 |
| [s-integrations](https://docs.ollama.com/integrations.md) | 2026-11-05T08:43:31.240683+00:00 | 是 |
| [s-linux](https://docs.ollama.com/linux.md) | 2026-11-05T08:47:26.807880+00:00 | 否 |
| [s-modelfile](https://docs.ollama.com/modelfile.md) | 2026-11-05T08:43:31.158898+00:00 | 是 |
| [s-openai](https://docs.ollama.com/api/openai-compatibility.md) | 2026-11-05T08:43:30.947890+00:00 | 是 |
| [s-overview](https://docs.ollama.com/quickstart.md) | 2026-11-05T08:43:26.855646+00:00 | 是 |
| [s-readme](https://github.com/ollama/ollama/blob/a6d33251620eef7629c73b09e672f2df243eb363/README.md) | 2026-11-05T08:47:24.787124+00:00 | 是 |
| [s-speech](https://docs.ollama.com/capabilities/speech.md) | 2026-11-05T09:00:07.031419+00:00 | 是 |
| [s-structured](https://docs.ollama.com/capabilities/structured-outputs.md) | 2026-11-05T08:43:29.571065+00:00 | 是 |
| [s-thinking](https://docs.ollama.com/capabilities/thinking.md) | 2026-11-05T08:43:29.566874+00:00 | 是 |
| [s-tools](https://docs.ollama.com/capabilities/tool-calling.md) | 2026-11-05T08:43:28.130498+00:00 | 是 |
| [s-vision](https://docs.ollama.com/capabilities/vision.md) | 2026-11-05T08:43:28.298688+00:00 | 是 |
| [s-websearch](https://docs.ollama.com/capabilities/web-search.md) | 2026-11-05T08:47:26.653271+00:00 | 是 |
| [s-webui-rag](https://docs.openwebui.com/features/chat-conversations/rag/) | 2026-11-05T08:56:19.594536+00:00 | 是 |
| [s-webui](https://docs.openwebui.com/getting-started/quick-start/) | 2026-11-05T08:47:28.109799+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：无额外措辞修订。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
