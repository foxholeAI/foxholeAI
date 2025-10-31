#!/bin/bash
# 手动执行日志轮转

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
python3 "$SCRIPT_DIR/log_rotation.py"


