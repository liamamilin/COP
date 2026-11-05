"""Build an independent, authored Chinese communication lesson (no runtime services).

Default: validate and compare all three JSON fixtures byte-for-byte, without writes.
--write: replace only the three explicitly named communication-basics JSON fixtures.
No source fetching, database, provider, learner commands, or publication occurs here.
The audit document is authored separately, never generated or overwritten by this CLI.
"""

# Adjacent prose is deliberately kept readable as complete Chinese paragraphs.
# ruff: noqa: E501

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.domain.cop_models import COPArtifact  # noqa: E402
from app.domain.learning_unit import (  # noqa: E402
    check_learning_unit,
    content_hash,
    unit_manifest,
)

ARTIFACT_PATH = ROOT / "fixtures/communication-basics-cop.json"
UNIT_PATH = ROOT / "fixtures/communication-basics-learning-unit.json"
MANIFEST_PATH = ROOT / "fixtures/communication-basics-learning-unit.manifest.json"
SOURCE_URL = (
    "https://socialsci.libretexts.org/Bookshelves/Communication/Introduction_to_Communication/"
    "Communication_in_the_Real_World_-_An_Introduction_to_Communication_Studies/"
    "01%3A_Introduction_to_Communication_Studies/1.02%3A_The_Communication_Process"
)
SOURCE_ID = "src.communication-process"
PATHS = ["paper"]
GOAL = "goal.communication-understanding"
PROCESS = "process.communication-inquiry"
ENTRY = "entry.case-and-paper"

CASE_FACTS = [
    "本课是作者编写的虚构案例，不是真实访谈或实验。以下引号内的消息和自述，是案例给定材料。",
    "案例日期为 2026 年 11 月 3 日（周二）。10:00，项目负责人周岚通过文字聊天给设计同事林宁发：‘周五前给我初稿’。林宁回：‘好的’。没有提供更早的聊天记录。",
    "同日 11:00 的案例回访中，周岚说：‘我想的是这周五上午十点，能讨论思路的提纲就行。’林宁说：‘我理解成这周五下班前，要交一份排好版的稿子。’这是两人此时的自述，不是对原先心理状态的直接测量。",
    "原消息未写日历日期、时刻、时区、初稿包含什么。案例也没有提供双方共享的截止时间或稿件标准。",
]
CASE_UNKNOWNS = [
    "周岚在发送原消息时究竟怎样理解‘周五前’，是否后来改变了想法；林宁当时是否已有与回访相同的理解。",
    "双方是否另有共同约定、是否漏看其他消息、当时的注意力与情绪如何。没有记录不能当作这些因素不存在。",
    "林宁回复‘好的’是理解一致、礼貌应答、顾虑关系还是别的原因；两人是否有时间和意愿完成任务。",
]


def question(identifier, kind, prompt, hints, criteria, stages):
    return {
        "id": identifier, "kind": kind, "prompt": prompt,
        "hints": hints, "criteria": criteria, "stage_refs": stages, "path_ids": PATHS,
    }


def concept(identifier, name, plain, example, contrast, why):
    return {
        "id": identifier, "name": name, "plain_language": plain,
        "concrete_example": example, "contrast": contrast, "why_here": why,
    }


def reasoning(observation, inference, warrant, limitation):
    return {
        "observation": observation, "inference": inference, "warrant": warrant,
        "limitation": limitation, "source_ids": [SOURCE_ID],
    }


