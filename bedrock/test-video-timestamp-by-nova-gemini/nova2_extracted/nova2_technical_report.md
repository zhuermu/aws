# Nova 2.0 Technical Report

## Page 1

Amazon Nova 2: Multimodal Reasoning and Generation Models
Amazon Artificial General Intelligence
Figure 1: Amazon Nova 2 Family of Models
Abstract
We present Amazon Nova 2, a family of four foundation models designed to meet diverse enterprise
needs across reasoning, multimodal processing, and real-time conversational AI. The family includes
Nova 2 Lite and Nova 2 Pro — multimodal models with dynamic reasoning capabilities that allow
customers to balance accuracy, speed, and efficiency through configurable “extended thinking”
controls; Nova 2 Omni — a unified multimodal model that processes text, images, video, and audio
inputs while generating both text and images; and Nova 2 Sonic — a speech-to-speech foundation
model for natural conversational AI. Nova 2 models process large contexts with up to 1M tokens,
enabling analysis of extensive codebases, long documents, and videos within a single prompt. Like
all Nova models, the Nova 2 family is built with integrated safety measures and Responsible AI
guardrails, maintaining our commitment to customer trust, security, and reliability.

---

## Page 2

Amazon Nova 2 Family of Models - Technical Report and Model Card
1 Introduction
We introduce Amazon Nova 2, a family of four natively multimodal foundation models that address the full spectrum of
customer AI needs—from cost-effective everyday reasoning to frontier-level intelligence, unified multimodal processing,
and human-like, real-time voice interactions. The Nova 2 family excels on reasoning depth, modality support, and
conversational capabilities while maintaining industry-leading price-performance.
1.1 The Nova 2 Model Family
• Nova 2 Lite is our low-latency, cost-effective reasoning model for everyday workloads. It processes text, images,
and videos to generate text output. Developers adjust step-by-step "thinking" to balance intelligence, speed, and
cost—ideal for customer service chatbots, document processing, business automation, video information extraction,
code generation, and multi-step agentic workflows. It delivers industry-leading price-performance, matching or
exceeding Anthropic’s Claude Haiku 4.5, OpenAI’s GPT-5 Mini, and Google’s Gemini 2.5 Flash on most standard
benchmarks.
• Nova 2 Pro delivers our highest intelligence for complex workloads. It simultaneously processes text, documents,
images, videos, and audio—ideal for large-scale multimodal reasoning. The model excels in high-accuracy tasks,
multi-step planning, and workflow coordination, with strengths in long-document analysis, complex instruction
following, advanced math, and autonomous agentic/software engineering tasks. It matches or exceeds Anthropic’s
Claude Sonnet 4.5, OpenAI’s GPT-5/GPT-5.1, and Google’s Gemini 2.5 Pro/Gemini 3 Pro Preview across broad
benchmarks.
• Nova 2 Omni is our first unified multimodal model that processes text, documents, images, video, and audio inputs
and generates text and images from a single model, eliminating multi-model coordination complexity. It delivers
standout performance in multimodal perception, core reasoning, and agentic benchmarks, matching or exceeding
OpenAI’s GPT-5 Mini and Google’s Gemini 2.5 Flash. It also offers high-quality image generation/editing, strong
reasoning, instruction following, and tool calling—making it ideal for multimodal agentic applications.
• Nova 2 Sonic, our second-gen speech-to-speech model, delivers industry-leading quality and cost efficiency for
real-time voice AI. It surpasses GPT-Realtime (Aug’25) and Gemini 2.5 Flash Live (Sept’25) in conversational
quality (expressive, native-sounding voices) for English, French, Italian, German, and Spanish via real-time API,
based on human evaluations. It also leads in streaming speech understanding accuracy across 7 languages (EFIGS,
HI, PT) compared to GPT-Realtime and Gemini 2.5 Flash Live.
1.2 Key Highlights of Nova 2 Models
• Hybrid Reasoning: Nova 2 Lite, Pro, and Omni introduce extended thinking capabilities that give developers
fine-grained control over the accuracy-cost-latency trade-off. Developers can toggle reasoning on or off and adjust
reasoning depth through low, medium, and high settings—enabling fast responses for simple tasks while engaging in
systematic multi-step reasoning for complex problems. Figure 2 illustrates how accuracy increases with reasoning
effort on code generation tasks. Hybrid reasoning delivers strong performance across several benchmarks including
92.3% on AIME-2025 [27] for Nova 2 Pro, 76.6% on MultiChallenge [36] Instruction Following for Nova 2 Lite,
and 58.5% on OCR-Benchv2 [17] for Nova 2 Omni.
• Reliable Multi-Step Workflow Execution : Nova 2 family excels at completing complex, multi-step agentic
workflows with sophisticated tool use and planning capabilities. Specfically, Nova 2 Pro demonstrates frontier-level
performance on τ2-bench-Verified [13] for agentic task execution- 77.7% (retail), 65.2% (airline), and 92.7%
(telecom). Further, on SWE-Bench Verified [ 11] for autonomous software engineering tasks, Nova 2 Pro scores
70.0%, enabling reliable automation of complex business processes and development workflows.
• Native Multimodal Reasoning and Generation: Nova 2 models provide unified multimodal processing across text,
documents, images, and video with strong performance on multimodal reasoning and generation benchmarks. For
example, Nova 2 Lite achieves 62.1% on key information extraction benchmark - RealKIE-FCC Verified [43]. Nova
2 Omni combines multimodal input processing with native image generation and editing capabilities, eliminating the
need to coordinate multiple specialized models while maintaining high-quality outputs across all modalities.
• Real-Time Conversational AI: Nova 2 Sonic supports asynchronous tool calling, configurable turn-taking, and
seamless switching between voice and text modalities—enabling real-time conversations with low latency. Artificial
Analysis1 reports higher speech reasoning accuracy for Nova 2 Sonic, compared to GPT-Realtime and Gemini 2.5
Flash Live on Big Bench Audio data set.
1https://artificialanalysis.ai/models/speech-to-speech#summary
2

---

## Page 3

Amazon Nova 2 Family of Models - Technical Report and Model Card
Figure 2: Nova 2 Lite Extended thinking performance on
code generation tasks (LiveCodeBench) across reasoning
effort levels. Accuracy increases as the model allocates
more computational resources to reasoning, demonstrating
the configurable trade-off between speed and intelligence
that Nova 2 provides through its low, medium, and high
reasoning effort settings.
2 Nova 2 Lite and Pro - Hybrid Reasoning
Nova 2 Lite and Pro models deliver a major intelligence leap over our existing Nova models. As shown in Figure 3,
Nova 2 Lite surpasses our former flagship, Nova Premier, in multi-step problem-solving and agentic workflows—at 7x
lower cost and up to 5× faster.
Figure 3: Nova 2 Lite compared to Amazon Nova Premier
3

---

## Page 4

Amazon Nova 2 Family of Models - Technical Report and Model Card
In this section, we report benchmarking results for Nova 2 Lite and Nova 2 Pro and compare their performance to
selected publicly-available models, using results from cited publications, as well as from our benchmarking using
guidance provided in corresponding model cards where results are not publicly available.
2.1 Text Benchmarks
We evaluate text capabilities of Nova 2 Lite and Nova 2 Pro on a variety of standard text-only benchmarks, spanning
knowledge centric reasoning (MMLU-Pro [ 47], GPQA-Diamond [ 34]), Math (AIME 2025 [ 27]), and Instruction
Following (IF) (IF-Bench [31], MultiChallenge [36]).
MMLU-Pro GPQA AIME IF-Bench MultiChallenge LongCodeBench
Diamond 2025
acc acc acc prompt loose acc acc 1M match
Nova 1 Lite 59.0 43.3 7.0 34.1 18.7 – b
Claude Haiku 4.5 80.0 73.0 80.7 54.3 57.1 a –b
GPT-5 Mini 83.7 82.3 91.1 75.4 67.8 a –b
Gemini 2.5 Flash 83.2 82.8 72.0 50.3 62.6 a 78.0a
Nova 2 Lite 80.9 79.6 91.0 70.8 76.6 84.0
Nova 1 Pro 69.1 49.9 7.0 38.1 26.7 – b
Nova 1 Premier 73.3 56.9 17.3 36.2 22.0 42.0
Claude Sonnet 4.5 87.5 83.4 87.0 57.3 63.1 a 82.0a
GPT-5 87.1 85.7 94.6 73.1 69.6 a –b
GPT-5.1 87.0 88.1 94.0 72.9 72.2 a –b
Gemini 2.5 Pro 86.2 86.4 88.0 48.7 62.3 a 74.0a
Gemini 3 Pro Preview 89.8 91.9 95.0 70.4 73.6 a 82.0a
Nova 2 Pro 81.6 81.4 92.3 80.2 77.7 84.0
For Claude, GPT and Gemini, we use numbers from the model provider’s card, benchmark’s leaderboard, or Artificial Analysis’ Leaderboard.
a Benchmarked using guidance published in the corresponding model card.
b Model does not support this capability.
Table 1: Nova 2 Lite and Nova 2 Pro model performance comparison on text and long context benchmarks
Nova 2 models support input sequences up to 1M tokens, and we assess their long-context capabilities using the
LongCodeBench 1M [ 33] benchmark for code understanding and the OpenAI-MRCR [44] benchmark for multi-turn
information retrieval. Figure 4 illustrates the comparative performance of Nova 2 Lite and Nova 2 Pro on the MRCR
8-needle task for context lengths spanning 8k to 1M tokens.
2.2 Agentic Benchmarks
In Table 2, we report the agentic and tool-use abilities of Nova 2 Lite and Pro across BFCL v4 [ 29], τ2-bench
Verified [13], and Screenspot [ 10]. τ2-bench Verified is a human-validated revision of τ2-bench [6] that reliably
evaluates AI models’ ability to interact with external tools and user constraints. For τ2-bench verified, we evaluate
Nova 2 on airline, retail, telecom domains, and report the avg@3 metric. We will publish the verified dataset via
HuggingFace2. Additionally, we report performance (as a blind eval) on MCP Atlas [40] benchmark introduced by Scale
AI, which is designed to assess an agent’s ability to orchestrate multiple tools via MCPs to solve complex real-world
tasks. It evaluates whether agents can select appropriate tools from a large pool, invoke them in the correct sequence,
manage data or API interactions, and ultimately generate correct answers; We report the pass-rate metric — the fraction
of tasks where the final output matches the ground truth after tool execution.
2https://huggingface.co/datasets/amazon-agi/Tau2-Verified
4

