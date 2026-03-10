# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from async_asgi_testclient import TestClient
from faker import Faker
from pytest_httpx import HTTPXMock

from dataops.components.central_node.device_storage import DeviceStorage
from dataops.components.central_node.device_storage import UploadData
from dataops.components.central_node.keycloak import KeycloakClient
from dataops.components.central_node.schemas import FileUploadSchema
from dataops.services.queue import QueueService


class TestCentralNodeViews:

    async def test_init_file_upload_returns_upload_key_and_login_url(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock, test_client: TestClient, fake: Faker
    ):
        user_code = fake.pystr()
        login_url = f'{keycloak_client.keycloak_url}/activate?user_code={user_code}'
        httpx_mock.add_response(
            url=keycloak_client.device_auth_url,
            json={
                'device_code': fake.pystr(),
                'user_code': user_code,
                'verification_uri': f'{keycloak_client.keycloak_url}/activate',
                'verification_uri_complete': login_url,
                'expires_in': 300,
                'interval': 5,
            },
        )
        payload = FileUploadSchema(
            file_id=fake.uuid4(),
            project_code=fake.project_code(),
            job_id=fake.uuid4(),
            session_id=fake.uuid4(),
            operator=fake.user_name(),
        ).to_payload()

        response = await test_client.post('/v1/central-node/upload', json=payload)

        assert response.status_code == 200
        body = response.json()
        assert 'upload_key' in body
        assert body['login_url'] == login_url

    async def test_wait_for_file_upload_authorization_returns_202_on_success(
        self,
        keycloak_client: KeycloakClient,
        queue_service: QueueService,
        storage: DeviceStorage,
        httpx_mock: HTTPXMock,
        test_client: TestClient,
        fake: Faker,
    ):
        data = UploadData(
            file_id=fake.uuid4(),
            project_code=fake.project_code(),
            job_id=fake.uuid4(),
            session_id=fake.uuid4(),
            operator=fake.user_name(),
            device_code=fake.pystr(),
        )
        upload_key = await storage.save_upload_data(data, ttl_seconds=60)
        httpx_mock.add_response(url=keycloak_client.token_url, json={'access_token': fake.pystr()})
        httpx_mock.add_response(
            method='POST', url=f'{queue_service.service_url}send_message', json={'result': 'SUCCEED'}
        )

        header = {'Authorization': 'Bearer faketoken'}
        response = await test_client.get(f'/v1/central-node/upload/{upload_key}', headers=header)

        assert response.status_code == 202