def lessons() -> list[dict]:
    """Authoring data: the COP route and teaching sidecar derive from one sequence."""
    return [
        {
            "id": "stage.communication.evidence",
            "title": "先看到了什么，再问它说明什么",
            "question": "一句‘好的’，足以说明两人理解相同吗？",
            "purpose": "从同一条消息和不同自述出发，把可见记录、解释与未知分开；否则一上来就说‘他不会沟通’，会把需要检验的判断当成原因。",
            "why_now": "我们首先需要一个值得解释的差异，而不是先背模型名称。先保存原话，后面的概念才有可对照的对象。",
            "next_gap": "知道自述不同还没有说明差异怎样形成。下一步要追踪‘想法—文字—对方想到的事’，并问语境怎样参与其中。",
            "output": "out.communication.evidence",
            "output_name": "纸上证据页：记录、解释与未知",
            "output_kind": "evidence",
            "output_description": "保留原消息与回访的引号、时间和出处，另列至少两种解释及各自还缺的证据；后续不擦掉旧判断，而在旁边修订。",
            "inputs": [("entry", ENTRY, "原消息和回访是分析的起点；纸笔让你把判断保留下来，下一步还能核对。", "能复述原消息与两段回访，且知道它们是虚构材料。")],
            "concepts": [
                concept(
                    "concept.communication.observation", "观察与推断",
                    "观察是你能指回某条材料的内容；推断是你据此提出的解释。‘记录里有好的’和‘他已经完全理解’不是同一件事。自述也是一种材料，但它首先证明‘他这样说过’，不直接证明最初的想法。",
                    "证据页写：聊天记录中林宁回复‘好的’；回访中林宁说自己理解成下班前的排版稿。另起一行写：原先的理解可能不同，也可能在回访前改变过。",
                    "推断不是坏事，解释必然需要推断；问题是能否说明依据，并留出被新证据改写的余地。没有写‘编码’等术语，不等于没有推断。",
                    "先区分证据与解释，才能避免后面借模型替人读心。来源给出沟通部件；这套证据记法是本课的作者教学方法，不是来源验证过的诊断工具。",
                ),
                concept(
                    "concept.communication.message", "人、消息与理解不是一个东西",
                    "参与者是沟通中的人；消息是传出的语言或非语言内容；理解是人由此想到的意思。消息相同，不自动带来相同理解。",
                    "周岚和林宁是参与者，‘周五前给我初稿’是文字消息；上午十点的提纲与下班前的排版稿，是回访中两种不同的理解。",
                    "不要把‘消息有歧义’变成‘任何理解都一样合理’，也不要替两人规定‘周五前’客观上必然是哪一天几点。本案缺共同约定，暂不能裁定。",
                    "我们要解释的恰好是：一份文字为何没锁定一个意思。先把消息和理解分开，下一步才看得见中间的转换。",
                ),
            ],
            "operation": "把给定原话与时间写在纸上，逐条标明材料来源；把自己的解释写在旁边，并为每条解释补一个尚不知道的条件。",
            "before": "‘好的’很容易被看成已经理解甚至承诺完成，而两段回访又容易被当成当时心理的录像。",
            "because": "将原话与解释分开放，使证据能约束判断：你可以保留多种可能，不必在材料不足时选定一个人的过错。它改善可追查性，不保证判断必然正确。",
            "after": "留下能回查原话的证据页，清楚区分材料支持什么、还不能支持什么。",
            "action": "在纸上写下原消息、‘好的’及两段回访，分别注明聊天记录或回访。旁边写两种对‘好的’的解释，例如理解一致或礼貌应答；每种解释后写还需问什么。最后保留‘原消息的日期、时刻和初稿标准尚未共同确认’这一未知，不用自己的习惯填空。",
            "method_note": "先自己写，再看示例。纸张形式不限；关键是保存具体原话与自己的推断，后续用新证据修订，而不是勾完一个栏目就算理解。",
            "walkthrough": [
                "证据页第一行抄录 10:00 的‘周五前给我初稿’，第二行抄录‘好的’；第三、四行写明 11:00 两人的自述。没有写‘周岚已明确要求周五十点’，因为原消息没说。",
                "我先猜‘两人对截止与初稿标准的理解不同’。依据是回访说法不同；限制是回访可能反映事后解释，不能直接还原 10:00 的想法。",
                "我再猜‘林宁只是先应答，尚未展开排期’。‘好的’与此相容，却不独有地支持它；要追问当时怎样安排工作，而不是把礼貌当成已证事实。",
                "纸上保留‘是否有共同约定，未知’。即使我本人习惯把‘周五前’理解为周四，也不把习惯写进案例事实。",
            ],
            "observation": "给定材料显示文字消息相同、回访自述不同。它使‘可能有理解差异’成为需要调查的问题，而不是已确定原因或责任。",
            "reasoning": [reasoning(
                "聊天记录仅有‘周五前给我初稿’和‘好的’，回访中两人报告了不同的时间与稿件标准。",
                "原消息并未在提供的记录中形成可核对的共同排期，理解差异是一个可调查假设。",
                "来源区分参与者与消息，并将理解涉及的转换分为编码和解码；这让‘同一消息不等于已知相同理解’成为合理区分。把具体回访记作证据，是本课的分析方法。",
                "来源不证明本案当时发生过何种误解；回访不是原先心理状态的直接观测，也没有排除共同约定。",
            )],
            "check_instruction": "把每个判断读给自己听：能否指出它来自哪句记录，还是由你解释出来？试着给‘好的’再写一个不同但不违背材料的解释。",
            "check_expected": "原话、回访、解释分得开；保留至少两种解释和未知；不把‘周五前’私自定成某个客观截止。",
            "check_why": "只有能回查依据，后面的解释才有机会被纠正；填满表格本身不构成理解。",
            "check_limit": "这能检查你是否混淆材料与解释，不能确定任何人的真实意图。",
            "repair": "若写了‘林宁敷衍’，先改成‘可能在礼貌应答’，补上依据与待问的问题；若把回访当原话，重新标注时间与来源。",
            "practice": question(
                "q.communication.predict", "predict",
                "根据已经读到的消息和回访，预测实际交付时仍可能出现的两种不同安排。哪些与材料相容？哪些还不能确定？注意：你已看过示例，这不是无提示前测。",
                ["想想两人对时间和初稿的自述，哪些安排仍可能发生；自述没有保证最终行动。", "把‘会在周五十点给提纲’与‘会在下班前给排版稿’都当预测，而非原消息已经写出的事实。", "回访能支持‘两人这样描述理解’，不能确认他们最终怎样交付。"],
                ["提出两种实质不同的安排，并指明它们如何从未明确的词产生。", "使用回访核对但不把回访变成原先意图的直接证明。", "保留日期、时刻和标准未共同确认的限制，不用个人习惯裁决。"],
                ["stage.communication.evidence"],
            ),
        },
        {
            "id": "stage.communication.mapping",
            "title": "沿着想法、文字和语境找可能的岔路",
            "question": "差异可能出在哪个转换处，模型又漏掉了什么？",
            "purpose": "用编码、解码和语境解释一条具体的可能路径，再比较模型各自照见什么；不把模型里少一条箭头误判成人在现实中不能做某件事。",
            "why_now": "上一页已把差异和未知留住。现在需要能定位差异的语言，而不只是重复‘沟通不畅’。",
            "next_gap": "映射能提出位置不同的假设，却还不知道哪种解释更接近本案。下一步用能暴露理解的反馈，并提前写出反例。",
            "output": "out.communication.map",
            "output_name": "纸上解释草图与竞争假设",
            "output_kind": "value",
            "output_description": "以具体原话连接两端自述，标出编码、解码及未知语境；保留至少两个假设和各自的反证，不靠凑齐部件数量诊断。",
            "inputs": [("output", "out.communication.evidence", "需要上一页原话与未知约束解释，避免模型把猜测伪装成事实。", "能指出原消息、回访及至少一项仍未知的条件。")],
            "concepts": [
                concept(
                    "concept.communication.encoding", "把想法说出来，再由话形成理解",
                    "编码就是把想到的事变成可传出的表达；解码就是接到表达后形成自己的理解。它们不是计算机密码，也不是把一份意思原封不动搬过去。",
                    "用回访作暂时线索：‘周五十点的提纲’可能被周岚压缩成‘周五前给我初稿’；林宁可能由这句话想到‘下班前的排版稿’。把两处‘可能’保留在纸上。",
                    "文字没有损坏、双方认识每个字，不等于意义一致。反过来，如果双方能准确复述同一安排却不同意接受，它就未必是编码或解码问题。",
                    "我们刚发现一份消息对应两种自述，转换过程能把含混的‘没沟通好’拆成可追问的具体环节。",
                ),
                concept(
                    "concept.communication.context", "词义与当时情境",
                    "语境就是人理解这句话时带着的条件：在哪儿、是否忙乱、已有关系和工作约定等。环境噪声是物理干扰；语义噪声是表达中的符号或词义让理解受阻。同一个词不必陌生，也可能被赋予不同意思。",
                    "‘初稿’在回访里分别指提纲与排版稿，是可追问的语义差异；是否有共享模板是未知语境。原材料没有手机故障、嘈杂现场或压力的证据，不能为了凑项目把它们编进去。",
                    "把‘初稿’圈出来不是找到病因：双方也可能早有共同标准，只是在回访时改变了说法。没有写某个术语，不代表分析中不存在推断；写齐术语，也不代表解释成立。",
                    "只看文字会遗漏人依靠的背景；但加入语境后更容易读心，所以必须带着上一页的‘已知与未知’进入。",
                ),
                concept(
                    "concept.communication.model", "模型是一张取景图，不是现实的边界",
                    "传递模型把一条消息从发送者到接收者的路画清楚，包含编码与解码，也讨论噪声；互动模型把往返反馈及物理、心理语境放进来；交互共构模型（transaction）还看人如何在社会、关系、文化语境里同时发送和接收，形成关系和共同现实。它们各自省略一些复杂性。",
                    "先用传递视角看这条文字怎样被理解；当我们要观察林宁怎样回应，就用互动视角看往返。后面若关心上下级关系如何影响能否说‘做不到’，再扩展到交互共构视角。不是每个案例都得用最复杂模型。",
                    "‘传递图没有画反馈回路’只说明图的表达范围，不说明现实里不能回问，更不说明优化解码是白费力气。模型里没有画到的因素也可能存在。",
                    "下一步将主动索取反馈。现在先交代为何换取景范围，免得把换模型说成换了现实机制，或把模型当成一张七格故障清单。",
                ),
            ],
            "operation": "沿着两端自述和中间原话画解释草图，逐一标出材料与假设；为措辞差异和其他解释分别提出可反驳的预测。",
            "before": "我们只有不同自述，尚不能定位理解差异，也容易把‘初稿含混’当成唯一原因。",
            "because": "把表达前后的意思并列，有助于定位待确认的词；把竞争解释和反证写出，能防止一张模型图包办所有诊断。此方法组织调查，不从草图本身证明因果。",
            "after": "形成可用于下一轮问话的假设：词义未对齐，或理解虽接近但顾虑、能力与安排另有问题；各有待取证处。",
            "action": "在证据页旁画‘周岚回访自述—原消息—林宁回访自述’，在两段转换处写编码、解码，并注明这不是原先思想的实测。用圈注标出‘周五前’和‘初稿’。写假设一：词义或标准不同；假设二：原本理解接近，但因安排或顾虑未表达。分别写一个会令它减弱的新证据。不要为未知环境编故事，不要求补齐任何固定数量的框。",
            "method_note": "草图的价值是带出下一句问题。例如‘你说的初稿具体包含哪些内容？’比‘你有没有解码失败？’更能取得可比较的材料。",
            "walkthrough": [
                "承接证据页，我画出三段，并用虚线连接回访自述与原话，提醒自己没有看到发送前的思想。编码和解码只是描述转换的词，不是已经抓到的故障。",
                "假设一：‘初稿’和时间的理解不同。若能找到发送前已共享且双方沿用的明确标准，‘原消息措辞差异是主因’就会减弱，但仍需核对双方是否实际采用。",
                "假设二：林宁理解了安排，却因忙碌或顾虑先应答。若他能在安全的问话中给出当时不同的具体安排，支持单纯‘理解一致’的证据会减弱；这也不能直接证明没有压力。两种因素可共存。",
                "我没有给‘环境噪声’填一个想象的吵闹办公室。用互动视角补一段回问，理由是需要看见对方怎样理解，不是因为现实中突然获得了一个原先不存在的反馈通道。",
            ],
            "observation": "两种假设都还只是解释候选。模型帮助提出‘你说的初稿是什么？’等问题，不能单凭部件齐缺确定原因。",
            "reasoning": [reasoning(
                "两段回访对‘初稿’和时间的说法不同；原消息没有给出可比较的细节。",
                "词义或标准的差异值得优先追问，但工作安排与关系顾虑仍是竞争解释。",
                "来源将编码定义为思想转成沟通、解码定义为沟通转成思想，说明语义噪声可能来自词义；互动和交互共构视角扩大语境范围。这支持提问方向，不验证本案诊断。",
                "原消息含混不充分证明它造成全部差异；没有环境证据不能证明无环境影响，模型也不是现实因素的完整清单。",
            ), reasoning(
                "传递视角没有显式往返反馈，而本案接收者仍需形成理解。",
                "为了看清后续回应可转向互动视角，但不能由画法推出现实中禁止反馈或改进解码无用。",
                "来源明确让传递模型包含接收者解码，并讨论环境与语义噪声；开头也说明所有模型都简化实际过程。",
                "视角比较不证明某个模型对本案已有预测优势；不能把模型差异当作人类能力的有无。",
            )],
            "check_instruction": "沿草图说明每一段为什么在这里；给两个假设各指出一个会令它减弱的可能材料，并说出图没覆盖的一件事。",
            "check_expected": "能用自己的话解释编码与解码，区分词义问题和无证据的语境猜测；反证针对假设，不是只把七个部件填满；承认模型省略不等于现实不存在。",
            "check_why": "能说明定位依据和反例，才表明模型在帮助思考，而不是用名词替代解释。",
            "check_limit": "一个像样的解释草图仍不是观察研究，更不能判定两人的责任。",
            "repair": "若每个问题都归为‘编码失败’，补写一个‘复述一致但做不到’的情况；若说线性模型不许解码，回到本课模型段落并重画接收者形成理解的一段。",
            "practice": question(
                "q.communication.explain", "explain",
                "不用‘沟通不畅’概括：‘初稿’可能怎样经历编码和解码而出现两种理解？为什么传递模型没画反馈，不等于现实中问一句也没用？",
                ["从周岚回访的提纲，到原话，再到林宁回访的排版稿逐段说。", "把你无法直接观察的思想标成假设；区分图里省略和现实中不能发生。", "传递模型本来就包含解码；互动模型让往返更容易分析。"],
                ["说明两次转换，不把编码解码说成文字加密。", "用具体材料指出一种可能岔路，同时保留原先心理未知。", "明确模型是简化表达，未画反馈不说明不能反馈，更不排除改进解码。"],
                ["stage.communication.mapping"],
            ),
        },
        {
            "id": "stage.communication.feedback",
            "title": "让反馈带来证据，而不只再收到一个‘好的’",
            "question": "怎样回问才能比较理解？什么新材料会推翻原来的诊断？",
            "purpose": "把笼统确认变成能暴露日期、时刻、交付标准与可行性的复述；在反馈出现前写预测与反例，再根据回应修订，而非把复述当保证。",
            "why_now": "上一页的假设已经指出想查的词和其他可能。现在可以设计一轮有区分力的反馈，而不是无目的地多说一次。",
            "next_gap": "即使双方准确复述同一要求，任务仍可能有冲突。最后需要练习在‘理解一致’之后改变问题，而不是无限改写措辞。",
            "output": "out.communication.feedback",
            "output_name": "纸上回问、回应与假设修订",
            "output_kind": "evidence",
            "output_description": "保留回问方案、先写的预测、明确标为虚构续段的回应及逐条修订，说明反馈能支持什么、不能保证什么。",
            "inputs": [("output", "out.communication.map", "回问必须回应上一页具体的未知和竞争假设，而非换一套无关话术。", "纸上有两个假设、各自反证及未被模型覆盖的条件。")],
            "concepts": [
                concept(
                    "concept.communication.feedback", "反馈是对方怎样回应的材料",
                    "反馈是对消息的回应。问‘懂了吗？’常只再得到‘懂了’；请对方用自己的话说要在何时交什么，更容易比较双方理解。你还得回应他的复述，协商后再确认，不是把复述当服从测试。",
                    "可问：‘我现在提议的是 11 月 6 日周五北京时间上午十点，先给三条设计思路和待确认问题，不要排版。你理解的日期、时刻和内容是什么？这个安排能否做到？有分歧请直接说。’这里‘现在提议’很重要，它不是把原消息的歧义倒推成已经客观解决。",
                    "准确复述是表达出来的理解证据，不保证真心同意、能够完成或以后不改变；一句‘好的’也不是零信息，只是区分不同理解的能力较弱。",
                    "上一页要查时间和初稿含义，这种问法直接生成可比较的回应，同时给能力或关系顾虑留下表达入口。",
                ),
                concept(
                    "concept.communication.hypothesis", "用预测与反例约束诊断",
                    "假设是有待核对的解释；先写它预期看到什么，再写看到什么会让你改变想法。反例让你知道一种解释何时不够用，而不是要求一次问话选出唯一原因。",
                    "如果主要是交付标准不同，明确提议并请复述后可能出现标准对齐；如果复述一致仍说‘我做不到’，就要调查工作安排而非继续断言对方没听懂。",
                    "只改一句话后事情好转，不证明所有利益冲突都已排除：问话可能同时改变注意力、信任和要求本身。本课虚构分支更不是因果实验。",
                    "反馈容易让人急着宣布修复成功。先设反例，能迫使我们在出现不同回应时改换解释，而不把任何结果都算作支持自己。",
                ),
            ],
            "operation": "针对假设先写两种可区分的回应预测，再设计具体复述和可行性回问；把反馈与原假设比较，写出保留、削弱与仍未知。",
            "before": "两个解释都与现有材料相容，再收一个‘好的’很难区分它们。",
            "because": "日期、时刻和内容的复述使理解可以比较；可行性问题增加非措辞解释的表达机会。先写反例能减少事后把任何回应都解释成成功的倾向，但不能消除回应失真。",
            "after": "得到一段能被比较的回应和有限度的修订，不声称因一次反馈就已保证理解、认同或交付。",
            "action": "在纸上先写两种预测：复述仍不同会怎样改问，复述一致却做不到会查什么。再写明确标为‘新提议’的回问，包含日历日期、时刻、时区、初稿内容，并邀请对方复述和表达可行性。阅读示例续段后，用它修订假设，最后写一句‘这次反馈仍不能证明……’。不联系真实同事，也不冒充实际发送过消息。",
            "method_note": "先预测再展开示例；如果日期只是你提出的条件，就一直称作新提议。不要用例子里的精准日期覆盖原消息留下的歧义。",
            "walkthrough": [
                "我先写：若仍复述成排版稿，继续问‘提纲和排版稿的差别在哪里’；若复述准确却说做不到，追问时间与资源约束，而非再要求说一遍。",
                "写下概念段中的新提议，并邀请复述及拒绝。它把双方尚未共同确认的内容摆到桌面上，不是在解释‘周五前’唯一正确的意思。",
                "以下是作者编写的虚构续段，不是已进行的问话结果：林宁回‘按你现在的提议，是 11 月 6 日北京时间十点，三条思路和问题，不排版。这个时间我还不能答应，我周五下午才拿到测试意见。’",
                "我据此写：对新提议的表达理解已有较强证据；‘只是词义不同’已不足以解释当前障碍。测试意见何时到达、可否提前、双方是否接受新标准，仍需核对。原来是否存在误解，并没有因此被证明或推翻。",
                "如果另一虚构分支里准确复述后准时交付，也只能说与‘明确提议有帮助’相容；问话改变了多项条件，不能据此证明措辞是唯一原因。",
            ],
            "observation": "续段中林宁能复述新提议，却拒绝承诺。这个作者设定的反例说明‘表达理解一致’与‘能完成且同意’需要分开，不是关于现实因果效应的数据。",
            "reasoning": [reasoning(
                "虚构续段里，林宁复述了新提议的日期、时刻和内容，随后表示尚不能答应。",
                "这段回应支持‘对新提议的表达理解较一致’，但当前障碍不能仅按词义问题处理。",
                "来源的互动模型把反馈看作对消息的回应，并放在物理、心理语境中；因此可以用回应比较表达出来的理解。预测、反例和可行性区分是本课作者的教学设计，不是来源对本案的实验结论。",
                "续段是虚构材料；准确复述不能保证原先理解、真实意愿、执行能力或未来交付，单次问话也不能排除所有竞争原因。",
            )],
            "check_instruction": "用笔分别划出‘新提议’、‘回应给出的理解证据’和‘仍未知的可行性’。看原来的两个假设是否真的可能被回应削弱。",
            "check_expected": "回问能比较具体条件且允许不同意；有先写的预测和反例；修订没有把复述等同于承诺，没有用新提议倒填原先意图。",
            "check_why": "只有反馈可能改变你的判断，它才在调查中起作用；若任何回应都被算成成功，假设就无法受证据约束。",
            "check_limit": "这只是用虚构回应练习证据更新，不是有效话术测试或真实沟通修复。",
            "repair": "若只问‘听懂了吗’，改为邀请具体复述与说明可行性；若写‘证明只是编码问题’，补上准确复述却做不到的反例，并降低结论强度。",
            "practice": question(
                "q.communication.diagnose", "diagnose",
                "林宁准确复述新提议，却说周五下午才拿到测试意见。请诊断‘再把消息写清楚一点就能解决’这句话缺了什么证据，并写一个不会预设对方有错的追问。",
                ["先分开听懂、同意、能做三件事。", "‘测试意见’是续段中的自述，还需要核对什么安排？", "可问‘你需要哪些测试意见才能给三条思路？有没有不依赖它的部分？’但不要预设一定可以拆分。"],
                ["指出准确复述已提供表达理解证据，不能继续把全部障碍归为措辞。", "追问资源或依赖、允许不可拆分或做不到的回答，不强迫承诺。", "承认能力与意愿仍未知，不把自述直接当已核实日程。"],
                ["stage.communication.feedback"],
            ),
        },
        {
            "id": "stage.communication.transfer",
            "title": "已经听明白，为什么仍谈不拢？",
            "question": "当措辞清楚而目标冲突，下一步为什么不再是润色一句话？",
            "purpose": "在同一案例的近迁移续段中，把理解问题与优先级、依赖和利益冲突分开，说明关系语境怎样影响能否提出异议，并选择能推进问题的下一步。",
            "why_now": "复述已经让新提议的理解可比较。现在引入一个措辞清楚却依然冲突的情况，检验我们是否把所有问题都硬套成编码失败。",
            "next_gap": "本单元止于提出可核对的协商方案；真正的可行性、接受情况与后续交付要由真实记录检验，不能靠本课示例宣布成功。",
            "output": "out.communication.transfer",
            "output_name": "纸上近迁移决策与理由",
            "output_kind": "value",
            "output_description": "记录理解证据、双方目标与依赖、一个可撤回的协商方案、可能失败的条件及下次应核对的材料。不是用一张完成勾选代替结果。",
            "inputs": [("output", "out.communication.feedback", "上一页已经说明新提议与复述的证据限度，近迁移要在此基础上换问题，而非抹去反馈重新猜意图。", "能指出复述支持什么，以及为什么还不能保证承诺与交付。")],
            "concepts": [
                concept(
                    "concept.communication.agreement", "理解一致不等于目标一致",
                    "听明白要求，是能说明对方要什么；同意要求，是愿意接受；能够完成，则要有时间、资源与条件。三者可能一起出现，也可能分开。措辞能帮助呈现分歧，不能凭空制造资源或消除利益冲突。",
                    "近迁移给定：双方都能说清 11 月 6 日十点要三条思路。周岚需要给客户预留上午评审；林宁担心没有下午测试意见就交思路，会让错误方案被定下来。两人要保护的东西不同，不是又忘了日期。",
                    "不能由目标冲突反推原先绝无误解；也不能由先前有词义差异，断言现在所有分歧仍是编码问题。分歧层次会随新材料改变。",
                    "上一页出现‘准确复述却不能承诺’，现在必须拆开理解、认同与能力，才能提出不是重复澄清的行动。",
                ),
                concept(
                    "concept.communication.transaction", "关系与规则也在沟通中形成",
                    "交互共构视角不仅看消息来回，还看人如何在社会规则、关系历史和文化背景中同时表达与接收，并形成‘谁能提异议、什么算承诺’这样的共同规则。关系会影响说话，但不能只凭职位或身份替人断定心理。",
                    "周岚是负责人，这可能使林宁不便拒绝，但本案尚无足够证据。可明确说‘复述不算接受排期，不能做到请说条件’，并观察后续是否真允许异议。若改成当面讨论，人在说话时也可能同时读取对方表情并调整表达；这是模型示例，不是本案已观察到的行为。",
                    "交易或交互共构不是‘讨价还价’的别名。它也不意味着一旦提到关系，就能断言某种文化或某个人必然服从。三种模型是视角，不是必须升级的等级。",
                    "现在的难点关乎能否拒绝、如何定义承诺，超出单条文字的传递。引入这个视角，是为解释为何需要协商规则，不是再往图上堆术语。",
                ),
            ],
            "operation": "以准确复述为已给证据，分别写出双方要保护的目标和待核实依赖，提出一个有条件的协商选项及失败时转向的决策；保留未获同意和未执行的状态。",
            "before": "双方能复述同一要求，却因上午评审和下午测试的冲突无法达成承诺。",
            "because": "将目标与条件并列，才能讨论范围、风险或截止的取舍；明确复述不等于承诺，能让异议成为可讨论材料，而不是被误记为已同意。它不保证权力关系安全或资源充足。",
            "after": "给出一个可检查但未必可接受的协商方案，写明需要谁确认什么；没有把理解一致伪装成冲突消失。",
            "action": "阅读本阶段虚构近迁移续段。在纸上先写双方已经共同复述的要求，再分别写周岚和林宁要保护的目标与仍待核实的条件。提出一个有条件的选项，例如上午给注明未测试的可讨论提纲、下午补测试结论；同时写若客户不接受未测试材料，应由谁在推迟评审、减范围或加资源中作决定。最后写下一条要问的话和判断方案可行所需的新材料，不宣布已经谈妥。",
            "method_note": "这不是要求你凑一个双赢结局。若条件不允许，承认冲突、寻找有权取舍的人，比继续润色同一句要求更诚实。",
            "walkthrough": [
                "作者给定的近迁移续段：双方明确重复‘11 月 6 日北京时间十点，三条思路与待确认问题，不排版’。周岚说客户上午评审必须有材料；林宁说下午才有测试意见，担心上午草案被当作定案。两人都表示听懂对方，但还未接受安排。",
                "我在纸上写：已经有表达理解一致的材料；冲突点是评审时点与未测试方案的风险。测试能否提前、客户是否接受风险标注、谁有权改评审，尚未核实。",
                "我提出而非宣布：‘如果客户接受不作为定案依据，上午是否可以给标明未测试的三条思路，下午再补结论？如果不接受，我们请有权改评审的人决定时间或范围。’这是一项待双方和客户确认的取舍，不是措辞能自动实现的结果。",
                "我再问：‘刚才的复述只确认我们听到相同安排，不算承诺。你还需要什么条件才能接受？如果不能拆分，也请直接说。’负责人是否真容许异议，要看接下来怎样回应，不能由一句邀请自证安全。",
                "反例保留在纸上：若法规或客户流程禁止未测试提纲，分阶段交付就不可行；若测试实际可提前，原方案也可能不再必要。新材料应能改变我们的行动。",
            ],
            "observation": "这个近迁移由作者特意设定为措辞清楚且表达理解一致，仍存在目标冲突；它用作概念边界的反例，不能当作对某组织关系或任何话术效果的实证。",
            "reasoning": [reasoning(
                "近迁移续段给定双方复述一致，并各自说明上午评审与下午测试风险，尚未承诺。",
                "当前应调查依赖并协商取舍，不宜继续把冲突全部归结为编码或解码。",
                "来源的交互共构模型把沟通放在社会、关系与文化语境中，讨论同时发送和接收以及共同现实的形成，提醒我们不只看单条消息。把本案分成理解、同意与能力，是作者为此案例所作的分析，并非来源证明的个案结论。",
                "续段为虚构反例；不能由职位推断恐惧，也不能从一项协商建议证明关系改善或利益冲突已被解决。",
            )],
            "check_instruction": "遮住模型名称，仍能否用具体材料解释为什么现在要协商取舍？再用‘客户拒绝未测试材料’检验自己的方案会否改变。",
            "check_expected": "指出复述证据和目标冲突；提出有条件的选项、所需确认者与可令方案失效的条件；不把复述当接受，不强行制造圆满结局。",
            "check_why": "在新条件下能改变行动依据，才显示概念帮助了决策；换几个名词而继续重复澄清不算迁移。",
            "check_limit": "纸上方案未经当事人、客户或资源约束验证；本课不能证明协商能力或实际问题已解决。",
            "repair": "若只改写截止句，先指出双方哪一项理解仍不一致；若找不到，就转去核对依赖与决策权限。若写‘已达成共识’，改为‘提议，待确认’，并补失败条件。",
            "practice": question(
                "q.communication.transfer", "transfer",
                "双方都能准确复述明确排期，却分别要保护客户评审和测试质量。请写下一句话、它为何不是单纯澄清，以及一个会使你的提议失效的条件。",
                ["先写听懂与尚未同意各有什么材料。", "考虑是否能改范围、时间、风险或资源；不要预设一定能分段交。", "若客户不允许未测试材料，谁有权决定评审时间？"],
                ["下一句话回应双方目标或依赖，不再只要求复述。", "说明为何需要协商取舍，提出需确认的条件与人员。", "给出具体失败条件，并据此调整而不是强行宣布成功。"],
                ["stage.communication.transfer"],
            ),
        },
    ]