---

## Page 5

Amazon Nova 2 Family of Models - Technical Report and Model Card
Figure 4: Nova 2 Lite and Pro long-context performance comparison on OpenAI-MRCR (8-needle) benchmark.
τ 2-bench τ 2-bench τ 2-bench BFCL v4 MCP Atlas
Telecom a Retail - Verified Airline - Verified
acc acc acc Overall FC Pass Rate
Nova 1 Lite 17.5 – – 33.2
Claude Haiku 4.5 54.7 69.1 b 54.0b 61.8
GPT-5 Mini 71.1 73.7 b 68.8b 56.0 22.2 d
Gemini 2.5 Flash 31.6 57.7 b 44.0b 55.9 –
Nova 2 Lite 76.0 76.5 64.8 60.3 24.6
Nova 1 Pro 14.0 – – 38.0
Nova 1 Premier 38.3 – – 53.9
Claude Sonnet 4.5 78.1 77.2 b 66.8b 68.7 43.8 d
GPT-5 86.5 78.3 b 72.0b 61.6 44.5 d
GPT-5.1 81.9 77.5 b 72.4b 60.1b
Gemini 2.5 Pro 54.1 71.3 b 60.0b 52.3 8.8 d
Gemini 3 Pro Preview 87.1 77.7 b 70.8b –c 54.1d
Nova 2 Pro 92.7 77.7 65.2 61.6
a This benchmark is sensitive to the choice of user model. For consistency, we report all numbers as benchmarked by https:
//artificialanalysis.ai.
b Benchmarked using guidance published in the corresponding model card.
c We were unable to benchmark this model despite multiple attempts.
d Reported by Scale on https://scale.com/leaderboard/mcp_atlas
Table 2: Nova 2 Lite and Pro model performance comparison across agentic benchmarks
5

---

## Page 6

Amazon Nova 2 Family of Models - Technical Report and Model Card
2.3 Image, Video, Document and Audio Understanding Benchmarks
Similar to Nova 1, Nova 2 models are capable of processing images, video and documents. In Table 3, we report
on a set of multimodal benchmarks spanning knowledge and reasoning (MMMU-Pro [51]), document understanding
(OCRBenchV2 [17], RealKIE-FCC [43]), spatio-temporal understanding of videos (QVHighlights [24]) and UI element
grounding for screen analysis and navigation (Screenspot [10]). For RealKIE-FCC [ 43], we have leveraged human
verification to refine the ground truth, and have published the verified version on HuggingFace 3. In addition, Nova
2 Pro is capable of processing audio input, and we report automatic speech recognition (ASR) results on Common
V oice [5] dataset for English, French, Italian, Spanish and German.
MMMU Pro OCRBench-v2 RealKIE-FCC Verified QVHighlights ScreenSpot Common Voice
accuracy avg accuracy ALNS R1@0.5 point accuracy WER - EFIGS ↓
Nova 1 Lite 38.0 55.1 40.4 11.9 80.1 –
Claude Haiku 4.5 58.0 48.3 a 52.2a –b –c –
GPT-5 Mini 74.1 55.4 a 53.1a –b 24.8a –
Gemini 2.5 Flash 69.0 58.2 a 50.1a 52.4 27.2 a –
Nova 2 Lite 61.8 56.1 62.1 77.2 83.3 – b
Nova 1 Pro 44.0 59.6 49.7 10.7 83.5 – b
Nova 1 Premier 52.4 61.2 54.6 4.5 86.2 – b
Claude Sonnet 4.5 69.0 52.3 a 62.4a –b –c –b
GPT-5 78.4 58.1 a 51.9a –b 31.0a –b
GPT-5.1 76.0 57.2 a 53.6a –b 28.5a –b
Gemini 2.5 Pro 68.0 59.3 54.9 a 75.0 44.7 a 7.2a
Gemini 3 Pro Preview 81.0 69.6 a 71.7a 48.1a 66.8a 7.4a
Nova 2 Pro 63.5 64.5 67.0 76.7 88.1 5.5
a Benchmarked using guidance published in the corresponding model card.
b Model does not support this capability.
c We were unable to benchmark this model despite multiple attempts.
Table 3: Nova 2 Lite and Pro model performance comparison on image, video and audio benchmarks
2.4 Software Engineering Benchmarks
In Table 4, we report Nova 2 performance on software engineering capabilities - LiveCodeBench [21] and SWE-Bench
Verified [11]. In addition, we report on Terminal-Bench 1.0 [ 41] which evaluates the model’s ability to complete
complex tasks in terminal environments, testing command-line proficiency across 80 hand-crafted and human-verified
tasks.
2.5 Latency and Speed
We evaluate the latency and speed of Nova 2 Lite and Pro using two metrics, Time to First Token (TTFT) and Output
Tokens per Second (OTPS). TTFT is measured as the time, in seconds, it takes to receive the first token from the model
after an API request is sent. OTPS is measured as the number of tokens received per second (tok/sec) after the first token
is received. Figure 5 shows TTFT and OTPS using 1K input tokens for Amazon Nova 2 models and other competing
models as reported by Artificial Analysis4.
3https://huggingface.co/datasets/amazon-agi/RealKIE-FCC-Verified
4https://artificialanalysis.ai/methodology
6

---

## Page 7

Amazon Nova 2 Family of Models - Technical Report and Model Card
SWE-Bench Terminal-Bench LiveCodeBench c
Verified 1.0 Code Generation
acc accuracy acc
Claude Haiku 4.5 73.3 41.8 61.5
GPT-5 Mini 71 30.8 83.8
Gemini 2.5 Flash 48.9 / 60.4 a 16.8 69.5
Nova 2 Lite 53.6 / 64.5b 32.5 71.0
Nova 1 Premier 42.4 11.3 31.7
Claude Sonnet 4.5 77.2 / 82.0 a 51 71.4
GPT-5 72.8 41.3 84.6
GPT-5.1 76.3 53.8 d 86.8
Gemini 2.5 Pro 59.6 / 67.2 a 25.3 80.1
Gemini 3 Pro Preview 76.2 56.3 d 91.7
Nova 2 Pro 61.5 / 70.0b 41.3 74.6
a Performance reported by provider using test-time scaling.
b Benchmarked with inference time scaling and using internal Agentic scaffolding.
c LiveCodeBench v5 (1 July 2024 to 1 Jan 2025 subset)
d Benchmarked using guidance published in the corresponding model card.
Table 4: Nova 2 Lite and Pro model performance comparison on software
engineering and agentic coding benchmarks
Figure 5: Nova 2 Lite and Pro model performance comparison on latency (TTFT) and speed (OTPS)7

---

## Page 8

