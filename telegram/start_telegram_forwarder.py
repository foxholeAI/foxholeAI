#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 转发器启动脚本
"""

import sys
import os
import asyncio

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from webhook_forwarder import main

if __name__ == "__main__":
    print("正在启动 Telegram 转发器...")
    asyncio.run(main())

