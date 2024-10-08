# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import Response

from dataops.components.health.dependencies import get_db_checker
from dataops.components.health.dependencies import get_redis_checker
from dataops.components.health.resource_checkers import DBChecker
from dataops.components.health.resource_checkers import RedisChecker
from dataops.logger import logger

router = APIRouter(prefix='/health', tags=['Health'])


@router.get('/', summary='Healthcheck if all service dependencies are online.')
async def get_health_status(
    db_checker: DBChecker = Depends(get_db_checker), redis_checker: RedisChecker = Depends(get_redis_checker)
) -> Response:
    """Return response that represents status of the database and redis connections."""

    logger.info('Checking if database is online.')
    is_online_db = await db_checker.is_online()
    logger.info(f'Received is_online status "{is_online_db}".')

    logger.info('Checking if redis is online.')
    is_online_redis = await redis_checker.is_online()
    logger.info(f'Received is_online status "{is_online_redis}".')

    response = Response(status_code=204)
    if not all([is_online_db, is_online_redis]):
        response = Response(status_code=503)

    return response