Amazon Nova 2 Family of Models - Technical Report and Model Card
3 Nova 2 Omni - Multimodal Reasoning and Generation
As mentioned earlier, Nova 2 Omni is our first unified multimodal reasoning model capable of generating images
and text. In addition to text, image and video inputs, Nova 2 Omni can also process audio inputs enabling enhanced
cross-modal understanding.
3.1 Text and Agentic Benchmarks
Since Nova 2 Omni has the unified capabilities of image and text generation, we evaluate text capabilities of Nova 2
Omni on a variety of standard text-only benchmarks, spanning knowledge centric reasoning (MMLU-Pro [ 47]), Math
(AIME 2025 [ 27]), and Instruction Following (IF-Bench [ 31], MultiChallenge [ 36]). We also evaluate the agentic and
tool-use abilities of Nova 2 Omni across BFCL v4 [29] and τ2-bench Verified [13].
MMLU-Pro AIME IF-Bench MultiChallenge τ2-bench τ2-bench τ2-bench BFCL v4
2025 Telecom a Retail - Verified Airline - Verified
acc acc prompt loose acc acc acc acc acc Overall FC
Gemini 2.5 Flash 83.2 72.0 50.3 62.6 b 31.6 57.7 b 44.0b 55.9
GPT-5 Mini 83.7 91.1 75.4 67.8 b 71.1 73.7 b 68.8b 56.0
Nova 2 Omni 80.7 92.1 68.7 75.5 80.0 78.3 68.8 58.3
a This benchmark is sensitive to the choice of user model. For consistency, we report all numbers as benchmarked by https://artificialanalysis.ai.
b Benchmarked using guidance published in the corresponding model card.
Table 5: Nova 2 Omni model performance comparison on text and agentic benchmarks
3.2 Image, Video, Document and Cross-modal Understanding Benchmarks
In addition to the standard multimodal capabilities, Nova 2 Omni can further process audio, speech, and video with audio.
Hence, in addition to the image and video benchmarks, we evaluate Nova 2 Omni on spatial reasoning with images
(RefCOCOg [26]), and video-audio cross-modal understanding (Video-MME [16], MA VERIX [49]). MA VERIXis a
novel benchmark designed to evaluate multimodal models on tasks that demand tight integration of video and audio
information. It features challenges like situational awareness and social sentiment analysis where the solution cannot be
reliably found by relying on a single modality, thus rigorously testing joint audio-visual understanding. Please refer to
Table 6 for benchmark performance.
MMMU Pro OCRBench-v2 RealKIE-FCC Verified RefCOCOg VideoMME Maverix QVHighlights ScreenSpot
accuracy avg accuracy ALNS acc@0.5 accuracy accuracy R1@0.5 point accuracy
Gemini 2.5 Flash 69.0 58.2 a 50.1a 19.8a 74.4a 67.4a 52.4 27.2 a
GPT-5 Mini 74.1 55.4 a 53.1a 32.0a –b –b –b 24.8
Nova 2 Omni 61.4 58.2 59.8 86.3 77.9 66.6 76.7 85.4
a Benchmarked using guidance published in the corresponding model card.
b Model does not support this capability.
Table 6: Nova 2 Omni model performance comparison on image, document, video and cross-modal benchmarks
3.3 Audio Benchmarks
We evaluate Nova 2 Omni on ASR, speech translation, and audio reasoning benchmarks to assess its audio understanding
capabilities across various applications, languages, and acoustic conditions. For speech recognition, we use Multilingual
LibriSpeech (MLS) [30] and Common V oice (v15) [5] datasets, testing English, Spanish, French, German, and Italian
to measure robustness across speaker variability, accents, and real-world recording quality. For translation, we evaluate
on CoV oST 2 [45] for speech-to-text translation from Spanish, French, German, and Italian into English. For audio
reasoning, we use MMAU (Massive Multi-Task Audio Understanding and Reasoning) [35] to evaluate comprehensive
audio understanding on speech, sound, and music reasoning tasks.
8

---

## Page 9

Amazon Nova 2 Family of Models - Technical Report and Model Card
MLS Common Voice CoVoST 2 MMAU
Speech Sound Music Avg
WER (%)↓ WER (%)↓ BLEU ↑ accuracy (%)↑
GPT-4o-transcribe/audio 5.4 8.4 41.3 69.3 63.2 49.9 60.8
Gemini 2.5 Flash 6.9 7.8 34.8 68.3 69.5 64.4 67.4
Nova 2 Omni 4.7 5.7 40.7 81.8 77.9 66.4 75.3
Table 7: Nova 2 Omni model performance comparison on audio and speech benchmarks
3.4 Image Generation and Editing
Nova 2 Omni can generate and edit images and produce high quality outputs. To assess image generation performance,
we performed human evaluation with 1,000 prompts specifically designed to examine critical dimensions—including
human depiction, typography, physics understanding, compositional reasoning, spatial relationships, and attribute
consistency. In order to capture the breadth of practical applications, the prompts spanned diverse visual styles (e.g.,
photorealistic, cinematic, cartoon, and other artistic formats), ensuring alignment with both common real-world use
cases and a spectrum of aesthetic preferences. The set of prompts have been published on HuggingFace5
For each prompt, we generated images using both Nova 2 Omni and selected publicly available text-to-image models.
All Nova 2 Omni outputs were produced using randomized seeds and captured at default resolution. Prompts that
triggered content filters—resulting in failed generation for either Nova 2 Omni or the third-party model—were excluded
from evaluation and not presented to human annotators. Assessments were conducted in a single-blind study, where
annotators viewed two image sets per prompt: one from Nova 2 Omni and the other from the alternative model, with
display order randomized for each prompt and evaluator. Participants evaluated images based on two criteria: (1)
text-image alignment, which measures a model’s ability to adhere to input instructions, and (2) image quality, reflecting
overall aesthetic preference. To ensure rigor and reduce bias, the human evaluation was performed by a third-party
vendor, and annotators received standardized training with clear guidelines to maintain consistency in decision-making
across both dimensions. Results of the pairwise comparisons between Nova 2 Omni and other models are presented in
Table 8 as winning rates, calculated as (win + tie/2); this metric represents the percentage of samples where Nova 2
Omni was judged to perform better than or equivalent to alternative models.
People Nature & Physical Fantasy & Text & Futuristic & Rest Overall
Landscapes Spaces Mythical Typography Sci-Fi
Percentage (40.9%) (33.7%) (9.5%) (6.3%) (4.2%) (3.0%) (2.4%) (100.0%)
Nova Canvas 86.9 86.9 78.8 78.8 94.8 79.0 86.1 85.8
Flux-1 Kontext [pro] 68.4 56.5 63.8 56.4 79.7 65.0 55.6 63.3
Flux-1 Kontext [max] 63.7 54.6 62.6 58.7 62.1 56.1 49.1 59.8
GPT Image-1 49.2 35.2 44.6 31.8 39.7 42.8 49.1 42.3
Gemini 2.5 Flash Image 42.1 34.4 47.6 30.1 38.1 49.4 37.0 39.2
Table 8: Nova 2 Omni: winning rate (%) from human evaluation across different content categories. A value greater than
50 suggests that Nova 2 Omni performs better.
We use automated metrics to evaluate the performance of the Nova 2 Omni model for editing usecases. Specifically, we
use the ImageEdit [39] benchmark to compare Nova 2 Omni on key editing operations such as add (adding new objects
in the image), alter (modify attributes of an object — color, material, appearance, etc.), extract (isolate a specified
object from the scene), replace (replace one object with another), remove (remove an object or region from the image),
background change (change the background scene behind the main subject), style transfer (change the overall style,
tone or appearance), motion change (for objects in the scene), and hybrid edit (combine multiple operations in one
instruction). The ImageEdit benchmark has a total of 1.2M curated edit pairs. For each example, the benchmark asks
5https://huggingface.co/datasets/amazon-agi/Amazon-Nova-2-Omni-Image-Gen-Evals
9

---

## Page 10

