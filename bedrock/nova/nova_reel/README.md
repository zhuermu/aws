# Nova Reel 视频生成器

使用 Amazon Bedrock Nova Reel 将图片和提示词转换为视频的 FastAPI 应用。

## 功能特性

- 🖼️ 支持多种图片格式 (PNG, JPG, JPEG, GIF, BMP)
- 📐 自动调整图片尺寸为 1280x720
- 🎬 生成 5-10 秒视频
- 🚀 基于 FastAPI 的现代化 Web 界面
- ☁️ 使用 AWS Bedrock 异步作业 API
- 📊 实时作业状态检查
- 💾 视频保存到 S3

## 前置要求

### AWS 配置
- AWS 凭证已配置
- 具有 Bedrock 和 S3 访问权限的 IAM 角色/用户
- 一个 S3 桶用于存储生成的视频

### 详细设置
请参考 [SETUP.md](./SETUP.md) 获取完整的设置指南。

## 快速开始

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置 S3 桶**
```bash
# 创建 S3 桶
aws s3 mb s3://your-nova-reel-bucket --region us-east-1

# 编辑 app.py，更新 S3 桶名称
# 找到: output_s3_uri = "s3://your-nova-reel-bucket"
# 替换为你的实际桶名
```

3. **启动应用**
```bash
./start.sh
# 或者直接运行
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

4. **访问应用**
打开浏览器访问: http://localhost:8000

## 使用方法

1. **上传图片文件** - 系统会自动调整为 1280x720
2. **输入视频描述提示词** - 详细描述想要的视频内容
3. **选择视频时长** (5-10秒)
4. **点击生成视频** - 启动异步作业
5. **等待完成** - 页面会自动检查作业状态
6. **下载视频** - 从 S3 获取生成的视频

## API 端点

- `GET /` - 主页面
- `POST /generate_video` - 启动视频生成作业
- `GET /check_job/{invocation_arn}` - 检查作业状态
- `GET /download/{filename}` - 下载文件
- `GET /health` - 健康检查

## 工作流程

1. **图片处理** - 上传的图片被调整为标准尺寸
2. **作业启动** - 使用 Bedrock 异步 API 启动视频生成
3. **状态监控** - 前端每15秒检查一次作业状态
4. **完成通知** - 作业完成后显示 S3 下载链接

## 注意事项

- 确保 AWS 账户有 Bedrock Nova Reel 访问权限
- 需要配置有效的 S3 桶用于存储视频
- 图片文件大小限制 16MB
- 视频生成通常需要几分钟时间
- 需要 Python 3.8+ 版本

## 故障排除

### 常见问题

1. **S3 权限错误**
   - 确保 IAM 用户有 S3 读写权限
   - 检查 S3 桶是否存在且可访问

2. **Bedrock 访问被拒绝**
   - 确认 IAM 权限包含 Bedrock 相关权限
   - 检查 Nova Reel 模型是否在你的区域可用

3. **作业失败**
   - 检查图片格式和大小
   - 确认提示词内容合适
   - 查看应用日志获取详细错误信息

### 测试工具

运行测试脚本验证配置：
```bash
python3 test_nova_reel_async.py
```

## 文件结构

```
nova_reel/
├── app.py                 # 主应用文件
├── templates/
│   └── index.html        # Web 界面
├── requirements.txt      # Python 依赖
├── start.sh             # 启动脚本
├── SETUP.md             # 详细设置指南
├── test_nova_reel_async.py  # 测试脚本
└── README.md            # 本文件
```

## 技术栈

- **后端**: FastAPI, Python 3.8+
- **前端**: HTML5, CSS3, JavaScript
- **AWS 服务**: Bedrock Nova Reel, S3
- **图片处理**: Pillow (PIL)
- **异步处理**: asyncio, aiofiles
