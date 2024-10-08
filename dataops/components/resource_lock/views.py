# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import APIRouter
from fastapi import Depends

from dataops.components.exceptions import AlreadyExists
from dataops.components.exceptions import BadRequest
from dataops.components.resource_lock.cache import ResourceLockerCache
from dataops.components.resource_lock.dependencies import get_resource_lock_cache
from dataops.components.resource_lock.schemas import ResourceLockBulkCreateSchema
from dataops.components.resource_lock.schemas import ResourceLockBulkResponseSchema
from dataops.components.resource_lock.schemas import ResourceLockCreateSchema
from dataops.components.resource_lock.schemas import ResourceLockResponseSchema
from dataops.logger import logger

router = APIRouter(prefix='/resource/lock', tags=['Resource Locking'])


@router.post('/', response_model=ResourceLockResponseSchema, summary='Create a new lock')
async def lock(
    body: ResourceLockCreateSchema, resource_locker: ResourceLockerCache = Depends(get_resource_lock_cache)
) -> ResourceLockResponseSchema:
    """Create operation lock on a respective resource via a resource key."""
    response = await resource_locker.perform_rw_lock(body.resource_key, body.operation)
    if not response.status:
        raise AlreadyExists()
    return response


@router.post('/bulk', response_model=ResourceLockBulkResponseSchema, summary='Create multiple locks')
async def bulk_lock(
    body: ResourceLockBulkCreateSchema, resource_locker: ResourceLockerCache = Depends(get_resource_lock_cache)
) -> ResourceLockBulkResponseSchema:
    """Bulk create operation locks on respective resources via resource keys."""
    response = await resource_locker.perform_bulk_lock(body.resource_keys, body.operation)
    if not response.is_successful():
        raise AlreadyExists()
    return response


@router.delete('/', response_model=ResourceLockResponseSchema, summary='Remove a lock')
async def unlock(
    body: ResourceLockCreateSchema, resource_locker: ResourceLockerCache = Depends(get_resource_lock_cache)
) -> ResourceLockResponseSchema:
    """Remove operation lock on a respective resource via a resource key."""
    response = await resource_locker.perform_rw_unlock(body.resource_key, body.operation)
    if not response.status:
        raise BadRequest()
    return response


@router.delete('/bulk', response_model=ResourceLockBulkResponseSchema, summary='Remove multiple locks')
async def bulk_unlock(
    body: ResourceLockBulkCreateSchema, resource_locker: ResourceLockerCache = Depends(get_resource_lock_cache)
) -> ResourceLockBulkResponseSchema:
    """Bulk remove operation locks on respective resources via resource keys."""
    response = await resource_locker.perform_bulk_unlock(body.resource_keys, body.operation)
    if not response.is_successful():
        raise BadRequest()
    return response


@router.get('/', response_model=ResourceLockResponseSchema, summary='Check a lock status')
async def check_lock(
    resource_key: str, resource_locker: ResourceLockerCache = Depends(get_resource_lock_cache)
) -> ResourceLockResponseSchema:
    """Retrieve status of lock via a resource key."""
    response = await resource_locker.check_lock_status(resource_key)
    return response
