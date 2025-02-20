"""
Redis cache configuration and utilities.
"""
from typing import Any, Optional
import json
import redis
from fastapi import HTTPException

# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PREFIX = "mcp:"
DEFAULT_EXPIRE = 3600  # 1 hour in seconds

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX_REQUESTS = 100  # requests per window

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def get_cache_key(*args: Any) -> str:
    """Generate cache key from arguments."""
    return REDIS_PREFIX + ":".join(str(arg) for arg in args)

async def get_cached_data(key: str) -> Optional[str]:
    """Get data from cache."""
    try:
        return redis_client.get(key)
    except redis.RedisError:
        return None

async def set_cached_data(key: str, data: Any, expire: int = DEFAULT_EXPIRE) -> bool:
    """Set data in cache."""
    try:
        return redis_client.setex(key, expire, json.dumps(data))
    except redis.RedisError:
        return False

async def delete_cached_data(key: str) -> bool:
    """Delete data from cache."""
    try:
        return bool(redis_client.delete(key))
    except redis.RedisError:
        return False

async def check_rate_limit(key: str) -> bool:
    """Check if rate limit is exceeded."""
    try:
        current = redis_client.get(key)
        if current is None:
            redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
            return True
        
        count = int(current)
        if count >= RATE_LIMIT_MAX_REQUESTS:
            return False
        
        redis_client.incr(key)
        return True
    except redis.RedisError:
        # If Redis is down, allow the request
        return True

def clear_cache_pattern(pattern: str) -> bool:
    """Clear all cache keys matching pattern."""
    try:
        keys = redis_client.keys(REDIS_PREFIX + pattern)
        if keys:
            return bool(redis_client.delete(*keys))
        return True
    except redis.RedisError:
        return False

# Cache decorators
def cache_response(expire: int = DEFAULT_EXPIRE):
    """Decorator to cache endpoint responses."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = get_cache_key(func.__name__, *args, *kwargs.values())
            
            # Try to get from cache
            cached = await get_cached_data(cache_key)
            if cached:
                return json.loads(cached)
            
            # Get fresh data
            result = await func(*args, **kwargs)
            
            # Cache the result
            await set_cached_data(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

def rate_limit(limit_key: str):
    """Decorator to apply rate limiting."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not await check_rate_limit(limit_key):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator