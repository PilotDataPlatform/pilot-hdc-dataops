# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from typing import Optional
from typing import Union

from redis.asyncio.client import Redis


class Cache:
    """Manage cache entries."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def set(self, key: str, value: Union[str, bytes]) -> bool:
        """Set the value for the key."""

        return await self.redis.set(key, value)

    async def get(self, key: str) -> Optional[bytes]:
        """Return the value for the key or None if the key doesn't exist."""

        return await self.redis.get(key)

    async def delete(self, key: str) -> bool:
        """Delete the value for the key.

        Return true if the key existed before the removal.
        """

        return bool(await self.redis.delete(key))

    async def is_exist(self, key: str) -> bool:
        """Return true if the value for the key exists."""
        return bool(await self.redis.exists(key))
