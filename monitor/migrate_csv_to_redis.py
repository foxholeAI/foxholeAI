#!/usr/bin/env python3
"""
CSV 数据迁移到 Redis 脚本
将 tokens_data.csv 中的数据导入到 Redis
"""

import csv
import redis
from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_KEY_PREFIX,
    REDIS_SET_KEY,
    CSV_FILE
)


def migrate_csv_to_redis():
    """将 CSV 数据迁移到 Redis"""
    
    # 连接 Redis
    print(f"连接 Redis: {REDIS_HOST}:{REDIS_PORT} (DB: {REDIS_DB})")
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        redis_client.ping()
        print("✓ Redis 连接成功\n")
    except Exception as e:
        print(f"✗ Redis 连接失败: {e}")
        return
    
    # 读取 CSV 文件
    print(f"读取 CSV 文件: {CSV_FILE}")
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # 跳过表头
            rows = list(reader)
        print(f"✓ 读取到 {len(rows)} 条记录\n")
    except FileNotFoundError:
        print(f"✗ CSV 文件不存在: {CSV_FILE}")
        return
    except Exception as e:
        print(f"✗ 读取 CSV 失败: {e}")
        return
    
    # 迁移数据
    print("开始迁移数据到 Redis...")
    migrated_count = 0
    error_count = 0
    
    for row in rows:
        if len(row) < 3:
            error_count += 1
            continue
        
        symbol, name, timestamp = row[0], row[1], row[2]
        token_key_str = f"{symbol}:{name}"
        
        try:
            # 存储到 Redis Hash
            redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
            token_data = {
                "symbol": symbol,
                "name": name,
                "timestamp": timestamp
            }
            redis_client.hset(redis_key, mapping=token_data)
            
            # 添加到集合
            redis_client.sadd(REDIS_SET_KEY, token_key_str)
            
            migrated_count += 1
            
            if migrated_count % 10 == 0:
                print(f"  已迁移: {migrated_count}/{len(rows)}")
        
        except Exception as e:
            print(f"  ✗ 迁移失败: {symbol}:{name} - {e}")
            error_count += 1
    
    print(f"\n迁移完成!")
    print(f"  成功: {migrated_count} 条")
    print(f"  失败: {error_count} 条")
    print(f"  总计: {len(rows)} 条")
    
    # 验证 Redis 数据
    print(f"\n验证 Redis 数据:")
    total_in_redis = redis_client.scard(REDIS_SET_KEY)
    print(f"  Redis 中的 token 总数: {total_in_redis}")


def clear_redis_data():
    """清空 Redis 中的 token 数据（慎用！）"""
    print("警告: 此操作将清空 Redis 中的所有 token 数据！")
    confirm = input("确认清空？ (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    
    # 删除集合
    redis_client.delete(REDIS_SET_KEY)
    
    # 删除所有 hash keys
    pattern = f"{REDIS_KEY_PREFIX}*"
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
    
    print("✓ Redis 数据已清空")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_redis_data()
    else:
        migrate_csv_to_redis()

