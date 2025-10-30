#!/usr/bin/env python3
"""
Redis Token 查询脚本
查询和显示 Redis 中存储的 token 数据
"""

import redis
import json
from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_KEY_PREFIX,
    REDIS_SET_KEY
)


def connect_redis():
    """连接 Redis"""
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        client.ping()
        return client
    except Exception as e:
        print(f"✗ Redis 连接失败: {e}")
        return None


def show_stats(redis_client):
    """显示统计信息"""
    total = redis_client.scard(REDIS_SET_KEY)
    print("=" * 60)
    print("Redis Token 数据统计")
    print("=" * 60)
    print(f"总 Token 数量: {total}")
    print("=" * 60)


def list_all_tokens(redis_client, limit=None):
    """列出所有 token"""
    token_keys = redis_client.smembers(REDIS_SET_KEY)
    
    if limit:
        token_keys = list(token_keys)[:limit]
    
    print(f"\nToken 列表 (显示 {len(token_keys)} 条):")
    print("-" * 60)
    
    for i, token_key_str in enumerate(token_keys, 1):
        # 获取详细信息
        redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
        token_data = redis_client.hgetall(redis_key)
        
        if token_data:
            print(f"{i}. {token_data['symbol']} | {token_data['name']}")
            print(f"   时间: {token_data['timestamp']}")
        else:
            print(f"{i}. {token_key_str} (数据缺失)")


def search_token(redis_client, keyword):
    """搜索 token"""
    token_keys = redis_client.smembers(REDIS_SET_KEY)
    
    results = []
    for token_key_str in token_keys:
        if keyword.lower() in token_key_str.lower():
            redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
            token_data = redis_client.hgetall(redis_key)
            if token_data:
                results.append(token_data)
    
    print(f"\n搜索结果 (关键词: '{keyword}'):")
    print("-" * 60)
    
    if not results:
        print("未找到匹配的 token")
    else:
        for i, token_data in enumerate(results, 1):
            print(f"{i}. {token_data['symbol']} | {token_data['name']}")
            print(f"   时间: {token_data['timestamp']}")


def get_token_detail(redis_client, symbol_or_key):
    """获取特定 token 的详细信息"""
    # 尝试直接作为 key 查询
    redis_key = f"{REDIS_KEY_PREFIX}{symbol_or_key}"
    token_data = redis_client.hgetall(redis_key)
    
    if not token_data:
        # 尝试搜索
        token_keys = redis_client.smembers(REDIS_SET_KEY)
        for token_key_str in token_keys:
            if symbol_or_key.lower() in token_key_str.lower():
                redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
                token_data = redis_client.hgetall(redis_key)
                if token_data:
                    break
    
    if token_data:
        print(f"\nToken 详细信息:")
        print("-" * 60)
        print(f"符号: {token_data['symbol']}")
        print(f"名称: {token_data['name']}")
        print(f"时间: {token_data['timestamp']}")
    else:
        print(f"未找到 token: {symbol_or_key}")


def export_to_json(redis_client, output_file="tokens_export.json"):
    """导出所有 token 到 JSON 文件"""
    token_keys = redis_client.smembers(REDIS_SET_KEY)
    
    tokens = []
    for token_key_str in token_keys:
        redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
        token_data = redis_client.hgetall(redis_key)
        if token_data:
            tokens.append(token_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 已导出 {len(tokens)} 个 token 到 {output_file}")


def main():
    """主函数"""
    import sys
    
    redis_client = connect_redis()
    if not redis_client:
        return
    
    if len(sys.argv) < 2:
        # 默认显示统计和前20个
        show_stats(redis_client)
        list_all_tokens(redis_client, limit=20)
        print("\n使用方法:")
        print("  python3 query_redis_tokens.py stats       # 显示统计")
        print("  python3 query_redis_tokens.py list [n]    # 列出所有/前n个 token")
        print("  python3 query_redis_tokens.py search <关键词>  # 搜索 token")
        print("  python3 query_redis_tokens.py get <符号>      # 获取详细信息")
        print("  python3 query_redis_tokens.py export      # 导出到 JSON")
    
    elif sys.argv[1] == "stats":
        show_stats(redis_client)
    
    elif sys.argv[1] == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
        show_stats(redis_client)
        list_all_tokens(redis_client, limit=limit)
    
    elif sys.argv[1] == "search":
        if len(sys.argv) < 3:
            print("请提供搜索关键词")
        else:
            search_token(redis_client, sys.argv[2])
    
    elif sys.argv[1] == "get":
        if len(sys.argv) < 3:
            print("请提供 token 符号或 key")
        else:
            get_token_detail(redis_client, sys.argv[2])
    
    elif sys.argv[1] == "export":
        output = sys.argv[2] if len(sys.argv) > 2 else "tokens_export.json"
        export_to_json(redis_client, output)
    
    else:
        print(f"未知命令: {sys.argv[1]}")


if __name__ == "__main__":
    main()

