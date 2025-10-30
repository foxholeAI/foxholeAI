#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket 到 Telegram 的消息转发器
从 WebSocket 服务器接收消息并转发到 Telegram
"""

import asyncio
import websockets
import json
import signal
import sys
from datetime import datetime
from typing import Set, Optional

from telegram_bot import TelegramBot
from message_formatter import MessageFormatter
from config import TelegramConfig


class WebSocketToTelegramForwarder:
    """WebSocket 到 Telegram 转发器"""
    
    def __init__(self, config: TelegramConfig):
        """
        初始化转发器
        
        Args:
            config: Telegram 配置对象
        """
        self.config = config
        self.bot = TelegramBot(config.BOT_TOKEN, debug=config.DEBUG)
        self.formatter = MessageFormatter(
            use_emojis=config.USE_EMOJIS,
            format_type=config.MESSAGE_FORMAT
        )
        self.ws_url = config.get_websocket_url()
        self.running = False
        self.websocket = None
        self.reconnect_attempts = 0
        
        # 统计信息
        self.stats = {
            "messages_received": 0,
            "messages_forwarded": 0,
            "errors": 0,
            "start_time": None,
        }
    
    async def connect_and_forward(self):
        """连接到 WebSocket 并开始转发消息"""
        self.running = True
        self.stats["start_time"] = datetime.now()
        
        print("=" * 70)
        print("Telegram WebSocket 转发器")
        print("=" * 70)
        print(f"WebSocket URL: {self.ws_url}")
        print(f"Telegram Bot: {self.config.BOT_TOKEN[:10]}...")
        print(f"目标 Chat IDs: {', '.join(self.config.CHAT_IDS)}")
        print(f"转发消息类型: {', '.join(self.config.FORWARD_MESSAGE_TYPES)}")
        print("=" * 70)
        print()
        
        # 测试 Telegram 连接
        if not self.bot.test_connection():
            print("[Forwarder] Telegram 连接测试失败，请检查 BOT_TOKEN")
            return
        
        print()
        
        while self.running:
            try:
                print(f"[Forwarder] 正在连接到 WebSocket: {self.ws_url}")
                
                async with websockets.connect(self.ws_url) as websocket:
                    self.websocket = websocket
                    self.reconnect_attempts = 0
                    print(f"[Forwarder] WebSocket 已连接")
                    
                    # 发送启动通知到 Telegram
                    await self._send_startup_notification()
                    
                    # 接收并转发消息
                    async for message in websocket:
                        await self._handle_message(message)
                        
            except websockets.exceptions.ConnectionClosed:
                print(f"[Forwarder] WebSocket 连接已关闭")
                if self.running and self.config.AUTO_RECONNECT:
                    await self._handle_reconnect()
                else:
                    break
                    
            except Exception as e:
                print(f"[Forwarder] 错误: {e}")
                self.stats["errors"] += 1
                if self.running and self.config.AUTO_RECONNECT:
                    await self._handle_reconnect()
                else:
                    break
        
        print("[Forwarder] 转发器已停止")
        await self._send_shutdown_notification()
    
    async def _handle_message(self, message: str):
        """
        处理接收到的 WebSocket 消息
        
        Args:
            message: WebSocket 消息字符串
        """
        self.stats["messages_received"] += 1
        
        try:
            # 解析 JSON
            data = json.loads(message)
            log_type = data.get("log_type", "")
            
            if self.config.DEBUG:
                print(f"[Forwarder] 收到消息: {log_type}")
            
            # 检查是否需要转发此类型的消息
            if log_type not in self.config.FORWARD_MESSAGE_TYPES:
                return
            
            # 格式化消息
            formatted_message = self.formatter.format_message(data)
            if not formatted_message:
                return
            
            # 发送到 Telegram
            parse_mode = "Markdown" if self.config.MESSAGE_FORMAT == "markdown" else None
            if self.config.MESSAGE_FORMAT == "html":
                parse_mode = "HTML"
            
            results = self.bot.send_to_multiple(
                self.config.CHAT_IDS,
                formatted_message,
                parse_mode=parse_mode
            )
            
            # 检查发送结果
            success_count = sum(1 for r in results if r.get("ok", False))
            if success_count > 0:
                self.stats["messages_forwarded"] += 1
                if self.config.DEBUG:
                    print(f"[Forwarder] 消息已转发到 {success_count}/{len(results)} 个 Chat")
            else:
                self.stats["errors"] += 1
                print(f"[Forwarder] 消息转发失败: {results}")
                
        except json.JSONDecodeError as e:
            print(f"[Forwarder] JSON 解析错误: {e}")
            self.stats["errors"] += 1
        except Exception as e:
            print(f"[Forwarder] 处理消息时出错: {e}")
            self.stats["errors"] += 1
    
    async def _handle_reconnect(self):
        """处理重连逻辑"""
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts > self.config.MAX_RECONNECT_ATTEMPTS:
            print(f"[Forwarder] 达到最大重连次数 ({self.config.MAX_RECONNECT_ATTEMPTS})，停止重连")
            self.running = False
            return
        
        delay = self.config.RECONNECT_DELAY * self.reconnect_attempts
        print(f"[Forwarder] {delay} 秒后尝试重连... (尝试 {self.reconnect_attempts}/{self.config.MAX_RECONNECT_ATTEMPTS})")
        await asyncio.sleep(delay)
    
    async def _send_startup_notification(self):
        """发送启动通知"""
        message = (
            f"🚀 *Telegram 转发器已启动*\n"
            f"\n"
            f"WebSocket: `{self.ws_url}`\n"
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"\n"
            f"开始监听消息..."
        )
        
        self.bot.send_to_multiple(
            self.config.CHAT_IDS,
            message,
            parse_mode="Markdown"
        )
    
    async def _send_shutdown_notification(self):
        """发送关闭通知"""
        uptime = datetime.now() - self.stats["start_time"] if self.stats["start_time"] else None
        uptime_str = str(uptime).split('.')[0] if uptime else "N/A"
        
        message = (
            f"🛑 *Telegram 转发器已停止*\n"
            f"\n"
            f"运行时间: {uptime_str}\n"
            f"接收消息: {self.stats['messages_received']}\n"
            f"转发消息: {self.stats['messages_forwarded']}\n"
            f"错误次数: {self.stats['errors']}\n"
            f"\n"
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        self.bot.send_to_multiple(
            self.config.CHAT_IDS,
            message,
            parse_mode="Markdown"
        )
    
    def stop(self):
        """停止转发器"""
        print("\n[Forwarder] 正在停止转发器...")
        self.running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())
    
    def print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 70)
        print("统计信息")
        print("=" * 70)
        print(f"运行时间: {datetime.now() - self.stats['start_time'] if self.stats['start_time'] else 'N/A'}")
        print(f"接收消息数: {self.stats['messages_received']}")
        print(f"转发消息数: {self.stats['messages_forwarded']}")
        print(f"错误次数: {self.stats['errors']}")
        print("=" * 70)


async def main():
    """主函数"""
    # 验证配置
    try:
        TelegramConfig.validate()
    except ValueError as e:
        print(f"配置错误: {e}")
        print("\n请设置以下环境变量:")
        print("  - TELEGRAM_BOT_TOKEN: Telegram Bot Token")
        print("  - TELEGRAM_CHAT_IDS: 目标 Chat ID(多个用逗号分隔)")
        print("\n示例:")
        print("  export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("  export TELEGRAM_CHAT_IDS='123456789,-100123456789'")
        return
    
    # 创建转发器
    forwarder = WebSocketToTelegramForwarder(TelegramConfig)
    
    # 设置信号处理
    def signal_handler(sig, frame):
        print("\n[Main] 收到中断信号")
        forwarder.stop()
        forwarder.print_stats()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动转发器
    try:
        await forwarder.connect_and_forward()
    except KeyboardInterrupt:
        pass
    finally:
        forwarder.print_stats()


if __name__ == "__main__":
    asyncio.run(main())

