#!/bin/bash
# 清理旧的日志备份文件

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DAYS=${1:-30}  # 默认清理 30 天前的文件

echo "=========================================="
echo "日志备份清理工具"
echo "=========================================="
echo ""
echo "项目目录: $PROJECT_DIR"
echo "清理天数: $DAYS 天前的备份"
echo ""

# 查找旧备份文件
echo "正在查找旧备份文件..."
echo ""

# ws.json 备份
WS_BACKUPS=$(find "$PROJECT_DIR/data" -name "ws.json.*" -mtime +$DAYS 2>/dev/null)
WS_COUNT=$(echo "$WS_BACKUPS" | grep -v '^$' | wc -l)

# 日志备份
LOG_BACKUPS=$(find "$PROJECT_DIR/logs" -name "*.log.*" -mtime +$DAYS 2>/dev/null)
LOG_COUNT=$(echo "$LOG_BACKUPS" | grep -v '^$' | wc -l)

TOTAL_COUNT=$((WS_COUNT + LOG_COUNT))

if [ $TOTAL_COUNT -eq 0 ]; then
    echo "✓ 没有找到需要清理的旧备份文件"
    exit 0
fi

echo "找到 $TOTAL_COUNT 个旧备份文件:"
echo ""

if [ $WS_COUNT -gt 0 ]; then
    echo "ws.json 备份 ($WS_COUNT 个):"
    echo "$WS_BACKUPS" | while read file; do
        if [ -n "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            echo "  - $(basename $file) ($size)"
        fi
    done
    echo ""
fi

if [ $LOG_COUNT -gt 0 ]; then
    echo "日志备份 ($LOG_COUNT 个):"
    echo "$LOG_BACKUPS" | while read file; do
        if [ -n "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            echo "  - $(basename $file) ($size)"
        fi
    done
    echo ""
fi

# 计算总大小
TOTAL_SIZE=$(du -ch $(echo "$WS_BACKUPS $LOG_BACKUPS") 2>/dev/null | tail -1 | cut -f1)
echo "总大小: $TOTAL_SIZE"
echo ""

# 确认删除
read -p "是否删除这些文件? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消操作"
    exit 0
fi

echo ""
echo "正在删除文件..."

# 删除 ws.json 备份
if [ $WS_COUNT -gt 0 ]; then
    find "$PROJECT_DIR/data" -name "ws.json.*" -mtime +$DAYS -delete
    echo "✓ 已删除 $WS_COUNT 个 ws.json 备份"
fi

# 删除日志备份
if [ $LOG_COUNT -gt 0 ]; then
    find "$PROJECT_DIR/logs" -name "*.log.*" -mtime +$DAYS -delete
    echo "✓ 已删除 $LOG_COUNT 个日志备份"
fi

echo ""
echo "=========================================="
echo "清理完成！释放空间: $TOTAL_SIZE"
echo "=========================================="


