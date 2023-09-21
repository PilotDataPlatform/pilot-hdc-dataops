# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from aioredis.client import Redis
from fastapi import Depends
from fastapi import Request

from dataops.components.authorization import Authorization
from dataops.components.resource_operations.crud.dispatcher import Dispatcher
from dataops.dependencies import get_redis
from dataops.services.metadata import MetadataService
from dataops.services.metadata import get_metadata_service
from dataops.services.queue import QueueService
from dataops.services.queue import get_queue_service


def get_resource_ops_dispatcher(
    metadata_client: MetadataService = Depends(get_metadata_service),
    queue_client: QueueService = Depends(get_queue_service),
    redis: Redis = Depends(get_redis),
) -> Dispatcher:
    """Return resource operation dispatcher as a dependency."""
    dispatcher = Dispatcher(metadata_client, queue_client, redis)
    return dispatcher


async def get_resource_ops_auth(request: Request) -> Authorization:
    """Return authorization object as a dependency."""
    authorize = Authorization(request)
    return authorize
