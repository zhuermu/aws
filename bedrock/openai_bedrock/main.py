#!/usr/bin/env python3
"""
OpenAI SDK 演示程序主入口
Main entry point for OpenAI SDK demos
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_environment():
    """检查环境配置"""
    print("环境检查:")
    print("-" * 20)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✓ OPENAI_API_KEY: {'*' * (len(api_key) - 8) + api_key[-8:]}")
    else:
        print("✗ OPENAI_API_KEY: 未设置")
        return False
    
    # 检查其他配置
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    print(f"✓ BASE_URL: {base_url}")
    print(f"✓ MODEL: {model}")
    
    # 检查依赖
    try:
        import openai
        print(f"✓ OpenAI SDK: {openai.__version__}")
    except ImportError:
        print("✗ OpenAI SDK: 未安装")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 50)
    print("OpenAI SDK 演示程序")
    print("=" * 50)
    print("1. 基础聊天完成 (basic_chat.py)")
    print("2. 流式聊天 (streaming_chat.py)")
    print("3. 高级功能 (advanced_features.py)")
    print("4. 错误处理和最佳实践 (error_handling.py)")
    print("5. 测试演示 - 包含模拟响应 (test_demo.py)")
    print("6. 流式聊天测试 - 包含降级处理 (streaming_test.py)")
    print("7. 环境检查")
    print("0. 退出")
    print("-" * 50)

def run_demo(choice):
    """运行指定的演示"""
    demos = {
        "1": "basic_chat.py",
        "2": "streaming_chat.py", 
        "3": "advanced_features.py",
        "4": "error_handling.py",
        "5": "test_demo.py",
        "6": "streaming_test.py"
    }
    
    if choice in demos:
        demo_file = demos[choice]
        print(f"\n运行演示: {demo_file}")
        print("=" * 50)
        
        try:
            # 动态导入并运行
            module_name = demo_file.replace('.py', '')
            module = __import__(module_name)
            
            if hasattr(module, 'main'):
                module.main()
            else:
                print(f"错误: {demo_file} 中没有找到 main() 函数")
                
        except ImportError as e:
            print(f"导入错误: {e}")
        except Exception as e:
            print(f"运行错误: {e}")
    
    elif choice == "7":
        check_environment()
    
    elif choice == "0":
        print("再见！")
        sys.exit(0)
    
    else:
        print("无效选择，请重试")

def main():
    """主函数"""
    print("欢迎使用 OpenAI SDK 演示程序！")
    
    # 首次环境检查
    if not check_environment():
        print("\n环境配置有问题，请先解决上述问题。")
        print("\n配置步骤:")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 中设置你的 OPENAI_API_KEY")
        print("3. 安装依赖: pip install -r requirements.txt")
        return
    
    # 主循环
    while True:
        try:
            show_menu()
            choice = input("请选择 (0-7): ").strip()
            run_demo(choice)
            
            if choice != "0":
                input("\n按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n程序被中断，再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()
