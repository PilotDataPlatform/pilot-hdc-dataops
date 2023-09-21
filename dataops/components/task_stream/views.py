# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from dataops.components.exceptions import BadRequest
from dataops.components.task_stream.crud import StreamCRUD
from dataops.components.task_stream.dependencies import get_auth_manager
from dataops.components.task_stream.dependencies import get_streams_crud
from dataops.components.task_stream.schemas import SSETaskStreamSchema
from dataops.components.task_stream.schemas import TaskStreamCreateSchema
from dataops.components.task_stream.schemas import TaskStreamDeleteSchema
from dataops.components.task_stream.schemas import TaskStreamResponseSchema
from dataops.components.task_stream.schemas import TaskStreamRetrieveSchema
from dataops.config import get_settings
from dataops.dependencies.auth import AuthManager

settings = get_settings()
logger = LoggerFactory(
    __name__,
    level_default=settings.LOG_LEVEL_DEFAULT,
    level_file=settings.LOG_LEVEL_FILE,
    level_stdout=settings.LOG_LEVEL_STDOUT,
    level_stderr=settings.LOG_LEVEL_STDERR,
).get_logger()

router = APIRouter(prefix='/task-stream', tags=['Task Streaming'])


@router.post('/', response_model=TaskStreamResponseSchema, summary='Write a new file status event to Redis')
async def write_status(
    data: TaskStreamCreateSchema, stream_crud: StreamCRUD = Depends(get_streams_crud)
) -> TaskStreamResponseSchema:
    """Write a new file status event to Redis."""
    status = await stream_crud.create_status(data)
    return status


@router.get('/', summary='Stream file status events over SSE')
async def get_status_with_sse(
    request: Request,
    params: SSETaskStreamSchema = Depends(SSETaskStreamSchema),
    stream_crud: StreamCRUD = Depends(get_streams_crud),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> EventSourceResponse:
    """Stream file status events over SSE."""
    current_identity = await auth_manager.get_current_identity(request)
    if not params.session_id.startswith(current_identity['username']):
        raise BadRequest()
    return await stream_crud.get_status_with_sse(request, params)


@router.get('/static/', response_model=TaskStreamResponseSchema, summary='Get file status events without SSE streaming')
async def get_static_status(
    params: TaskStreamRetrieveSchema = Depends(TaskStreamRetrieveSchema),
    stream_crud: StreamCRUD = Depends(get_streams_crud),
) -> TaskStreamResponseSchema:
    """Get file status events without SSE streaming."""
    return await stream_crud.get_status_without_sse(params)


@router.delete(
    '/', response_model=TaskStreamResponseSchema, summary='Delete a user\'s old file status events from Redis'
)
async def delete_status(
    params: TaskStreamDeleteSchema = Depends(TaskStreamDeleteSchema),
    stream_crud: StreamCRUD = Depends(get_streams_crud),
) -> TaskStreamResponseSchema:
    """Delete a user's old file status events from Redis."""
    return await stream_crud.delete_old_statuses(params)
