#!/usr/bin/env python3
"""
OpenAI SDK 高级功能示例
Advanced OpenAI SDK Features Demo
"""

import os
import json
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

def system_prompt_example(client, model="gpt-3.5-turbo"):
    """系统提示词示例"""
    print("1. 系统提示词示例")
    print("-" * 30)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个专业的Python编程助手，总是用简洁明了的方式回答问题，并提供可运行的代码示例。"
                },
                {
                    "role": "user", 
                    "content": "如何读取JSON文件？"
                }
            ],
            max_completion_tokens=500,
            temperature=0.3
        )
        
        print(f"回复: {response.choices[0].message.content}")
        print(f"使用tokens: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"错误: {e}")

def function_calling_example(client, model="gpt-3.5-turbo"):
    """函数调用示例"""
    print("\n2. 函数调用示例")
    print("-" * 30)
    
    # 定义函数
    functions = [
        {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位"
                    }
                },
                "required": ["city"]
            }
        }
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "北京今天天气怎么样？"}
            ],
            functions=functions,
            function_call="auto",
            max_completion_tokens=500
        )
        
        message = response.choices[0].message
        
        if message.function_call:
            print(f"函数调用: {message.function_call.name}")
            print(f"参数: {message.function_call.arguments}")
            
            # 模拟函数执行结果
            function_result = {
                "city": "北京",
                "temperature": "22°C",
                "condition": "晴朗",
                "humidity": "45%"
            }
            
            # 将函数结果返回给模型
            second_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "北京今天天气怎么样？"},
                    message,
                    {
                        "role": "function",
                        "name": "get_weather",
                        "content": json.dumps(function_result, ensure_ascii=False)
                    }
                ],
                max_completion_tokens=500
            )
            
            print(f"最终回复: {second_response.choices[0].message.content}")
        else:
            print(f"普通回复: {message.content}")
            
    except Exception as e:
        print(f"错误: {e}")

def multi_turn_conversation(client, model="gpt-3.5-turbo"):
    """多轮对话示例"""
    print("\n3. 多轮对话示例")
    print("-" * 30)
    
    conversation = [
        {"role": "user", "content": "我想学习Python，从哪里开始？"},
        {"role": "assistant", "content": "学习Python是个很好的选择！建议从以下几个方面开始：\n1. 安装Python环境\n2. 学习基础语法\n3. 练习简单程序\n4. 学习常用库\n\n你想先了解哪个方面？"},
        {"role": "user", "content": "请详细说说基础语法包括什么？"}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=conversation,
            max_completion_tokens=800,
            temperature=0.5
        )
        
        print("对话历史:")
        for i, msg in enumerate(conversation[:-1], 1):
            role = "用户" if msg["role"] == "user" else "助手"
            print(f"{i}. {role}: {msg['content'][:50]}...")
        
        print(f"\n最新问题: {conversation[-1]['content']}")
        print(f"回复: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"错误: {e}")

def different_models_comparison(client):
    """不同模型对比"""
    print("\n4. 不同模型对比")
    print("-" * 30)
    
    models = ["gpt-3.5-turbo", "gpt-4"]
    question = "用一句话解释什么是机器学习"
    
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": question}],
                max_completion_tokens=100,
                temperature=0.5
            )
            
            print(f"{model}: {response.choices[0].message.content}")
            print(f"Tokens: {response.usage.total_tokens}")
            print()
            
        except Exception as e:
            print(f"{model} 调用失败: {e}")

def custom_parameters_example(client, model="gpt-3.5-turbo"):
    """自定义参数示例"""
    print("\n5. 自定义参数示例")
    print("-" * 30)
    
    parameters = [
        {"temperature": 0.1, "description": "保守/一致性"},
        {"temperature": 0.7, "description": "平衡"},
        {"temperature": 1.2, "description": "创造性"}
    ]
    
    question = "给我讲个关于程序员的笑话"
    
    for param in parameters:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": question}],
                max_completion_tokens=200,
                temperature=param["temperature"]
            )
            
            print(f"Temperature {param['temperature']} ({param['description']}):")
            print(f"{response.choices[0].message.content}")
            print()
            
        except Exception as e:
            print(f"错误: {e}")

def main():
    """主函数"""
    print("OpenAI SDK 高级功能示例")
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
    
    # 运行各种示例
    system_prompt_example(client, model)
    function_calling_example(client, model)
    multi_turn_conversation(client, model)
    different_models_comparison(client)
    custom_parameters_example(client, model)

if __name__ == "__main__":
    main()
