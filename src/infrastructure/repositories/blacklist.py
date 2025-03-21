from datetime import timedelta

from fastapi import Depends
from redis.asyncio import Redis

from src.db.redis import get_redis
from src.domain.repositories import AbstractBlacklistRepository


class RedisBlacklistRepository(AbstractBlacklistRepository):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get_value(self, key: str) -> str | None:
        """
        Проверяет, есть ли значение в Redis.
        :param key: Ключ в Redis
        :return: Значение по ключу, если оно есть, иначе None
        """
        value = await self._redis.get(name=key)
        return value

    async def set_value(self, key: str, value: str, exp: timedelta | int | None = None) -> None:
        """
        Устанавливает одиночное значение в Redis с возможным временем жизни.
        :param key: Ключ
        :param value: Значение
        :param exp: Время жизни (если передано)
        """

        if exp:
            exp = timedelta(minutes=exp)
            await self._redis.set(name=key, value=value, ex=int(exp.total_seconds()))
        else:
            await self._redis.set(name=key, value=value)

    async def set_many_values(self, values: dict[str, str], exp: timedelta | None = None):
        """
        Устанавливает несколько значений в Redis.
        :param values: Словарь {ключ: значение}
        :param exp: Время жизни (если передано, будет установлено для всех)
        """
        async with self._redis.pipeline() as pipe:
            await pipe.mset(values)
            if exp:
                exp = timedelta(minutes=exp)
                for key in values.keys():
                    await pipe.expire(name=key, time=int(exp.total_seconds()))
            await pipe.execute()


def get_blacklist_repository(redis_client: Redis = Depends(get_redis)):
    black_list_service = RedisBlacklistRepository(redis=redis_client)
    return black_list_service