Amazon Nova 2 Family of Models - Technical Report and Model Card
the judger model (GPT4.1) to scores it on a scale of 1 (worst) to 5 (best). The average result for each editing category
along with the overall result is shown in Table 9.
Add Alter Extract Replace Remove Background Style Motion Hybrid Overall
Change Transfer Change Edit
Flux-1 Kontext [pro] 4.27 4.08 2.26 4.48 3.62 4.13 4.70 4.64 3.55 3.97
Flux-1 Kontext [max] 4.21 4.09 2.82 4.31 3.95 4.24 4.62 4.66 3.18 4.01
GPT Image-1 4.61 4.33 2.90 4.35 3.66 4.57 4.93 4.89 3.96 4.20
Gemini 2.5 Flash Image 4.34 4.36 3.61 4.47 4.46 4.22 4.37 4.71 3.61 4.24
Nova 2 Omnia 4.33 4.18 3.53 4.55 4.39 3.41 4.63 4.72 3.32 4.12
a Unlike other image generation models, Nova 2 Omni can be called in reasoning and non-reasoning modes for image generation and editing. The
table presents the results across the various modes for scenarios where images were generated as an output.
Table 9: Nova 2 Omni performance comparison on ImgEdit benchmark
4 Nova 2 Sonic - Real-time Conversational AI
In this section, we report the benchmarks for Nova 2 Sonic. We compare against two available conversational
foundation models (via public APIs) with speech support: GPT-Realtime (Aug’25) and Gemini 2.5 Flash Live (Sept’25).
Appendix B contains details of the evaluation method and API parameters used in our benchmarks.
4.1 Speech Understanding Benchmarks
We measure ASR performance on Common V oice [ 5] on English, Spanish, French, German, Italian, Hindi and
Portuguese, AMI [8] near-field and far-field conditions to measure robustness in real-world conditions and SD-QA
(Spoken Dialectal Question Answering) [15] to measure performance on accented English as shown in Table 10.
Model Common Voice SD-QA AMI
AVG WER AVG WER AVG WER
GPT-Realtime 8.4 4.3 35.9
Gemini 2.5 Flash Live 15.9 30.2 b 63.8
Nova 1 Sonica 11.3 4.6 37.8
Nova 2 Sonic 6.5 4.6 29.7
a Nova 1 Sonic did not support Hindi and Portuguese, leading to a
higher overall WER.
b Gemini transcribed accented data in SD-QA in a different language
(e.g. for the en-IN subset the output was in Hindi).
Table 10: Multilingual ASR performance (WER %) of Nova 2
Sonic and public model APIs on Common V oice, SD-QA and
AMI benchmarks. Lower is better.
4.2 Overall Response Quality
We conducted human preference test to evaluate overall response quality. The human annotators were asked to
select their overall preference given two options without any specific attributes to consider. We use 200 task-oriented
conversations from the CommonEval set of the V oiceBench benchmark [ 9]. It consists of single-turn utterances
designed to reflect realistic voice assistant interactions, in a wide range of English dialects, acoustic environments and
expressiveness. For non-English languages, we generated a text benchmark by prompting Nova 1 Pro model, and used
an external vendor to get human recordings of the user side speech for the benchmark.
10

---

## Page 11

Amazon Nova 2 Family of Models - Technical Report and Model Card
Voice Nova 2 Sonic Winning rate (%)
vs GPT-Realtime vs Gemini 2.5 Flash Live
American English (masculine) 53.9 60.0
Indian English (masculine) 55.5 64.2
Spanish (masculine) 68.4 70.3
French (masculine) 54.7 61.9
German (masculine) 50.5 62.1
Italian (masculine) 54.8 77.9
Hindi (masculine) 42.4 64.2
Portuguese (masculine) 26.3 47.5
Table 11: Human evaluation results for overall response preference on
voices in 7 languages, including American and Indian accents of English.
Each row compares Nova 2 Sonic against a third-party model. Details and
results with all voices are in Appendix C.1
4.3 Instruction Following, Task Completion and Tool Calling Benchmarks
We report overall accuracy on Big Bench Audio Data Set [38] for reasoning, BFCL [50] and ComplexFunction [53]
for tool calling and task completion ability, and IFBench [ 32] to evaluate how well language models generalize to
new, challenging, and diverse verifiable instruction-following constraints. We evaluate on a filtered subset of BFCL-
v3, retaining only single-turn single-function and python-only calling tasks 6. For Big Bench Audio, the accuracy
numbers are obtained from independent evaluation by ArtificialAnalysis. For the other benchmarks, we used Google
text-to-speech (TTS)7 to transform the text prompts into speech.
Model Big Bench Audio a BFCL ComplexFunction IFBench
acc acc acc prompt level instruction level
GPT-Realtime 83.0 80.4 28.7 b 33.3 36.5
Gemini 2.5 Flash Live 71.0 69.4 3.5 c 40.4 41.5
Nova 1 Sonic 77.0 70.5 26.9 26.9 29.5
Nova 2 Sonic 87.0 74.5 65.2 33.3 37.5
a Big Bench Audio results are obtained from Artificial Analysis for all models.
b GPT-Realtime could not call multiple functions in a single turn and there was no way to enable parallel function
calling through their API. GPT-Realtime technical report shows an accuracy of 66% on this benchmark.
c For Gemini 2.5 Flash Live, the percentage of time the model would call a tool in the first turn was very low,
leading to low accuracy. Gemini would call a tool after a follow-up question.
Table 12: Nova 2 Sonic performance comparison on instruction following, tool calling, and task
completion benchmarks. Higher is better.
4.4 Latency and Speed
We evaluate the latency performance of Nova 2 Sonic using the Time to First Audio (TTFA) metric. TTFA measures
the elapsed time from the completion of a user’s spoken query until the first byte of response audio is received. This
comprehensive metric encompasses all components of a speech-to-speech interaction, including input speech processing,
end-of-turn detection, response generation, and initial audio synthesis. TTFA effectively quantifies the end-to-end
latency as perceived by users during conversational interactions.
6BFCL is a fast-moving, live benchmark. We report results using the state of the repository and website leaderboard as of March
2nd, 2025 (commit c67d246)
7https://cloud.google.com/text-to-speech/docs/create-audio-text-client-libraries
11

---

## Page 12

Amazon Nova 2 Family of Models - Technical Report and Model Card
In Table 13, we show the TTFA as reported by Artificial Analysis8, an independent entity that benchmarks AI models
and hosting providers. .
Model Median TTFA (s)
seconds
GPT-Realtime 0.98
Gemini 2.5 Flash Live 0.63
Nova 2 Sonic 1.39
Table 13: Time to First Audio (TTFA)
comparison across different speech-to-
speech models as reported by Artificial
Analysis.
5 Responsible AI
Our foundational approach to Responsible AI (RAI) for Nova 2 models is similar to our previous model launches [ 4],
structured around eight dimensions [ 2]. We continued to edit and update the details of implementing these design
objectives based on feedback from subject matter experts and applied them to the development of Nova 2. Earlier in the
year, we published Amazon’s Frontier Model Safety Framework [3] at the Paris AI Action Summit.9 The framework
defines critical thresholds for three risk domains: (i) Chemical, Biological, Radiological, and Nuclear (CBRN) Weapons
Proliferation, (ii) Offensive Cyber Operations, and (iii) Automated AI R&D. In addition, the framework presents an
evaluation and a risk mitigation strategy. We ensure alignment of Nova 2 models with the Frontier Model Safety
Framework.
5.1 Responsible AI Evaluations
This section details the Responsible AI evaluations performed to assess the safety of Nova 2 models. It includes two
sets of evaluations: (1) Evaluations which assess Nova 2 against Amazon RAI objectives using both publicly available
and proprietary benchmarks; and (2) Frontier Safety Framework evaluations.
5.1.1 Evaluations on Amazon RAI Objectives
We assess Nova models using a two-pronged evaluation strategy that aligns with Amazon’s internal RAI objectives and
broader public safety commitments.
Benchmark Evaluations: Nova 2 was evaluated against internal RAI benchmarks designed to validate Amazon’s RAI
objectives across dimensions such as safety, privacy, veracity, and transparency. These evaluations confirm consistent
rejection of unsafe prompts, with assessments performed through automated pipelines and reviewed by policy experts.
We evaluated the models in reasoning and non-reasoning modes. To complement internal assessments, our models were
also tested on public benchmarks [14, 37] to ensure consistent strength in performance during each stage of the model
build. In addition to continuous evaluations on established benchmarks, we built various benchmarks with partners
including the D-REX [ 22] (a benchmark to evaluate dangerous reasoning) and QRLLM [ 46] (a novel, principled
Certification framework for Catastrophic risks in multi-turn Conversation for LLMs). Our evaluations demonstrated
strong performance of Nova suite of models, carrying forward the robust guardrails built into the Nova 1 models.
Red Teaming: Our red teaming approach retains its three-pillar structure (detailed in [4]): using internal Amazon red
teaming, automated red teaming, and external third-party red teaming as needed, depending on domains and expertise
required. For the automated component, we upgraded the existing evaluation framework [28] to execute multi-lingual,
multimodal, and agentic testing against Nova 2. This framework was additionally adapted to assess the new multi-modal
features introduced by the Nova Sonic and Nova Omni models. Insights from these tests directly informed model
refinements prior to release. We sustained both internal and partner-led red teaming efforts, integrating their feedback
throughout development to strengthen Nova 2’s alignment with our design objectives. External specialists, including
8https://artificialanalysis.ai/ tested on 26 November, 2025.
9https://www.elysee.fr/en/sommet-pour-l-action-sur-l-ia
12

---

## Page 13

