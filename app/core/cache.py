import redis.asyncio as redis # Use async Redis client
from app.core.config import REDIS_URL

# Global Redis client instance
redis_client: redis.Redis = None

async def connect_to_redis():
    """Establishes connection to Redis."""
    global redis_client
    if not redis_client:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        try:
            # Ping Redis to ensure connection is established
            await redis_client.ping()
            print("Successfully connected to Redis!")
        except Exception as e:
            print(f"Could not connect to Redis: {e}")
            redis_client = None # Set to None if connection fails

async def close_redis_connection():
    """Closes the Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("Redis connection closed.")
        redis_client = None

def get_redis_client() -> redis.Redis:
    """Returns the Redis client instance."""
    if not redis_client:
        raise RuntimeError("Redis client not initialized. Call connect_to_redis() first.")
    return redis_client