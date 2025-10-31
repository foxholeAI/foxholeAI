#!/bin/bash
# 设置日志轮转 - 使用 cron 定期执行

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_ROTATION_SCRIPT="$SCRIPT_DIR/log_rotation.py"

echo "=========================================="
echo "设置日志轮转"
echo "=========================================="
echo ""

# 检查 Python 脚本是否存在
if [ ! -f "$LOG_ROTATION_SCRIPT" ]; then
    echo "错误: 找不到日志轮转脚本 $LOG_ROTATION_SCRIPT"
    exit 1
fi

# 设置执行权限
chmod +x "$LOG_ROTATION_SCRIPT"
echo "✓ 已设置执行权限"

# 创建 cron 任务
CRON_CMD="cd $PROJECT_DIR && /usr/bin/python3 $LOG_ROTATION_SCRIPT >> $PROJECT_DIR/logs/log_rotation.log 2>&1"

# 检查是否已存在相同的 cron 任务
if crontab -l 2>/dev/null | grep -F "$LOG_ROTATION_SCRIPT" > /dev/null; then
    echo "⚠ Cron 任务已存在"
    echo ""
    echo "当前的 cron 任务:"
    crontab -l | grep -F "$LOG_ROTATION_SCRIPT"
    echo ""
    read -p "是否要删除旧任务并重新创建? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 删除旧任务
        crontab -l | grep -v "$LOG_ROTATION_SCRIPT" | crontab -
        echo "✓ 已删除旧任务"
    else
        echo "取消操作"
        exit 0
    fi
fi

# 添加新的 cron 任务
echo ""
echo "选择日志轮转频率:"
echo "1) 每小时检查一次（推荐）"
echo "2) 每6小时检查一次"
echo "3) 每天凌晨2点检查"
echo "4) 每天检查3次（凌晨2点、上午10点、下午6点）"
echo "5) 手动输入 cron 表达式"
echo ""
read -p "请选择 (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="每小时"
        ;;
    2)
        CRON_SCHEDULE="0 */6 * * *"
        DESCRIPTION="每6小时"
        ;;
    3)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="每天凌晨2点"
        ;;
    4)
        CRON_SCHEDULE="0 2,10,18 * * *"
        DESCRIPTION="每天3次（2点、10点、18点）"
        ;;
    5)
        read -p "请输入 cron 表达式: " CRON_SCHEDULE
        DESCRIPTION="自定义"
        ;;
    *)
        echo "无效选择，使用默认值：每小时"
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="每小时"
        ;;
esac

# 添加 cron 任务
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_CMD") | crontab -

echo ""
echo "=========================================="
echo "✓ 日志轮转设置完成"
echo "=========================================="
echo ""
echo "轮转频率: $DESCRIPTION ($CRON_SCHEDULE)"
echo "执行脚本: $LOG_ROTATION_SCRIPT"
echo "日志文件: $PROJECT_DIR/logs/log_rotation.log"
echo ""
echo "查看当前 cron 任务:"
echo "  crontab -l"
echo ""
echo "查看轮转日志:"
echo "  tail -f $PROJECT_DIR/logs/log_rotation.log"
echo ""
echo "手动执行一次轮转:"
echo "  cd $PROJECT_DIR && python3 $LOG_ROTATION_SCRIPT"
echo ""
echo "=========================================="


