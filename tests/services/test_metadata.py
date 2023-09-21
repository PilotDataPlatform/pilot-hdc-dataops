# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import uuid

import pytest

from dataops.components.exceptions import NotFound
from dataops.components.exceptions import UnhandledException


class TestMetadataClient:
    async def test_return_item_info_from_id(self, httpx_mock, metadata_service, get_items_response):
        item_id = get_items_response['result']['id']
        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{item_id}/',
            status_code=200,
            json=get_items_response,
        )
        resource = await metadata_service.get_resource_by_id(item_id=item_id)
        assert resource == get_items_response['result']

    async def test_raise_exception_item_not_found(self, httpx_mock, metadata_service, get_items_response_not_found):
        item_id = str(uuid.uuid4())
        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{item_id}/',
            status_code=200,
            json=get_items_response_not_found,
        )
        with pytest.raises(NotFound):
            await metadata_service.get_resource_by_id(item_id=item_id)

    async def test_raise_exception_metadata_service_status_error(
        self, httpx_mock, metadata_service, get_items_response
    ):
        item_id = get_items_response['result']['id']
        httpx_mock.add_response(
            method='GET', url=f'{metadata_service.service_url}item/{item_id}/', status_code=500, json={}
        )
        with pytest.raises(UnhandledException):
            await metadata_service.get_resource_by_id(item_id=item_id)
