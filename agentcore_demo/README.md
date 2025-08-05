# AWS Bedrock AgentCore 客户支持助手

这是一个基于 AWS Bedrock AgentCore 构建的智能客户支持助手演示项目，展示了如何使用 Strands 框架和 Bedrock AgentCore SDK 创建一个功能完整的 AI 代理。

## 项目概述

该项目实现了一个客户支持助手，具备以下功能：
- 根据邮箱地址查询客户信息
- 查询客户订单详情
- 提供产品知识库信息
- 支持计算器和时间查询工具
- 集成记忆管理和身份认证服务

## 目录结构

```
agentcore_demo/
├── my_agent.py              # 主要的代理实现
├── my_memory.py             # 记忆管理示例
├── my_identify.py           # 身份认证服务示例
├── test_my_agent.py         # 代理测试脚本
├── requirements.txt         # Python 依赖
├── Dockerfile              # Docker 构建文件
├── .dockerignore           # Docker 忽略文件
├── .gitignore              # Git 忽略文件
├── .env                    # 环境变量配置（敏感信息）
├── sample.env              # 环境变量配置模板
├── codebuild-policy.json   # CodeBuild 策略文件
├── execution-role-policy.json # 执行角色策略文件
└── README.md               # 项目文档
```

## 系统要求

- **Python**: 3.12+
- **Docker**: 20.10+ (推荐 25.0+)
- **AWS CLI**: 配置好的 AWS 凭证
- **操作系统**: Linux (推荐 Amazon Linux 2023, Ubuntu 20.04+)
- **架构**: 支持 AMD64 和 ARM64

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd agentcore_demo

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境变量配置

```bash
# 复制环境变量模板
cp sample.env .env

# 编辑 .env 文件，填入你的实际配置
nano .env
```

需要配置的主要环境变量：
- `AWS_REGION`: AWS 区域
- `AGENT_RUNTIME_ARN`: 代理运行时 ARN（用于测试，部署后自动生成）
- `GOOGLE_CLIENT_ID`: Google OAuth2 客户端 ID（可选）
- `GOOGLE_CLIENT_SECRET`: Google OAuth2 客户端密钥（可选）
- `PERPLEXITY_API_KEY`: Perplexity AI API 密钥（可选）

**注意**: `.bedrock_agentcore.yaml` 是自动生成的配置文件，包含部署相关的配置信息，不需要手动配置环境变量。

### 3. 本地开发

```bash
# 运行代理（本地开发模式）
python my_agent.py

# 测试代理
python test_my_agent.py
```

### 4. Docker 构建

#### 本地构建（AMD64）
```bash
docker build -t customer-support-agent .
docker run -p 8080:8080 customer-support-agent
```

#### 跨架构构建（ARM64）
```bash
# 安装多架构支持
docker run --privileged --rm tonistiigi/binfmt --install all

# 创建多架构构建器
docker buildx create --name multiarch-builder --driver docker-container --use
docker buildx inspect --bootstrap

# 构建 ARM64 镜像
docker buildx build --platform linux/arm64 --load -t customer-support-agent:arm64 .

# 多平台构建并推送
docker buildx build --platform linux/amd64,linux/arm64 --push -t <your-registry>/customer-support-agent:latest .
```

## 功能特性

### 核心工具

1. **客户查询工具**
   - `get_customer_id(email_address)`: 根据邮箱获取客户 ID
   - `get_orders(customer_id)`: 查询客户订单信息

2. **知识库工具**
   - `get_knowledge_base_info(topic)`: 获取产品相关信息

3. **内置工具**
   - `calculator`: 数学计算
   - `current_time`: 当前时间查询

### 扩展服务

1. **记忆管理** (`my_memory.py`)
   - 创建和管理对话记忆
   - 支持语义记忆策略
   - 事件存储和检索

2. **身份认证** (`my_identify.py`)
   - OAuth2 凭证提供者
   - API 密钥管理
   - 工作负载身份管理

## API 使用示例

### 基本对话
```python
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

payload = {
    "prompt": "Hello, I need help with my order. My email is me@example.net"
}

response = client.invoke_agent_runtime(
    agentRuntimeArn="your-agent-runtime-arn",
    qualifier="DEFAULT",
    payload=json.dumps(payload)
)
```

