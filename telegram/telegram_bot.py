#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot 核心类
处理与 Telegram API 的交互
"""

import requests
import json
from typing import List, Optional, Dict
from datetime import datetime


class TelegramBot:
    """Telegram Bot 类"""
    
    def __init__(self, bot_token: str, debug: bool = False):
        """
        初始化 Telegram Bot
        
        Args:
            bot_token: Telegram Bot Token
            debug: 是否启用调试模式
        """
        self.bot_token = bot_token
        self.api_base_url = f"https://api.telegram.org/bot{bot_token}"
        self.debug = debug
        self.session = requests.Session()
        
    def send_message(self, chat_id: str, text: str, 
                     parse_mode: Optional[str] = None,
                     disable_web_page_preview: bool = True) -> Dict:
        """
        发送消息到指定的 Chat
        
        Args:
            chat_id: Chat ID
            text: 消息文本
            parse_mode: 解析模式 ("Markdown", "HTML", 或 None)
            disable_web_page_preview: 是否禁用网页预览
            
        Returns:
            API 响应字典
        """
        url = f"{self.api_base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if self.debug:
                print(f"[TelegramBot] 消息已发送到 {chat_id}")
                
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"发送消息失败: {e}"
            if self.debug:
                print(f"[TelegramBot] {error_msg}")
            return {"ok": False, "error": error_msg}
    
    def send_to_multiple(self, chat_ids: List[str], text: str,
                         parse_mode: Optional[str] = None) -> List[Dict]:
        """
        发送消息到多个 Chat
        
        Args:
            chat_ids: Chat ID 列表
            text: 消息文本
            parse_mode: 解析模式
            
        Returns:
            API 响应列表
        """
        results = []
        for chat_id in chat_ids:
            if chat_id.strip():  # 跳过空字符串
                result = self.send_message(chat_id.strip(), text, parse_mode)
                results.append(result)
        return results
    
    def get_me(self) -> Dict:
        """
        获取 Bot 信息
        
        Returns:
            Bot 信息字典
        """
        url = f"{self.api_base_url}/getMe"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}
    
    def test_connection(self) -> bool:
        """
        测试与 Telegram API 的连接
        
        Returns:
            连接是否成功
        """
        result = self.get_me()
        if result.get("ok"):
            bot_info = result.get("result", {})
            print(f"[TelegramBot] 连接成功")
            print(f"  Bot 名称: {bot_info.get('first_name')}")
            print(f"  用户名: @{bot_info.get('username')}")
            print(f"  Bot ID: {bot_info.get('id')}")
            return True
        else:
            print(f"[TelegramBot] 连接失败: {result.get('error')}")
            return False
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()

