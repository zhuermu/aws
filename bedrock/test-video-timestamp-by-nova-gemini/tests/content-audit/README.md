# 🎯 视频内容审核测试

评估 AI 模型识别视频中用户操作行为的准确性。

## 🎯 测试目标

识别视频中的用户行为：
1. 关键词搜索
2. 视频标题验证
3. 创作者信息验证
4. 观看时长判断（1/2/3 分钟）

## 🤖 测试模型

- Amazon Nova Lite v1.0
- Amazon Nova 2 Lite v1.0 (Standard)
- Amazon Nova 2 Lite v1.0 (Reasoning)
- Amazon Nova Pro v1.0
- Google Gemini 2.5 Flash
- Google Gemini 2.5 Flash Lite

## 🚀 运行测试

```bash
python video_content_audit_test.py
```

或使用快捷脚本：
```bash
./run_audit_test.sh
```

## 📊 查看结果

双击打开 `audit_results_visualization_v2.html`

## 📁 文件说明

- `video_content_audit_test.py` - 主测试脚本
- `audit_results_visualization_v2.html` - 可视化界面（推荐）
- `audit_test_results.json` - 测试结果数据
- `audit_test_report.md` - Markdown 格式报告
- `video-1.mp4` ~ `video-4.mp4` - 测试视频
