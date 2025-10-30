#!/bin/bash
# Telegram 转发器启动脚本

# 切换到 telegram 目录
cd "$(dirname "$0")"

echo "=================================="
echo "启动 Telegram WebSocket 转发器"
echo "=================================="
echo ""

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "❌ 错误: .env 文件不存在"
    echo ""
    echo "请先创建 .env 文件并配置以下参数:"
    echo "  cp .env.example .env"
    echo "  然后编辑 .env 文件填入实际值"
    echo ""
    exit 1
fi

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖..."
python3 -c "import requests, websockets, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  依赖未完全安装，正在安装..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

echo "✅ 依赖检查完成"
echo ""

# 启动转发器
echo "正在启动转发器..."
echo ""

python3 webhook_forwarder.py

# 捕获退出信号
trap "echo ''; echo '停止转发器...'; exit 0" SIGINT SIGTERM

