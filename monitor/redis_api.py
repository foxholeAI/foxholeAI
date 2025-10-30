#!/usr/bin/env python3
"""
Redis Token API 服务
提供 RESTful API 访问 Redis 中的 token 数据
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_KEY_PREFIX,
    REDIS_SET_KEY
)

app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 连接 Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    try:
        redis_client.ping()
        return jsonify({
            "status": "ok",
            "redis": "connected"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "redis": "disconnected",
            "error": str(e)
        }), 500


@app.route('/api/tokens/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        total = redis_client.scard(REDIS_SET_KEY)
        return jsonify({
            "status": "success",
            "data": {
                "total_tokens": total,
                "redis_host": REDIS_HOST,
                "redis_port": REDIS_PORT
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/tokens', methods=['GET'])
def get_tokens():
    """
    获取 token 列表
    参数:
        - limit: 限制返回数量（默认 50）
        - offset: 偏移量（默认 0）
        - search: 搜索关键词
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        search = request.args.get('search', '', type=str)
        
        # 获取所有 token keys
        all_token_keys = list(redis_client.smembers(REDIS_SET_KEY))
        
        # 搜索过滤
        if search:
            all_token_keys = [
                key for key in all_token_keys 
                if search.lower() in key.lower()
            ]
        
        # 排序
        all_token_keys.sort()
        
        # 分页
        total = len(all_token_keys)
        token_keys = all_token_keys[offset:offset + limit]
        
        # 获取详细信息
        tokens = []
        for token_key_str in token_keys:
            redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
            token_data = redis_client.hgetall(redis_key)
            if token_data:
                tokens.append(token_data)
        
        return jsonify({
            "status": "success",
            "data": {
                "tokens": tokens,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total
                }
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/tokens/search', methods=['GET'])
def search_tokens():
    """
    搜索 token
    参数:
        - q: 搜索关键词（必需）
        - limit: 限制返回数量（默认 50）
    """
    try:
        keyword = request.args.get('q', '', type=str)
        limit = request.args.get('limit', 50, type=int)
        
        if not keyword:
            return jsonify({
                "status": "error",
                "message": "搜索关键词不能为空"
            }), 400
        
        # 获取所有 token keys
        all_token_keys = redis_client.smembers(REDIS_SET_KEY)
        
        # 搜索
        results = []
        for token_key_str in all_token_keys:
            if keyword.lower() in token_key_str.lower():
                redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
                token_data = redis_client.hgetall(redis_key)
                if token_data:
                    results.append(token_data)
                    if len(results) >= limit:
                        break
        
        return jsonify({
            "status": "success",
            "data": {
                "keyword": keyword,
                "count": len(results),
                "tokens": results
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/tokens/<path:token_key>', methods=['GET'])
def get_token(token_key):
    """
    获取特定 token 的详细信息
    参数:
        - token_key: token key（格式：symbol:name）
    """
    try:
        redis_key = f"{REDIS_KEY_PREFIX}{token_key}"
        token_data = redis_client.hgetall(redis_key)
        
        if not token_data:
            return jsonify({
                "status": "error",
                "message": f"Token 不存在: {token_key}"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": token_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/tokens/symbol/<symbol>', methods=['GET'])
def get_tokens_by_symbol(symbol):
    """
    根据 symbol 获取所有匹配的 token
    参数:
        - symbol: token 符号
    """
    try:
        all_token_keys = redis_client.smembers(REDIS_SET_KEY)
        
        results = []
        for token_key_str in all_token_keys:
            if token_key_str.startswith(f"{symbol}:"):
                redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
                token_data = redis_client.hgetall(redis_key)
                if token_data:
                    results.append(token_data)
        
        if not results:
            return jsonify({
                "status": "error",
                "message": f"未找到符号为 {symbol} 的 token"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": {
                "symbol": symbol,
                "count": len(results),
                "tokens": results
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/tokens/latest', methods=['GET'])
def get_latest_tokens():
    """
    获取最新添加的 token
    参数:
        - limit: 限制返回数量（默认 20）
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # 获取所有 token
        all_token_keys = list(redis_client.smembers(REDIS_SET_KEY))
        
        # 获取所有 token 的时间戳
        tokens_with_time = []
        for token_key_str in all_token_keys:
            redis_key = f"{REDIS_KEY_PREFIX}{token_key_str}"
            token_data = redis_client.hgetall(redis_key)
            if token_data:
                tokens_with_time.append(token_data)
        
        # 按时间戳排序（最新的在前）
        tokens_with_time.sort(
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        # 取前 limit 个
        latest_tokens = tokens_with_time[:limit]
        
        return jsonify({
            "status": "success",
            "data": {
                "count": len(latest_tokens),
                "tokens": latest_tokens
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """API 文档"""
    return jsonify({
        "name": "NLP Meme Token Redis API",
        "version": "1.0.0",
        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "健康检查"
            },
            "stats": {
                "method": "GET",
                "path": "/api/tokens/stats",
                "description": "获取统计信息"
            },
            "list": {
                "method": "GET",
                "path": "/api/tokens",
                "description": "获取 token 列表",
                "params": {
                    "limit": "限制返回数量（默认 50）",
                    "offset": "偏移量（默认 0）",
                    "search": "搜索关键词"
                }
            },
            "search": {
                "method": "GET",
                "path": "/api/tokens/search",
                "description": "搜索 token",
                "params": {
                    "q": "搜索关键词（必需）",
                    "limit": "限制返回数量（默认 50）"
                }
            },
            "get": {
                "method": "GET",
                "path": "/api/tokens/<token_key>",
                "description": "获取特定 token 详情",
                "example": "/api/tokens/KITKAT:Justice For KitKat"
            },
            "by_symbol": {
                "method": "GET",
                "path": "/api/tokens/symbol/<symbol>",
                "description": "根据 symbol 获取所有匹配的 token",
                "example": "/api/tokens/symbol/KITKAT"
            },
            "latest": {
                "method": "GET",
                "path": "/api/tokens/latest",
                "description": "获取最新添加的 token",
                "params": {
                    "limit": "限制返回数量（默认 20）"
                }
            }
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Redis Token API 服务启动")
    print("=" * 60)
    print(f"Redis: {REDIS_HOST}:{REDIS_PORT} (DB: {REDIS_DB})")
    print("API 地址: http://0.0.0.0:5000")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  GET  /                          - API 文档")
    print("  GET  /health                    - 健康检查")
    print("  GET  /api/tokens/stats          - 统计信息")
    print("  GET  /api/tokens                - Token 列表")
    print("  GET  /api/tokens/search?q=...   - 搜索")
    print("  GET  /api/tokens/<key>          - 获取详情")
    print("  GET  /api/tokens/symbol/<sym>   - 按符号查询")
    print("  GET  /api/tokens/latest         - 最新 Token")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

