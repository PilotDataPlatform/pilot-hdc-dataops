# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from pydantic import BaseModel

from dataops.components.schemas import BaseSchema


class TaskSchema(BaseSchema):
    """Schema for creating session job."""

    session_id: str
    label: str = 'Container'
    task_id: str = 'default_task'
    job_id: str
    source: str
    action: str
    target_status: str = 'INIT'
    code: str
    operator: str
    progress: int = 0
    payload: dict = {}


class TaskDeleteSchema(BaseSchema):
    """Schema for deleting session job."""

    session_id: str
    label: str = 'Container'
    job_id: str = '*'
    action: str = '*'
    code: str = '*'
    operator: str = '*'


class TaskUpdateSchema(BaseSchema):
    """Schema for updating session job."""

    session_id: str
    label: str = 'Container'
    job_id: str
    status: str
    add_payload: dict = {}
    progress: int = 0


class TaskResponseSchema(BaseModel):
    """Response schema for creating session job."""

    task_status: str = 'SUCCEED'


class TaskRetrieveResponseSchema(BaseModel):
    """Response schema for retrieving session job info."""

    task_info: list = []


class TaskUpdateResponseSchema(BaseModel):
    """Response schema for updating session job info."""

    task_info: dict = {}
