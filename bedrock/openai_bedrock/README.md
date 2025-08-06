# OpenAI SDK 大模型调用演示

这是一个全面的 OpenAI SDK 使用演示项目，包含了从基础到高级的各种功能示例。

## 项目结构

```
.
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖包
├── .env.example             # 环境变量示例文件
├── main.py                  # 主程序入口
├── test_demo.py             # 测试演示（包含模拟响应）
├── streaming_test.py        # 流式聊天测试（包含降级处理）
├── basic_chat.py            # 基础聊天完成示例
├── streaming_chat.py        # 流式聊天示例
├── advanced_features.py     # 高级功能示例
└── error_handling.py        # 错误处理和最佳实践
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 OpenAI API 配置：
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

**注意**: 确保使用有效的 OpenAI API 密钥格式（以 `sk-` 开头）。

### 3. 运行演示

运行主程序：
```bash
python main.py
```

运行测试演示（包含模拟响应）：
```bash
python test_demo.py
```

运行流式聊天测试（包含降级处理）：
```bash
python streaming_test.py
```

或者直接运行单个演示：
```bash
python basic_chat.py
python streaming_chat.py
python advanced_features.py
python error_handling.py
```

## 重要说明

### API 参数更新
本项目已更新为使用最新的 OpenAI API 参数：
- ✅ 使用 `max_completion_tokens` 替代已弃用的 `max_tokens`
- ✅ 兼容 OpenAI SDK 1.0+ 版本
- ✅ 包含完整的错误处理和重试机制

### 测试和演示
- `test_demo.py` 包含模拟响应，即使 API 调用失败也能演示功能
- `streaming_test.py` 专门测试流式聊天功能，包含降级处理
- 所有示例都包含详细的错误处理和说明
- 支持多种 OpenAI 兼容的 API 端点
- 自动检测模型是否支持流式响应，不支持时自动降级

## 功能特性

### 1. 基础聊天完成 (`basic_chat.py`)
- ✅ 基本的聊天完成功能
- ✅ 客户端创建和配置
- ✅ 简单的错误处理
- ✅ 多个测试用例

**主要功能：**
- 创建 OpenAI 客户端
- 发送单轮对话请求
- 处理响应结果
- 基础错误处理

### 2. 流式聊天 (`streaming_chat.py`)
- ✅ 实时流式响应
- ✅ 交互式聊天模式
- ✅ 对话历史管理
- ✅ 优雅的用户界面

**主要功能：**
- 流式内容生成
- 实时显示AI回复
- 多轮对话支持
- 对话历史限制

### 3. 高级功能 (`advanced_features.py`)
- ✅ 系统提示词使用
- ✅ 函数调用 (Function Calling)
- ✅ 多轮对话管理
- ✅ 不同模型对比
- ✅ 参数调优示例

**主要功能：**
- 系统角色设定
- 工具函数集成
- 对话上下文管理
- 模型性能对比
- 温度参数调节

### 4. 错误处理和最佳实践 (`error_handling.py`)
- ✅ 完善的错误处理机制
- ✅ 自动重试和退避策略
- ✅ 输入验证
- ✅ Token使用监控
- ✅ 批量处理支持
- ✅ 日志记录

**主要功能：**
- 网络错误重试
- 速率限制处理
- 输入数据验证
- 资源使用监控
- 批量请求处理

## API 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 无 | ✅ |
| `OPENAI_BASE_URL` | API 基础URL | `https://api.openai.com/v1` | ❌ |
| `OPENAI_MODEL` | 默认使用的模型 | `gpt-3.5-turbo` | ❌ |

### 支持的模型

- `gpt-3.5-turbo` - 快速、经济的选择
- `gpt-4` - 更强大的推理能力
- `gpt-4-turbo` - 平衡性能和成本
- 其他 OpenAI 兼容模型

## 使用示例

### 基础用法

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "你好！"}
    ]
)

print(response.choices[0].message.content)
```

### 流式响应

```python
stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "讲个故事"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

### 函数调用

```python
functions = [
    {
        "name": "get_weather",
        "description": "获取天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"}
            },
            "required": ["city"]
        }
    }
]

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "北京天气如何？"}],
    functions=functions,
    function_call="auto"
)
```

## 错误处理

项目包含完善的错误处理机制：

- **网络错误**: 自动重试，指数退避
- **速率限制**: 智能等待和重试
- **认证错误**: 清晰的错误提示
- **输入验证**: 防止无效请求
- **资源监控**: Token使用量跟踪

## 最佳实践

1. **API密钥安全**: 使用环境变量存储敏感信息
2. **错误处理**: 实现完善的异常捕获和重试机制
3. **资源监控**: 跟踪Token使用量，控制成本
4. **输入验证**: 验证用户输入，防止无效请求
5. **日志记录**: 记录关键操作和错误信息
6. **批量处理**: 合理控制请求频率，避免速率限制

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   AuthenticationError: Invalid API key
   ```
   解决方案: 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确

2. **网络连接问题**
   ```
   APIConnectionError: Connection error
   ```
   解决方案: 检查网络连接，确认 `OPENAI_BASE_URL` 可访问

3. **速率限制**
   ```
   RateLimitError: Rate limit exceeded
   ```
   解决方案: 程序会自动重试，或手动增加请求间隔

4. **模型不存在**
   ```
   APIError: Model not found
   ```
   解决方案: 检查 `OPENAI_MODEL` 设置，确认模型名称正确

### 调试技巧

1. 启用详细日志：
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. 检查环境配置：
   ```bash
   python main.py
   # 选择选项 5 进行环境检查
   ```

3. 测试网络连接：
   ```bash
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请创建 Issue 或联系项目维护者。
