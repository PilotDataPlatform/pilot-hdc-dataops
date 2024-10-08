# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import APIRouter
from fastapi import Depends

from dataops.components.authorization import Authorization
from dataops.components.resource_operations.crud.dispatcher import Dispatcher
from dataops.components.resource_operations.dependencies import get_resource_ops_auth
from dataops.components.resource_operations.dependencies import get_resource_ops_dispatcher
from dataops.components.resource_operations.schemas import ResourceOperationResponseSchema
from dataops.components.resource_operations.schemas import ResourceOperationSchema
from dataops.logger import logger

router = APIRouter(prefix='/files/actions', tags=['Resource Operations'])


@router.post(
    '/',
    response_model=ResourceOperationResponseSchema,
    summary='API to invoke resource operation request',
    status_code=202,
)
async def invoke_dispatcher(
    body: ResourceOperationSchema,
    dispatcher: Dispatcher = Depends(get_resource_ops_dispatcher),
    current_identity: Authorization = Depends(get_resource_ops_auth),
) -> ResourceOperationResponseSchema:
    """Invoke dispatcher for incoming resource operation request."""

    logger.info('Dispatching resource operation request')
    token = await current_identity.jwt_required()
    operation_request = await dispatcher.execute(body, token)
    return operation_request
