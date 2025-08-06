#!/usr/bin/env python3
"""
错误处理和最佳实践示例
Error Handling and Best Practices Demo
"""

import os
import time
import logging
from openai import OpenAI
from openai import RateLimitError, APIError, APIConnectionError, AuthenticationError
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        base_url=base_url,
        timeout=30.0,  # 设置超时时间
        max_retries=3   # 设置重试次数
    )

def robust_api_call(client, messages, model="gpt-3.5-turbo", max_retries=3):
    """
    健壮的API调用，包含错误处理和重试机制
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试第 {attempt + 1} 次API调用")
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=1000,
                temperature=0.7
            )
            
            logger.info("API调用成功")
            return response
            
        except RateLimitError as e:
            logger.warning(f"速率限制错误: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logger.error("达到最大重试次数，速率限制错误")
                raise
                
        except APIConnectionError as e:
            logger.warning(f"网络连接错误: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logger.error("达到最大重试次数，网络连接错误")
                raise
                
        except AuthenticationError as e:
            logger.error(f"认证错误: {e}")
            logger.error("请检查API密钥是否正确")
            raise
            
        except APIError as e:
            logger.error(f"API错误: {e}")
            if e.status_code >= 500:  # 服务器错误，可以重试
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"服务器错误，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error("达到最大重试次数，服务器错误")
                    raise
            else:  # 客户端错误，不重试
                logger.error("客户端错误，不进行重试")
                raise
                
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise

def validate_input(message):
    """输入验证"""
    if not message or not message.strip():
        raise ValueError("消息不能为空")
    
    if len(message) > 4000:  # 假设token限制
        raise ValueError("消息过长，请缩短内容")
    
    return message.strip()

def token_usage_monitor(response):
    """监控token使用情况"""
    if hasattr(response, 'usage'):
        usage = response.usage
        logger.info(f"Token使用情况:")
        logger.info(f"  提示tokens: {usage.prompt_tokens}")
        logger.info(f"  完成tokens: {usage.completion_tokens}")
        logger.info(f"  总tokens: {usage.total_tokens}")
        
        # 警告高token使用
        if usage.total_tokens > 3000:
            logger.warning("Token使用量较高，请注意成本控制")

def safe_chat_completion(client, message, model="gpt-3.5-turbo"):
    """安全的聊天完成函数"""
    try:
        # 输入验证
        validated_message = validate_input(message)
        
        # 构建消息
        messages = [{"role": "user", "content": validated_message}]
        
        # 调用API
        response = robust_api_call(client, messages, model)
        
        # 监控token使用
        token_usage_monitor(response)
        
        # 返回结果
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "usage": response.usage._asdict() if hasattr(response, 'usage') else None
        }
        
    except ValueError as e:
        logger.error(f"输入验证错误: {e}")
        return {"success": False, "error": f"输入错误: {e}"}
        
    except RateLimitError as e:
        logger.error(f"速率限制: {e}")
        return {"success": False, "error": "请求过于频繁，请稍后再试"}
        
    except AuthenticationError as e:
        logger.error(f"认证失败: {e}")
        return {"success": False, "error": "API密钥无效"}
        
    except APIConnectionError as e:
        logger.error(f"连接错误: {e}")
        return {"success": False, "error": "网络连接失败"}
        
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return {"success": False, "error": f"系统错误: {str(e)}"}

def batch_processing_example(client, messages, model="gpt-3.5-turbo"):
    """批量处理示例"""
    print("批量处理示例")
    print("-" * 30)
    
    results = []
    
    for i, message in enumerate(messages, 1):
        print(f"处理消息 {i}/{len(messages)}: {message[:30]}...")
        
        result = safe_chat_completion(client, message, model)
        results.append(result)
        
        if result["success"]:
            print(f"✓ 成功")
        else:
            print(f"✗ 失败: {result['error']}")
        
        # 避免速率限制
        time.sleep(1)
    
    return results

def main():
    """主函数"""
    print("OpenAI SDK 错误处理和最佳实践示例")
    print("=" * 50)
    
    # 创建客户端
    try:
        client = create_client()
        logger.info("OpenAI 客户端创建成功")
    except Exception as e:
        logger.error(f"客户端创建失败: {e}")
        return
    
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 测试各种场景
    test_cases = [
        "你好，请介绍一下自己",  # 正常情况
        "",  # 空消息
        "a" * 5000,  # 过长消息
        "什么是人工智能？",  # 正常情况
    ]
    
    print("\n单个消息测试:")
    print("-" * 30)
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        result = safe_chat_completion(client, message, model)
        
        if result["success"]:
            print(f"✓ 成功: {result['content'][:100]}...")
            if result["usage"]:
                print(f"  Token使用: {result['usage']['total_tokens']}")
        else:
            print(f"✗ 失败: {result['error']}")
    
    # 批量处理测试
    print("\n\n批量处理测试:")
    print("-" * 30)
    
    batch_messages = [
        "什么是Python？",
        "如何学习编程？",
        "人工智能的应用领域有哪些？"
    ]
    
    batch_results = batch_processing_example(client, batch_messages, model)
    
    # 统计结果
    success_count = sum(1 for r in batch_results if r["success"])
    print(f"\n批量处理结果: {success_count}/{len(batch_results)} 成功")

if __name__ == "__main__":
    main()
