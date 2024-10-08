# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from aioredis.client import Redis
from fastapi import Depends

from dataops.components.task_stream.crud import StreamCRUD
from dataops.config import Settings
from dataops.config import get_settings
from dataops.dependencies import get_redis
from dataops.dependencies.auth import AuthManager


def get_streams_crud(redis: Redis = Depends(get_redis)) -> StreamCRUD:
    """Returns an instance of StreamCRUD as a dependency."""
    return StreamCRUD(redis)


async def get_auth_manager(settings: Settings = Depends(get_settings)) -> AuthManager:
    """Returns an instance of AuthManager as a dependency."""
    return AuthManager(settings)
