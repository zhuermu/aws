#!/usr/bin/env python3
"""
基础的 OpenAI SDK 聊天完成示例
Basic OpenAI SDK Chat Completion Example
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_client():
    """创建 OpenAI 客户端"""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if not api_key:
        raise ValueError("请设置 OPENAI_API_KEY 环境变量")
    
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )

def basic_chat_completion(client, message, model="gpt-3.5-turbo"):
    """基础聊天完成"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ],
            max_completion_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"调用 API 时出错: {e}")
        return None

def main():
    """主函数"""
    print("OpenAI SDK 基础聊天示例")
    print("=" * 40)
    
    # 创建客户端
    try:
        client = create_client()
        print("✓ OpenAI 客户端创建成功")
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        return
    
    # 测试消息
    test_messages = [
        "你好，请介绍一下自己",
        "什么是人工智能？",
        "用Python写一个简单的Hello World程序"
    ]
    
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    print(f"使用模型: {model}")
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"测试 {i}: {message}")
        print("-" * 30)
        
        response = basic_chat_completion(client, message, model)
        
        if response:
            print(f"回复: {response}")
        else:
            print("获取回复失败")
        
        print()

if __name__ == "__main__":
    main()
