https://aws.amazon.com/cn/tutorials/deploy-webapp-eks/module-three/


sequenceDiagram
    participant A as EndUser
    participant B as Cloudfront@func
    A->>B: /path?token=xxx or cookies
    B-->>A: 403 Invalid token

sequenceDiagram
    participant A as UserClient
    participant B as WebServer
    participant C as RTC Network
    participant D as Agent
    A->>B: 1.1 /v1/api/genertateToken
    B-->>A: 1.2 200 OK {token: xxx, channel: agora_xxx}
    A->>C: 1.3 connect websocket with token and channel
    C-->A: 1.4 establish connection
    A->>B: 2.1 /v1/api/start {channel: agora_xxx}
    B->>D: 2.2 start agent with user_uid and channel
    D->>C: 2.3 start RTC connection with channel
    B-->>A: 2.3 200 OK

**用户量**：月活用户1000人，每人每天使用1小时，每月总计30000小时，每个人产生120轮对话
**流量大小**：
视频传出: 每次最多10张图片，每张图片大小约 0.1MB，120轮对话，每次对话10张图片：0.1 * 10 * 120 * 1000 * 30 / 1000 = 3600GB
音频传出：默认：48 KHz, 1 channel, 16-bit, bitrate: 48 Kbps，每秒：约 0.093 MB
音频：1000 * 120 * 15(一轮对话产生15秒音频) * 0.093 M * 30 / 1000 = 5022 GB
**语音识别STT**
每轮对话20秒语音（问题5秒，回答15秒，不需要识别）
120 * 5 * 1000 * 30 / 60= 30万 分钟
25 万分钟 * 0.024 USD = 6000 USD
5 万分钟 * 0.015 USD = 750 USD
总计：6250 USD
**TTS**
每轮对话20秒语音（问题5秒,不需要合成，回答15秒）
15 秒约 200 字符
120 * 200 * 1000 * 30 / 1000000 = 720 百万字符
720 * 30.00 USB  = 21600 USD

**AWS部署资源**
1. EKS集群,按小时付费
2. CloudFront,按流量付费
   - functions: 每月200次万免费套餐，1000 * 3600 * 30 = 108万次，
   - 数据传出费用： 1T免费流量，可忽略，使用声网传出音视频，每月网页和文本应该在1T内 
   - HTTP：100万免费次用，180万次，每次 10000次 0.01 USD，180 * 0.01 = 1.8 USD
3. ALB 按请求数付费
   - 新连接数（每秒）： 1000/每天1小时，分散到12小时，每小时有83人，每分钟1.38人，每秒发送一个请求检查心跳
   - 活跃连接数（每分钟）：1000人，12个小时内，1.38 * 60 = 83人
4. EC2实例-c8g.large（2cpu,4G),按需/RI 月 USD 38.38 USD
    - 每小时平局在线83人，高峰期假设为平时3倍，83 * 3 = 249人，
    - 249 用户session内存占用： 249 * (20张图片（历史和本轮） * 0.1MB + 其他开销 1M) = 747 MB 
    - 3 台实例高可用，38.38 * 3 = 115.14 USD
5. 网络费用
6. agora.io
7. Transribe、Polly、Nova模型调用费用
Nova模型调用费用
每个人1小时 3600 / 30(每轮对话时间) = 120次调用
每次token input 800 * 10 = 8000 token output 100 token
总input token 8000 * 120 * 1000 * 30 = 2880000000
总output token 100 * 120 * 1000 * 30 = 36000000
lite input总费用 2880000000/1000 * 0.00006 = 1728
lite output总费用 36000000/1000 * 0.00014 = 8.64 
Pro input总费用 2880000000/1000 * 0.0008 = 23040
Pro output总费用 36000000/1000 * 0.0032 = 115.2

| Image Resolution | Dimensions | Estimated Token Count |
| --- | --- | --- |
| HxW or WxH      | 900 x 450  | ~800              |
| HxW or WxH      | 900 x 900  | ~1300             |
| HxW or WxH      | 1400 x 900 | ~1800             |
| HxW or WxH      | 1.8K x 900 | ~2400             |
| HxW or WxH      | 1.3K x 1.3K| ~2600             |

| 服务 | 费用 | 计费 | 说明 |
| --- | --- | --- | --- |
EKS集群	| 72 USD|	0.1/h USD|	每月 0.10 * 24 * 30 = 72
EC2实例 |	115.14 USD	|c8g.large(2cpu,4G),按需/RI 月 38.38 USD|	每月 38.38 * 3 = 115.14
网络传出|	926.24 USD|	0.09 GB USD|	调用Transcribe 和Polly：6696 GB * 0.09 = 602.64 USD
调用大模型：1000 * 120 * 10 张图片 * 0.0001G * 30 * 0.09 = 324 USD
CloudFront|	1.8 USD|	200次万免费套餐|	functions+输出传出+HTTPS 0.0+0.0+1.8=1.8 USD
ALB|	16.29 USD|	每小时 USD 0.0225 + LCU 每小时008|	基础费用：0.0225 * 24 * 30 = 16.2， 83 * 0.008 = 0.09，16.29
agora.io|	9960 元	|150万分钟 8300元/月|	1000人 * 30个小时* 60分钟=180万分钟， 8300 / 150 * 1800 = 9960 元
Nova|	23155.2 USD	|input 1000token/0.0008,output 1000/0.0032 USD|	Pro: 23040 + 115.2 = 23155.2 USD
Transribe|	6750 USD|	前25万分钟 0.24,25～75万 0.015 USD|	120 * 5 * 1000 * 30 / 60= 30万分钟
25万分钟 * 0.024USD = 6000USD,
5万分钟 * 0.015 USD = 750 USD
Polly|	21600 USD|	生成式 TTS per 100万个字符 30 USD| 	120 * 200 * 1000 * 30 / 1百万 = 1080 百万字符, 1080 万百万字符 * 30.00 USB = 21600 USD
总计	|53901.05 USD	||	72 + 115.14 + 926.24 + 1.8 + 16.29 + 9960/7.3 + 23155.2 + 6750 + 21500 = 53901.05