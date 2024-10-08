# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import re
from typing import Optional
from typing import Union
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import validator

from dataops.components.schemas import BaseSchema
from dataops.components.schemas import EActionType
from dataops.components.schemas import EFileStatus


class TaskStreamRetrieveSchema(BaseModel):
    """Schema for retrieving file status."""

    session_id: str
    container_code: Optional[str]
    container_type: Optional[str]
    action_type: Optional[str]
    target_names: Optional[str]
    job_id: Optional[UUID]


class SSETaskStreamSchema(TaskStreamRetrieveSchema):
    """Schema for stream SSE timeout."""

    request_timeout: Optional[int]


class TaskStreamCreateSchema(BaseSchema):
    """Schema for writing file status."""

    session_id: str
    target_names: list[str]
    target_type: str
    container_code: str
    container_type: str
    action_type: str
    status: str
    job_id: Optional[UUID] = uuid4()
    entry_id: str = None

    @validator('session_id')
    def session_id_valid(cls, v):
        """Validates session id."""
        pattern = r'.*-[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}'
        if not re.search(pattern, v):
            raise ValueError(f'Invalid session_id {v}')
        return v

    @validator('target_type')
    def target_type_valid(cls, v, values):
        """Validates target type."""
        if v not in ['file', 'folder', 'batch']:
            raise ValueError(f'Invalid target_type {v}')
        if v != 'batch' and len(values['target_names']) > 1:
            raise ValueError(f'Too many target_names for target_type {v}')
        return v

    @validator('container_type')
    def container_type_valid(cls, v):
        """Validates container type."""
        if v not in ['project', 'dataset']:
            raise ValueError(f'Invalid container_type {v}')
        return v

    @validator('action_type')
    def action_type_valid(cls, v):
        """Validates action type."""
        if v not in [action_type.name for action_type in EActionType]:
            raise ValueError(f'Invalid action_type {v}')
        return v

    @validator('status')
    def status_valid(cls, v):
        """Validates status."""
        if v not in [status.name for status in EFileStatus]:
            raise ValueError(f'Invalid status {v}')
        return v


class TaskStreamDeleteSchema(BaseModel):
    """Schema for deleting file status."""

    user: str


class TaskStreamResponseSchema(BaseModel):
    """Response schema for writing and retrieving file status."""

    total: int = 0
    stream_info: Union[dict, list, list[dict]] = {}
