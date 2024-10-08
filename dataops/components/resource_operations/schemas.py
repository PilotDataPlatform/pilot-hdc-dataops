# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from enum import Enum
from enum import unique
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Extra

from dataops.components.schemas import BaseSchema
from dataops.components.schemas import EFileStatus


@unique
class ResourceType(str, Enum):
    """Base schema for defining resource types."""

    NAME_FOLDER = 'name_folder'
    FILE = 'file'
    FOLDER = 'folder'
    CONTAINER = 'container'


@unique
class ItemStatus(str, Enum):
    # the new enum type for file status
    # - REGISTERED means file is created by upload service
    #   but not complete yet. either in progress or fail.
    # - ACTIVE means file uploading is complete.
    # - ARCHIVED means the file has been deleted

    REGISTERED = 'REGISTERED'
    ACTIVE = 'ACTIVE'
    ARCHIVED = 'ARCHIVED'


class ResourceOperationTargetSchema(BaseSchema):
    """Schema of resource operation target id for session job creation."""

    id: str

    class Config:
        extra = Extra.ignore


class ResourceOperationPayloadSchema(BaseSchema):
    """Schema of payload for resource operation request."""

    request_info: Optional[dict]
    targets: List[ResourceOperationTargetSchema]
    source: str
    destination: Optional[str]


class ResourceOperationSchema(BaseSchema):
    """Schema of resource operation request for session job creation."""

    session_id: str
    task_id: str = 'default_task_id'
    job_id: str = 'default_job_id'
    payload: ResourceOperationPayloadSchema
    operator: str
    operation: str
    project_code: str
    status = str = EFileStatus.RUNNING.name
    progress = int = 0


class FileStatusSchema(BaseSchema):
    """Schema of file status update for Redis streams."""

    session_id: str
    target_names: list[str]
    target_type: str
    container_code: str
    container_type: str
    action_type: str
    status: str = EFileStatus.RUNNING.name
    job_id: UUID


class ResourceOperationResponseSchema(BaseModel):
    """Schema of resource operation request response."""

    operation_info: List[FileStatusSchema]
