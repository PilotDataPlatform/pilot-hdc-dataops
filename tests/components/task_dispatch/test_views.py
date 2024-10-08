# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from dataops.components.schemas import EActionType


class TestTaskDispatchViews:
    async def test_create_new_task_return_200(self, test_client, create_fake_job_response, fake_job_save_status):
        payload = {
            'session_id': '12345',
            'task_id': '5678',
            'job_id': 'fake_global_entity_id',
            'source': 'any',
            'action': EActionType.data_transfer.name,
            'target_status': 'TRANSFER',
            'operator': 'me',
            'progress': 0,
            'code': 'testcode',
            'payload': {
                'task_id': 'fake_global_entity_id',
                'resumable_identifier': 'fake_global_entity_id',
                'parent_folder_geid': None,
            },
            'update_timestamp': '1643041440',
        }
        response = await test_client.post('/v1/tasks/', json=payload)
        res = response.json()['task_status']
        assert response.status_code == 200
        assert res == 'SUCCEED'

    async def test_create_new_task_with_duplicate_job_id_return_409(self, test_client, create_fake_job):
        payload = {
            'session_id': '12345',
            'task_id': '5678',
            'job_id': 'fake_global_entity_id',
            'source': 'any',
            'action': EActionType.data_transfer.name,
            'target_status': 'TRANSFER',
            'operator': 'me',
            'progress': 0,
            'code': 'testcode',
            'payload': {
                'task_id': 'fake_global_entity_id',
                'resumable_identifier': 'fake_global_entity_id',
                'parent_folder_geid': None,
            },
            'update_timestamp': '1643041440',
        }
        response = await test_client.post('/v1/tasks/', json=payload)
        assert response.status_code == 409

    async def test_get_task_return_200(self, test_client, create_fake_job):
        payload = {
            'session_id': '12345',
            'label': 'Container',
            'job_id': 'fake_global_entity_id',
            'code': 'testcode',
            'action': EActionType.data_transfer.name,
            'operator': 'me',
            'source': 'any',
        }
        response = await test_client.get('/v1/tasks/', query_string=payload)
        res = response.json()['task_info'][0]
        assert res['session_id'] == '12345'
        assert res['progress'] == 'SUCCESS'
        assert res['update_timestamp'] == '1643041442'
        assert response.status_code == 200

    async def test_delete_task_return_200(self, test_client, create_fake_job_delete_response):
        payload = {
            'session_id': '12345',
            'label': 'Container',
            'job_id': 'fake_global_entity_id',
            'code': 'testcode',
            'action': EActionType.data_transfer.name,
            'operator': 'me',
            'source': 'any',
        }
        response = await test_client.delete('/v1/tasks/', json=payload)
        res = response.json()['task_status']
        assert response.status_code == 200
        assert res == 'SUCCEED'

    async def test_update_task_return_200(
        self, test_client, create_fake_job_updated, fake_job_save_status_updated_task
    ):
        payload = {
            'session_id': '12345',
            'label': 'Container',
            'job_id': 'fake_global_entity_id',
            'progress': 1,
            'status': 'SUCCEED',
            'add_payload': {'parent_folder_geid': 'newgeid'},
        }
        response = await test_client.put('/v1/tasks/', json=payload)
        res = response.json()['task_info']
        assert response.status_code == 200
        assert res['payload']['parent_folder_geid'] == 'newgeid'
