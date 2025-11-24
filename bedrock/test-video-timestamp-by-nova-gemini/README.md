# 🎬 视频分析模型测试系统

多模型视频理解能力评估平台，包含两个独立的测试用例。

## 🚀 快速开始

直接双击 `index.html` 在浏览器中打开，选择要查看的测试结果。

## 📁 项目结构

```
.
├── index.html                          # 统一入口页面 ⭐
├── tests/
│   ├── badminton-timeline/            # 测试用例 1: 羽毛球时间线识别
│   │   ├── video_timeline_test.py     # 测试脚本
│   │   ├── test_results_visualization.html  # 结果可视化
│   │   └── ...
│   └── content-audit/                 # 测试用例 2: 视频内容审核
│       ├── video_content_audit_test.py  # 测试脚本
│       ├── audit_results_visualization_v2.html  # 结果可视化
│       └── ...
├── video/                             # 测试视频文件
└── requirements.txt                   # Python 依赖

```

## 📊 测试用例

### 1. 羽毛球时间线识别测试

**目标**: 评估模型识别羽毛球比赛回合起止时间的能力

**测试模型**:
- Amazon Nova Lite v1.0
- Amazon Nova 2 Lite v1.0 (Standard & Reasoning)
- Amazon Nova Pro v1.0
- Google Gemini 2.5 Flash
- Google Gemini 2.5 Flash Lite

**运行测试**:
```bash
cd tests/badminton-timeline
python video_timeline_test.py
```

**查看结果**: 打开 `tests/badminton-timeline/test_results_visualization.html`

---

### 2. 视频内容审核测试

**目标**: 评估模型识别视频中用户操作行为的准确性

**测试内容**:
- 关键词搜索识别
- 视频标题验证
- 创作者信息验证
- 观看时长判断

**运行测试**:
```bash
cd tests/content-audit
python video_content_audit_test.py
```

**查看结果**: 打开 `tests/content-audit/audit_results_visualization_v2.html`

## 🛠️ 环境配置

### 安装依赖
```bash
pip install -r requirements.txt
```

### AWS 配置
```bash
aws configure
# 或
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Gemini 配置（可选）
```bash
export GEMINI_API_KEY='your-api-key'
```

## 📈 评估指标

- ✅ 准确性 - 识别结果的正确性
- ✅ 完整性 - 是否识别所有目标内容
- ✅ 响应时间 - 模型处理速度
- ✅ Token 使用量 - 成本效益分析
- ✅ 输出格式 - JSON 格式规范性

## 📚 技术栈

- **Python 3.8+**
- **boto3** - AWS SDK
- **google-generativeai** - Gemini API
- **Chart.js** - 数据可视化

---

**版本**: 2.0.0  
**更新日期**: 2024-11-24
