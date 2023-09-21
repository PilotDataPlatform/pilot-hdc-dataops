# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Depends
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from dataops.components.health.resource_checkers import DBChecker
from dataops.components.health.resource_checkers import RedisChecker
from dataops.dependencies import get_db_session
from dataops.dependencies import get_redis


def get_db_checker(db_session: AsyncSession = Depends(get_db_session)) -> DBChecker:
    """Return an instance of DBChecker as a dependency."""

    return DBChecker(db_session)


def get_redis_checker(redis: Redis = Depends(get_redis)) -> RedisChecker:
    """Return an instance of RedisChecker as a dependency."""

    return RedisChecker(redis)
