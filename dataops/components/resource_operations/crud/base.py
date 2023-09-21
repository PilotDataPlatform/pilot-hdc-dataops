# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from time import time
from typing import List
from uuid import UUID

from common import LoggerFactory

from dataops.components.crud import RedisCRUD
from dataops.components.exceptions import InvalidInput
from dataops.components.resource_operations.filtering import ItemFilter
from dataops.components.resource_operations.schemas import FileStatusSchema
from dataops.components.resource_operations.schemas import ItemStatus
from dataops.components.resource_operations.schemas import ResourceOperationResponseSchema
from dataops.components.resource_operations.schemas import ResourceOperationSchema
from dataops.components.resource_operations.schemas import ResourceOperationTargetSchema
from dataops.components.resource_operations.schemas import ResourceType
from dataops.components.schemas import EActionType
from dataops.config import get_settings

settings = get_settings()
logger = LoggerFactory(
    __name__,
    level_default=settings.LOG_LEVEL_DEFAULT,
    level_file=settings.LOG_LEVEL_FILE,
    level_stdout=settings.LOG_LEVEL_STDOUT,
    level_stderr=settings.LOG_LEVEL_STDERR,
).get_logger()


class BaseResourceProcessing(RedisCRUD):
    """Base class for managing resource operation request validation and processing."""

    def __init__(self, metadata_client, queue_client, redis):
        self.metadata_client = metadata_client
        self.queue_client = queue_client
        super().__init__(redis)

    async def validate_base(self, item_id: str) -> bool:
        """Validate resource type of base source and destination locations for resource operation."""
        resource = await self.metadata_client.get_resource_by_id(item_id)
        if resource['type'] in [ResourceType.NAME_FOLDER, ResourceType.FOLDER, ResourceType.CONTAINER]:
            return True
        else:
            logger.exception(f'Source/destination is not a valid resource type: {item_id}')
            raise InvalidInput()

    async def validate_targets(self, targets: List[ResourceOperationTargetSchema]) -> ItemFilter:
        """Validate resource type and archive status of target ids involved in resource operation."""
        fetched = []
        for target in targets:
            item = await self.metadata_client.get_resource_by_id(target.id)
            if item['status'] == ItemStatus.ARCHIVED:
                logger.exception(f'Target resource is archived and cannot be used for requested operation: {target.id}')
                raise InvalidInput()
            if item['type'] not in [ResourceType.FILE, ResourceType.FOLDER]:
                logger.exception(f'Target resource is not a valid resource type: {item}')
                raise InvalidInput()
            fetched.append(item)
        return ItemFilter(fetched)

    async def update_status(
        self, data: ResourceOperationSchema, targets: ItemFilter, job_id: UUID
    ) -> ResourceOperationResponseSchema:
        """Updates resource operation request status in Redis streams."""
        status_data = FileStatusSchema(
            session_id=data.session_id,
            target_names=targets.names,
            target_type=targets.target_type,
            container_type='project',
            container_code=data.project_code,
            action_type=EActionType.data_transfer.name if data.operation == 'copy' else EActionType.data_delete.name,
            job_id=job_id,
            status=data.status,
        )
        values = status_data.to_payload()
        values.pop('session_id')
        values['target_names'] = str(values['target_names'])
        await self.streams_xadd(data.session_id, values, '*')
        return ResourceOperationResponseSchema(operation_info=[status_data])

    async def send_message(self, job_id: UUID, data: ResourceOperationSchema, targets: ItemFilter, token: str) -> None:
        """Create and send message of resource operation to queue."""
        message = {
            'event_type': 'folder_copy' if data.operation == 'copy' else 'folder_delete',
            'payload': {
                'session_id': data.session_id,
                'job_id': str(job_id),
                'source_geid': data.payload.source,
                'include_geids': list(targets.ids),
                'project': data.project_code,
                'generic': True,
                'operator': data.operator,
                'access_token': token,
            },
            'create_timestamp': time(),
        }

        if data.operation == 'copy':
            message['payload']['request_info'] = data.payload.request_info or {}
            message['payload']['destination_geid'] = data.payload.destination

        await self.queue_client.send_message(message)
