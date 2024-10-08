# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from uuid import uuid4

from dataops.components.resource_operations.crud.base import BaseResourceProcessing
from dataops.components.resource_operations.schemas import ResourceOperationResponseSchema
from dataops.components.resource_operations.schemas import ResourceOperationSchema
from dataops.components.schemas import EFileStatus


class Dispatcher(BaseResourceProcessing):
    """Manages execution of resource operation request."""

    async def execute(self, data: ResourceOperationSchema, token: str) -> ResourceOperationResponseSchema:
        """Creates resource operation job in Redis and sends operation request to the queue."""
        job_id = uuid4()
        if data.operation == 'copy':
            await self.validate_base(data.payload.destination)

        await self.validate_base(data.payload.source)
        targets = await self.validate_targets(data.payload.targets)
        status_info = await self.update_status(data, targets, job_id)
        try:
            await self.send_message(job_id=job_id, targets=targets, data=data, token=token)
        except Exception:
            data.status = EFileStatus.FAILED.name
            await self.update_status(data, targets, job_id)
            raise
        return status_info