### 订单查询
```python
payload = {
    "prompt": "Can you check my recent orders? My email is me@example.net"
}
```

### 产品支持
```python
payload = {
    "prompt": "How do I install the smartphone cover?"
}
```

## 部署指南

### AWS Bedrock AgentCore 部署

1. **配置 AWS 凭证**
```bash
aws configure
```

2. **部署代理**
```bash
# 使用 Bedrock AgentCore CLI
bedrock-agentcore deploy
```

3. **验证部署**
```bash
# 测试代理端点
python test_my_agent.py
```

### CodeBuild 集成

项目包含 CodeBuild 配置文件，支持自动化构建和部署：

- `codebuild-policy.json`: CodeBuild 服务策略
- `execution-role-policy.json`: 执行角色权限策略

## 开发指南

### 添加新工具

1. 在 `my_agent.py` 中定义新的工具函数：
```python
@tool
def your_new_tool(parameter: str) -> str:
    """工具描述"""
    # 实现逻辑
    return json.dumps(result)
```

2. 将工具添加到代理配置：
```python
agent = Agent(
    model="us.amazon.nova-lite-v1:0",
    system_prompt=SYSTEM_PROMPT,
    tools=[calculator, current_time, your_new_tool, ...]
)
```

### 自定义系统提示

修改 `SYSTEM_PROMPT` 变量来调整代理行为：
```python
SYSTEM_PROMPT = """
你的自定义系统提示...
"""
```

### 环境变量管理

所有敏感配置都通过环境变量管理：
- 开发环境：使用 `.env` 文件
- 生产环境：使用 AWS Systems Manager Parameter Store 或 Secrets Manager

## 测试

### 单元测试
```bash
# 运行基本测试
python test_my_agent.py
```

### 集成测试
```bash
# 测试完整工作流
python -c "
import json
from my_agent import app

# 测试客户查询
result = app.entrypoint({'prompt': 'Check orders for me@example.net'})
print(result)
"
```

## 故障排除

### 常见问题

1. **"exec format error" 错误**
   - 确保已安装 QEMU 模拟器
   - 重新创建 Docker buildx 构建器

2. **环境变量未加载**
   - 检查 `.env` 文件是否存在
   - 确认 `python-dotenv` 已安装

3. **AWS 权限错误**
   - 验证 AWS 凭证配置
   - 检查 IAM 角色权限

### 调试模式

启用详细日志：
```bash
export PYTHONPATH=.
export DEBUG=1
python my_agent.py
```

## 性能优化

### Docker 优化
- 使用多阶段构建减少镜像大小
- 合理使用 `.dockerignore` 排除不必要文件
- 利用 Docker 层缓存

### 代理优化
- 优化工具函数的响应时间
- 使用适当的模型配置
- 实现结果缓存机制

## 安全最佳实践

1. **敏感信息管理**
   - 所有敏感信息存储在环境变量中
   - 使用 AWS Secrets Manager 管理生产环境密钥
   - 定期轮换 API 密钥

2. **访问控制**
   - 实施最小权限原则
   - 使用 IAM 角色而非长期凭证
   - 启用 CloudTrail 审计

3. **网络安全**
   - 使用 VPC 端点访问 AWS 服务
   - 配置安全组限制访问
   - 启用传输加密

## 监控和日志

### CloudWatch 集成
- 自动收集应用日志
- 设置性能指标监控
- 配置告警规则

### 可观测性
```yaml
observability:
  enabled: true
  metrics:
    - request_count
    - response_time
    - error_rate
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果遇到问题或需要帮助：

1. 查看 [故障排除](#故障排除) 部分
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue 描述问题
4. 联系项目维护者

## 相关资源

- [AWS Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Strands 框架文档](https://strands.ai/docs)
- [Docker 多架构构建指南](https://docs.docker.com/build/building/multi-platform/)
- [AWS CodeBuild 用户指南](https://docs.aws.amazon.com/codebuild/latest/userguide/)

---

**注意**: 本项目仅用于演示目的，生产环境使用前请进行充分的安全评估和测试。
