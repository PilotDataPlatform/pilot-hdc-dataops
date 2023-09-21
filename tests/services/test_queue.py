# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import pytest

from dataops.components.exceptions import UnhandledException


class TestQueueClient:
    async def test_return_message_response_from_queue(
        self, httpx_mock, fake, queue_service, get_queue_message_send, get_queue_message_response
    ):
        httpx_mock.add_response(
            method='POST',
            url=f'{queue_service.service_url}send_message',
            status_code=200,
            json=get_queue_message_response,
        )
        resource = await queue_service.send_message(get_queue_message_send)
        assert resource == get_queue_message_response['result']

    async def test_raise_exception_status_error(self, httpx_mock, fake, queue_service, get_queue_message_send):
        httpx_mock.add_response(
            method='POST',
            url=f'{queue_service.service_url}send_message',
            status_code=500,
            json={},
        )
        with pytest.raises(UnhandledException):
            await queue_service.send_message(get_queue_message_send)
