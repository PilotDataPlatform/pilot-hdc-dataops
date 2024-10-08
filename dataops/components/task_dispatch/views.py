# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import APIRouter
from fastapi import Depends

from dataops.components.task_dispatch.crud import SessionJobCRUD
from dataops.components.task_dispatch.dependencies import get_session_job_crud
from dataops.components.task_dispatch.schemas import TaskDeleteSchema
from dataops.components.task_dispatch.schemas import TaskResponseSchema
from dataops.components.task_dispatch.schemas import TaskRetrieveResponseSchema
from dataops.components.task_dispatch.schemas import TaskSchema
from dataops.components.task_dispatch.schemas import TaskUpdateResponseSchema
from dataops.components.task_dispatch.schemas import TaskUpdateSchema

router = APIRouter(prefix='/tasks', tags=['Task Dispatch'])


@router.post('/', response_model=TaskResponseSchema, summary='Asynchronized Task Management API, Create a new task')
async def post(data: TaskSchema, session_crud: SessionJobCRUD = Depends(get_session_job_crud)) -> TaskResponseSchema:
    """Create new job if job_id does not exist for a given session."""
    await session_crud.check_job_id(data)
    await session_crud.set_job(data)
    return TaskResponseSchema()


@router.get(
    '/', response_model=TaskRetrieveResponseSchema, summary='Asynchronized Task Management API, Get task information'
)
async def get(
    session_id,
    label='Container',
    job_id='*',
    code='*',
    action='*',
    operator='*',
    session_crud: SessionJobCRUD = Depends(get_session_job_crud),
) -> TaskRetrieveResponseSchema:
    """Retrieve job info for a given session."""
    fetched = await session_crud.get_job(session_id, label, job_id, code, action, operator, sorting=True)
    response = TaskRetrieveResponseSchema(task_info=fetched)
    return response


@router.delete('/', response_model=TaskResponseSchema, summary='Asynchronized Task Management API, Delete tasks')
async def delete(
    data: TaskDeleteSchema, session_crud: SessionJobCRUD = Depends(get_session_job_crud)
) -> TaskResponseSchema:
    """Delete job for a given session."""
    await session_crud.delete_job(data)
    return TaskResponseSchema()


@router.put('/', summary='Asynchronized Task Management API, Update tasks', response_model=TaskUpdateResponseSchema)
async def put(
    data: TaskUpdateSchema, session_crud: SessionJobCRUD = Depends(get_session_job_crud)
) -> TaskUpdateResponseSchema:
    """Update job info for a given session."""
    job = await session_crud.update_job(
        data.session_id, '*', '*', '*', data.label, data.job_id, data.add_payload, data.status, data.progress
    )
    response = TaskUpdateResponseSchema(task_info=job)
    return response
