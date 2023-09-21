# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import pytest


class TestResourceLockViews:
    @pytest.mark.parametrize('operation', ['read', 'write'])
    async def test_lock(self, test_client, fake, operation):
        payload = {
            'resource_key': fake.pystr(),
            'operation': operation,
        }

        response = await test_client.post('/v2/resource/lock/', json=payload)
        assert response.status_code == 200

        response = await test_client.delete('/v2/resource/lock/', json=payload)
        assert response.status_code == 200

    @pytest.mark.parametrize('operation', ['read', 'write'])
    async def test_bulk_lock_performs_lock_for_multiple_keys_return_200(self, test_client, fake, operation):
        key1 = f'a_{fake.pystr()}'
        key2 = f'b_{fake.pystr()}'
        payload = {
            'resource_keys': [key1, key2],
            'operation': operation,
        }

        response = await test_client.post('/v2/resource/lock/bulk', json=payload)
        assert response.status_code == 200

        expected_result = [
            [key1, True],
            [key2, True],
        ]
        result = response.json()['keys_status']

        assert expected_result == result

    @pytest.mark.parametrize('operation', ['read', 'write'])
    async def test_bulk_lock_stops_locking_when_lock_attempt_fails_return_409(self, test_client, fake, operation):
        key1 = f'a_{fake.pystr()}'
        key2 = f'b_{fake.pystr()}'
        key3 = f'c_{fake.pystr()}'

        await test_client.post('/v2/resource/lock/', json={'resource_key': key2, 'operation': 'write'})

        payload = {
            'resource_keys': [key1, key2, key3],
            'operation': operation,
        }

        response = await test_client.post('/v2/resource/lock/bulk', json=payload)
        assert response.status_code == 409

    @pytest.mark.parametrize('operation', ['read', 'write'])
    async def test_bulk_unlock_performs_unlock_for_multiple_keys_return_200(self, test_client, fake, operation):
        key1 = f'a_{fake.pystr()}'
        key2 = f'b_{fake.pystr()}'

        for key in [key1, key2]:
            await test_client.post('/v2/resource/lock/', json={'resource_key': key, 'operation': 'write'})

        payload = {
            'resource_keys': [key1, key2],
            'operation': operation,
        }

        response = await test_client.delete('/v2/resource/lock/bulk', json=payload)
        assert response.status_code == 200

        expected_result = [
            [key1, True],
            [key2, True],
        ]
        result = response.json()['keys_status']

        assert expected_result == result

    @pytest.mark.parametrize('operation', ['read', 'write'])
    async def test_bulk_unlock_continues_unlocking_when_unlock_attempt_fails_return_400(
        self, test_client, fake, operation
    ):
        key1 = f'a_{fake.pystr()}'
        key2 = f'b_{fake.pystr()}'

        await test_client.post('/v2/resource/lock/', json={'resource_key': key2, 'operation': 'write'})

        payload = {
            'resource_keys': [key1, key2],
            'operation': operation,
        }

        response = await test_client.delete('/v2/resource/lock/bulk', json=payload)
        assert response.status_code == 400

    @pytest.mark.parametrize('operation', ['read', 'write'])
    async def test_lock_returns_404_for_not_existing_lock(self, test_client, fake, operation):
        payload = {
            'resource_key': fake.pystr(),
            'operation': operation,
        }

        response = await test_client.delete('/v2/resource/lock/', json=payload)
        assert response.status_code == 400

    async def test_read_lock_not_exist_after_multiple_lock_unlock_operations_return_200(self, test_client, fake):
        payload = {
            'resource_key': fake.pystr(),
            'operation': 'read',
        }

        num = 10
        for _ in range(num):
            response = await test_client.post('/v2/resource/lock/', json=payload)
            assert response.status_code == 200

        for _ in range(num):
            response = await test_client.delete('/v2/resource/lock/', json=payload)
            assert response.status_code == 200

        response = await test_client.get('/v2/resource/lock/', query_string=payload)
        status = response.json()['status']
        assert status is None

    async def test_second_write_lock_is_not_allowed_and_return_409(self, test_client, fake):
        payload = {
            'resource_key': fake.pystr(),
            'operation': 'write',
        }

        response = await test_client.post('/v2/resource/lock/', json=payload)
        assert response.status_code == 200

        response = await test_client.post('/v2/resource/lock/', json=payload)
        assert response.status_code == 409
