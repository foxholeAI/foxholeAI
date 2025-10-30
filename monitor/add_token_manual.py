#!/usr/bin/env python3
"""
手动添加 token 到 CSV 和 Redis
"""

import csv
import redis
import sys

# 配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY_PREFIX = "nlpmeme:token:"
REDIS_SET_KEY = "nlpmeme:tokens:all"
CSV_FILE = "tokens_data.csv"


def add_token(symbol, name, timestamp):
    """
    添加 token 到 CSV 和 Redis
    
    Args:
        symbol: token 符号
        name: token 名称
        timestamp: 时间戳
    """
    print(f"添加 token: {symbol} | {name}")
    print(f"时间戳: {timestamp}")
    print("-" * 60)
    
    # 1. 连接 Redis
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        redis_client.ping()
        print("✓ Redis 连接成功")
    except Exception as e:
        print(f"✗ Redis 连接失败: {e}")
        return False
    
    # 2. 添加到 Redis
    try:
        token_key_str = f"{symbol}:{name}"
        token_data = {
            "symbol": symbol,
            "name": name,
            "timestamp": timestamp
        }
        
        # 存储到 Redis Hash
        redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
        redis_client.hset(redis_key, mapping=token_data)
        
        # 添加到集合
        redis_client.sadd(REDIS_SET_KEY, token_key_str)
        
        print(f"✓ 已添加到 Redis: {redis_key}")
    except Exception as e:
        print(f"✗ Redis 添加失败: {e}")
        return False
    
    # 3. 添加到 CSV
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([symbol, name, timestamp])
        
        print(f"✓ 已追加到 CSV: {CSV_FILE}")
    except Exception as e:
        print(f"✗ CSV 添加失败: {e}")
        return False
    
    print("-" * 60)
    print("✓ 添加成功！")
    return True


if __name__ == '__main__':
    if len(sys.argv) == 4:
        # 命令行参数
        symbol = sys.argv[1]
        name = sys.argv[2]
        timestamp = sys.argv[3]
    else:
        # 默认值（从用户请求）
        symbol = "索拉拉"
        name = "索拉拉"
        timestamp = "2025-10-31T00:14:56.710423"
    
    add_token(symbol, name, timestamp)

