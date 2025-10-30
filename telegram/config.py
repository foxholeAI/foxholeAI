#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class TelegramConfig:
    """Telegram 配置类"""
    
    # Telegram Bot Token (从环境变量获取)
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Telegram Chat ID (可以是个人ID、群组ID或频道ID)
    # 支持多个 Chat ID，用逗号分隔
    CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")
    
    # WebSocket 服务器配置
    WS_HOST = os.getenv("WS_HOST", "localhost")
    WS_PORT = int(os.getenv("WS_PORT", "8765"))
    
    # 消息过滤配置
    # 转发哪些类型的消息
    FORWARD_MESSAGE_TYPES = [
        "raw_twitter_message",  # Twitter 原始消息
        "search_token",         # 代币搜索结果
        "token_info",           # 代币信息
        "heuristic_analysis",   # 启发式分析
        "ai_analysis",          # AI 分析结果
        "audit_complete",       # 审计完成
        "contract_found",       # 发现合约地址
    ]
    
    # 是否在消息中包含表情符号
    USE_EMOJIS = True
    
    # 消息格式
    MESSAGE_FORMAT = "markdown"  # 可选: "markdown", "html", "text"
    
    # 重连配置
    AUTO_RECONNECT = True
    MAX_RECONNECT_ATTEMPTS = 10
    RECONNECT_DELAY = 5  # 秒
    
    # 调试模式
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        """验证配置是否有效"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN 未设置")
        
        if not cls.CHAT_IDS or cls.CHAT_IDS == [""]:
            errors.append("TELEGRAM_CHAT_IDS 未设置")
        
        if errors:
            raise ValueError("配置错误:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    @classmethod
    def get_websocket_url(cls):
        """获取 WebSocket 连接 URL"""
        return f"ws://{cls.WS_HOST}:{cls.WS_PORT}"

