#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息格式化工具
将 WebSocket 消息格式化为 Telegram 友好的格式
"""

from typing import Dict, Optional
from datetime import datetime
import json


class MessageFormatter:
    """消息格式化器"""
    
    def __init__(self, use_emojis: bool = True, format_type: str = "markdown"):
        """
        初始化格式化器
        
        Args:
            use_emojis: 是否使用表情符号
            format_type: 格式类型 ("markdown", "html", "text")
        """
        self.use_emojis = use_emojis
        self.format_type = format_type
        
        # 表情符号映射
        self.emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
            "token": "🪙",
            "contract": "📝",
            "analysis": "🔍",
            "twitter": "🐦",
            "audit": "🛡️",
            "high_risk": "🔴",
            "medium_risk": "🟡",
            "low_risk": "🟢",
            "unknown": "⚪",
            "time": "🕐",
            "user": "👤",
        }
    
    def get_emoji(self, key: str) -> str:
        """获取表情符号"""
        if not self.use_emojis:
            return ""
        return self.emojis.get(key, "") + " "
    
    def format_message(self, data: Dict) -> Optional[str]:
        """
        格式化消息
        
        Args:
            data: WebSocket 消息数据
            
        Returns:
            格式化后的消息字符串，如果不需要转发则返回 None
        """
        log_type = data.get("log_type", "unknown")
        
        # 根据日志类型选择格式化方法
        formatters = {
            "raw_twitter_message": self._format_twitter_message,
            "token_info": self._format_token_info,
            "ai_analysis": self._format_ai_analysis,
            "audit_complete": self._format_audit_complete,
            "contract_found": self._format_contract_found,
            "server_info": self._format_server_info,
            "search_token": self._format_search_token,
            "heuristic_analysis": self._format_heuristic_analysis,
        }
        
        formatter = formatters.get(log_type)
        if formatter:
            return formatter(data)
        
        return None
    
    def _format_twitter_message(self, data: Dict) -> str:
        """格式化 Twitter 消息"""
        # 支持两种数据结构
        # 1. 新结构: data.message.data.twitterUser / data.message.data.status
        # 2. 旧结构: data.tweet.user / data.tweet
        
        message = data.get("message", {})
        message_data = message.get("data", {})
        
        # 尝试新结构
        if message_data:
            user = message_data.get("twitterUser", {})
            status = message_data.get("status", {})
            screen_name = user.get("screenName", "unknown")
            name = user.get("name", "unknown")
            text = status.get("text", "N/A")
        else:
            # 回退到旧结构
            tweet = data.get("tweet", {})
            user = tweet.get("user", {})
            screen_name = user.get("screen_name", "unknown")
            name = user.get("name", "unknown")
            text = tweet.get("text", "N/A")
        
        lines = [
            f"{self.get_emoji('twitter')}*新推文*",
            "",
            f"{self.get_emoji('user')}用户: @{screen_name} ({name})",
            f"{self.get_emoji('time')}时间: {self._format_timestamp(data.get('timestamp'))}",
            "",
            f"内容: {text[:500]}",  # 限制长度
        ]
        
        # 检测到的代币（可能在不同位置）
        detected_tokens = data.get("detected_tokens", [])
        if not detected_tokens and message_data:
            # 尝试从 changes 中提取
            changes = message_data.get("changes", {})
            if changes:
                detected_tokens = []  # 可以根据需要提取
        
        if detected_tokens:
            lines.append("")
            lines.append(f"{self.get_emoji('token')}检测到代币: {', '.join(f'${t}' for t in detected_tokens)}")
        
        return "\n".join(lines)
    
    def _format_token_info(self, data: Dict) -> str:
        """格式化代币信息"""
        # 支持多种数据结构
        # 1. data.token (简单结构)
        # 2. data.data.pairs[0] (DexScreener 结构)
        
        token = data.get("token", {})
        dex_data = data.get("data", {})
        
        # 如果是 DexScreener 格式
        if dex_data and "pairs" in dex_data:
            pairs = dex_data.get("pairs", [])
            if pairs:
                pair = pairs[0]
                base_token = pair.get("baseToken", {})
                symbol = base_token.get("symbol", "UNKNOWN")
                name = base_token.get("name", "N/A")
                address = base_token.get("address", "N/A")
                price_usd = pair.get("priceUsd", "N/A")
                liquidity_usd = pair.get("liquidity", {}).get("usd", 0)
                volume_24h = pair.get("volume", {}).get("h24", 0)
                dex_url = pair.get("url", "")
                
                lines = [
                    f"{self.get_emoji('token')}*代币信息: ${symbol}*",
                    "",
                    f"名称: {name}",
                    f"合约地址: `{address}`",
                    f"价格: ${price_usd}",
                    f"流动性: ${liquidity_usd:,.2f}" if isinstance(liquidity_usd, (int, float)) else f"流动性: ${liquidity_usd}",
                    f"24h 交易量: ${volume_24h:,.2f}" if isinstance(volume_24h, (int, float)) else f"24h 交易量: ${volume_24h}",
                ]
                
                if dex_url:
                    lines.append(f"链接: {dex_url}")
                
                return "\n".join(lines)
        
        # 简单格式
        symbol = token.get("symbol", "UNKNOWN")
        
        lines = [
            f"{self.get_emoji('token')}*代币信息: ${symbol}*",
            "",
            f"名称: {token.get('name', 'N/A')}",
            f"合约地址: `{token.get('address', 'N/A')}`",
        ]
        
        # 添加其他可用信息
        if token.get("decimals"):
            lines.append(f"精度: {token.get('decimals')}")
        
        if token.get("total_supply"):
            lines.append(f"总供应量: {token.get('total_supply')}")
        
        return "\n".join(lines)
    
    def _format_ai_analysis(self, data: Dict) -> str:
        """格式化 AI 分析结果"""
        analysis = data.get("analysis", {})
        token_symbol = data.get("token_symbol", "UNKNOWN")
        
        lines = [
            f"{self.get_emoji('analysis')}*AI 分析: ${token_symbol}*",
            "",
        ]
        
        # 风险等级
        risk_level = analysis.get("risk_level", "unknown").lower()
        risk_emoji = self.get_emoji(f"{risk_level}_risk")
        lines.append(f"风险等级: {risk_emoji}{risk_level.upper()}")
        
        # 置信度
        confidence = analysis.get("confidence", 0)
        lines.append(f"置信度: {confidence:.2%}")
        
        # 分析摘要
        summary = analysis.get("summary", "")
        if summary:
            lines.append("")
            lines.append(f"摘要: {summary[:300]}")
        
        # 关键发现
        findings = analysis.get("findings", [])
        if findings:
            lines.append("")
            lines.append("关键发现:")
            for finding in findings[:5]:  # 最多显示5条
                lines.append(f"  • {finding}")
        
        return "\n".join(lines)
    
    def _format_audit_complete(self, data: Dict) -> str:
        """格式化审计完成消息"""
        token = data.get("token", "UNKNOWN")
        status = data.get("status", "unknown")
        risk_level = data.get("risk_level", "unknown").lower()
        
        risk_emoji = self.get_emoji(f"{risk_level}_risk")
        
        lines = [
            f"{self.get_emoji('audit')}*审计完成: ${token}*",
            "",
            f"状态: {status}",
            f"风险等级: {risk_emoji}{risk_level.upper()}",
            f"{self.get_emoji('time')}完成时间: {self._format_timestamp(data.get('timestamp'))}",
        ]
        
        # 添加推荐的合约信息（如果有）
        recommended = data.get("recommended", {})
        if recommended:
            lines.append("")
            lines.append("推荐合约:")
            lines.append(f"  地址: `{recommended.get('token_address', 'N/A')}`")
            lines.append(f"  DEX: {recommended.get('dex', 'N/A')}")
            lines.append(f"  价格: ${recommended.get('price_usd', 'N/A')}")
            lines.append(f"  流动性: ${recommended.get('liquidity_usd', 0):,.2f}")
            
            dex_url = recommended.get("dex_url", "")
            if dex_url:
                lines.append(f"  链接: {dex_url}")
        
        return "\n".join(lines)
    
    def _format_contract_found(self, data: Dict) -> str:
        """格式化合约地址发现消息"""
        contract = data.get("contract_address", "UNKNOWN")
        token_symbol = data.get("token_symbol", "")
        confidence = data.get("confidence", 0)
        
        lines = [
            f"{self.get_emoji('contract')}*发现合约地址*",
            "",
        ]
        
        if token_symbol:
            lines.append(f"代币: ${token_symbol}")
        
        lines.append(f"合约地址: `{contract}`")
        lines.append(f"置信度: {confidence:.2%}")
        
        # 上下文
        context = data.get("context", "")
        if context:
            lines.append("")
            lines.append(f"上下文: {context[:200]}")
        
        return "\n".join(lines)
    
    def _format_server_info(self, data: Dict) -> str:
        """格式化服务器信息"""
        lines = [
            f"{self.get_emoji('info')}*服务器信息*",
            "",
            f"消息: {data.get('message', 'N/A')}",
            f"版本: {data.get('server_version', 'N/A')}",
            f"连接数: {data.get('connected_clients', 0)}",
        ]
        
        return "\n".join(lines)
    
    def _format_search_token(self, data: Dict) -> str:
        """格式化代币搜索结果"""
        token_symbol = data.get("token_symbol", "UNKNOWN")
        status = data.get("status", "unknown")
        total_pairs = data.get("total_pairs", 0)
        
        if status == "success" and total_pairs > 0:
            lines = [
                f"{self.get_emoji('token')}*发现代币: ${token_symbol}*",
                "",
                f"找到 {total_pairs} 个交易对",
                f"{self.get_emoji('time')}时间: {self._format_timestamp(data.get('timestamp'))}",
            ]
        else:
            lines = [
                f"{self.get_emoji('warning')}*代币搜索: ${token_symbol}*",
                "",
                f"未找到交易对",
            ]
        
        return "\n".join(lines)
    
    def _format_heuristic_analysis(self, data: Dict) -> str:
        """格式化启发式分析结果"""
        token_symbol = data.get("token_symbol", "UNKNOWN")
        total_contracts = data.get("total_contracts", 0)
        recommended = data.get("recommended_contract", {})
        
        if not recommended:
            return None
        
        address = recommended.get("address", "N/A")
        risk_score = recommended.get("risk_score", 0)
        risk_level = recommended.get("risk_level", "unknown")
        
        risk_emoji = self.get_emoji(f"{risk_level}_risk")
        
        lines = [
            f"{self.get_emoji('analysis')}*分析完成: ${token_symbol}*",
            "",
            f"找到 {total_contracts} 个合约",
            f"风险等级: {risk_emoji}{risk_level.upper()}",
            f"风险评分: {risk_score}/10",
            "",
            f"推荐合约: `{address[:8]}...{address[-6:]}`",
        ]
        
        return "\n".join(lines)
    
    def _format_timestamp(self, timestamp: Optional[str]) -> str:
        """格式化时间戳"""
        if not timestamp:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp
    
    def escape_markdown(self, text: str) -> str:
        """转义 Markdown 特殊字符"""
        if self.format_type != "markdown":
            return text
        
        # Telegram Markdown 需要转义的字符
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text

