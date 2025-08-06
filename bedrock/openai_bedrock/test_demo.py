#!/usr/bin/env python3
"""
OpenAI SDK 测试演示 - 包含模拟响应
Test Demo with Mock Responses
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_client():
    """创建 OpenAI 客户端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-test-key-for-demo")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )

def test_basic_chat():
    """测试基础聊天功能"""
    print("OpenAI SDK 基础聊天测试")
    print("=" * 40)
    
    # 创建客户端
    try:
        client = create_client()
        print("✓ OpenAI 客户端创建成功")
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        return
    
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    print(f"使用模型: {model}")
    print()
    
    # 测试消息
    test_messages = [
        "你好，请介绍一下自己",
        "什么是人工智能？",
        "用Python写一个简单的Hello World程序"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"测试 {i}: {message}")
        print("-" * 30)
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": message}
                ],
                max_completion_tokens=1000,
                temperature=0.7
            )
            
            print(f"回复: {response.choices[0].message.content}")
            if hasattr(response, 'usage'):
                print(f"Token使用: {response.usage.total_tokens}")
            
        except Exception as e:
            print(f"调用 API 时出错: {e}")
            print("这可能是由于以下原因:")
            print("1. API密钥无效或格式不正确")
            print("2. 网络连接问题")
            print("3. 模型名称不正确")
            print("4. API端点不可访问")
            
            # 提供模拟响应以演示功能
            print("\n--- 模拟响应 (仅用于演示) ---")
            mock_responses = {
                "你好，请介绍一下自己": "你好！我是一个AI助手，基于大型语言模型构建。我可以帮助你回答问题、编写代码、翻译文本等多种任务。",
                "什么是人工智能？": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统，如学习、推理、感知和决策。",
                "用Python写一个简单的Hello World程序": "```python\nprint('Hello, World!')\n```\n这是最简单的Python程序，使用print()函数输出文本到控制台。"
            }
            
            if message in mock_responses:
                print(f"模拟回复: {mock_responses[message]}")
        
        print()

def test_streaming_chat():
    """测试流式聊天功能"""
    print("流式聊天测试")
    print("=" * 40)
    
    client = create_client()
    message = "请讲一个关于编程的小故事"
    
    try:
        stream = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": message}],
            max_completion_tokens=500,
            temperature=0.7,
            stream=True
        )
        
        print(f"用户: {message}")
        print("AI回复: ", end="", flush=True)
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
        
        print()
        
    except Exception as e:
        print(f"流式聊天测试失败: {e}")
        print("\n--- 模拟流式响应 ---")
        mock_story = "从前有一个程序员，他每天都在写代码。有一天，他发现了一个神奇的bug，这个bug让他的程序运行得比预期更好。他意识到，有时候最好的解决方案来自于意外的发现。"
        
        print(f"用户: {message}")
        print("AI回复: ", end="", flush=True)
        
        import time
        for char in mock_story:
            print(char, end="", flush=True)
            time.sleep(0.05)  # 模拟流式输出
        print()

def main():
    """主函数"""
    print("OpenAI SDK 功能测试演示")
    print("=" * 50)
    print("注意: 如果API调用失败，将显示模拟响应以演示功能")
    print()
    
    # 显示当前配置
    print("当前配置:")
    api_key = os.getenv("OPENAI_API_KEY", "未设置")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else f"API Key: {api_key}")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print()
    
    # 运行测试
    test_basic_chat()
    print("\n" + "=" * 50)
    test_streaming_chat()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n如需使用真实的OpenAI API:")
    print("1. 获取有效的OpenAI API密钥")
    print("2. 在.env文件中设置正确的OPENAI_API_KEY")
    print("3. 确保OPENAI_BASE_URL指向正确的API端点")
    print("4. 选择支持的模型名称")

if __name__ == "__main__":
    main()