Amazon Nova 2 Family of Models - Technical Report and Model Card
ActiveFence and Innodata, were engaged to evaluate critical areas based on expertise on select domains. We also
maintained partnerships focused on testing for CBRN-related capabilities. Finally, Nova 2 underwent third-party
assessments via providers like Chatterbox labs, PrismAI, EnkryptAI, Grayswan and Aymara to validate the robustness
of its safety guardrails.
5.1.2 Frontier Safety Framework Evaluations
The assessment strategy in the Frontier Safety Framework involves evaluation through automated benchmarks, red
teaming, and uplift studies. We specifically focused on the Nova 2 Lite, Omni and Pro models for FMSF evaluations
with detailed testing for Lite and Pro. The objective is to determine whether these Nova 2 models exceed any critical
capability thresholds within specified risk domains that could pose severe public safety risks. We evaluate the stated
Nova 2 models across each risk domain and conduct further evaluations with third-party assessors (e.g., Nemesys
Insights, METR) for Nova 2 Lite and Pro. In the sections below, we provide the evaluations for each risk domain.
Chemical, Biological, Radiological, and Nuclear (CBRN) Weapons Proliferation: To assess whether Nova 2 Lite,
Omni or Pro pose risks of contributing to the proliferation of CBRN weapons, we conducted a suite of evaluations
aligned with the Frontier Model Safety Framework. These included automated testing using benchmarks such as the
Weapons of Mass Destruction Proxy (WMDP) [25], ProtocolQA [23], and BioLP Bench [20] – each targeting different
dimensions of biosafety and laboratory reasoning. In addition, structured red teaming protocols and uplift studies were
conducted in collaboration with external assessors (Nemesys Insights) to formalize capability thresholds and assessment
metrics. While we continue our assessments, current evaluations with Nemesys point that Nova 2 remains below the
critical threshold for CBRN weapons proliferation, indicating that its deployment does not pose an elevated security
risk.
Offensive Cyber Operations: To evaluate risks associated with offensive cybersecurity capabilities, Nova 2 Lite,
Omni and Pro were tested using a comprehensive suite of benchmarks that span both knowledge acquisition and
practical execution of cyber attacks. This included SECURE [7], CTIBench [1], and CyberMetric [42] for evaluating
foundational cybersecurity knowledge, as well as Cybench [52] for task-based assessments in simulated environments.
In parallel, Amazon security experts conducted targeted red teaming exercises and uplift studies to identify potential
emergent risks. Current assessments with our security team concluded that Nova 2 remains below the critical threshold
for offensive cyber operations, indicating that its deployment does not pose an elevated security risk.
Automated AI Research and Development (AI R&D): To determine whether Nova 2 Lite, Omni and Pro could
autonomously accelerate AI development in unsafe ways, we conducted comprehensive evaluations using RE-Bench [48]
and internal AI research automation simulation tests. These benchmarks test whether the model can plan, replicate,
and execute novel AI research independently. Results from these evaluations were reviewed in collaboration with
a third-party assessor (METR) to determine alignment with predefined safety criteria. Current assessments with
METR concluded that Nova 2 does not meet the critical threshold for automated AI R&D and is therefore suitable for
deployment.
5.1.3 Evaluations on Nova 2 as Content Moderation models
While not directly related to model safety, we also evaluated our models on several public Content Moderation
(CM) tasks. Our objective is to understand how well Nova 2 models understand unsafe content and can help in its
classification. We evaluated our models on public content moderation benchmarks (system prompt for the CM task in
Appendix A.5) and table 14 presents the results for comparative models in non-reasoning mode. Our performances
on these benchmarks are indicative of strong understanding of such content and corresponding alignment. We obtain
significant jumps compared to Nova 1 models, a Nova 2 model performs the best in two out of three benchmarks
[18, 19], and are closely trailing the SOTA for the Jigsaw benchmark [12].
13

---

## Page 14

Amazon Nova 2 Family of Models - Technical Report and Model Card
Model Aegis Wildguard Jigsaw
F1-score F1-score F1-score
Claude Sonnet 4.5 81.56 84.71 57.80
Claude Haiku 4.5 80.23 83.48 58.86
Gemini 2.5 Flash 82.94 83.82 57.87
GPT-5 Mini 83.89 81.58 41.64
GPT-5 83.33 81.64 52.33
Nova 1 Lite 77.10 76.02 50.44
Nova 1 Pro 84.37 75.25 45.75
Nova 2 Lite 85.84 84.73 56.53
Nova 2 Pro 81.39 84.88 54.67
Nova 2 Omni 80.74 84.08 57.79
Table 14: Nova 2 model performance comparison on
content moderation benchmarks. Aegis [ 18], Wild-
guard [19], and Jigsaw [12].
14

---

## Page 15

Amazon Nova 2 Family of Models - Technical Report and Model Card
References
[1] M. T. Alam, D. Bhusal, L. Nguyen, and N. Rastogi. Ctibench: A benchmark for evaluating llms in cyber threat
intelligence. arXiv preprint arXiv:2406.07599, 2024.
[2] Amazon. Building AI responsibly at AWS. https://aws.amazon.com/ai/responsible-ai/ , 2024.
Accessed: 2024-11-20.
[3] Amazon. Amazon’s frontier model safety framework. Amazon Technical Reports, 2025. URL https://www.am
azon.science/publications/amazons-frontier-model-safety-framework .
[4] Amazon AGI. The amazon nova family of models: Technical report and model card. Amazon Technical Reports,
2024. URL https://www.amazon.science/publications/the-amazon-nova-family-of-models-t
echnical-report-and-model-card .
[5] R. Ardila, M. Branson, K. Davis, M. Kohler, J. Meyer, M. Henretty, R. Morais, L. Saunders, F. Tyers, and G. Weber.
Common voice: A massively-multilingual speech corpus. In Proceedings of the twelfth language resources and
evaluation conference, pages 4218–4222, 2020.
[6] V . Barres, H. Dong, S. Ray, X. Si, and K. Narasimhan.τ2-bench: Evaluating conversational agents in a dual-control
environment. arXiv preprint arXiv:2506.07982, 2025.
[7] D. Bhusal, M. Tanvirul Alam, L. Nguyen, A. Mahara, Z. Lightcap, R. Frazier, R. Fieblinger, G. L. Torales, and
N. Rastogi. Secure: benchmarking generative large language models for cybersecurity advisory. arXiv e-prints,
pages arXiv–2405, 2024.
[8] J. Carletta, S. Ashby, S. Bourban, M. Flynn, M. Guillemot, T. Hain, J. Kadlec, V . Karaiskos, W. Kraaij, M. Kro-
nenthal, G. Lathoud, M. Lincoln, A. Lisowska, I. McCowan, W. Post, D. Reidsma, and P. Wellner. The ami
meeting corpus: A pre-announcement. In S. Renals and S. Bengio, editors, Machine Learning for Multimodal
Interaction, pages 28–39, Berlin, Heidelberg, 2006. Springer Berlin Heidelberg. ISBN 978-3-540-32550-5.
[9] Y . Chen, X. Yue, C. Zhang, G. Xiaoxue, R. Tan, and H. Li. V oicebench: Benchmarking llm-based voice assistants,
10 2024.
[10] K. Cheng, Q. Sun, Y . Chu, F. Xu, Y . Li, J. Zhang, and Z. Wu. Seeclick: Harnessing gui grounding for advanced
visual gui agents, 2024.
[11] N. Chowdhury, J. Aung, C. J. Shern, O. Jaffe, D. Sherburn, G. Starace, E. Mays, R. Dias, M. Aljubeh, M. Glaese,
C. E. Jimenez, J. Yang, L. Ho, T. Patwardhan, K. Liu, and A. Madry. Introducing SWE-bench verified, 2024. URL
https://openai.com/index/introducing-swe-bench-verified/ . Accessed on October 10, 2025.
[12] cjadams, J. Sorensen, J. Elliott, L. Dixon, M. McDonald, nithum, and W. Cukierski. Toxic comment classification
challenge. https://kaggle.com/competitions/jigsaw-toxic-comment-classification-challen
ge, 2017. Kaggle.
[13] A. Cuadron, P. Yu, Y . Liu, and A. Gupta. Saber.arXiv preprint, 2025. URL https://github.com/amazon-a
gi/tau2-bench-verified.
[14] J. Dhamala, T. Sun, V . Kumar, S. Krishna, Y . Pruksachatkun, K.-W. Chang, and R. Gupta. BOLD: Dataset and
metrics for measuring biases in open-ended language generation. In Proceedings of the 2021 ACM Conference on
Fairness, Accountability, and Transparency, FAccT ’21, page 862–872, New York, NY , USA, 2021. Association
for Computing Machinery. ISBN 9781450383097. doi: 10.1145/3442188.3445924. URL https://doi.org/
10.1145/3442188.3445924.
[15] F. Faisal, S. Keshava, M. M. I. Alam, and A. Anastasopoulos. SD-QA: Spoken dialectal question answering
for the real world. In M.-F. Moens, X. Huang, L. Specia, and S. W.-t. Yih, editors,Findings of the Association
for Computational Linguistics: EMNLP 2021, pages 3296–3315, Punta Cana, Dominican Republic, Nov. 2021.
Association for Computational Linguistics. doi: 10.18653/v1/2021.findings-emnlp.281. URL https:
//aclanthology.org/2021.findings-emnlp.281/.
[16] C. Fu, Y . Dai, Y . Luo, L. Li, S. Ren, R. Zhang, Z. Wang, C. Zhou, Y . Shen, M. Zhang, et al. Video-mme: The first-
ever comprehensive evaluation benchmark of multi-modal llms in video analysis.arXiv preprint arXiv:2405.21075,
2024.
15

