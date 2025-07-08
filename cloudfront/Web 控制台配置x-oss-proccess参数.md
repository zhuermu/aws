## 问题分析

您的CloudFront 默认会分配使用了"Managed-CachingOptimized"缓存策略，该策略配置为
不转发任何查询参数（QueryStringBehavior: "none"）。这就是为什么您的
x-oss-process=image/resize,p_50参数没有被传递到阿里云OSS的原因。

## 解决方案

您需要在AWS管理控制台中创建一个新的缓存策略，并将其应用到您的CloudFront分配。以下是详细步
骤：

### 1. 创建自定义缓存策略

1. 登录AWS管理控制台
2. 进入CloudFront服务
3. 在左侧导航栏中选择"策略"
4. 选择"缓存策略"选项卡
5. 点击"创建缓存策略"按钮
6. 填写以下信息：
   • 名称：OSS-Image-Processing-Policy（或您喜欢的任何名称）
   • 描述：允许转发x-oss-process参数到阿里云OSS
   • 最小TTL：根据您的需求设置（例如：1秒）
   • 最大TTL：根据您的需求设置（例如：31536000秒）
   • 默认TTL：根据您的需求设置（例如：86400秒/1天）
7. 在"缓存键设置"部分：
   • 启用"包含查询字符串"
   • 选择"包含指定的查询字符串"
   • 添加x-oss-process作为要包含的查询字符串
   • 保持"不包含HTTP头"和"不包含Cookie"的设置
8. 点击"创建"按钮保存策略


### 2. 更新CloudFront分配以使用新的缓存策略

1. 在CloudFront控制台中，选择您的分配（例如：EW9T1MVPJM70V）
2. 点击"行为"选项卡
3. 找到处理图片文件的缓存行为（例如：/*.jpg、/*.jpeg等）
4. 选择该行为并点击"编辑"
5. 在"缓存键和源请求"部分：
   • 缓存策略：选择您刚刚创建的OSS-Image-Processing-Policy
   • 保持原始请求策略不变（您已经使用的是"Managed-AllViewer"，这是正确的）
6. 点击"保存更改"
7. 对所有图片相关的路径模式（*.jpg、*.jpeg、*.png等）重复此过程

### 3. 使更改生效

1. 等待CloudFront部署您的更改（状态将从"正在部署"变为"已部署"）
2. 创建缓存失效以清除现有缓存：
   • 在CloudFront控制台中，选择您的分配
   • 点击"失效"选项卡
   • 点击"创建失效"
   • 输入路径模式（例如：/*.jpg）以失效所有图片
   • 点击"创建失效"按钮

### 4. 测试配置

完成上述步骤后，尝试使用带有x-oss-process参数的URL访问您的图片，例如：
https://d67t168ivf3b6.cloudfront.net/upload/icon/uid-80371282_md5-fe7ec853f32cd4050c2c3765b786668f_w-1276_h-1584_s-666395_mc-ced7e3.jpg?x-oss-process=image/resize,p_50

现在，CloudFront应该会将x-oss-process参数转发到阿里云OSS，并且您应该能够看到压缩后的图片。

这样配置后，CloudFront将根据不同的x-oss-process参数值分别缓存图片，同时仍然保持高效的缓存
行为。