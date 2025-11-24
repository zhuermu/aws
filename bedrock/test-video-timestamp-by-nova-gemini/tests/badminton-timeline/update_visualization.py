#!/usr/bin/env python3
"""
自动更新可视化数据脚本
当 test_results.json 修改后，运行此脚本更新 test_data.js
"""

import json

def update_test_data():
    """读取 test_results.json 并生成 test_data.js"""
    try:
        # 读取 JSON 文件
        with open('test_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 写入 JavaScript 文件
        with open('test_data.js', 'w', encoding='utf-8') as f:
            f.write('const testData = ')
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
            f.write(';')
        
        print('✓ test_data.js 已成功更新！')
        print('  现在可以刷新浏览器查看最新数据')
        
    except FileNotFoundError:
        print('✗ 错误: 找不到 test_results.json 文件')
    except json.JSONDecodeError as e:
        print(f'✗ 错误: JSON 格式不正确 - {e}')
    except Exception as e:
        print(f'✗ 错误: {e}')

if __name__ == '__main__':
    update_test_data()
