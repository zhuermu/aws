"""
从 audit_test_results.json 生成完整的测试报告
"""

import json
from datetime import datetime

# 读取测试结果
with open('audit_test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['results']

# 生成 Markdown 报告
report = []
report.append("# 视频内容审核测试报告\n\n")
report.append(f"**测试日期**: {datetime.fromisoformat(data['test_date']).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
report.append("---\n\n")

report.append("## 测试概述\n\n")
report.append("本测试评估多个模型对视频内容的理解和审核能力：\n\n")
report.append("- amazon.nova-lite-v1:0\n")
report.append("- amazon.nova-2-lite-v1:0 (standard mode)\n")
report.append("- amazon.nova-2-lite-v1:0 (reasoning mode, maxReasoningEffort=low)\n")
report.append("- amazon.nova-pro-v1:0\n")
report.append("- gemini-2.5-flash\n")
report.append("- gemini-2.5-flash-lite\n\n")

# 按视频分组
videos = {}
for result in results:
    video = result['video']
    if video not in videos:
        videos[video] = []
    videos[video].append(result)

# 为每个视频生成报告
for video_name in sorted(videos.keys()):
    report.append(f"\n## {video_name.upper()}\n\n")
    
    video_results = videos[video_name]
    
    # 显示期望值
    if video_results and 'expected' in video_results[0]:
        report.append("**期望值**:\n")
        expected = video_results[0]['expected']
        report.append(f"- 搜索关键词: {expected['search_keyword'] or '无搜索动作'}\n")
        report.append(f"- 视频标题: {expected['title'] or '没观看视频'}\n")
        report.append(f"- 作者: {expected['creator'] or '无作者'}\n")
        report.append(f"- 观看时长: {expected['watch_duration']}分钟\n\n")
    
    # 结果汇总表
    report.append("### 测试结果汇总\n\n")
    report.append("| 模型 | 状态 | 响应时间(秒) | 输入Token | 输出Token |\n")
    report.append("|------|------|-------------|-----------|----------|\n")
    
    for result in video_results:
        status = "✅" if result['success'] else "❌"
        model = result['model']
        elapsed = f"{result['elapsed_time']:.2f}"
        input_tokens = result.get('input_tokens', 'N/A')
        output_tokens = result.get('output_tokens', 'N/A')
        
        report.append(f"| {model} | {status} | {elapsed} | {input_tokens} | {output_tokens} |\n")
    
    # 详细结果
    report.append("\n### 详细响应\n\n")
    
    for i, result in enumerate(video_results, 1):
        report.append(f"\n#### {i}. {result['model']}\n\n")
        
        if result['success']:
            report.append(f"**状态**: ✅ 成功\n")
            report.append(f"**响应时间**: {result['elapsed_time']:.2f} 秒\n\n")
            
            report.append("**模型响应**:\n")
            report.append("```json\n")
            # 截取前 1000 字符
            response = result['response']
            if len(response) > 1000:
                report.append(response[:1000] + "\n... (已截断)")
            else:
                report.append(response)
            report.append("\n```\n")
        else:
            report.append(f"**状态**: ❌ 失败\n")
            report.append(f"**错误**: {result.get('error', 'Unknown error')}\n")

report.append("\n---\n\n")
report.append("## 总体统计\n\n")

# 计算统计信息
total_tests = len(results)
successful_tests = sum(1 for r in results if r['success'])
failed_tests = total_tests - successful_tests

report.append(f"- **总测试数**: {total_tests}\n")
report.append(f"- **成功**: {successful_tests} ({successful_tests*100//total_tests}%)\n")
report.append(f"- **失败**: {failed_tests}\n")

# 按模型统计
model_stats = {}
for result in results:
    model = result['model']
    if model not in model_stats:
        model_stats[model] = {'success': 0, 'total': 0, 'avg_time': 0, 'times': []}
    
    model_stats[model]['total'] += 1
    if result['success']:
        model_stats[model]['success'] += 1
        model_stats[model]['times'].append(result['elapsed_time'])

report.append("\n### 按模型统计\n\n")
report.append("| 模型 | 成功率 | 平均响应时间 |\n")
report.append("|------|--------|-------------|\n")

for model, stats in sorted(model_stats.items()):
    success_rate = f"{stats['success']}/{stats['total']}"
    avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
    report.append(f"| {model} | {success_rate} | {avg_time:.2f}s |\n")

report_text = "".join(report)

with open('audit_test_report.md', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("✅ 报告生成完成！")
print("- 输入: audit_test_results.json")
print("- 输出: audit_test_report.md")
print(f"- 总测试数: {total_tests}")
print(f"- 成功: {successful_tests}")
print(f"- 失败: {failed_tests}")
