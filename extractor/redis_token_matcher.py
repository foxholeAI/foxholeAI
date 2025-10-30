#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Token 匹配器
在消息中快速匹配 Redis 中已保存的 token_symbol
"""

import re
import redis
from typing import List, Dict, Set, Tuple
from datetime import datetime


class RedisTokenMatcher:
    """Redis Token 匹配器 - 用正则快速匹配消息中的已知 token"""
    
    def __init__(self, redis_host='127.0.0.1', redis_port=6379, redis_db=0,
                 redis_set_key='nlpmeme:tokens:all', redis_key_prefix='nlpmeme:token:'):
        """
        初始化匹配器
        
        Args:
            redis_host: Redis 主机
            redis_port: Redis 端口
            redis_db: Redis 数据库编号
            redis_set_key: 存储所有 token 的集合 key
            redis_key_prefix: Token 详情的 key 前缀
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_set_key = redis_set_key
        self.redis_key_prefix = redis_key_prefix
        
        # 连接 Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.redis_client.ping()
            print(f"[RedisTokenMatcher] Connected to Redis: {redis_host}:{redis_port}")
        except Exception as e:
            print(f"[RedisTokenMatcher] Failed to connect to Redis: {e}")
            self.redis_client = None
        
        # Token 符号缓存（用于快速匹配）
        self.token_symbols_cache: Set[str] = set()
        self.token_details_cache: Dict[str, Dict] = {}
        
        # 上次刷新缓存的时间
        self.last_cache_refresh = None
        self.cache_refresh_interval = 300  # 5分钟刷新一次缓存
        
        # 加载初始数据
        self._refresh_cache()
    
    def _refresh_cache(self) -> bool:
        """
        从 Redis 刷新本地缓存
        
        Returns:
            是否刷新成功
        """
        if not self.redis_client:
            return False
        
        try:
            print("[RedisTokenMatcher] Refreshing token cache from Redis...")
            
            # 获取所有 token keys
            token_keys = self.redis_client.smembers(self.redis_set_key)
            
            # 提取 symbol
            new_symbols = set()
            new_details = {}
            
            for token_key_str in token_keys:
                # token_key_str 格式: "symbol:name"
                parts = token_key_str.split(':', 1)
                if len(parts) >= 1:
                    symbol = parts[0]
                    # 对英文转大写，中文保持原样
                    if symbol.encode('utf-8').isalpha() and symbol.isascii():
                        symbol_normalized = symbol.upper()
                    else:
                        symbol_normalized = symbol
                    
                    new_symbols.add(symbol_normalized)
                    
                    # 获取详细信息
                    redis_key = f"{self.redis_key_prefix}{token_key_str}"
                    token_data = self.redis_client.hgetall(redis_key)
                    if token_data:
                        new_details[symbol_normalized] = token_data
            
            self.token_symbols_cache = new_symbols
            self.token_details_cache = new_details
            self.last_cache_refresh = datetime.now()
            
            print(f"[RedisTokenMatcher] Cache refreshed: {len(self.token_symbols_cache)} tokens loaded")
            return True
            
        except Exception as e:
            print(f"[RedisTokenMatcher] Failed to refresh cache: {e}")
            return False
    
    def _should_refresh_cache(self) -> bool:
        """
        判断是否需要刷新缓存
        
        Returns:
            是否需要刷新
        """
        if not self.last_cache_refresh:
            return True
        
        elapsed = (datetime.now() - self.last_cache_refresh).total_seconds()
        return elapsed >= self.cache_refresh_interval
    
    def match_tokens_in_text(self, text: str, auto_refresh=True) -> List[Dict]:
        """
        在文本中匹配 Redis 中已知的 token
        
        Args:
            text: 要匹配的文本
            auto_refresh: 是否自动刷新缓存
            
        Returns:
            匹配到的 token 列表
        """
        if not text:
            return []
        
        # 检查是否需要刷新缓存
        if auto_refresh and self._should_refresh_cache():
            self._refresh_cache()
        
        if not self.token_symbols_cache:
            return []
        
        matched_tokens = []
        
        # 方法1: 匹配 $SYMBOL 格式（支持中文和英文）
        dollar_pattern = re.compile(r'\$([A-Za-z0-9\u4e00-\u9fff]+)', re.IGNORECASE)
        dollar_matches = dollar_pattern.findall(text)
        
        for match in dollar_matches:
            # 对英文符号转大写，中文保持原样
            if match.encode('utf-8').isalpha() and match.isascii():
                symbol_normalized = match.upper()
            else:
                symbol_normalized = match
            
            # 检查缓存时也要考虑原文
            if symbol_normalized in self.token_symbols_cache or match in self.token_symbols_cache:
                token_info = {
                    'symbol': match,  # 保持原样（中文不变）
                    'matched_text': f'${match}',
                    'match_type': 'dollar_sign',
                    'confidence': 0.9,  # $SYMBOL 格式置信度高
                    'source': 'redis_matcher'
                }
                
                # 添加详细信息（尝试两种形式）
                if symbol_normalized in self.token_details_cache:
                    token_info.update(self.token_details_cache[symbol_normalized])
                elif match in self.token_details_cache:
                    token_info.update(self.token_details_cache[match])
                
                matched_tokens.append(token_info)
        
        # 方法2: 匹配纯英文大写单词（需要更严格的条件）
        word_pattern = re.compile(r'\b([A-Z][A-Z0-9]{1,10})\b')
        word_matches = word_pattern.findall(text)
        
        # 停用词（避免误匹配常见大写词）
        stopwords = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 
                    'CAN', 'WAS', 'GET', 'GOT', 'NEW', 'NOW', 'OUT', 'DAY',
                    'WHO', 'WHY', 'HOW', 'WHAT', 'WHEN', 'WHERE'}
        
        for match in word_matches:
            symbol_upper = match.upper()
            
            # 跳过停用词和已匹配的
            if symbol_upper in stopwords:
                continue
            if any(t['symbol'] == symbol_upper for t in matched_tokens):
                continue
            
            if symbol_upper in self.token_symbols_cache:
                # 检查上下文（周围是否有加密货币相关词汇）
                context_score = self._calculate_context_score(text, match)
                
                # 只有上下文分数够高才添加（避免误报）
                if context_score >= 0.3:
                    token_info = {
                        'symbol': symbol_upper,
                        'matched_text': match,
                        'match_type': 'word',
                        'confidence': 0.6 + context_score * 0.3,  # 根据上下文调整置信度
                        'context_score': context_score,
                        'source': 'redis_matcher'
                    }
                    
                    # 添加详细信息
                    if symbol_upper in self.token_details_cache:
                        token_info.update(self.token_details_cache[symbol_upper])
                    
                    matched_tokens.append(token_info)
        
        # 方法3: 匹配中文 token（直接匹配，不需要 $ 符号）
        # 遍历所有已知的中文 token，看是否在文本中出现
        for symbol in self.token_symbols_cache:
            # 判断是否为中文 token（包含中文字符）
            if re.search(r'[\u4e00-\u9fff]', symbol):
                # 跳过已匹配的
                if any(t['symbol'] == symbol for t in matched_tokens):
                    continue
                
                # 检查是否在文本中
                if symbol in text:
                    # 计算上下文分数
                    context_score = self._calculate_context_score(text, symbol)
                    
                    # 中文 token 降低阈值（0.0），允许无上下文匹配
                    # 注意：这会增加误报率，建议在生产环境调整为 0.1 或 0.2
                    if context_score >= 0.0:
                        token_info = {
                            'symbol': symbol,
                            'matched_text': symbol,
                            'match_type': 'chinese_word',
                            'confidence': 0.7 + context_score * 0.2,  # 基础置信度 0.7
                            'context_score': context_score,
                            'source': 'redis_matcher'
                        }
                        
                        # 添加详细信息
                        if symbol in self.token_details_cache:
                            token_info.update(self.token_details_cache[symbol])
                        
                        matched_tokens.append(token_info)
        
        return matched_tokens
    
    def _calculate_context_score(self, text: str, token: str, window=50) -> float:
        """
        计算 token 周围的上下文相关度（支持中英文）
        
        Args:
            text: 完整文本
            token: 要检查的 token
            window: 上下文窗口大小（字符数）
            
        Returns:
            上下文分数 (0-1)
        """
        # 加密货币相关关键词（英文 + 中文）
        crypto_keywords = {
            # 英文关键词
            'crypto', 'token', 'coin', 'blockchain', 'defi', 'nft', 'meme',
            'launch', 'pump', 'moon', 'buy', 'sell', 'trade', 'dex', 'swap',
            'contract', 'address', 'ca', 'launched', '$',
            # 中文关键词
            '代币', '币', '区块链', '加密', '发布', '上线', '启动', '购买',
            '买入', '卖出', '交易', '合约', '地址', '登月', 'pump', 'moon',
            '冲', '涨', '暴涨', '飞', '起飞', '新币', '项目', '发行',
            'DexScreener', 'dex', 'pancakeswap'
        }
        
        # 找到 token 在文本中的位置
        text_lower = text.lower()
        token_lower = token.lower()
        
        try:
            pos = text_lower.index(token_lower)
            
            # 提取上下文
            start = max(0, pos - window)
            end = min(len(text), pos + len(token) + window)
            context = text_lower[start:end]
            
            # 计算关键词密度
            keyword_count = sum(1 for kw in crypto_keywords if kw in context)
            
            # 归一化分数
            score = min(1.0, keyword_count / 3.0)
            
            return score
            
        except ValueError:
            return 0.0
    
    def get_token_details(self, symbol: str) -> Dict:
        """
        获取 token 的详细信息
        
        Args:
            symbol: Token 符号
            
        Returns:
            Token 详细信息字典
        """
        symbol_upper = symbol.upper()
        
        # 先检查缓存
        if symbol_upper in self.token_details_cache:
            return self.token_details_cache[symbol_upper]
        
        # 缓存中没有，尝试从 Redis 获取
        if not self.redis_client:
            return {}
        
        try:
            # 查找所有匹配的 token keys
            all_keys = self.redis_client.smembers(self.redis_set_key)
            
            for token_key_str in all_keys:
                if token_key_str.startswith(f"{symbol_upper}:"):
                    redis_key = f"{self.redis_key_prefix}{token_key_str}"
                    token_data = self.redis_client.hgetall(redis_key)
                    if token_data:
                        return token_data
            
            return {}
            
        except Exception as e:
            print(f"[RedisTokenMatcher] Error getting token details: {e}")
            return {}
    
    def force_refresh(self):
        """强制刷新缓存"""
        self._refresh_cache()
    
    def get_cache_stats(self) -> Dict:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_tokens': len(self.token_symbols_cache),
            'last_refresh': self.last_cache_refresh.isoformat() if self.last_cache_refresh else None,
            'cache_age_seconds': (datetime.now() - self.last_cache_refresh).total_seconds() if self.last_cache_refresh else None,
            'redis_connected': self.redis_client is not None
        }


if __name__ == '__main__':
    """测试模块"""
    
    # 创建匹配器
    matcher = RedisTokenMatcher()
    
    # 测试文本
    test_texts = [
        "Just bought $KITKAT! Going to the moon! 🚀",
        "New token launch: $BTC is pumping",
        "Check out this MEME coin, it's amazing!",
        "KITKAT token just launched on DexScreener",
        "The weather is nice today"
    ]
    
    print("\n" + "="*70)
    print("Testing Redis Token Matcher")
    print("="*70)
    
    for text in test_texts:
        print(f"\nText: {text}")
        matches = matcher.match_tokens_in_text(text)
        
        if matches:
            print(f"✓ Found {len(matches)} match(es):")
            for match in matches:
                print(f"  - {match['symbol']} ({match['match_type']}, confidence: {match['confidence']:.2f})")
        else:
            print("✗ No matches found")
    
    # 显示缓存统计
    print("\n" + "="*70)
    print("Cache Stats:")
    print("="*70)
    stats = matcher.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

