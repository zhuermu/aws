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
