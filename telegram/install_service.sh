#!/bin/bash
# 将 Telegram 转发器安装为系统服务

echo "=================================="
echo "安装 Telegram 转发器系统服务"
echo "=================================="
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 权限运行此脚本"
    echo "   sudo ./install_service.sh"
    exit 1
fi

# 复制服务文件
SERVICE_FILE="/etc/systemd/system/telegram_forwarder.service"
cp telegram_forwarder.service "$SERVICE_FILE"

if [ $? -eq 0 ]; then
    echo "✅ 服务文件已复制到: $SERVICE_FILE"
else
    echo "❌ 复制服务文件失败"
    exit 1
fi

# 重新加载 systemd
systemctl daemon-reload
echo "✅ systemd 配置已重新加载"

# 启用服务（开机自启）
read -p "是否启用开机自启动？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl enable telegram_forwarder.service
    echo "✅ 已启用开机自启动"
fi

echo ""
echo "=================================="
echo "安装完成！"
echo "=================================="
echo ""
echo "使用以下命令管理服务:"
echo "  启动: sudo systemctl start telegram_forwarder"
echo "  停止: sudo systemctl stop telegram_forwarder"
echo "  重启: sudo systemctl restart telegram_forwarder"
echo "  状态: sudo systemctl status telegram_forwarder"
echo "  日志: sudo journalctl -u telegram_forwarder -f"
echo ""

