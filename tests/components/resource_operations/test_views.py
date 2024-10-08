# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from dataops.components.schemas import EActionType


class TestResourceOperationViews:
    async def test_create_copy_operation_job_return_202(
        self, test_client, httpx_mock, create_fake_xadd_response, metadata_service, queue_service, fake
    ):
        source_id = fake.uuid4()
        task_id = fake.uuid4()
        session_id = f'admin-{fake.uuid4()}'
        destination_id = fake.uuid4()
        target_id = fake.uuid4()
        target_name = fake.word()
        container_code = fake.word()

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{destination_id}/',
            status_code=200,
            json={'result': {'name': 'admin', 'type': 'name_folder', 'status': 'ACTIVE', 'zone': 0}},
        )

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{source_id}/',
            status_code=200,
            json={'result': {'name': 'admin', 'type': 'name_folder', 'status': 'ACTIVE', 'zone': 0}},
        )

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{target_id}/',
            status_code=200,
            json={
                'result': {
                    'id': f'{target_id}',
                    'name': target_name,
                    'type': 'file',
                    'status': 'ACTIVE',
                    'zone': 0,
                    'container_code': container_code,
                }
            },
        )

        httpx_mock.add_response(
            method='POST',
            url=f'{queue_service.service_url}send_message',
            status_code=200,
            json={'result': 'SUCCEED'},
        )

        header = {'Authorization': 'Bearer faketoken'}

        payload = {
            'session_id': session_id,
            'task_id': task_id,
            'payload': {
                'targets': [{'id': f'{target_id}'}],
                'source': f'{source_id}',
                'destination': f'{destination_id}',
            },
            'operator': 'admin',
            'operation': 'copy',
            'project_code': container_code,
        }
        response = await test_client.post('/v1/files/actions/', json=payload, headers=header)
        res = response.json()['operation_info'][0]
        assert response.status_code == 202
        assert res['session_id'] == session_id
        assert res['target_names'] == [target_name]
        assert res['target_type'] == 'file'
        assert res['container_code'] == container_code
        assert res['action_type'] == EActionType.data_transfer.name

    async def test_create_delete_operation_job_return_202(
        self, test_client, httpx_mock, create_fake_xadd_response, metadata_service, queue_service, fake
    ):
        source_id = fake.uuid4()
        task_id = fake.uuid4()
        session_id = f'admin-{fake.uuid4()}'
        destination_id = fake.uuid4()
        target_id = fake.uuid4()
        target_name = fake.word()
        container_code = fake.word()

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{source_id}/',
            status_code=200,
            json={'result': {'name': 'admin', 'type': 'name_folder', 'status': 'ACTIVE', 'zone': 0}},
        )

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{target_id}/',
            status_code=200,
            json={
                'result': {
                    'id': f'{target_id}',
                    'name': target_name,
                    'type': 'file',
                    'status': 'ACTIVE',
                    'zone': 0,
                    'container_code': container_code,
                }
            },
        )

        httpx_mock.add_response(
            method='POST',
            url=f'{queue_service.service_url}send_message',
            status_code=200,
            json={'result': 'SUCCEED'},
        )

        header = {'Authorization': 'Bearer faketoken'}

        payload = {
            'session_id': session_id,
            'task_id': task_id,
            'payload': {
                'targets': [{'id': f'{target_id}'}],
                'source': f'{source_id}',
                'destination': f'{destination_id}',
            },
            'operator': 'admin',
            'operation': 'delete',
            'project_code': container_code,
        }
        response = await test_client.post('/v1/files/actions/', json=payload, headers=header)
        res = response.json()['operation_info'][0]
        assert response.status_code == 202
        assert res['session_id'] == session_id
        assert res['target_names'] == [target_name]
        assert res['target_type'] == 'file'
        assert res['container_code'] == container_code
        assert res['action_type'] == EActionType.data_delete.name

    async def test_create_copy_operation_job_failed_message_to_queue_return_500(
        self, test_client, httpx_mock, create_fake_xadd_response, metadata_service, queue_service, fake
    ):
        source_id = fake.uuid4()
        task_id = fake.uuid4()
        session_id = f'admin-{fake.uuid4()}'
        destination_id = fake.uuid4()
        target_id = fake.uuid4()
        target_name = fake.word()
        container_code = fake.word()

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{destination_id}/',
            status_code=200,
            json={'result': {'name': 'admin', 'type': 'name_folder', 'status': 'ACTIVE', 'zone': 0}},
        )

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{source_id}/',
            status_code=200,
            json={'result': {'name': 'admin', 'type': 'name_folder', 'status': 'ACTIVE', 'zone': 0}},
        )

        httpx_mock.add_response(
            method='GET',
            url=f'{metadata_service.service_url}item/{target_id}/',
            status_code=200,
            json={
                'result': {
                    'id': f'{target_id}',
                    'name': target_name,
                    'type': 'file',
                    'status': 'ACTIVE',
                    'zone': 0,
                    'container_code': container_code,
                }
            },
        )

        httpx_mock.add_response(
            method='POST',
            url=f'{queue_service.service_url}send_message',
            status_code=500,
            json={},
        )
        header = {'Authorization': 'Bearer faketoken'}
        payload = {
            'session_id': session_id,
            'task_id': task_id,
            'payload': {
                'targets': [{'id': f'{target_id}'}],
                'source': f'{source_id}',
                'destination': f'{destination_id}',
            },
            'operator': 'admin',
            'operation': 'copy',
            'project_code': container_code,
        }
        response = await test_client.post('/v1/files/actions/', json=payload, headers=header)
        assert response.status_code == 500
