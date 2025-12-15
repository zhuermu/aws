# Nova 2 Presentation Content

## Slide 1

Nova 2.0系列模型的Preview测试效果和踩坑指南

郝鑫

SSO GenAI GTMS 
xinha@

GCR GenAI Office Hour

高云怡

SSO GenAI SSA
yunyigao@

唐清原

SSO GenAI SSA
tangqy@

---

## Slide 2

会议目标
Nova 模型系列有哪些发布？
Nova 2.0 Lite，Nova 1.0 Lite的升级版。研发阶段希望对标Gemini 2.5 Flash。
Nova 2.0 Sonic，新增中日韩等共10种语言支持、文字模态输入、增强tool use和语义理解能力。
Nova Omni (preview)作为首个“Any-to-Any”模型，支持文字、图片、视频、音频输入，当前输出支持文字和图片（后续扩展其他模态）。
Nova 2.0 Pro (preview)， Nova 1.0 Pro的升级版。
Nova Act和Nova Forge。

在GCR的Preview测试中，Nova 2.0 Lite的表现如何？
Nova 2.0系列相比上一代有较大提升，但能力并不均衡（中文等非拉丁语种场景限制较多）。
建议GCR同事们继续“扬长避短，场景聚焦”，赢得优势场景，并通过roadmap持续补齐短板。

Next Action
引导客户测试优势场景，帮助客户建立信心（避免与Gemini 2.5 Flash全面竞争）
抛砖引玉，发挥集体智慧，探索Nova 2.0系列模型的更多优势场景

---

## Slide 3

3

全新的Nova模型产品组合

1. Nova Foundation Models快速、性价比极高的基础模型系列。
GA: Nova 2 Lite，Nova 2 Sonic，Nova MME
Preview：Nova 2 Pro，Nova 2 Omni

2. Nova Forge一项以前沿方式构建自定义模型的全新服务。

3. Nova Act一个由 Nova 2 Lite 自定义模型驱动的 Agent 构建服务，用于自动化 UI 工作流（i.e., computer use）。

Nova产品主页及价格
https://aws.amazon.com/cn/nova/pricing/

---

## Slide 4

4

Nova Forge：构建企业专有的前沿AI模型

什么是 Nova Act？
首个"开放训练"的前沿模型构建服务
基于Amazon Nova模型系列构建自定义模型
可从预训练、中期训练、后训练阶段开始
融合专有数据与AWS精选的训练数据
构建Nova + 企业数据的融合体
强化学习环境：在自定义环境中使用奖励函数进行强化微调
安全工具包：内置AI安全工具包实现自定义安全防护

解决的核心问题
传统微调的局限：无法深度整合企业专有知识
开源模型的风险：再训练时易导致"灾难性遗忘"
从零开始的成本：巨大的计算和资源投入
解决方案：在最优阶段注入专有数据，保留基础能力

四个训练阶段
预训练
大量非结构化数据，在学习能力最强时引入
中期训练
中等量数据，在保留通用能力的同时学习特定域知识
有监督微调
标记的指令-响应数据集，教模型特定应用响应
强化学习
使用奖励信号和真实反馈进一步优化行为

---

## Slide 5

5

Nova ACT：大规模自动化UI工作流的AI代理服务

什么是 Nova Act？
90% UI workflow 自动化可靠度
领先于行业的 browser agent 基准性能（超越3.7 sonnet）
自动完成：浏览器操作、API 调用、工具执行（如生成 PDF）
复杂情况可升级到人工监督
工作流由自然语言 + 更确定性的 Python 脚本组合
使用定制的Nova 2 Lite模型驱动
Deployed Nova Act workflows：$4.75 per agent hour

核心能力
自主网页导航与交互
复杂表单填写与数据提交
API调用与第三方工具集成
人机协作与智能升级处理
支持并行运行数千个工作流

典型应用场景
自动化测试
端到端UI测试，加速发布周期，减少手工工作
数据录入
跨系统表单填写，提高准确率，释放人力
数据提取
从网页源自动提取和整合信息，支持竞争情报收集
订单处理
自动化购物、预订、结账流程，跨多个平台