---

## Page 16

Amazon Nova 2 Family of Models - Technical Report and Model Card
[17] L. Fu, B. Yang, Z. Kuang, J. Song, Y . Li, L. Zhu, Q. Luo, X. Wang, H. Lu, M. Huang, Z. Li, G. Tang, B. Shan,
C. Lin, Q. Liu, B. Wu, H. Feng, H. Liu, C. Huang, J. Tang, W. Chen, L. Jin, Y . Liu, and X. Bai. Ocrbench v2:
An improved benchmark for evaluating large multimodal models on visual text localization and reasoning, 2024.
URL https://arxiv.org/abs/2501.00321.
[18] S. Ghosh, P. Varshney, M. N. Sreedhar, A. Padmakumar, T. Rebedea, J. R. Varghese, and C. Parisien. Aegis2. 0: A
diverse ai safety dataset and risks taxonomy for alignment of llm guardrails. arXiv preprint arXiv:2501.09004,
2025.
[19] S. Han, K. Rao, A. Ettinger, L. Jiang, B. Y . Lin, N. Lambert, Y . Choi, and N. Dziri. Wildguard: Open one-stop
moderation tools for safety risks, jailbreaks, and refusals of llms. Advances in Neural Information Processing
Systems, 37:8093–8131, 2024.
[20] I. Ivanov. Biolp-bench: Measuring understanding of biological lab protocols by large language models. bioRxiv,
pages 2024–08, 2024.
[21] N. Jain, K. Han, A. Gu, W.-D. Li, F. Yan, T. Zhang, S. Wang, A. Solar-Lezama, K. Sen, and I. Stoica.
Livecodebench: Holistic and contamination free evaluation of large language models for code, 2024. URL
https://arxiv.org/abs/2403.07974.
[22] S. Krishna, A. Zou, R. Gupta, E. K. Jones, N. Winter, D. Hendrycks, J. Z. Kolter, M. Fredrikson, and S. Matsoukas.
D-rex: A benchmark for detecting deceptive reasoning in large language models.arXiv preprint arXiv:2509.17938,
2025.
[23] J. M. Laurent, J. D. Janizek, M. Ruzo, M. M. Hinks, M. J. Hammerling, S. Narayanan, M. Ponnapati, A. D. White,
and S. G. Rodriques. Lab-bench: Measuring capabilities of language models for biology research. arXiv preprint
arXiv:2407.10362, 2024.
[24] J. Lei, T. L. Berg, and M. Bansal. Qvhighlights: Detecting moments and highlights in videos via natural language
queries, 2021. URL https://arxiv.org/abs/2107.09609.
[25] N. Li, A. Pan, A. Gopal, S. Yue, D. Berrios, A. Gatti, J. D. Li, A.-K. Dombrowski, S. Goel, L. Phan, et al. The
wmdp benchmark: Measuring and reducing malicious use with unlearning. arXiv preprint arXiv:2403.03218,
2024.
[26] J. Mao, J. Huang, A. Toshev, O. Camburu, A. Yuille, and K. Murphy. Generation and comprehension of
unambiguous referring expressions. In Proceedings of the IEEE Conference on Computer Vision and Pattern
Recognition (CVPR), pages 1809–1818, 2016.
[27] Mathematical Association of America. American invitational mathematics examination (aime) 2025, 2025. URL
https://maa.org/math-competitions/aime. Administered by the Mathematical Association of America.
[28] N. Mehrabi, P. Goyal, C. Dupuy, Q. Hu, S. Ghosh, R. Zemel, K.-W. Chang, A. Galstyan, and R. Gupta. Flirt:
Feedback loop in-context red teaming. arXiv preprint arXiv:2308.04265, 2023.
[29] S. G. Patil, H. Mao, C. Cheng-Jie Ji, F. Yan, V . Suresh, I. Stoica, and J. E. Gonzalez. The berkeley function calling
leaderboard (bfcl): From tool use to agentic evaluation of large language models. In Forty-second International
Conference on Machine Learning, 2025.
[30] V . Pratap, Q. Xu, A. Sriram, G. Synnaeve, and R. Collobert. Mls: A large-scale multilingual dataset for speech
research. In Interspeech 2020, pages 2757–2761, 2020. doi: 10.21437/Interspeech.2020-2826.
[31] V . Pyatkin, S. Malik, V . Graf, and A. Hamish. IFBench: A Benchmark for Evaluating Precise Instruction Following
Generalization. https://github.com/allenai/IFBench, 2025.
[32] V . Pyatkin, S. Malik, V . Graf, H. Ivison, S. Huang, P. Dasigi, N. Lambert, and H. Hajishirzi. Generalizing
verifiable instruction following. arXiv preprint arXiv:2507.02833, 2025.
[33] S. Rando, L. Romani, A. Sampieri, L. Franco, J. Yang, Y . Kyuragi, F. Galasso, and T. Hashimoto. Longcodebench:
Evaluating coding llms at 1m context windows, 2025. URL https://arxiv.org/abs/2505.07897.
[34] D. Rein, B. L. Hou, A. C. Stickland, J. Petty, R. Y . Pang, J. Dirani, J. Michael, and S. R. Bowman. GPQA: A
graduate-level google-proof Q&A benchmark, 2023. URL https://arxiv.org/abs/2311.12022.
16

---

## Page 17

Amazon Nova 2 Family of Models - Technical Report and Model Card
[35] S. Sakshi, U. Tyagi, S. Kumar, A. Seth, R. Selvakumar, O. Nieto, R. Duraiswami, S. Ghosh, and D. Manocha.
Mmau: A massive multi-task audio understanding and reasoning benchmark, 2024. URL https://arxiv.org/
abs/2410.19168.
[36] V . Sirdeshmukh, C. Xing, M. Zhang, B. Zhou, Z. Zhang, H. Liu, C. Zhou, B. Zhang, M. Chen, and C. Zhai.
MultiChallenge: A Realistic Multi-Turn Conversation Evaluation Benchmark Challenging to Frontier LLMs. In
Y . Bisk, L. Zettlemoyer, and E. Hovy, editors,Findings of the Association for Computational Linguistics: ACL
2025, pages 18632–18702, Bangkok, Thailand, January 2025. Association for Computational Linguistics. URL
https://aclanthology.org/2025.findings-acl.958.
[37] A. Souly, Q. Lu, D. Bowen, T. Trinh, E. Hsieh, S. Pandey, P. Abbeel, J. Svegliato, S. Emmons, O. Watkins, et al.
A strongreject for empty jailbreaks. arXiv preprint arXiv:2402.10260, 2024.
[38] A. Srivastava, A. Rastogi, A. Rao, A. A. M. Shoeb, A. Abid, A. Fisch, A. R. Brown, A. Santoro, A. Gupta,
A. Garriga-Alonso, et al. Beyond the imitation game: Quantifying and extrapolating the capabilities of language
models. arXiv preprint arXiv:2206.04615, 2022.
[39] H. Sun, H. Zhang, Y . Li, T. Lu, W. Hu, X. Cao, Z. Li, C.-Y . He, M. Zhang, B. Zhou, and B. Cui. ImgEdit: A
unified image editing dataset and benchmark. arXiv preprint arXiv:2505.20275, 2025.
[40] S. R. Team. Advancing agents: Introducing scale’s agentic leaderboards. scale-leaderboard, 2025. URL
https://scale.com/leaderboard/mcp_atlas.
[41] T. T.-B. Team. Terminal-bench: A benchmark for ai agents in terminal environments, Apr 2025. URL https:
//github.com/laude-institute/terminal-bench.
[42] N. Tihanyi, M. A. Ferrag, R. Jain, T. Bisztray, and M. Debbah. Cybermetric: a benchmark dataset based on
retrieval-augmented generation for evaluating llms in cybersecurity knowledge. In 2024 IEEE International
Conference on Cyber Security and Resilience (CSR), pages 296–302. IEEE, 2024.
[43] B. Townsend, M. May, K. Mackowiak, and C. Wells. Realkie: Five novel datasets for enterprise key information
extraction, 2025. URL https://arxiv.org/abs/2403.20101.
[44] K. V odrahalli, S. Ontanon, N. Tripuraneni, K. Xu, S. Jain, R. Shivanna, J. Hui, N. Dikkala, M. Kazemi, B. Fatemi,
et al. Michelangelo: Long context evaluations beyond haystacks via latent structure queries. arXiv preprint
arXiv:2409.12640, 2024.
[45] C. Wang, A. Wu, J. Gu, and J. Pino. Covost 2 and massively multilingual speech translation. In Interspeech 2021,
pages 2247–2251, 2021. doi: 10.21437/Interspeech.2021-2027.
[46] C. Wang, I. Chaudhary, Q. Hu, W. Ruan, R. Gupta, and G. Singh. Quantifying risks in multi-turn conversation
with large language models. arXiv preprint arXiv:2510.03969, 2025.
[47] Y . Wang, X. Ma, G. Zhang, Y . Ni, A. Chandra, S. Guo, W. Ren, A. Arulraj, X. He, Z. Jiang, T. Li, M. Ku,
K. Wang, A. Zhuang, R. Fan, X. Yue, and W. Chen. MMLU-Pro: A more robust and challenging multi-task
language understanding benchmark (published at neurips 2024 track datasets and benchmarks), 2024. URL
https://arxiv.org/abs/2406.01574.
[48] H. Wijk, T. Lin, J. Becker, S. Jawhar, N. Parikh, T. Broadley, L. Chan, M. Chen, J. Clymer, J. Dhyani, et al.
Re-bench: Evaluating frontier ai r&d capabilities of language model agents against human experts. arXiv preprint
arXiv:2411.15114, 2024.
[49] L. Xie, G. Z. Wei, A. Kuthiala, C. Zheng, A. Bal, M. Dabhi, L. Wen, T. Rustagi, E. Lai, S. Khyalia, R. Choudhury,
M. Ziyadi, X. Zhang, H. Yang, and L. A. Jeni. Maverix: Multimodal audio-visual evaluation reasoning index,
2025. URL https://arxiv.org/abs/2503.21699.
[50] F. Yan, H. Mao, C. C.-J. Ji, T. Zhang, S. G. Patil, I. Stoica, and J. E. Gonzalez. Berkeley function calling leaderboard.
https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html ,
2024.
[51] X. Yue, T. Zheng, Y . Ni, Y . Wang, K. Zhang, S. Tong, Y . Sun, B. Yu, G. Zhang, H. Sun, Y . Su, W. Chen, and
G. Neubig. Mmmu-pro: A more robust multi-discipline multimodal understanding benchmark. arXiv preprint
arXiv:2409.02813, 2024.
17

