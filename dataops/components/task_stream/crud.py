# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import asyncio
import json
from time import time

from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from dataops.components.crud import RedisCRUD
from dataops.components.task_stream.parsing import StreamParser
from dataops.components.task_stream.schemas import SSETaskStreamSchema
from dataops.components.task_stream.schemas import TaskStreamCreateSchema
from dataops.components.task_stream.schemas import TaskStreamDeleteSchema
from dataops.components.task_stream.schemas import TaskStreamResponseSchema
from dataops.components.task_stream.schemas import TaskStreamRetrieveSchema
from dataops.config import get_settings
from dataops.logger import logger

settings = get_settings()


class StreamCRUD(StreamParser, RedisCRUD):
    """Manages file status events with Redis streams."""

    async def create_status(self, data: TaskStreamCreateSchema) -> TaskStreamResponseSchema:
        """Writes file status to streams."""
        stream_data = data.to_payload()
        stream_data.pop('entry_id')
        values = stream_data.copy()
        session_id = values['session_id']
        values.pop('session_id')
        values['target_names'] = str(values['target_names'])
        try:
            await self.streams_xadd(session_id, values, '*')
        except Exception:
            logger.error('An exception occurred while performing writing file status to streams.')
            raise

        return TaskStreamResponseSchema(stream_info=stream_data, total=1)

    async def get_status_with_sse(self, request: Request, params: SSETaskStreamSchema) -> EventSourceResponse:
        """Retrieve file status events over SSE."""

        async def event_generator() -> str:
            """Generate event from stream."""
            request_start_time = time()
            redis_stream_offset = '0'
            logger.info(f'Handling request for session {params.session_id}')
            while True:
                time_elapsed = time() - request_start_time
                timed_out = params.request_timeout and time_elapsed >= params.request_timeout
                disconnected = await request.is_disconnected()
                if disconnected or timed_out:
                    logger.info('Disconnected from client (via disconnect/timeout)')
                    break
                else:
                    try:
                        redis_results = await self.streams_xread(params.session_id, redis_stream_offset)
                    except Exception:
                        logger.error('An exception occurred while retrieving status from stream.')
                        raise
                    if redis_results:
                        file_statuses = self.parse_file_status(redis_results)
                        redis_stream_offset = file_statuses[
                            len(file_statuses) - 1
                        ].entry_id  # keep last entry ID as new offset
                        filtered_file_statuses = self.filter_parsed_status(file_statuses, params)
                        logger.info(f'Returning data from Redis for session {params.session_id}')
                        for file_status in filtered_file_statuses:
                            yield json.dumps(file_status)
                    await asyncio.sleep(1.0)

        return EventSourceResponse(event_generator(), ping=settings.SSE_PING_INTERVAL)

    async def get_status_without_sse(self, params: TaskStreamRetrieveSchema) -> TaskStreamResponseSchema:
        """Retrieve file status events without SSE."""
        filtered_file_statuses = []
        redis_results = await self.streams_xread(params.session_id, '0')
        if redis_results:
            file_statuses = self.parse_file_status(redis_results)
            filtered_file_statuses = self.filter_parsed_status(file_statuses, params)

        return TaskStreamResponseSchema(stream_info=filtered_file_statuses, total=len(filtered_file_statuses))

    async def delete_old_statuses(self, params: TaskStreamDeleteSchema) -> TaskStreamResponseSchema:
        """Delete a user's old file status events from Redis."""
        pattern = f'{params.user}*'
        redis_results = await self.streams_scan(0, pattern, 50)
        if not redis_results:
            logger.error(f'No streams found for user {params.user}')
        response_streams = []
        for stream in redis_results:
            stream = stream.decode('utf-8')
            response_streams.append(stream)
            logger.info(f'Attempting to delete stream {stream}')
            await self.delete_by_key(stream)
        return TaskStreamResponseSchema(stream_info=response_streams, total=len(response_streams))
