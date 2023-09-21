# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Depends
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError

from dataops.config import Settings
from dataops.config import get_settings


class GetRedis:
    """Class to create Redis connection instance."""

    def __init__(self) -> None:
        self.instance = None

    async def __call__(self, settings: Settings = Depends(get_settings)) -> Redis:
        """Return an instance of Redis class."""

        if not self.instance:
            self.instance = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                socket_keepalive=True,
                retry_on_timeout=True,
                retry_on_error=[
                    ConnectionError,
                ],
            )
        return self.instance


get_redis = GetRedis()