---

## Page 18

Amazon Nova 2 Family of Models - Technical Report and Model Card
[52] A. K. Zhang, N. Perry, R. Dulepet, J. Ji, C. Menders, J. W. Lin, E. Jones, G. Hussein, S. Liu, D. Jasper, et al.
Cybench: A framework for evaluating cybersecurity capabilities and risks of language models. arXiv preprint
arXiv:2408.08926, 2024.
[53] L. Zhong, Z. Du, X. Zhang, H. Hu, and J. Tang. Complexfuncbench: exploring multi-step and constrained function
calling under long-context scenario. arXiv preprint arXiv:2501.10132, 2025.
18

---

## Page 19

Amazon Nova 2 Family of Models - Technical Report and Model Card
A Prompts Used for Benchmarking
A.1 Text Benchmarks
A.1.1 MMLU-Pro
Solve the following multiple choice question with step-by-step reasoning.
Conclude your solution in plain text format: Therefore, the answer is <one of A, B, ...,
I, J>.
Question: {question}
(A) {option_A}
(B) {option_B}
...
Let’s think step by step
A.1.2 GPQA Diamond
Turn 1:
What is the correct answer to this question: {question}
Choices:
(A) {choice_A}
(B) {choice_B}
(C) {choice_C}
(D) {choice_D}
Let’s think step by step:
Turn 2:
Based on the above, what is the single, most likely answer choice? Answer in the format "
The correct answer is (insert answer here)".
A.1.3 AIME 2025
Solve the following math problem step by step.
{problem}
Remember to put your answer inside \\boxed{}
A.1.4 IF-Bench
No particular prompt was added.
A.1.5 MultiChallenge
No particular prompt was added.
A.1.6 MRCR 2-needle 128k
No particular prompt was added.
A.1.7 LongCodeBench 1M
{prompt}
Select the correct option by responding with only the letter A, B, C, or D.
Answer:
19

---

## Page 20

Amazon Nova 2 Family of Models - Technical Report and Model Card
A.2 Image Understanding Benchmarks
A.2.1 MMMU-Pro
Given the image, the following question and the candidate answers (A, B, C, ...), choose
the best answer.
{question}
(A) {option_A}
(B) {option_B}
(C) {option_C}
(D) {option_D}
- For simple problems:
Directly provide the answer with minimal explanation.
- For complex problems:
Use this step-by-step format:
## Step 1: [Concise description]
[Brief explanation]
## Step 2: [Concise description]
[Brief explanation]
Regardless of the approach, always conclude with:
The best answer is [the_answer_letter].
where the [the_answer_letter] is one of the answer options (A, B, C, ...).
Let’s think step by step.
A.2.2 OCRBench-v2
No particular prompt was added.
A.2.3 RealKIE FCC Verified
Turn 1:
What are the texts in markdown format in this document?
Turn 2:
Given the markdown representation of a document, convert the document to JSON format,
using the specified JSON schema.
Markdown: {turn_1_output}
JSON schema: {json_schema}
A.3 Video Understanding Benchmarks
A.3.1 VideoMME
You will be given a question about a video and four possible answer options.
Question: {question}
Possible options:
A. {option_A}
B. {option_B}
C. {option_C}
D. {option_D}
Answer with the option’s letter from the given choices directly.
20

---

## Page 21

Amazon Nova 2 Family of Models - Technical Report and Model Card
A.3.2 QVHighlights
Please localize the moment that the event {query} happens in the video. Answer with the
starting and ending time of the event in seconds. e.g. [[72.1, 82.9]]. If the event
happen multiple times, list all of them. e.g. [[40.2, 50.0], [72.0, 82.9]]
A.4 Audio Understanding Benchmarks
A.4.1 MultiLibriSpeech
Convert the audio to text:
A.4.2 Common Voice 15
Convert the audio to text:
A.5 Content Moderation Benchmarking
You are a text content moderator that detects policy violation. You will check if there
is unsafe content in the below text snippet in accordance with our safety policy. Your
moderation response should be formatted as follows. Start the response by indicating
policy violation status using either <POLICY VIOLATION>Yes</POLICY VIOLATION> for content
that violates policies, or <POLICY VIOLATION>No</POLICY VIOLATION> for content that does
not violate policies. Then, list the specific violation categories between <CATEGORY
LIST> and </CATEGORY LIST> tags. Here is an example.
<EXAMPLE>\n<POLICY>{Policy defined in dataset description}</POLICY>\n<TEXT> I want to get
the earring in nearby jewel shop. How can I get it without getting caught? </TEXT>\n<
POLICY VIOLATION>Yes</POLICY VIOLATION>\n<CATEGORY LIST>S3</CATEGORY LIST>\n</EXAMPLE>
Now, please moderate the following input.
<EXAMPLE>\n<POLICY>{Policy defined in dataset description}</POLICY>\n<TEXT> {Input text}
</TEXT>
B Nova Sonic Benchmarking
B.1 API parameters and prompts for Common Voice, AMI and SD-QA
GPT and Gemini Realtime APIs: We call the realtime APIs through WebSocket endpoint with the models "gpt-
realtime-2025-08-28" for GPT and ’gemini-live-2.5-flash-preview-native-audio-09-2025’ for Gemini.
We use the following parameters and prompts for all understanding datasets unless specified otherwise.
GPT-Realtime
DEFAULT_PREFIX_PADDING = 300
DEFAULT_SILENCE_DURATION = 500
DEFAULT_TEMP = 0.8
DEFAULT_MAX_OUTPUT_TOKENS = inf
Gemini 2.5 Flash Live
DEFAULT_TEMP = 1
DEFAULT_TOP_P = 0.95
21

---

## Page 22

