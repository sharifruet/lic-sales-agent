"""Redis client management utilities."""

from __future__ import annotations

from typing import AsyncGenerator, Optional

from redis.asyncio import Redis

from config.settings import settings


class RedisManager:
    """Lazy-initialised Redis client singleton."""

    def __init__(self) -> None:
        self._client: Optional[Redis] = None

    async def connect(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    async def ping(self) -> bool:
        client = await self.connect()
        try:
            return bool(await client.ping())
        except Exception:
            return False

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None


redis_manager = RedisManager()


async def get_redis() -> AsyncGenerator[Redis, None]:
    client = await redis_manager.connect()
    try:
        yield client
    finally:
        pass

