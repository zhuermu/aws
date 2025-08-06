#!/usr/bin/env python3
"""
流式聊天示例 - 实时显示生成的内容
Streaming Chat Example - Real-time content generation
"""

import os
import sys
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

def streaming_chat(client, message, model="gpt-3.5-turbo"):
    """流式聊天完成（如果模型不支持流式，则降级为普通响应）"""
    try:
        # 首先尝试流式响应
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ],
            max_completion_tokens=1000,
            temperature=0.7,
            stream=True  # 启用流式响应
        )
        
        print("AI回复: ", end="", flush=True)
        full_response = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print()  # 换行
        return full_response
    
    except Exception as e:
        error_message = str(e)
        if "unsupported for streaming" in error_message or "streaming" in error_message.lower():
            print(f"模型 {model} 不支持流式响应，降级为普通响应...")
            print()
            
            # 降级为普通响应
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": message}
                    ],
                    max_completion_tokens=1000,
                    temperature=0.7,
                    stream=False  # 禁用流式响应
                )
                
                content = response.choices[0].message.content
                print("AI回复: ", end="", flush=True)
                
                # 模拟流式输出效果
                import time
                for char in content:
                    print(char, end="", flush=True)
                    time.sleep(0.02)  # 稍微延迟以模拟流式效果
                
                print()  # 换行
                return content
                
            except Exception as fallback_error:
                print(f"普通响应也失败: {fallback_error}")
                return None
        else:
            print(f"调用 API 时出错: {e}")
            return None

def interactive_chat(client, model="gpt-3.5-turbo"):
    """交互式聊天"""
    print("交互式聊天模式 (输入 'quit' 退出)")
    print("=" * 40)
    
    conversation_history = []
    supports_streaming = None  # 用于记录模型是否支持流式
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            # 添加用户消息到历史
            conversation_history.append({"role": "user", "content": user_input})
            
            # 如果还没有测试过流式支持，或者已知支持流式
            if supports_streaming is None or supports_streaming:
                try:
                    # 尝试流式生成回复
                    stream = client.chat.completions.create(
                        model=model,
                        messages=conversation_history,
                        max_completion_tokens=1000,
                        temperature=0.7,
                        stream=True
                    )
                    
                    print("AI: ", end="", flush=True)
                    ai_response = ""
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            print(content, end="", flush=True)
                            ai_response += content
                    
                    print()  # 换行
                    supports_streaming = True  # 标记支持流式
                    
                except Exception as e:
                    error_message = str(e)
                    if "unsupported for streaming" in error_message or "streaming" in error_message.lower():
                        print(f"模型 {model} 不支持流式响应，切换到普通模式...")
                        supports_streaming = False  # 标记不支持流式
                        
                        # 降级为普通响应
                        response = client.chat.completions.create(
                            model=model,
                            messages=conversation_history,
                            max_completion_tokens=1000,
                            temperature=0.7,
                            stream=False
                        )
                        
                        ai_response = response.choices[0].message.content
                        print("AI: ", end="", flush=True)
                        
                        # 模拟流式输出效果
                        import time
                        for char in ai_response:
                            print(char, end="", flush=True)
                            time.sleep(0.02)
                        
                        print()  # 换行
                    else:
                        print(f"\n发生错误: {e}")
                        continue
            else:
                # 已知不支持流式，直接使用普通响应
                response = client.chat.completions.create(
                    model=model,
                    messages=conversation_history,
                    max_completion_tokens=1000,
                    temperature=0.7,
                    stream=False
                )
                
                ai_response = response.choices[0].message.content
                print("AI: ", end="", flush=True)
                
                # 模拟流式输出效果
                import time
                for char in ai_response:
                    print(char, end="", flush=True)
                    time.sleep(0.02)
                
                print()  # 换行
            
            # 添加AI回复到历史
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # 限制对话历史长度，避免token过多
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
        
        except KeyboardInterrupt:
            print("\n\n程序被中断，再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")

def main():
    """主函数"""
    print("OpenAI SDK 流式聊天示例")
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
    
    # 选择模式
    print("\n选择模式:")
    print("1. 单次流式对话")
    print("2. 交互式聊天")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == "1":
        message = input("\n请输入你的问题: ").strip()
        if message:
            print()
            streaming_chat(client, message, model)
    elif choice == "2":
        interactive_chat(client, model)
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
