#!/bin/bash
# 卸载 Token Monitor 系统服务

echo "=========================================="
echo "卸载 Token Monitor 系统服务"
echo "=========================================="
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 权限运行此脚本"
    echo "   sudo ./uninstall_service.sh"
    exit 1
fi

SERVICE_NAME="token_monitor"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# 检查服务是否存在
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ 服务未安装"
    exit 1
fi

# 停止服务
echo "停止服务..."
systemctl stop "$SERVICE_NAME"
if [ $? -eq 0 ]; then
    echo "✅ 服务已停止"
else
    echo "⚠️  停止服务失败或服务未运行"
fi

# 禁用服务
echo "禁用开机自启..."
systemctl disable "$SERVICE_NAME"
if [ $? -eq 0 ]; then
    echo "✅ 已禁用开机自启"
fi

# 删除服务文件
echo "删除服务文件..."
rm -f "$SERVICE_FILE"
if [ $? -eq 0 ]; then
    echo "✅ 服务文件已删除"
else
    echo "❌ 删除服务文件失败"
    exit 1
fi

# 重新加载 systemd
systemctl daemon-reload
echo "✅ systemd 配置已重新加载"

echo ""
echo "=========================================="
echo "卸载完成！"
echo "=========================================="
echo ""

