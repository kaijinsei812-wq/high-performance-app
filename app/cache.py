"""
Redis キャッシュユーティリティ
Redis未接続時はキャッシュなし（フォールバック）で動作する
"""
import os
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

_redis_client = None


def get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        _redis_client.ping()
        logger.info("✅ Redis接続成功")
        return _redis_client
    except Exception as e:
        logger.warning(f"⚠️ Redis未接続（フォールバックモード）: {e}")
        return None


def cache_get(key: str) -> Optional[Any]:
    r = get_redis()
    if r is None:
        return None
    try:
        value = r.get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = 60) -> bool:
    r = get_redis()
    if r is None:
        return False
    try:
        r.setex(key, ttl, json.dumps(value))
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    r = get_redis()
    if r is None:
        return False
    try:
        r.delete(key)
        return True
    except Exception:
        return False


def cache_delete_pattern(pattern: str) -> int:
    r = get_redis()
    if r is None:
        return 0
    try:
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
        return len(keys)
    except Exception:
        return 0
