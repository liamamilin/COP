# 大模型微调 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `p-dialogue`｜结果视角｜让语言模型适配目标任务的示范对话｜s-sft
2. `p-domain`｜结果视角｜让生成模型适应一类专门文本语料｜s-causal
3. `p-preferences`｜结果视角｜以偏好样本定向调整模型回答行为｜s-dpo
4. `p-reward-task`｜结果视角｜训练面向可计算任务奖励的模型｜s-grpo
5. `p-judge`｜结果视角｜训练对候选回复进行质量评分的模型｜s-reward
6. `p-small-adapter`｜结果视角｜用较少可训练参数完成任务适配｜s-peft
7. `p-quantized-training`｜扩展视角｜在量化权重上继续做任务适配｜s-quant
8. `p-multigpu`｜扩展视角｜把单机放不进一张卡的训练状态分摊到多卡｜s-multigpu
9. `p-distill`｜结果视角｜把教师模型行为蒸馏到较小学生模型｜s-distill
10. `p-vision`｜扩展视角｜让视觉语言模型适配图像和对话样本｜s-sft
11. `p-tools`｜扩展视角｜让模型适配带工具调用和返回结果的任务｜s-sft
12. `p-json-catalog`｜示例视角｜把商品标题和描述适配成目标语言结构化目录｜s-example
13. `p-private-code`｜示例视角｜让代码模型适配组织自己的代码与约定｜s-code-example
14. `p-portable-adapter`｜结果视角｜以较小适配器工件共享任务变化｜s-checkpoints
15. `p-merge-task-models`｜扩展视角｜组合多个适配器形成候选多任务模型｜s-adapters
16. `p-standalone`｜结果视角｜导出合并权重以便独立推理部署｜s-lora
17. `p-evaluate`｜结果视角｜为适配结果计算可重复的任务指标｜s-evaluate
18. `p-training-selection`｜结果视角｜按验证结果保存和选择训练检查点｜s-training
19. `p-resume`｜结果视角｜从保存状态接续被打断的训练｜s-resume

## 归一化、补漏与停止依据

结果视角先提取目标对话/领域适配、偏好、可计算奖励、评分模型与小模型蒸馏等不同产物，而不是先按训练库的 API 分类。
示例视角读取波斯语商品 JSON 目录、私有代码适配和因果语言建模完整流程，记录数据、硬件及旧依赖限制。
扩展视角补查 PEFT、量化训练、FSDP/DeepSpeed、多模态/工具样本、适配器工件与融合，区分训练结果和部署能力。
去重时把 LoRA 变体、不同训练 CLI 和超参数写进实现条件；保留可计算奖励、较少训练参数、量化基座和工件交付等不同用户目的。
补漏追加训练选择、评估和断点恢复后，后续页面主要是同类训练/适配器变体；剩余质量、数据和兼容问题列为待验证，不以成功示例代替实测。

## 保留的未知项

- 未运行大规模 GPU 训练或逐模型复现案例，不能保证训练后的准确率、风格、稳定性、推理成本或显存占用。
- 未把微调视作实时知识库更新、权限控制、可靠事实检索或自动消除幻觉的替代。
- 实际取回文档横跨多个版本；部分页面或旧 Cookbook 用不同 API，依赖、模板、量化后端与模型家族必须在项目中核对。
- 尚未深入比较所有偏好算法、在线反馈闭环、训练数据治理和跨节点容错；没有按算法变体或超参数拆分微小 P。
- 医疗、法律等领域模型即使能够训练，也未被据此确认可作实际专业决策；授权数据、隐私、基座许可和发布许可仍需独立验证。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-adapters](https://huggingface.co/docs/peft/en/developer_guides/model_merging) | 2026-11-05T08:49:57.558140+00:00 | 是 |
| [s-causal](https://huggingface.co/docs/transformers/en/tasks/language_modeling) | 2026-11-05T08:49:58.346165+00:00 | 是 |
| [s-checkpoints](https://huggingface.co/docs/peft/en/developer_guides/checkpoint) | 2026-11-05T09:09:38.240922+00:00 | 是 |
| [s-code-example](https://huggingface.co/learn/cookbook/fine_tuning_code_llm_on_single_gpu) | 2026-11-05T09:09:38.517876+00:00 | 是 |
| [s-distill](https://huggingface.co/docs/trl/en/distillation_trainer) | 2026-11-05T08:49:58.924140+00:00 | 是 |
| [s-dpo](https://huggingface.co/docs/trl/en/dpo_trainer) | 2026-11-05T08:49:55.398731+00:00 | 是 |
| [s-evaluate](https://huggingface.co/docs/evaluate/en/a_quick_tour) | 2026-11-05T09:09:38.575257+00:00 | 是 |
| [s-example](https://huggingface.co/learn/cookbook/fine_tuning_llm_to_generate_persian_product_catalogs_in_json_format) | 2026-11-05T08:49:59.067100+00:00 | 是 |
| [s-grpo](https://huggingface.co/docs/trl/en/grpo_trainer) | 2026-11-05T08:49:56.544256+00:00 | 是 |
| [s-inference](https://huggingface.co/docs/peft/en/developer_guides/peft_inference) | 2026-11-05T09:09:37.639292+00:00 | 否 |
| [s-lora](https://huggingface.co/docs/peft/v0.21.0/package_reference/lora) | 2026-11-05T08:49:59.261035+00:00 | 是 |
| [s-multigpu](https://huggingface.co/docs/accelerate/en/concept_guides/fsdp_and_deepspeed) | 2026-11-05T09:09:38.328569+00:00 | 是 |
| [s-peft](https://huggingface.co/docs/peft/en/index) | 2026-11-05T08:49:55.910388+00:00 | 是 |
| [s-quant](https://huggingface.co/docs/peft/en/developer_guides/quantization) | 2026-11-05T08:49:56.811314+00:00 | 是 |
| [s-resume](https://huggingface.co/docs/accelerate/en/usage_guides/checkpoint) | 2026-11-05T09:15:34.945468+00:00 | 是 |
| [s-reward](https://huggingface.co/docs/trl/en/reward_trainer) | 2026-11-05T08:49:56.070025+00:00 | 是 |
| [s-sft](https://huggingface.co/docs/trl/en/sft_trainer) | 2026-11-05T08:49:55.276726+00:00 | 是 |
| [s-trainer](https://huggingface.co/docs/transformers/en/trainer) | 2026-11-05T08:49:58.529491+00:00 | 否 |
| [s-training](https://huggingface.co/docs/transformers/en/training) | 2026-11-05T09:09:38.437194+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`p-training-selection`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
