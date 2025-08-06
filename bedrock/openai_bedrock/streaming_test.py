#!/usr/bin/env python3
"""
流式聊天测试 - 包含模拟响应和降级处理
Streaming Chat Test with Mock Responses and Fallback
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_client():
    """创建 OpenAI 客户端"""
    api_key = os.getenv("OPENAI_API_KEY", "sk-test-key")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )

def test_streaming_with_fallback(client, message, model="gpt-3.5-turbo"):
    """测试流式响应，包含降级处理"""
    print(f"测试消息: {message}")
    print("-" * 40)
    
    try:
        # 首先尝试流式响应
        print("尝试流式响应...")
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_completion_tokens=500,
            temperature=0.7,
            stream=True
        )
        
        print("AI回复 (流式): ", end="", flush=True)
        full_response = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print()
        print("✓ 流式响应成功")
        return full_response
        
    except Exception as e:
        error_message = str(e)
        print(f"流式响应失败: {e}")
        
        if "unsupported for streaming" in error_message or "streaming" in error_message.lower():
            print("→ 模型不支持流式，尝试普通响应...")
            
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": message}],
                    max_completion_tokens=500,
                    temperature=0.7,
                    stream=False
                )
                
                content = response.choices[0].message.content
                print("AI回复 (普通): ", end="", flush=True)
                
                # 模拟流式输出效果
                for char in content:
                    print(char, end="", flush=True)
                    time.sleep(0.02)
                
                print()
                print("✓ 普通响应成功")
                return content
                
            except Exception as fallback_error:
                print(f"普通响应也失败: {fallback_error}")
                return provide_mock_response(message)
        else:
            print("→ 其他错误，提供模拟响应...")
            return provide_mock_response(message)

def provide_mock_response(message):
    """提供模拟响应"""
    print("→ 使用模拟响应演示功能...")
    
    mock_responses = {
        "你是谁": "我是一个AI助手，基于大型语言模型构建。我可以帮助你回答问题、编写代码、翻译文本等多种任务。我的目标是为用户提供有用、准确和友好的帮助。",
        "你好": "你好！很高兴与你交流。我是一个AI助手，可以帮助你解答问题、提供信息或协助完成各种任务。有什么我可以帮助你的吗？",
        "讲个故事": "从前有一个程序员，他每天都在写代码。有一天，他发现了一个神奇的bug，这个bug让他的程序运行得比预期更好。他意识到，有时候最好的解决方案来自于意外的发现。这个故事告诉我们，在编程的世界里，保持开放的心态和好奇心是非常重要的。",
        "什么是AI": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。这包括学习、推理、感知、理解自然语言、识别模式等能力。AI技术正在改变我们的生活和工作方式。"
    }
    
    # 寻找最匹配的响应
    response = None
    for key, value in mock_responses.items():
        if key in message or message in key:
            response = value
            break
    
    if not response:
        response = "这是一个模拟响应。在实际使用中，AI会根据你的问题提供相应的回答。请确保API配置正确以获得真实的AI响应。"
    
    print("AI回复 (模拟): ", end="", flush=True)
    
    # 模拟流式输出
    for char in response:
        print(char, end="", flush=True)
        time.sleep(0.03)
    
    print()
    print("✓ 模拟响应完成")
    return response

def main():
    """主函数"""
    print("流式聊天功能测试")
    print("=" * 50)
    
    # 显示配置信息
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    api_key = os.getenv("OPENAI_API_KEY", "未设置")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    print(f"模型: {model}")
    print(f"API端点: {base_url}")
    print(f"API密钥: {api_key[:10]}..." if len(api_key) > 10 else f"API密钥: {api_key}")
    print()
    
    # 创建客户端
    try:
        client = create_client()
        print("✓ OpenAI 客户端创建成功")
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        return
    
    # 测试消息
    test_messages = [
        "你是谁",
        "你好",
        "讲个故事",
        "什么是AI"
    ]
    
    print("\n开始测试流式响应功能...")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n测试 {i}/{len(test_messages)}")
        test_streaming_with_fallback(client, message, model)
        
        if i < len(test_messages):
            print("\n" + "-" * 50)
            time.sleep(1)  # 短暂暂停
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n功能说明:")
    print("1. 优先尝试流式响应")
    print("2. 如果模型不支持流式，自动降级为普通响应")
    print("3. 如果API调用失败，提供模拟响应演示功能")
    print("4. 所有响应都会模拟流式输出效果")

if __name__ == "__main__":
    main()
