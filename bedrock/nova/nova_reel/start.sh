#!/bin/bash

# 检查是否安装了 Python 3.8+
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要 Python 3.8 或更高版本，当前版本: $python_version"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建必要的目录
mkdir -p uploads outputs static templates

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，请复制 env.example 并配置您的 AWS 凭证"
    echo "cp env.example .env"
fi

# 启动应用
echo "启动 Nova Reel 视频生成器..."
echo "访问地址: http://localhost:8000"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