开发到部署流程
快速原型
无代码在线Playground，使用自然语言提示(nova.amazon.com/act)
优化调试
在VS Code等IDE中进行开发和调试，https://aws.amazon.com/blogs/aws/accelerate-ai-agent-development-with-the-nova-act-ide-extension/
一键部署
只需几步即可部署到AWS
监控管理
集成CloudWatch和IAM进行管理

---

## Slide 6

6

全新的Nova 2 Foundation Models家族

*所有模型均支持高达上下文窗口1M tokens，单次响应可生成多达65,536个tokens。*对于具备推理能力的模型，支持混合推理模式，可根据任务需要开启或关闭推理功能；支持设置“低”、“中”、“高”三档推理预算。*Nova 2 Pro和Nova 2 Omni，当前仅有Nova Forge客户和授权客户可获得早期访问权限。

---

## Slide 7

7

核心智能能力 (CORE INTELLIGENCE)
MMLU-Pro - 涵盖数学、科学、历史等570个学科的多选题测试，代表模型的广泛学科知识和推理能力。
GPQA Diamond - 由博士级PhD问题组成的科学推理测试，代表模型的深度科学理解和高难度推理能力。
AIME 2025 - 美国数学竞赛题目集合，代表模型的数学问题求解和复杂运算能力。
IF-Bench - 要求模型按照特定指令精准执行的测试，代表模型的指令遵循和精准理解能力。
MultiChallenge - 多个指令遵循任务的综合测试，代表模型的多样化指令执行能力。
LongCodeBench 1M - 包含百万Token级长文本的代码理解测试，代表模型的长文本处理和代码理解能力。

多模态感知能力 (MULTIMODAL PERCEPTION)
MMMU-Pro - 包含图片、表格、图表的复杂视觉推理测试，代表模型的多模态理解和视觉推理能力。
OCRBench-v2 - 文档光学字符识别和理解测试，代表模型的文本识别和文档解析能力。
RealKIE - 真实世界信息抽取任务（从图像中提取关键信息），代表模型的视觉信息提取能力。
QVHighlights - 基于查询的视频亮点提取，代表模型的视频理解和关键信息定位能力。

代理工作流能力 (AGENTIC WORKFLOWS)
T²-bench Telecom - 电信领域的工具使用和决策测试，代表模型的特定领域工具调用和问题解决能力。
T²-bench Retail Verified - 零售场景下的验证工具使用，代表模型的现实商业场景中的实际应用能力。
T²-bench Airline Verified - 航空领域的工具使用验证，代表模型的行业特定工作流处理能力。
BFCL Overall FC V4 - 函数调用能力综合测试，代表模型的与外部API/工具集成的能力。
Scale MCP Atlas - 多步骤规划和协调能力测试，代表模型的复杂任务规划能力。
ScreenSpot - UI界面理解和交互测试，代表模型的用户界面导航和理解能力。

软件工程能力 (SOFTWARE ENGINEERING)
SWE-Bench Verified - 真实Python代码库中的软件工程任务，代表模型的实际代码问题解决能力。
Terminal-Bench 1 Overall - 终端命令行操作和编码测试，代表模型的系统级命令执行和脚本能力。
LiveCodeBench - 代码生成实时更新的代码竞赛任务，代表模型的最新代码生成和创意编程能力。

**Images:** slide_7_image_1.png

---

## Slide 8

8

来源：https://artificialanalysis.ai/，12月3日

**Images:** slide_8_image_2.png

---

## Slide 9

9

*Nova 2 Lite支持Prompt Cached（输入2.5折），Batch（输入输出5折），Priority Tier（OD*1.75倍），Flex Tier（输入输出5折）

---

## Slide 10

10

Resources

Internal only

Developer Guide for Amazon Nova 2


Nova 2 Lite FAQ


Amazon Nova 2.0 Lite 模型内部Preview测试报告


Nova 2.0 Sonic及Nova Omni reinvent预计发布

---

## Slide 11

Thank You！

11

---

