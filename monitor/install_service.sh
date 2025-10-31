#!/bin/bash
# 将 Token Monitor 安装为系统服务

echo "=========================================="
echo "安装 Token Monitor 系统服务"
echo "=========================================="
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 权限运行此脚本"
    echo "   sudo ./install_service.sh"
    exit 1
fi

# 检查 Redis 是否运行
echo "检查 Redis 服务..."
if ! systemctl is-active --quiet redis-server && ! systemctl is-active --quiet redis; then
    echo "⚠️  Redis 服务未运行"
    echo "   尝试启动 Redis..."
    systemctl start redis-server 2>/dev/null || systemctl start redis 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Redis 已启动"
    else
        echo "❌ 无法启动 Redis，请手动安装并启动"
        echo "   安装: sudo apt install redis-server"
        exit 1
    fi
else
    echo "✅ Redis 服务正在运行"
fi

# 复制服务文件
SERVICE_FILE="/etc/systemd/system/token_monitor.service"
cp token_monitor.service "$SERVICE_FILE"

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
    systemctl enable token_monitor.service
    echo "✅ 已启用开机自启动"
fi

# 询问是否立即启动
echo ""
read -p "是否立即启动服务？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start token_monitor.service
    sleep 2
    if systemctl is-active --quiet token_monitor.service; then
        echo "✅ 服务启动成功"
    else
        echo "❌ 服务启动失败，查看日志:"
        systemctl status token_monitor.service
    fi
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "使用以下命令管理服务:"
echo "  启动: sudo systemctl start token_monitor"
echo "  停止: sudo systemctl stop token_monitor"
echo "  重启: sudo systemctl restart token_monitor"
echo "  状态: sudo systemctl status token_monitor"
echo "  日志: sudo journalctl -u token_monitor -f"
echo "  或者: tail -f /root/nlpmeme/monitor/monitor.log"
echo ""
echo "开机自启:"
echo "  启用: sudo systemctl enable token_monitor"
echo "  禁用: sudo systemctl disable token_monitor"
echo ""

