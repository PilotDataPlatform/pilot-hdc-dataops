# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from aioredis.client import Redis
from common import LoggerFactory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from dataops.config import get_settings

settings = get_settings()
logger = LoggerFactory(
    __name__,
    level_default=settings.LOG_LEVEL_DEFAULT,
    level_file=settings.LOG_LEVEL_FILE,
    level_stdout=settings.LOG_LEVEL_STDOUT,
    level_stderr=settings.LOG_LEVEL_STDERR,
).get_logger()


class DBChecker:
    """Perform checks against the database."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def is_online(self) -> bool:
        """Check if database is online."""

        try:
            cursor = await self.session.execute(select(1))
            result = cursor.scalars().first()
            return result == 1
        except Exception:
            logger.exception('An exception occurred while performing database query.')

        return False


class RedisChecker:
    """Perform checks against redis."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def is_online(self) -> bool:
        """Check if redis is online."""

        try:
            if await self.redis.ping():
                return True
        except Exception:
            logger.exception('An exception occurred while pinging redis.')

        return False
