# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from aioredis.client import Redis
from fastapi import Depends

from dataops.components.resource_lock.cache import ResourceLockerCache
from dataops.dependencies import get_redis


def get_resource_lock_cache(
    redis: Redis = Depends(get_redis),
) -> ResourceLockerCache:
    """Return resource locker as a dependency."""
    resource_locker = ResourceLockerCache(redis)
    return resource_locker
