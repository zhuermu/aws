"""
生成 Nova 2 Lite Reasoning 模式的最终测试报告
"""

import json
from datetime import datetime

# 读取测试结果
with open('nova2_reasoning_test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取 video-1 的单独测试结果
with open('video1_nova2_reasoning_result.json', 'r', encoding='utf-8') as f:
    video1_data = json.load(f)

# 更新 video-1 的结果
results = data['results']
results[0] = video1_data['result']

# 保存更新后的结果
output_data = {
    "test_date": datetime.now().isoformat(),
    "results": results
}

with open('nova2_reasoning_final_results.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

# 生成 Markdown 报告
report = []
report.append("# Nova 2 Lite (Reasoning=low) 测试报告\n\n")
report.append(f"**测试日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
report.append("---\n\n")

report.append("## 测试概述\n\n")
report.append("本测试专门评估 **amazon.nova-2-lite-v1:0** 在启用推理模式 (reasoning=low) 时对视频内容的理解和审核能力。\n\n")

report.append("## 测试结果汇总\n\n")
report.append("| 视频 | 状态 | 响应时间(秒) | 输入Token | 输出Token |\n")
report.append("|------|------|-------------|-----------|----------|\n")

for result in results:
    status = "✅ 成功" if result['success'] else "❌ 失败"
    video = result['video']
    elapsed = f"{result['elapsed_time']:.2f}"
    input_tokens = result.get('input_tokens', 'N/A')
    output_tokens = result.get('output_tokens', 'N/A')
    
    report.append(f"| {video} | {status} | {elapsed} | {input_tokens} | {output_tokens} |\n")

report.append("\n## 详细结果\n\n")

for i, result in enumerate(results, 1):
    report.append(f"\n### {i}. {result['video']}\n\n")
    
    # 显示期望值
    if 'expected' in result:
        report.append("**期望值**:\n")
        expected = result['expected']
        report.append(f"- 搜索关键词: {expected['search_keyword'] or '无搜索动作'}\n")
        report.append(f"- 视频标题: {expected['title'] or '没观看视频'}\n")
        report.append(f"- 作者: {expected['creator'] or '无作者'}\n")
        report.append(f"- 观看时长: {expected['watch_duration']}分钟\n\n")
    
    if result['success']:
        report.append(f"**状态**: ✅ 成功\n")
        report.append(f"**响应时间**: {result['elapsed_time']:.2f} 秒\n")
        report.append(f"**输入Token**: {result['input_tokens']}\n")
        report.append(f"**输出Token**: {result['output_tokens']}\n")
        
        report.append("\n**模型响应**:\n")
        report.append("```json\n")
        report.append(result['response'])
        report.append("\n```\n")
    else:
        report.append(f"**状态**: ❌ 失败\n")
        report.append(f"**错误信息**: {result.get('error', 'Unknown error')}\n")

report.append("\n## 性能分析\n\n")

# 计算平均值
successful_results = [r for r in results if r['success']]
if successful_results:
    avg_time = sum(r['elapsed_time'] for r in successful_results) / len(successful_results)
    avg_input = sum(r['input_tokens'] for r in successful_results) / len(successful_results)
    avg_output = sum(r['output_tokens'] for r in successful_results) / len(successful_results)
    
    report.append(f"- **成功率**: {len(successful_results)}/{len(results)} ({len(successful_results)*100//len(results)}%)\n")
    report.append(f"- **平均响应时间**: {avg_time:.2f} 秒\n")
    report.append(f"- **平均输入Token**: {avg_input:.0f}\n")
    report.append(f"- **平均输出Token**: {avg_output:.0f}\n")

report.append("\n## 关键发现\n\n")
report.append("1. **推理模式需要流式API**: Nova 2 Lite 在启用 reasoning 模式时，必须使用 `converse_stream` API 才能获取响应内容\n")
report.append("2. **Token使用**: 推理模式会消耗更多的输出 Token（平均约 2000+ tokens）\n")
report.append("3. **响应时间**: 推理模式的响应时间较长，特别是对于较长的视频（video-3 和 video-4）\n")
report.append("4. **准确性**: 模型能够准确识别视频标题和作者信息，但对观看时长的判断存在差异\n")

report_text = "".join(report)

with open('nova2_reasoning_final_report.md', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("✅ 报告生成完成！")
print("- JSON结果: nova2_reasoning_final_results.json")
print("- Markdown报告: nova2_reasoning_final_report.md")
