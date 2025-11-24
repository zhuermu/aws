"""
Gemini 文件管理工具
用于查看、删除已上传到 Gemini 的文件
"""

import google.generativeai as genai
import os
from datetime import datetime

def list_files():
    """列出所有已上传的文件"""
    print("=" * 80)
    print("已上传的文件列表")
    print("=" * 80)
    
    files = list(genai.list_files())
    
    if not files:
        print("没有找到已上传的文件")
        return []
    
    print(f"\n总共 {len(files)} 个文件:\n")
    
    for i, file in enumerate(files, 1):
        print(f"{i}. {file.display_name}")
        print(f"   URI: {file.name}")
        print(f"   状态: {file.state.name}")
        print(f"   大小: {file.size_bytes / (1024*1024):.2f} MB")
        if hasattr(file, 'create_time'):
            print(f"   创建时间: {file.create_time}")
        print("-" * 80)
    
    return files

def delete_file(file_name: str):
    """删除指定文件"""
    try:
        genai.delete_file(file_name)
        print(f"✅ 已删除文件: {file_name}")
        return True
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return False

def delete_all_files():
    """删除所有文件"""
    files = list(genai.list_files())
    
    if not files:
        print("没有文件需要删除")
        return
    
    print(f"\n将删除 {len(files)} 个文件")
    confirm = input("确认删除所有文件? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("取消删除")
        return
    
    success_count = 0
    for file in files:
        if delete_file(file.name):
            success_count += 1
    
    print(f"\n✅ 成功删除 {success_count}/{len(files)} 个文件")

def delete_video_files():
    """只删除视频文件 (.mov, .mp4)"""
    files = list(genai.list_files())
    
    video_files = [f for f in files if f.display_name.endswith(('.mov', '.mp4', '.MOV', '.MP4'))]
    
    if not video_files:
        print("没有找到视频文件")
        return
    
    print(f"\n找到 {len(video_files)} 个视频文件:")
    for file in video_files:
        print(f"  - {file.display_name}")
    
    confirm = input("\n确认删除这些视频文件? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("取消删除")
        return
    
    success_count = 0
    for file in video_files:
        if delete_file(file.name):
            success_count += 1
    
    print(f"\n✅ 成功删除 {success_count}/{len(video_files)} 个视频文件")

def main():
    """主函数"""
    # 从环境变量获取 API Key
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ 错误: 未设置 GEMINI_API_KEY 环境变量")
        print("请设置: export GEMINI_API_KEY='your-api-key'")
        return
    
    genai.configure(api_key=api_key)
    
    while True:
        print("\n" + "=" * 80)
        print("Gemini 文件管理工具")
        print("=" * 80)
        print("1. 列出所有文件")
        print("2. 删除所有文件")
        print("3. 只删除视频文件")
        print("4. 删除指定文件")
        print("0. 退出")
        print("=" * 80)
        
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '0':
            print("退出程序")
            break
        elif choice == '1':
            list_files()
        elif choice == '2':
            delete_all_files()
        elif choice == '3':
            delete_video_files()
        elif choice == '4':
            files = list_files()
            if files:
                try:
                    index = int(input("\n请输入要删除的文件编号: ")) - 1
                    if 0 <= index < len(files):
                        delete_file(files[index].name)
                    else:
                        print("无效的文件编号")
                except ValueError:
                    print("请输入有效的数字")
        else:
            print("无效的选择，请重试")

if __name__ == "__main__":
    main()