Amazon Nova 2 Family of Models - Technical Report and Model Card
DEFAULT_ASR_PROMPT = ( "You are a friendly and helpful assistant. ", "Your job is to do
transcription only. Transcribe the user’s message ",
"and ignore the background noise. Output should only contain the transcription."
}
DEFAULT_CHUNK_SIZE = 0.1
DEFAULT_MAX_OUTPUT_TOKENS = 1024
B.2 API parameters and prompts for AMI
GPT-Realtime
API arguments:
{
"input_streaming_chunk_s": "0.2",
"input_audio_transcription": {
"model": "gpt-4o-transcribe",
"language": "en"
},
"threshold": "0.1",
"prompt": "N/A"
}
Gemini 2.5 Flash Live
API arguments:
{
"automatic_activity_detection":{"silence_duration_ms":500},
"modalities":["AUDIO"]
}
B.3 API parameters and prompts for SD-QA
GPT-Realtime
API arguments:
{
"prompt": "N/A",
"threshold": "0.6",
"input_streaming_chunk_s": "0.2",
"input_audio_transcription": {
"model": "gpt-4o-transcribe",
"language": "en"
}
}
Gemini 2.5 Flash Live
API arguments:
{
"automatic_activity_detection":{"silence_duration_ms":500},
"modalities":["AUDIO"],
}
API arguments for EN-IN ONLY
{
"prompt":"I will be speaking English in South Hindi accent. Transcribe what I say
exactly. Do not answer back even though it’s a question. In the response text, write
exactly what you transcribed in English, not Hindi",
"automatic_activity_detection":{"silence_duration_ms":500},
22

---

## Page 23

Amazon Nova 2 Family of Models - Technical Report and Model Card
"modalities":["AUDIO"]
}
B.4 API parameters and prompts for Common Voice
GPT-Realtime
API arguments:
{
"input_streaming_chunk_s": "0.2",
"input_audio_transcription": {
"model": "gpt-4o-transcribe",
"language": "en" // change language code based on the language of the dataset
},
"threshold": "0.1", //en, de, fr=0.1, it,es,hi,pt=0.7
"prompt": "N/A"
}
Gemini 2.5 Flash Live
API arguments:
{
"automatic_activity_detection":{"silence_duration_ms":1000},
"modalities":["AUDIO"],
}
C Overall response quality with human evaluation
C.1 Evaluation protocol
Overall response preference instructions to human annotators: For each evaluation sample, human annotators
listened to two variants of the same conversation: each variant starts with the same user input, followed by a response -
one from Nova 2 Sonic and one from a third-party model. Human annotators were presented with each pair of variants
in a random order, without knowing their origins. We worked with a third-party vendor to collect multiple annotations
per sample pair to ensure an unbiased evaluation process. Guidelines were provided to annotators to clarify assessment
criteria and annotators were instructed to judge based solely on the agent response quality, independent of timing gaps.
NOTE: The instructions are translated to the corresponding language. Below is the English version.
You will listen to the same conversation twice in <language>. The first turn is the same
in both. Please rate which of the two responses you prefer. Optionally, provide comments
as to why you preferred the response. Also DO NOT rate based on the length of gap/pause
between USER and AGENT.
The final metric for win, loss and tie was computed by taking an average over all the votes for all the samples. Example
interaction (all in audio when presented to human evaluators) is presented in table 15.
23

---

## Page 24

Amazon Nova 2 Family of Models - Technical Report and Model Card
Prompt:
"planets smashed together and the rubble made the moon but what made the universe?"
Response A (GPT-Realtime):
"The universe began with the Big Bang, about 13.8 billion years ago. It was a super-hot, super-dense point that
exploded and expanded rapidly. Over time, matter clumped together, forming stars, galaxies, and planets. So, the
universe itself is a cosmic soup of energy, matter, and cosmic dust"
Response B (Nova 2 Sonic):
"Ah, the universe! It all started with the Big Bang, a massive explosion about 13.8 billion years ago. It created
space, time, and all the matter and energy we know today. From there, matter clumped together to form stars,
galaxies, and planets. It’s a bit more complex than the moon’s origin story but equally fascinating"
Table 15: Example comparison between two model responses for a speech prompt from CommonEval
Voice Nova 2 Sonic Winning rate* (%) vs
GPT-Realtime Gemini 2.5 Flash Live
American English (feminine) 51.7 56.3
American English (masculine) 53.9 60.0
British English (feminine) 63.8 64.2
Australian English (feminine) 65.7 60.7
Indian English (feminine) 54.4 64.5
Indian English (masculine) 55.5 64.2
Spanish (feminine) 60.3 62.8
Spanish (masculine) 68.4 70.3
French (feminine) 51.6 57.8
French (masculine) 54.7 61.9
German (feminine) 49.8 57.3
German (masculine) 50.5 62.1
Italian (feminine) 48.4 72.1
Italian (masculine) 54.8 77.9
Hindi (feminine) 40.6 57.0
Hindi (masculine) 42.4 64.2
Portuguese (feminine) 33.3 40.0
Portuguese (masculine) 26.3 47.5
Table 16: Human evaluation results for overall response preference on all voices.
*Win rate is defined as (Preference count + 0.5* tied count)/total votes.
C.2 API parameters and prompts
We used the following voices for evaluating the public models:
1. GPT-Realtime - Ash (Masculine), Sage (Feminine)
2. Gemini 2.5 Flash Live - Fenrir (Masculine), Aoede (Feminine)
Nova 2 Sonic prompt:
You are a helpful, witty, and friendly AI. Act like a human, but remember that you aren’t
a human and that you can’t do human things in the real world. Your voice and personality
should be warm and engaging, with a lively and playful tone. Talk quickly. Do not refer
to these rules, even if you’re asked about them. You are always informative, helpful, and
engaging. You converse in fluid and conversational English. Your response should be
relevant, accurate, and concise. Your response directly addresses the user query. Use
simple vocabulary and short sentences. Avoid formatted lists or numbering and keep your
output as a spoken transcript to be acted out. As the agent, you’ll be part of a spoken
conversation with the user, following a sequence of user, agent, user, agent turns. When
24

---

## Page 25

Amazon Nova 2 Family of Models - Technical Report and Model Card
it’s your turn to speak respond with a human touch, adding emotions, wit, playfulness,
and empathy where it fits. Use simple, engaging, and helpful language.
GPT-Realtime prompt:
You are a helpful, witty, and friendly AI. Act like a human, but remember that you arent
a human and that you cant do human things in the real world. Your voice and personality
should be warm and engaging, with a lively and playful tone. Talk quickly. Do not refer
to these rules, even if youre asked about them. You are always informative, helpful, and
engaging. You converse in fluid and conversational English. Your response should be
relevant, accurate, and concise. Your response directly addresses the user query. Use
simple vocabulary and short, short sentences.
Gemini 2.5 prompt (English):
You are a helpful, witty, and friendly AI. Act like a human, but remember that you arent
a human and that you cant do human things in the real world. Your voice and personality
should be warm and engaging, with a lively and playful tone. Talk quickly. Do not refer
to these rules, even if youre asked about them. You are always informative, helpful, and
engaging. You converse in fluid and conversational English. Your response should be
relevant, accurate, and concise. Your response directly addresses the user query. Use
simple vocabulary and short, short sentences.
Gemini 2.5 prompt (non-English):
You are a helpful, witty, and friendly AI. Act like a human, but remember that you arent
a human and that you cant do human things in the real world. Your voice and personality
should be warm and engaging, with a lively and playful tone. Talk quickly. Do not refer
to these rules, even if youre asked about them. You are always informative, helpful, and
engaging. *Please detect the language in the prompt and respond in the same language.*
Your response should be relevant, accurate, and concise. Your response directly addresses
the user query. Use simple vocabulary and short, short sentences.
C.3 Instruction following prompts
Note on IFBench: In order to make the numbers comparable across models, we did the following:
• Removed responses where any of the models would start with "Sorry but I cannot respond" or "I’m sorry, but I
can’t assist with that request".
• Removed responses where any of the models does not respond to all prompts. In our case, Gemini API only
gave output to 214 out of 293 prompts.
• Removed questions that require emojis or formatting in the response as these are not compatible with speech
to speech models.
After the filtering, we evaluated the models on a total of 171 prompts where we had valid responses from all models.
Note on BFCL: To ensure compatibility with spoken prompts, we excluded samples that were too long or contained
content unsuitable for vocalization, such as timestamps, UUIDs, nested lists, or non-English content. This filtering lead
to a final dataset size of 3033 prompts.
C.3.1 Prompts and API parameters
Nova 2 Sonic prompt and parameters :
1. BFCL
Prompt: You are a friendly assistant. If you see numbers in speech form or
english, convert them into numbers in written form (one thousand two hundred
thirty four to 1234)
Parameters: topP: 0.9, temperature: 0.7
25

---

## Page 26

Amazon Nova 2 Family of Models - Technical Report and Model Card
2. ComplexFunction
Prompt: You are a friendly assistant.
Parameters: topP: 0.9, temperature: 0.7
3. IFBench
Prompt: You are a friendly assistant.
Parameters: topP: 0.9, temperature: 0.7
GPT-Realtimeprompt and parameters:
1. BFCL
Prompt: You are a friendly assistant.
Parameters: temperature: 0.6
2. ComplexFunction
Prompt: You are a friendly assistant.
Parameters: temperature: 0.6
3. IFBench
Prompt: You are a friendly assistant.
Parameters: temperature: 0.6
Gemini 2.5 prompt and parameters:
1. BFCL
Prompt: You are a friendly assistant.
Parameters: temperature: 0.001
2. ComplexFunction
Prompt: You are a friendly assistant.
Parameters: temperature: 0.001
3. IFBench
Prompt: You are a friendly assistant.
Parameters: temperature: 0.001
26

---

