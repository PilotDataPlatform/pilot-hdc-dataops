# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from time import time

import pytest
from fakeredis.aioredis import FakeRedis

from dataops.components.schemas import EActionType
from dataops.dependencies.redis import GetRedis


@pytest.fixture
def redis():
    yield FakeRedis()


@pytest.fixture
def get_redis():
    yield GetRedis()


@pytest.fixture
async def create_fake_xadd_response(monkeypatch):
    from dataops.components.task_dispatch.crud import RedisCRUD

    async def fake_return(w, x, y, z):
        return b''

    monkeypatch.setattr(RedisCRUD, 'streams_xadd', fake_return)


@pytest.fixture
async def fake_redis_streams_xadd(monkeypatch):
    from dataops.components.task_dispatch.crud import RedisCRUD

    async def fake_function(w, x, y, z):
        current_time_ms = int(time() * 1000)
        return bytes(f'{current_time_ms}-0', 'utf-8')

    monkeypatch.setattr(RedisCRUD, 'streams_xadd', fake_function)


@pytest.fixture
async def fake_redis_streams_xread(monkeypatch):
    from dataops.components.task_dispatch.crud import RedisCRUD

    async def fake_function(self, key, offset, block=None, count=None):
        all_entries = [
            (
                bytes('1669237933000-0', 'utf-8'),
                {
                    b'target_names': b"['file_1.txt', 'file_2.txt']",
                    b'target_type': b'batch',
                    b'container_code': b'test_project',
                    b'container_type': b'project',
                    b'action_type': bytes(EActionType.data_transfer.name, 'utf-8'),
                    b'status': b'SUCCEED',
                    b'job_id': b'875d55fd-8154-4eec-a969-016664b9b86b',
                },
            ),
            (
                bytes('1669237934500-0', 'utf-8'),
                {
                    b'target_names': b"['file_3.txt']",
                    b'target_type': b'file',
                    b'container_code': b'test_project',
                    b'container_type': b'project',
                    b'action_type': bytes(EActionType.data_upload.name, 'utf-8'),
                    b'status': b'RUNNING',
                    b'job_id': b'1b51ac5e-eb49-40c8-b072-9115ef3ec2a5',
                },
            ),
            (
                bytes('1669237936000-0', 'utf-8'),
                {
                    b'target_names': b"['file_4.txt']",
                    b'target_type': b'file',
                    b'container_code': b'test_project_2',
                    b'container_type': b'project',
                    b'action_type': bytes(EActionType.data_delete.name, 'utf-8'),
                    b'status': b'RUNNING',
                    b'job_id': b'82ea9a79-30b1-46eb-b5db-6263b7579d6e',
                },
            ),
        ]
        entries_after_offset = []
        for entry in all_entries:
            offset_int = int(offset) if offset == '0' else int(offset[:-2])
            if int(entry[0].decode()[:-2]) > offset_int:
                entries_after_offset.append(entry)
        if entries_after_offset:
            return [[bytes(key, 'utf-8'), entries_after_offset]]
        return []

    monkeypatch.setattr(RedisCRUD, 'streams_xread', fake_function)


@pytest.fixture
async def fake_redis_scan(monkeypatch):
    from redis.asyncio.client import Redis

    async def fake_function(v, w, x, y, z):
        return (
            0,
            [
                b'user-2ce0197f-3fdd-4c48-af90-65be3864f936',
                b'user-13404d2e-e0a7-46cb-861e-df786a3923a8',
                b'user-ce30cdc7-45b3-44f2-9315-5fe97c2a1c1d',
                b'user-2ce0197f-3fdd-4c48-af90-65be3864f936',
            ],
        )

    monkeypatch.setattr(Redis, 'scan', fake_function)


@pytest.fixture
async def fake_redis_delete_by_key(monkeypatch):
    from dataops.components.task_dispatch.crud import RedisCRUD

    async def fake_function(w, x):
        return '(integer) 1'

    monkeypatch.setattr(RedisCRUD, 'delete_by_key', fake_function)
