# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import json
import time
from typing import Optional
from typing import Union

from dataops.components.crud import RedisCRUD
from dataops.components.exceptions import AlreadyExists
from dataops.components.exceptions import NotFound
from dataops.components.schemas import BaseSchema
from dataops.components.task_dispatch.sorting import sort_by_update_time
from dataops.logger import logger


class SessionJobCRUD(RedisCRUD):
    """CRUD for managing jobs for a user session, which are stored in Redis using RedisCRUD."""

    async def get_job(
        self,
        session_id: str,
        label: str,
        job_id: str,
        code: str,
        action: str,
        operator: str,
        sorting: Optional[bool] = False,
    ) -> list:
        """Get job records in Redis for a respective session."""
        key = 'dataaction:{}:{}:{}:{}:{}:{}'.format(session_id, label, job_id, action, code, operator)
        value = await self.mget_by_prefix(key)
        value_decode = [json.loads(record.decode('utf-8')) for record in value] if value else []
        session_jobs = sort_by_update_time(value_decode) if sorting else value_decode
        return session_jobs

    async def check_job_id(self, entry: BaseSchema):
        """Verifies if job_id already exists for respective session."""
        job = entry.dict()
        record = await self.get_job(
            job['session_id'], job['label'], job['job_id'], job['code'], job['action'], job['operator']
        )
        if record:
            logger.exception(f'Job id already exists: {job["job_id"]}')
            raise AlreadyExists()

    async def set_job(self, entry: Union[BaseSchema, dict]) -> dict:
        """Create new or update existing job record (key,value) in Redis for a respective session."""

        job = dict(entry)
        key = 'dataaction:{}:{}:{}:{}:{}:{}:{}'.format(
            job['session_id'],
            job['label'],
            job['job_id'],
            job['action'],
            job['code'],
            job['operator'],
            job['source'],
        )

        value = {
            'session_id': job['session_id'],
            'label': job['label'],
            'task_id': job['task_id'],
            'job_id': job['job_id'],
            'source': job['source'],
            'action': job['action'],
            'status': job['target_status'],
            'code': job['code'],
            'operator': job['operator'],
            'progress': job['progress'],
            'payload': job['payload'],
            'update_timestamp': str(round(time.time())),
        }
        my_value = json.dumps(value)
        await self.set_by_key(key, my_value, 24)
        return value

    async def update_job(
        self,
        session_id: str,
        code: str,
        action: str,
        operator: str,
        label: str,
        job_id: str,
        payload: dict,
        status: str,
        progress: int,
    ) -> dict:
        """Update existing job for a respective session."""
        retrieved_job = await self.get_job(session_id, label, job_id, code, action, operator)
        if not retrieved_job:
            logger.exception(f'Job id not found: {job_id}')
            raise NotFound()
        job = retrieved_job[0]
        for key, value in payload.items():
            payload[key] = value
        job['target_status'] = status
        job['progress'] = progress
        updated_job = await self.set_job(job)
        return updated_job

    async def delete_job(self, entry: BaseSchema) -> list:
        """Delete existing job for a respective session."""
        job = entry.dict()
        key = 'dataaction:{}:{}:{}:{}:{}:{}'.format(
            job['session_id'], job['label'], job['job_id'], job['action'], job['code'], job['operator']
        )
        value = await self.mdele_by_prefix(key)
        return value