def artifact(authored: list[dict]) -> dict:
    stages = []
    concepts = []
    operations = []
    for lesson in authored:
        operation_id = lesson["id"].replace("stage.", "operation.", 1)
        concept_ids = [item["id"] for item in lesson["concepts"]]
        stages.append({
            "id": lesson["id"], "title": lesson["title"], "local_goal": lesson["purpose"],
            "why_it_exists": lesson["why_now"], "local_outcome": lesson["after"],
            "concept_refs": concept_ids, "operation_refs": [operation_id], "branch_refs": [],
            "implementation_details": [{
                "title": lesson["output_name"], "action": lesson["action"], "command": "",
                "expected_result": lesson["check_expected"],
            }],
            "example": {
                "summary": lesson["observation"],
                "input": "；".join(item[1] for item in lesson["inputs"]),
                "output": "\n".join(lesson["walkthrough"]),
                "note": "作者虚构的教学演示，不是真实观测、已执行行动或因果实验。",
            },
            "evidence_refs": [{"source_id": SOURCE_ID, "quote_hint": "仅支持一般概念；虚构案例及其诊断不是来源事实。"}],
        })
        for item in lesson["concepts"]:
            concepts.append({
                "id": item["id"], "name": item["name"], "definition": item["plain_language"],
                "role": item["why_here"], "related_concept_refs": [],
                "key_operation_refs": [operation_id],
            })
        operations.append({
            "id": operation_id, "name": lesson["output_name"], "definition": lesson["operation"],
            "purpose": lesson["purpose"], "acts_on_concept_refs": concept_ids,
            "common_failures": [lesson["repair"]],
        })
    return {
        "schema_version": "0.1", "artifact_id": "cop.communication-basics.authored",
        "domain": {
            "name": "沟通基础：同一条排期消息，为何两个人理解不同？",
            "scope": "一条虚构排期消息的证据分析、模型取景、反馈与近迁移；不是完整传播学教材。",
            "target_user": "能读日常中文、遇到过排期分歧的初学者；不要求编程或术语基础。",
            "non_goals": ["不诊断真实个人心理或组织文化。", "不保证话术有效，不替代资源与利益协商。", "不自动生成、执行、评分、入库或发布。"],
        },
        "mental_model": {
            "summary": "先保留记录和未知，再用转换与语境提出解释，通过可比较的反馈修订；若理解已一致，转向目标、资源与关系条件，不把一切当编码故障。",
            "flow": [item["question"] for item in authored],
        },
        "goals": [{
            "id": GOAL, "title": "有依据地解释排期理解差异，并在新条件下选择下一步",
            "outcome": "用纸上材料区分观察与推断，解释模型为何有用又不等于现实；设计能改变判断的反馈，并在清晰表达仍有冲突时转向协商。",
            "why_it_matters": "避免把‘好的’当共同理解、把模型当现实边界、把利益冲突误判成措辞问题。",
            "prerequisite_goal_refs": [], "evidence_refs": [{"source_id": SOURCE_ID}],
        }],
        "shared_foundations": [],
        "main_processes": [{
            "id": PROCESS, "goal_ref": GOAL, "title": "围绕同一案例逐步解释与修订",
            "start": {"type": "zero", "ref": None}, "stage_refs": [item["id"] for item in authored],
            "outcome": "留下四份相互承接的纸上记录，以及一个有限度、可被新证据改写的行动判断。",
            "practice_ref": "practice.communication.inquiry",
        }],
        "stages": stages, "concepts": concepts, "operations": operations, "branches": [],
        "practices": [{
            "id": "practice.communication.inquiry", "goal_ref": GOAL,
            "title": "从原消息到近迁移的纸上证据链",
            "instructions": [item["action"] for item in authored],
            "expected_outcome": "四份持久纸上记录有依据、反例、修订与未验证项，不以术语齐全或勾选完成代替理解。",
            "checkpoint_questions": [item["question"] for item in authored],
        }],
        "expansion_map": [],
        "metadata": {
            "language": "zh-CN", "generated_at": "2026-11-03T00:00:00Z",
            "generator": "authored-communication-prototype/1 (fixed revision label, not a runtime timestamp)",
            "source_ids": [SOURCE_ID],
        },
    }


