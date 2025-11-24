# 🏸 羽毛球视频时间线识别测试

评估多个 AI 模型识别羽毛球比赛回合起止时间的能力。

## 🎯 测试目标

识别视频中每个回合的：
- 开始时间戳
- 结束时间戳
- 结束原因（得分/失误/出界等）

## 🤖 测试模型

- Amazon Nova Lite v1.0
- Amazon Nova 2 Lite v1.0 (Standard)
- Amazon Nova 2 Lite v1.0 (Reasoning)
- Amazon Nova Pro v1.0
- Google Gemini 2.5 Flash
- Google Gemini 2.5 Flash Lite

## 🚀 运行测试

```bash
python video_timeline_test.py
```

## 📊 查看结果

双击打开 `test_results_visualization.html`

## 📁 文件说明

- `video_timeline_test.py` - 主测试脚本
- `test_results_visualization.html` - 可视化界面
- `test_data.js` - 测试数据（自动生成）
- `update_visualization.py` - 更新可视化数据
- `manage_gemini_files.py` - Gemini 文件管理工具
