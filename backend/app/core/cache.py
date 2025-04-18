import redis.asyncio as redis
import json
import logging
from typing import Any, Optional, Union
from .config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache connection handler"""
    
    _redis = None
    
    @classmethod
    async def connect(cls):
        """Connect to Redis cache"""
        try:
            logger.info(f"Connecting to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            password = settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None
            cls._redis = await redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=password,
                decode_responses=True
            )
            # Test connection
            await cls._redis.ping()
            logger.info("Successfully connected to Redis")
            return cls._redis
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from Redis cache"""
        if cls._redis:
            await cls._redis.close()
            logger.info("Disconnected from Redis")
    
    @classmethod
    async def get_redis(cls):
        """Get Redis instance"""
        if cls._redis is None:
            await cls.connect()
        return cls._redis
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """Get value from cache"""
        redis_client = await cls.get_redis()
        data = await redis_client.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None
    
    @classmethod
    async def set(cls, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration time (default: 1 hour)"""
        redis_client = await cls.get_redis()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await redis_client.set(key, value, ex=expire)
    
    @classmethod
    async def delete(cls, key: str) -> int:
        """Delete value from cache"""
        redis_client = await cls.get_redis()
        return await redis_client.delete(key)
    
    @classmethod
    async def exists(cls, key: str) -> bool:
        """Check if key exists in cache"""
        redis_client = await cls.get_redis()
        return await redis_client.exists(key) > 0
    
    @classmethod
    async def get_hash(cls, name: str, key: str) -> Optional[str]:
        """Get value from hash"""
        redis_client = await cls.get_redis()
        return await redis_client.hget(name, key)
    
    @classmethod
    async def set_hash(cls, name: str, key: str, value: str) -> int:
        """Set value in hash"""
        redis_client = await cls.get_redis()
        return await redis_client.hset(name, key, value)
    
    @classmethod
    async def increment(cls, key: str, amount: int = 1) -> int:
        """Increment value in cache"""
        redis_client = await cls.get_redis()
        return await redis_client.incrby(key, amount)

# Redis cache instance
cache = RedisCache() 