# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import json

import pytest

from dataops.components.schemas import EActionType


@pytest.fixture
async def create_fake_job(monkeypatch):
    from dataops.components.crud import RedisCRUD

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'task_id': '5678',
        'source': '/path/to/file',
        'job_id': 'fake_global_entity_id',
        'action': EActionType.data_transfer.name,
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': None,
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(x, y):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(RedisCRUD, 'mget_by_prefix', fake_return)


@pytest.fixture
async def create_fake_job_response(monkeypatch):
    from dataops.components.crud import RedisCRUD

    async def fake_return(x, y):
        return b''

    monkeypatch.setattr(RedisCRUD, 'mget_by_prefix', fake_return)


@pytest.fixture
async def create_fake_job_delete_response(monkeypatch):
    from dataops.components.crud import RedisCRUD

    async def fake_return(x, y):
        return b''

    monkeypatch.setattr(RedisCRUD, 'mdele_by_prefix', fake_return)


@pytest.fixture
async def fake_job_save_status(monkeypatch):
    from dataops.components.crud import RedisCRUD

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'source': 'any',
        'task_id': '5678',
        'job_id': 'fake_global_entity_id',
        'action': EActionType.data_transfer.name,
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': None,
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(w, x, y, z):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(RedisCRUD, 'set_by_key', fake_return)


@pytest.fixture
async def create_fake_job_updated(monkeypatch):
    from dataops.components.crud import RedisCRUD

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'task_id': '5678',
        'source': '/path/to/file',
        'job_id': 'fake_global_entity_id',
        'action': EActionType.data_transfer.name,
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': 'newgeid',
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(x, y):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(RedisCRUD, 'mget_by_prefix', fake_return)


@pytest.fixture
async def fake_job_save_status_updated_task(monkeypatch):
    from dataops.components.crud import RedisCRUD

    record = {
        'session_id': '12345',
        'label': 'testlabel',
        'source': 'any',
        'task_id': '5678',
        'job_id': 'fake_global_entity_id',
        'action': EActionType.data_transfer.name,
        'status': 'TRANSFER',
        'code': 'any',
        'operator': 'me',
        'progress': 'SUCCESS',
        'payload': {
            'task_id': 'fake_global_entity_id',
            'resumable_identifier': 'fake_global_entity_id',
            'parent_folder_geid': 'newgeid',
        },
        'update_timestamp': '1643041442',
    }

    async def fake_return(w, x, y, z):
        return [bytes(json.dumps(record), 'utf-8')]

    monkeypatch.setattr(RedisCRUD, 'set_by_key', fake_return)
