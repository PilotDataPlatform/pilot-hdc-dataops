# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import ast
import re
import uuid

from dataops.components.schemas import EActionType
from dataops.components.schemas import EFileStatus


def parse_sse_response(response) -> list[dict]:
    lines = response.text.split('\n')
    response_data = []
    for line in lines:
        if line.startswith('data: '):
            response_data.append(ast.literal_eval(line[6:]))
    return response_data


class TestTaskStreamViews:
    async def test_create_file_status_entry_return_200(self, test_client, fake, fake_redis_streams_xadd):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name()],
            'target_type': 'file',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_upload.name,
            'status': EFileStatus.RUNNING.name,
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 200
        assert response.json()['total'] == 1
        for key in payload:
            assert response.json()['stream_info'][key] == payload[key]
        uuid_pattern = r'[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}'
        assert re.search(uuid_pattern, response.json()['stream_info']['job_id'])

    async def test_create_file_status_entry_custom_job_id_return_200(self, test_client, fake, fake_redis_streams_xadd):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name()],
            'target_type': 'file',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_upload.name,
            'status': EFileStatus.RUNNING.name,
            'job_id': str(uuid.uuid4()),
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 200
        assert response.json()['total'] == 1
        for key in payload:
            assert response.json()['stream_info'][key] == payload[key]

    async def test_create_file_status_entry_batch_return_200(self, test_client, fake, fake_redis_streams_xadd):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name(), fake.file_name(), fake.file_name()],
            'target_type': 'batch',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_transfer.name,
            'status': EFileStatus.RUNNING.name,
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 200
        assert response.json()['total'] == 1
        for key in payload:
            assert response.json()['stream_info'][key] == payload[key]

    async def test_create_file_status_entry_invalid_session_id_return_422(
        self, test_client, fake, fake_redis_streams_xadd
    ):
        payload = {
            'session_id': 'invalid-session-id',
            'target_names': [fake.file_name()],
            'target_type': 'file',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_upload.name,
            'status': EFileStatus.RUNNING.name,
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['loc'][1] == 'session_id'

    async def test_create_file_status_entry_mismatched_target_names_target_type_return_422(
        self, test_client, fake, fake_redis_streams_xadd
    ):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name(), fake.file_name(), fake.file_name()],
            'target_type': 'file',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_upload.name,
            'status': EFileStatus.RUNNING.name,
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['loc'][1] == 'target_type'

    async def test_create_file_status_entry_invalid_target_type_return_422(
        self, test_client, fake, fake_redis_streams_xadd
    ):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name()],
            'target_type': 'invalid_type',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_upload.name,
            'status': EFileStatus.RUNNING.name,
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['loc'][1] == 'target_type'

    async def test_create_file_status_entry_invalid_container_type_return_422(
        self, test_client, fake, fake_redis_streams_xadd
    ):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name()],
            'target_type': 'file',
            'container_code': 'test_project',
            'container_type': 'invalid',
            'action_type': EActionType.data_upload.name,
            'status': EFileStatus.RUNNING.name,
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['loc'][1] == 'container_type'

    async def test_create_file_status_entry_invalid_action_type_return_422(
        self, test_client, fake, fake_redis_streams_xadd
    ):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name()],
            'target_type': 'file',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': 'invalid',
            'status': EFileStatus.RUNNING.name,
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['loc'][1] == 'action_type'

    async def test_create_file_status_entry_invalid_status_return_422(self, test_client, fake, fake_redis_streams_xadd):
        payload = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'target_names': [fake.file_name()],
            'target_type': 'file',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_upload.name,
            'status': 'invalid',
        }
        response = await test_client.post('/v1/task-stream/', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['loc'][1] == 'status'

    async def test_get_file_status_entry_return_200(
        self,
        test_client,
        fake_redis_streams_xread,
        mock_get_token,
        mock_decode_validate_token,
        mock_get_current_identity,
    ):
        params = {
            'session_id': f'test-{str(uuid.uuid4())}',
            'request_timeout': 1,
        }
        response = await test_client.get('/v1/task-stream/', query_string=params)
        assert response.status_code == 200
        response_data = parse_sse_response(response)
        assert len(response_data) == 3

    async def test_get_file_status_entry_filter_by_container_code_return_200(
        self,
        test_client,
        fake_redis_streams_xread,
        mock_get_token,
        mock_decode_validate_token,
        mock_get_current_identity,
    ):
        params = {
            'session_id': f'test-{str(uuid.uuid4())}',
            'container_code': 'test_project',
            'container_type': 'project',
            'request_timeout': 1,
        }
        response = await test_client.get('/v1/task-stream/', query_string=params)
        assert response.status_code == 200
        response_data = parse_sse_response(response)
        for entry in response_data:
            assert entry['container_code'] == 'test_project'

    async def test_get_static_file_status_entry_return_200(self, test_client, fake, fake_redis_streams_xread):
        params = {'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}'}
        response = await test_client.get('/v1/task-stream/static/', query_string=params)
        assert response.status_code == 200
        assert response.json()['total'] == 3

    async def test_get_static_file_status_entry_filter_by_container_code_return_200(
        self, test_client, fake, fake_redis_streams_xread
    ):
        params = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'container_code': 'test_project',
            'container_type': 'project',
        }
        response = await test_client.get('/v1/task-stream/static/', query_string=params)
        assert response.status_code == 200
        assert response.json()['total'] == 2
        for entry in response.json()['stream_info']:
            assert entry['container_code'] == 'test_project'

    async def test_get_file_status_entry_filter_by_action_type_return_200(
        self,
        test_client,
        fake_redis_streams_xread,
        mock_get_token,
        mock_decode_validate_token,
        mock_get_current_identity,
    ):
        params = {
            'session_id': f'test-{str(uuid.uuid4())}',
            'container_code': 'test_project',
            'container_type': 'project',
            'action_type': EActionType.data_upload.name,
            'request_timeout': 1,
        }
        response = await test_client.get('/v1/task-stream/', query_string=params)
        assert response.status_code == 200
        response_data = parse_sse_response(response)
        for entry in response_data:
            assert entry['container_code'] == 'test_project'
            assert entry['action_type'] == EActionType.data_upload.name

    async def test_get_file_status_entry_filter_by_target_names_return_200(
        self,
        test_client,
        fake_redis_streams_xread,
        mock_get_token,
        mock_decode_validate_token,
        mock_get_current_identity,
    ):
        params = {
            'session_id': f'test-{str(uuid.uuid4())}',
            'container_code': 'test_project',
            'container_type': 'project',
            'target_names': 'file_3.txt',
            'request_timeout': 1,
        }
        response = await test_client.get('/v1/task-stream/', query_string=params)
        assert response.status_code == 200
        response_data = parse_sse_response(response)
        for entry in response_data:
            assert entry['container_code'] == 'test_project'
            assert entry['target_names'] == 'file_3.txt'

    async def test_get_file_status_entry_filter_by_job_id_return_200(
        self,
        test_client,
        fake_redis_streams_xread,
        mock_get_token,
        mock_decode_validate_token,
        mock_get_current_identity,
    ):
        params = {
            'session_id': f'test-{str(uuid.uuid4())}',
            'container_code': 'test_project',
            'container_type': 'project',
            'job_id': '1b51ac5e-eb49-40c8-b072-9115ef3ec2a5',
            'request_timeout': 1,
        }
        response = await test_client.get('/v1/task-stream/', query_string=params)
        assert response.status_code == 200
        response_data = parse_sse_response(response)
        for entry in response_data:
            assert entry['container_code'] == 'test_project'
            assert entry['job_id'] == '1b51ac5e-eb49-40c8-b072-9115ef3ec2a5'

    async def test_delete_file_statuses_return_200(self, test_client, fake, fake_redis_scan, fake_redis_delete_by_key):
        params = {'user': fake.user_name()}
        response = await test_client.delete('/v1/task-stream/', query_string=params)
        assert response.status_code == 200
        assert response.json()['total'] == 3
        assert len(response.json()['stream_info']) == 3

    async def test_get_file_status_entry_session_id_token_not_matching(
        self,
        test_client,
        fake,
        fake_redis_streams_xread,
        mock_get_token,
        mock_decode_validate_token,
        mock_get_current_identity,
    ):
        params = {
            'session_id': f'{fake.user_name()}-{str(uuid.uuid4())}',
            'request_timeout': 1,
        }
        response = await test_client.get('/v1/task-stream/', query_string=params)
        assert response.status_code == 400
