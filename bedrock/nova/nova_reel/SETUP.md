# Nova Reel 视频生成器设置指南

## 前置要求

### 1. AWS 配置

确保你已经配置了 AWS 凭证：

```bash
aws configure
```

或者设置环境变量：
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. IAM 权限

你的 AWS 用户/角色需要以下权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:StartAsyncInvoke",
                "bedrock:GetAsyncInvoke",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-nova-reel-bucket",
                "arn:aws:s3:::your-nova-reel-bucket/*"
            ]
        }
    ]
}
```

### 3. S3 桶设置

1. **创建 S3 桶**：
   ```bash
   aws s3 mb s3://your-nova-reel-bucket --region us-east-1
   ```

2. **更新应用配置**：
   编辑 `app.py` 文件，找到这一行：
   ```python
   output_s3_uri = "s3://your-nova-reel-bucket"
   ```
   替换为你的实际 S3 桶名称。

3. **测试 S3 访问**：
   ```bash
   aws s3 ls s3://your-nova-reel-bucket
   ```

## 启动应用

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **启动应用**：
   ```bash
   ./start.sh
   ```
   或者：
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **访问应用**：
   打开浏览器访问 http://localhost:8000

## 使用流程

1. **上传图片** - 支持 PNG, JPG, JPEG, GIF, BMP 格式
2. **输入提示词** - 描述你想要的视频内容
3. **选择时长** - 5-10秒
4. **提交作业** - 系统会启动异步视频生成作业
5. **等待完成** - 页面会自动检查作业状态
6. **获取视频** - 完成后可以从 S3 下载视频

## 故障排除

### 常见错误

1. **AccessDeniedException**
   - 检查 AWS 凭证配置
   - 确认 IAM 权限设置正确

2. **S3 相关错误**
   - 确认 S3 桶存在且可访问
   - 检查 S3 桶权限设置

3. **ValidationException**
   - 检查图片格式和大小
   - 确认提示词不为空

### 调试步骤

1. **测试 AWS 连接**：
   ```bash
   python3 test_nova_reel_async.py
   ```

2. **检查应用日志**：
   ```bash
   tail -f app.log
   ```

3. **验证 S3 配置**：
   ```bash
   aws s3 ls s3://your-nova-reel-bucket
   ```

## 注意事项

- Nova Reel 视频生成通常需要几分钟时间
- 生成的视频会保存在你的 S3 桶中
- 请注意 AWS 使用费用
- 图片会自动调整为 1280x720 分辨率
- 支持的视频时长为 5-10 秒

## 支持

如果遇到问题，请检查：
1. AWS 凭证和权限
2. S3 桶配置
3. 网络连接
4. 应用日志文件
