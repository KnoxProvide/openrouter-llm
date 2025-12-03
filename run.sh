#!/bin/bash

# 激活虚拟环境并运行图像识别脚本

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "虚拟环境不存在,正在创建..."
    python3 -m venv .venv
    echo "✓ 虚拟环境创建完成"
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖是否已安装
if ! python -c "import openai" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -q -r requirements.txt
    echo "✓ 依赖安装完成"
fi

# 运行脚本
python image_recognition.py