def causal_links(lesson: dict) -> list[dict]:
    """Explain each concept's distinct role instead of repeating a stage paragraph."""
    moves = {
        "concept.communication.observation": (
            "把‘好的’直接解释成理解一致，容易把待查判断写成事实。",
            "将原话、回访时间与自己的解释分开记录。",
            "可回指的材料使后续解释受约束；分开记录让新证据能够修订判断，不等于消除了误判。",
            "纸上留下哪些是材料、哪些是解释，以及原先心理仍未知的边界。",
        ),
        "concept.communication.message": (
            "同一文字与两种回访自述混在一起，差异的对象不清楚。",
            "并列写出参与者、实际文字和两种自述中的理解，不把三者合成同一件事。",
            "把消息与理解分开，才看得出需要解释的是意义如何形成，而不是先假定谁没收到文字。",
            "保留一个具体待解问题：文字相同，为何自述的安排不同？",
        ),
        "concept.communication.encoding": (
            "只说‘没沟通好’，无法指出应追问哪里。",
            "沿回访自述、原话与另一端自述，标出可能的编码和解码转换。",
            "两处转换能定位待追问的表达与理解；原先思想未被直接观察，故连线仍标为假设。",
            "可以追问‘初稿指哪些内容’，而不是给人贴‘解码失败’标签。",
        ),
        "concept.communication.context": (
            "圈出含混词后，容易忽略既有约定，也容易为噪声编造背景。",
            "写出已知词义差异与未知语境，并为候选解释列可能反证。",
            "同一词的含义可能受约定影响；将未知保留为未知，能防止模型项目代替证据。",
            "语义差异成为优先追问方向，环境与关系条件仍待取证。",
        ),
        "concept.communication.model": (
            "看到传递图没画反馈，可能误以为现实里回问无用。",
            "说明传递视角包含解码，再为观察往返改用互动视角，并写出各自省略。",
            "模型是选择性表示，不是现实边界；按问题选择取景范围，比把部件齐缺当病因更有解释力。",
            "能说明为什么此时要看反馈，而不声称现实刚新增了某种能力。",
        ),
        "concept.communication.feedback": (
            "再得到一句‘好的’，仍难比较时间和初稿标准。",
            "将具体条件标为新提议，请对方复述并表达可行性。",
            "回应使表达出来的理解可被比较；邀请说明可行性有机会暴露其他障碍，但不保证真实同意。",
            "得到关于新提议的理解材料，同时保留意愿、能力和交付未知。",
        ),
        "concept.communication.hypothesis": (
            "看到反馈后容易把任何结果都算成原诊断成功。",
            "先写不同回应的预测及反例，再用续段逐条修订假设。",
            "让证据可能削弱判断，能约束事后解释；虚构反例只检验概念边界，不估计实际因果效应。",
            "准确复述却不能承诺时，转查依赖，不再把措辞当充分解释。",
        ),
        "concept.communication.agreement": (
            "明确条件被双方准确复述，仍没有排期承诺。",
            "分别写出听懂的要求、双方目标和待核实资源，提出有条件的取舍。",
            "理解证据不能替代同意或能力证据；区分三者，才知道该核对依赖而非只重写消息。",
            "得到待确认的选项和可令方案失效的条件，而不是虚构共识。",
        ),
        "concept.communication.transaction": (
            "要求复述有可能被误记为接受，职位关系也可能影响提出异议。",
            "明确复述不算承诺，邀请表达条件，并核对谁有权改变安排。",
            "共同规则与关系条件影响消息的作用；说出允许拒绝仅是开始，还需观察实际回应，不能自证安全。",
            "把承诺规则、决策权限与后续观察写入协商方案，不凭身份判断心理。",
        ),
    }
    return [{
        "concept_ref": item["id"],
        "operation_ref": lesson["id"].replace("stage.", "operation.", 1),
        **dict(zip(("before", "action", "because", "after"), moves[item["id"]], strict=True)),
    } for item in lesson["concepts"]]


