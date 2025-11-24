"""
更新 audit_test_results.json_bak 中的 Nova 2 Lite reasoning 结果
"""

import json

# 读取新的 reasoning 结果
with open('nova2_reasoning_final_results.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)
    new_reasoning_results = new_data['results']

# 读取旧的完整测试结果
with open('audit_test_results.json_bak', 'r', encoding='utf-8') as f:
    old_data = json.load(f)

# 创建一个字典来快速查找新的 reasoning 结果
new_results_dict = {}
for result in new_reasoning_results:
    video = result['video']
    new_results_dict[video] = result

# 替换旧结果中的 reasoning 结果
updated_results = []
for result in old_data['results']:
    # 检查是否是 reasoning 模式
    if 'reasoning=low' in result['model']:
        video = result['video']
        if video in new_results_dict:
            # 使用新的结果替换
            print(f"✅ 替换 {video} 的 reasoning 结果")
            updated_results.append(new_results_dict[video])
        else:
            print(f"⚠️  未找到 {video} 的新结果，保留旧结果")
            updated_results.append(result)
    else:
        # 保留非 reasoning 的结果
        updated_results.append(result)

# 更新数据
old_data['results'] = updated_results
old_data['test_date'] = new_data['test_date']

# 保存更新后的结果
with open('audit_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(old_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ 更新完成！")
print(f"- 输入文件: audit_test_results.json_bak")
print(f"- 新 reasoning 结果: nova2_reasoning_final_results.json")
print(f"- 输出文件: audit_test_results.json")
print(f"- 总结果数: {len(updated_results)}")
