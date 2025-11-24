#!/bin/bash

# 视频内容审核测试运行脚本

echo "=================================="
echo "视频内容审核测试"
echo "=================================="

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import boto3" 2>/dev/null || {
    echo "错误: 未安装 boto3，请运行: pip install boto3"
    exit 1
}

# 检查 AWS 凭证
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ ! -f ~/.aws/credentials ]; then
    echo "警告: 未配置 AWS 凭证"
    echo "请运行: aws configure"
    echo "或设置环境变量: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
fi

# 检查 Gemini API Key (可选)
if [ -z "$GEMINI_API_KEY" ]; then
    echo "提示: 未设置 GEMINI_API_KEY，将跳过 Gemini 模型测试"
    echo "如需测试 Gemini 模型，请设置: export GEMINI_API_KEY='your-api-key'"
fi

# 运行测试
echo ""
echo "开始运行测试..."
python3 video_content_audit_test.py

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "测试完成！"
    echo "=================================="
    echo "结果文件:"
    echo "  - audit_test_results.json"
    echo "  - audit_test_report.md"
else
    echo ""
    echo "测试失败，请检查错误信息"
    exit 1
fi
