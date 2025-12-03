"""Rate limiting service using Redis."""
from typing import Dict, Tuple, Optional
from redis import asyncio as redis_async
from app.src.config import settings


class RateLimiterService:
    """Rate limiting service using Redis for distributed rate limiting."""
    
    def __init__(self, redis_client: Optional[redis_async.Redis] = None):
        """Initialize rate limiter with Redis client."""
        self._redis = redis_client or redis_async.from_url(
            settings.redis_url,
            password=settings.redis_password,
            decode_responses=True
        )
        self.limits: Dict[str, Tuple[int, int]] = {
            "conversation_message": (60, 60),  # 60 per minute
            "api_call": (settings.rate_limit_per_minute, 60),  # per minute
            "api_call_hourly": (settings.rate_limit_per_hour, 3600),  # per hour
            "lead_creation": (10, 60),  # 10 per minute
            "auth_login": (5, 60),  # 5 per minute
        }
    
    async def check_limit(
        self,
        key: str,
        limit_type: str = "api_call"
    ) -> Tuple[bool, int, int]:
        """
        Check if rate limit is exceeded.
        
        Args:
            key: Unique identifier (IP address, session_id, user_id, etc.)
            limit_type: Type of limit to check (e.g., "api_call", "conversation_message")
        
        Returns:
            Tuple of (allowed: bool, remaining: int, retry_after: int)
            - allowed: True if request is allowed, False if rate limited
            - remaining: Number of requests remaining in current window
            - retry_after: Seconds until the rate limit window resets (0 if allowed)
        """
        if limit_type not in self.limits:
            # Unknown limit type, allow request
            return True, 999, 0
        
        max_requests, window_seconds = self.limits[limit_type]
        redis_key = f"rate_limit:{limit_type}:{key}"
        
        try:
            # Get current count
            current = await self._redis.get(redis_key)
            count = int(current) if current else 0
            
            if count >= max_requests:
                # Rate limit exceeded
                # Get TTL (time remaining in seconds)
                ttl = await self._redis.ttl(redis_key)
                retry_after = max(ttl, 0) if ttl > 0 else window_seconds
                return False, 0, retry_after
            
            # Increment counter
            await self._redis.incr(redis_key)
            if count == 0:
                # First request in window, set expiration
                await self._redis.expire(redis_key, window_seconds)
            
            remaining = max(0, max_requests - count - 1)
            return True, remaining, 0
        
        except Exception as e:
            # If Redis fails, allow request (fail open)
            # In production, consider logging this
            return True, 999, 0
    
    async def get_limit_info(
        self,
        key: str,
        limit_type: str = "api_call"
    ) -> Dict[str, int]:
        """
        Get rate limit information without incrementing counter.
        
        Returns:
            Dictionary with limit information:
            - limit: Maximum requests allowed
            - remaining: Requests remaining
            - reset: Seconds until window resets
        """
        if limit_type not in self.limits:
            return {"limit": 999, "remaining": 999, "reset": 0}
        
        max_requests, window_seconds = self.limits[limit_type]
        redis_key = f"rate_limit:{limit_type}:{key}"
        
        try:
            current = await self._redis.get(redis_key)
            count = int(current) if current else 0
            ttl = await self._redis.ttl(redis_key)
            
            return {
                "limit": max_requests,
                "remaining": max(0, max_requests - count),
                "reset": max(0, ttl) if ttl > 0 else window_seconds
            }
        except Exception:
            # If Redis fails, return defaults
            return {"limit": max_requests, "remaining": max_requests, "reset": 0}
    
    async def reset_limit(
        self,
        key: str,
        limit_type: str = "api_call"
    ) -> bool:
        """Reset rate limit for a key (useful for testing or admin operations)."""
        redis_key = f"rate_limit:{limit_type}:{key}"
        try:
            await self._redis.delete(redis_key)
            return True
        except Exception:
            return False