def unit(authored: list[dict], cop: dict) -> dict:
    steps = []
    outputs = []
    route = []
    for index, lesson in enumerate(authored):
        inputs = [{
            "kind": kind, "ref": ref, "why_needed": why, "readiness_check": ready, "path_ids": PATHS,
        } for kind, ref, why, ready in lesson["inputs"]]
        outputs.append({
            "id": lesson["output"], "name": lesson["output_name"],
            "description": lesson["output_description"], "producer_stage_ref": lesson["id"],
            "kind": lesson["output_kind"], "persistence": "durable", "format": "text",
            "content_ref": None, "path_ids": PATHS,
        })
        route.append({
            "stage_ref": lesson["id"], "question": lesson["question"],
            "builds_on": [] if index == 0 else [authored[index - 1]["id"]],
            "why_now": lesson["why_now"], "next_gap": lesson["next_gap"],
        })
        steps.append({
            "stage_ref": lesson["id"], "purpose": lesson["purpose"], "inputs": inputs,
            "concepts": [{
                "concept_ref": item["id"], **{key: item[key] for key in (
                    "plain_language", "concrete_example", "contrast", "why_here",
                )},
            } for item in lesson["concepts"]],
            "causal_chain": causal_links(lesson),
            "reasoning": lesson["reasoning"],
            "methods": [{"detail_index": 0, "teaching_note": lesson["method_note"], "optional": False, "path_ids": PATHS}],
            "output_refs": [lesson["output"]],
            "worked_case": {
                "kind": "illustration", "input_refs": [item["ref"] for item in inputs],
                "output_refs": [lesson["output"]], "walkthrough": lesson["walkthrough"],
                "observation": lesson["observation"],
            },
            "checks": [{
                "output_ref": lesson["output"], "instruction": lesson["check_instruction"],
                "expected": lesson["check_expected"], "why": lesson["check_why"],
                "limitation": lesson["check_limit"], "on_failure": lesson["repair"], "path_ids": PATHS,
            }],
            "practice": lesson["practice"],
        })
    stage_ids = [item["id"] for item in authored]
    return {
        "schema_version": "0.1-experimental", "unit_id": "unit.communication-basics.authored",
        "title": "同一条排期消息，为何两个人理解不同？",
        "outcome": "你能依据原话与回访提出而非断言解释，用自己的话说明编码、解码、语境与模型边界；能设计有反例的反馈，在表达理解一致但目标冲突时改选协商行动。",
        "task_brief": "请把自己当作案例讨论者，不是裁判。先读开篇事实与未知，再沿四个问题保存纸上证据、解释草图、反馈修订和迁移决策。示例供你跟随推理；到了练习，先独立作答，再按需逐条打开提示和复核依据。这是示例后的练习，不是未见示例的前测。全程无需终端、文件、网络或付费服务；不用联系真实同事。示例是作者虚构的推演，不是你已经执行过的沟通。",
        "binding": {"artifact_sha256": content_hash(cop), "goal_ref": GOAL, "process_ref": PROCESS},
        "orientation": {
            "question": "同一句‘周五前给我初稿’，为什么会对应两种安排，我们凭什么判断并选择下一步？",
            "why_this_route": "若先背模型，容易把每次分歧都贴成‘编码失败’。我们先保住原话与未知，确定要解释的差异；再沿想法变文字、文字形成理解的路找假设，说明模型照见什么又省略什么；随后用反馈让假设有机会被改写；最后用理解一致却目标冲突的近迁移，检验何时应停下润色、转向协商。这是为本题编写的一条路径，不宣称所有沟通都按四步发生。",
            "running_case": "周岚与林宁围绕一份初稿排期产生不同自述。本课始终沿用这两人；第三、四阶段新增材料都明确标为作者虚构续段。给定记录不等于作者知道所有未写出的心理与背景。",
            "case_facts": CASE_FACTS, "case_unknowns": CASE_UNKNOWNS, "route": route,
        },
        "profile": {
            "audience": "能读日常中文、经历过任务排期但未学过沟通模型的初学者。",
            "prior_knowledge": ["能区分一段原话与自己对它的解释；若还做不到，第一阶段会示范。", "不要求掌握传播学术语、编程、命令行或研究方法。"],
            "environment": ["已打开或拿到本课文本，以及能保留四份记录的纸笔；纸张布局不作要求。", "可独自完成或与同伴讨论，讨论不需要透露真实职场隐私。"],
            "exclusions": ["不据虚构案例裁定真实人的意图、过错或心理状态。", "不保证任何反馈话术必然奏效，不替代组织决策或利益协商。", "页面不替你执行行动、自动评分或认证学习效果。"],
            "resources": [{
                "id": ENTRY, "name": "本课虚构消息、回访与纸笔",
                "provenance": "案例、后续分支与纸上方法由本课作者编写；一般沟通概念改述自所列 OER。纸笔由学习者自备。",
                "readiness_check": "能读到开篇四项案例事实和三项未知；准备能留下原判断并在旁修订的纸张。不要求下载或创建文件。",
                "path_ids": PATHS,
            }],
        },
        "paths": [{
            "id": "paper", "label": "纸上探究：完整学习路径",
            "description": "阅读给定材料并保留四份纸上分析，完成预测、解释、诊断与近迁移。完整指覆盖本单元目标，不表示已通过真人验收或真实冲突已解决。",
            "goal_scope": "full", "needs_network": False, "may_cost": False,
        }],
        "outputs": outputs, "steps": steps,
        "assessment": [
            question(
                "q.review.predict", "predict",
                "若周岚只追加‘初稿就行，懂了吗’，林宁又回‘好的’，预测哪项关键未知可能仍保留。再设计一个更有区分力的回应要求。",
                ["比较两个‘好的’能否区分提纲和排版稿。", "让对方说明要在何日何时交什么，不是要求背诵术语。"],
                ["具体指出日期、时刻或交付标准仍可能不同。", "回应要求让不同理解可被观察，并允许表达不同意见。", "不把弱证据说成零信息或绝对无效。"],
                stage_ids[:3],
            ),
            question(
                "q.review.explain", "explain",
                "向没学过术语的人解释本案为何先记原话，再画转换，再索取反馈；传递、互动与交互共构三个视角分别帮你多看见什么，又不能替你证明什么？",
                ["先解释如果跳过原话，猜测会怎样冒充事实。", "传递看表达与理解，互动看往返，交互共构看关系与共同规则；各自仍有省略。", "用‘没有画反馈’与‘现实不能反馈’的差别检验自己的解释。"],
                ["用具体案例说明顺序的依赖，而不是只罗列模型定义。", "准确说明编码和解码，传递视角不排除解码。", "说明模型简化现实，未画某因素不证明其不存在；来源不能认证本案诊断。"],
                stage_ids,
            ),
            question(
                "q.review.diagnose", "diagnose",
                "同伴说：‘原消息没写编码、解码这些词，说明没有推断。把七个部件空格填齐，就知道病因；我只改一句话后事情好了，所以所有利益问题都排除了。’请分别指出证据缺口，并写出能改变诊断的新材料。",
                ["有没有术语，与有没有从材料推到解释，是两件事。", "图是否完整，与某因素是否造成这次分歧，也是两件事。", "想一个双方复述完全一致却仍拒绝排期的反例；想问话时还可能同时变了什么。"],
                ["用具体解释展示：即使没有术语，也存在推断。", "指出填框不确立因果，至少提出一个竞争解释及可令它减弱的材料。", "说明一次措辞变化与结果相伴不能排除利益等因素，且虚构推演不是因果实验。"],
                stage_ids,
            ),
            question(
                "q.review.transfer", "transfer",
                "近迁移变式：客户明确不接受未测试提纲，且测试无法提前；双方仍准确复述原定的明确时间和内容。请修改上一阶段的提议，写要交给谁作什么取舍、还需核对什么，以及为什么不再只润色一句话。",
                ["这两个新增条件使哪个旧方案失效？", "可以提出调整评审时间、范围或资源，但谁有权同意必须核对。", "允许暂时没有双方都接受的方案，不把复述当成承诺。"],
                ["撤回或修订未测试提纲的方案，回应新条件而非照抄示例。", "提出有权者需决定的具体取舍及待核实的权限或资源，不虚构已经同意。", "用复述一致与条件冲突的材料解释为何不只改措辞；保留理解、同意、能力的区别。"],
                stage_ids[2:],
            ),
        ],
        "sources": [{
            "id": SOURCE_ID,
            "title": "Anonymous，Communication in the Real World: An Introduction to Communication Studies，1.2: The Communication Process（LibreTexts，2026-11-03 检索）",
            "url": SOURCE_URL,
            "scope": "用于本课一般概念的主要开放教材来源：模型简化实际沟通；参与者、消息；编码是思想转成沟通、解码是沟通转成思想；环境与语义噪声；互动模型纳入反馈及物理、心理语境；交互共构模型描述同时发送和接收及社会、关系、文化语境。传递模型也包含解码，不能据图无反馈推出现实不能反馈。该页不证明本课任何具体心理、病因、责任、话术效应或协商结果。检索页当前署名 Anonymous，许可 CC BY-NC-SA 3.0（https://creativecommons.org/licenses/by-nc-sa/3.0/）；本课以该许可对改述与教学改编作教育原型提供，作了中文改述、新增虚构案例、证据方法与练习；非来源认可或背书。未复用来源图片、图表或长段原文。检索记录是文本核对，不是存档快照。",
        }],
        "limitations": [
            "手工编写的独立教育原型，不是 Harness 自动生成质量或跨领域因果改进的证明；学习单元仍为可选演进的 0.1-experimental，无生产迁移。",
            "一般概念改述自 Anonymous 所列教材页面，CC BY-NC-SA 3.0；本课教育改编同许可，保留链接、署名及改编说明，不暗示来源认可；无外部图示复用。",
            "案例、回访、续段、预测与反例均由作者虚构。它们展示如何限制结论，不提供真实因果效应、人物心理或组织文化的证据。",
            "原‘周五前’的日历日期与时刻没有因新提议而被客观追溯解决；复述仅为表达理解的证据，不保证同意、能力、未来交付或关系安全。",
            "结构检查与哈希只验证结构、引用、绑定和漂移，不判断概念正确、推理充分、学习者理解或迁移；纸张存在和完成勾选也不是学习证据。",
            "真人完成、解释、排错与无示例近迁移的验收仍 pending；复核标准用于具体反馈，不自动给分、排名或认证。",
        ],
    }


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def build() -> dict[Path, bytes]:
    authored = lessons()
    cop = artifact(authored)
    COPArtifact.model_validate(cop)
    lesson = unit(authored, cop)
    issues = check_learning_unit(lesson, cop)
    if issues:
        for item in issues:
            print(f"{item['code']} {item['ref']}: {item['message']}", file=sys.stderr)
        raise SystemExit(f"Learning unit has {len(issues)} contract issue(s); nothing was written.")
    manifest = unit_manifest(lesson, cop)
    if manifest["scope"] != "structure-and-bindings-only" or manifest["issues"]:
        raise SystemExit("Unexpected manifest result; nothing was written.")
    return {ARTIFACT_PATH: encode(cop), UNIT_PATH: encode(lesson), MANIFEST_PATH: encode(manifest)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write only the three named communication-basics JSON fixtures")
    args = parser.parse_args()
    expected = build()  # Validate every payload before writing any file.
    if args.write:
        for path, payload in expected.items():
            path.write_bytes(payload)
        print("Communication lesson valid; 0 contract issues. Wrote only the three communication-basics JSON fixtures.")
        return
    drift = [str(path.relative_to(ROOT)) for path, payload in expected.items()
             if not path.is_file() or path.read_bytes() != payload]
    if drift:
        for path in drift:
            print(f"FIXTURE_DRIFT {path}", file=sys.stderr)
        raise SystemExit("Check failed; nothing was written. Review authored changes, then use --write explicitly.")
    print("Communication lesson valid; 0 contract issues; all three fixtures match. Structure only; human acceptance pending.")


if __name__ == "__main__":
    main()
