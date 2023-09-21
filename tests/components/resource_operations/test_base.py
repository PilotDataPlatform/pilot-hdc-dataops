# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import uuid

import pytest

from dataops.components.exceptions import InvalidInput
from dataops.components.resource_operations.filtering import ItemFilter
from dataops.components.resource_operations.schemas import ResourceOperationResponseSchema
from dataops.components.resource_operations.schemas import ResourceOperationSchema
from dataops.components.resource_operations.schemas import ResourceOperationTargetSchema
from dataops.components.schemas import EActionType
from dataops.components.schemas import EFileStatus


class TestBaseResourceProcessing:
    async def test_validate_base_return_validated_resource_type(
        self, httpx_mock, fake, get_BaseResourceProcessing, metadata_service, get_items_response_folder
    ):
        item_id = fake.uuid4()
        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{item_id}/',
            status_code=200,
            json=get_items_response_folder,
        )
        validity = await get_BaseResourceProcessing.validate_base(item_id)
        assert validity

    async def test_validate_base_raise_invalid_input(
        self, httpx_mock, fake, get_BaseResourceProcessing, metadata_service, get_items_response
    ):
        get_items_response['result']['type'] = 'file'
        item_id = fake.uuid4()
        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{item_id}/',
            status_code=200,
            json=get_items_response,
        )

        with pytest.raises(InvalidInput):
            await get_BaseResourceProcessing.validate_base(item_id)

    async def test_validate_targets_return_validated_target(
        self, httpx_mock, fake, get_BaseResourceProcessing, metadata_service, get_items_response
    ):
        item_id = fake.uuid4()
        targets = ResourceOperationTargetSchema(id=item_id)
        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{item_id}/',
            status_code=200,
            json=get_items_response,
        )
        validity = await get_BaseResourceProcessing.validate_targets([targets])
        assert isinstance(validity, ItemFilter)

    async def test_validate_targets_raise_invalid_input_archived_item(
        self, httpx_mock, fake, get_BaseResourceProcessing, metadata_service, get_items_response
    ):
        item_id = fake.uuid4()
        targets = ResourceOperationTargetSchema(id=item_id)
        get_items_response['result']['status'] = 'ARCHIVED'
        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{item_id}/',
            status_code=200,
            json=get_items_response,
        )
        with pytest.raises(InvalidInput):
            await get_BaseResourceProcessing.validate_targets([targets])

    async def test_validate_targets_raise_invalid_input(
        self, httpx_mock, fake, get_BaseResourceProcessing, metadata_service, get_items_response
    ):
        item_id = fake.uuid4()
        targets = ResourceOperationTargetSchema(id=item_id)
        get_items_response['result']['type'] = 'invalid'
        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{item_id}/',
            status_code=200,
            json=get_items_response,
        )
        with pytest.raises(InvalidInput):
            await get_BaseResourceProcessing.validate_targets([targets])

    async def test_update_status_return_resource_operations_response(
        self, mocker, fake, get_BaseResourceProcessing, create_item
    ):
        item_1 = create_item()
        item_filter = ItemFilter([item_1])
        job_id = uuid.uuid4()
        session_id = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        destination_id = str(uuid.uuid4())
        project_code = fake.word()
        operator = fake.name()
        data = ResourceOperationSchema(
            session_id=session_id,
            payload={'targets': [{'id': item_1.id}], 'destination': destination_id, 'source': source_id},
            operation='copy',
            operator=operator,
            project_code=project_code,
        )

        mocker.patch(
            'dataops.components.resource_operations.crud.base.BaseResourceProcessing.streams_xadd', return_value={}
        )
        status_response = await get_BaseResourceProcessing.update_status(data, targets=item_filter, job_id=job_id)
        assert isinstance(status_response, ResourceOperationResponseSchema)
        operation_info = status_response.operation_info[0]
        assert operation_info.session_id == session_id
        assert operation_info.target_names == [item_1.name]
        assert operation_info.target_type == item_1['type']
        assert operation_info.container_code == project_code
        assert operation_info.action_type == EActionType.data_transfer.name
        assert operation_info.status == EFileStatus.RUNNING.name
        assert operation_info.job_id == job_id
