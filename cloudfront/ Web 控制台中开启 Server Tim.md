在 AWS CloudFront 的 Web 控制台中开启 Server Timing 的步骤如下：

1. 登录 AWS 管理控制台
   • 打开 https://console.aws.amazon.com/
   • 登录您的 AWS 账户

2. 导航到 CloudFront 控制台
   • 在服务列表中选择 CloudFront 或直接访问 https://console.aws.amazon.com/cloudfront/

3. 创建响应标头策略
   • 在左侧导航栏中，点击 "Policies"（策略）
   • 选择 "Response headers"（响应标头）选项卡
   • 点击 "Create policy"（创建策略）按钮
   • 输入策略名称，例如 "EnableServerTiming"
   • 添加描述（可选）

4. 配置 Server Timing 设置
   • 向下滚动到 "Server-timing header" 部分
   • 勾选 "Enable" 复选框启用 Server Timing
   • 设置采样率（Sampling rate）- 可以设置为 100% 以获取所有请求的数据，或设置较低的百分比
以减少开销
   • 点击 "Create"（创建）按钮保存策略

5. 将策略应用到您的 CloudFront 分配
   • 返回 CloudFront 控制台主页
   • 在分配列表中找到您的分配（例如 E3VSG6PS4BT85T）
   • 点击分配 ID 进入详情页面
   • 点击 "Behaviors"（行为）选项卡
   • 选择要修改的缓存行为，然后点击 "Edit"（编辑）
   • 向下滚动到 "Response headers policy"（响应标头策略）部分
   • 从下拉菜单中选择您刚才创建的 "EnableServerTiming" 策略
   • 点击 "Save changes"（保存更改）按钮

6. 等待部署完成
   • CloudFront 会将更改部署到所有边缘位置，这可能需要几分钟时间
   • 部署完成后，您的分配将开始在响应中包含 Server-Timing 标头

启用后，您可以通过浏览器开发者工具的网络面板查看这些 Server-Timing 标头，它们提供了有关请
求处理各个阶段的详细性能信息，有助于您分析和优化内容交付性能。


命中：
server-timing
cdn-cache-hit,cdn-pop;desc="SFO5-P3",cdn-hit-layer;desc="REC",cdn-rid;desc="JlflyrFsU4HGbRo5cSjdjbWFvkLuhB-5eYyWOTBr-qjBaveXOLomeQ==",cdn-downstream-fbl=4

不命中：
server-timing
cdn-upstream-layer;desc="REC",cdn-upstream-dns;dur=0,cdn-upstream-connect;dur=180,cdn-upstream-fbl;dur=404,cdn-cache-miss,cdn-pop;desc="SFO5-P3",cdn-rid;desc="T9ymQP6Mfc-cJdDVsD0Y-kCnxA4k290ASqILrCQwqfVly-Q6aZ6Ehw==",cdn-downstream-fbl=410

我来解释一下 server-timing 参数中的信息，这些信息可以帮助您了解 CloudFront 的缓存状态和请
求处理情况。

## 缓存命中的 server-timing 信息解析

server-timing
cdn-cache-hit,cdn-pop;desc="SFO5-P3",cdn-hit-layer;desc="REC",cdn-rid;desc="JlflyrFsU4HGbRo5cSjdjbWFvkLuhB-5eYyWOTBr-qjBaveXOLomeQ==",cdn-downstream-fbl=4


• cdn-cache-hit: 表示请求在 CloudFront 缓存中命中，无需向源站请求
• cdn-pop;desc="SFO5-P3": 表示处理请求的 CloudFront 接入点(PoP)位于旧金山(SFO5-P3)
• cdn-hit-layer;desc="REC": 表示缓存命中发生在区域边缘缓存(Regional Edge Cache, REC)层
• cdn-rid: 请求的唯一标识符，用于故障排查
• cdn-downstream-fbl=4: 表示从 CloudFront 到客户端的第一个字节延迟为 4 毫秒，非常快

## 缓存未命中的 server-timing 信息解析

server-timing
cdn-upstream-layer;desc="REC",cdn-upstream-dns;dur=0,cdn-upstream-connect;dur=180,cdn-upstream-fbl;dur=404,cdn-cache-miss,cdn-pop;desc="SFO5-P3",cdn-rid;desc="T9ymQP6Mfc-cJdDVsD0Y-kCnxA4k290ASqILrCQwqfVly-Q6aZ6Ehw==",cdn-downstream-fbl=410


• cdn-upstream-layer;desc="REC": 表示请求是从区域边缘缓存(REC)转发到源站的
• cdn-upstream-dns;dur=0: DNS 解析源站域名所需时间为 0 毫秒
• cdn-upstream-connect;dur=180: 连接到源站所需时间为 180 毫秒
• cdn-upstream-fbl;dur=404: 从源站接收到第一个字节的延迟为 404 毫秒
• cdn-cache-miss: 表示请求在 CloudFront 缓存中未命中，需要向源站请求
• cdn-pop;desc="SFO5-P3": 同样是旧金山的接入点
• cdn-rid: 请求的唯一标识符
• cdn-downstream-fbl=410: 从 CloudFront 到客户端的第一个字节延迟为 410 毫秒

## 比较分析

通过比较这两个 server-timing 信息，我们可以看出：

1. 缓存命中时，响应速度非常快（downstream-fbl 只有 4 毫秒）
2. 缓存未命中时，需要向源站请求，总延迟明显增加（downstream-fbl 为 410 毫秒）
3. 向源站请求的主要延迟来自连接时间（180 毫秒）和等待源站响应的时间（404 毫秒）

这些信息对于分析 CloudFront 性能和排查问题非常有用。如果您看到大量的缓存未命中情况，可能需
要检查您的缓存策略是否正确配置，特别是在处理带有查询参数（如 x-oss-process）的请求时。

您可以通过这些信息确认我们之前讨论的缓存策略修改是否生效 - 如果修改后带有 x-oss-process 参
数的请求能够命中缓存，您应该会看到 cdn-cache-hit 而不是 cdn-cache-miss。