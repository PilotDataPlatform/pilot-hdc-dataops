# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import ast
from typing import Union

from dataops.components.task_stream.schemas import SSETaskStreamSchema
from dataops.components.task_stream.schemas import TaskStreamCreateSchema
from dataops.components.task_stream.schemas import TaskStreamRetrieveSchema
from dataops.logger import logger


class StreamParser:
    """Manages redis stream parsing."""

    def parse_file_status(self, results: list) -> list[TaskStreamCreateSchema]:
        """Parses file statuses in a stream for a respective session id."""
        status = []
        session_id = results[0][0].decode()
        for entry in results[0][1]:
            try:
                entry_id = entry[0].decode()
                entry_values = entry[1]
                redis_file_status = TaskStreamCreateSchema(
                    entry_id=entry_id,
                    session_id=session_id,
                    target_names=ast.literal_eval(entry_values[b'target_names'].decode()),
                    target_type=entry_values[b'target_type'].decode(),
                    container_code=entry_values[b'container_code'].decode(),
                    container_type=entry_values[b'container_type'].decode(),
                    action_type=entry_values[b'action_type'].decode(),
                    status=entry_values[b'status'].decode(),
                    job_id=entry_values[b'job_id'].decode(),
                )
                status.append(redis_file_status)
            except Exception:
                logger.exception(f'Failed to parse a file status entry with session ID {session_id}')
                continue
        return status

    def filter_parsed_status(
        self, file_statuses: list[TaskStreamCreateSchema], params: Union[TaskStreamRetrieveSchema, SSETaskStreamSchema]
    ) -> list[dict]:
        """Filters parsed file statuses."""
        filtered_statuses = []
        for file_status in file_statuses:
            if (
                (not params.container_code or file_status.container_code == params.container_code)
                and (not params.container_type or file_status.container_type == params.container_type)
                and (not params.action_type or file_status.action_type == params.action_type)
                and (not params.target_names or file_status.target_names == params.target_names)
                and (not params.job_id or file_status.job_id == params.job_id)
            ):
                filtered_statuses.append(file_status.to_payload())
        return filtered_statuses
