# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from time import time

import pytest

from dataops.config import get_settings
from dataops.services.queue import QueueService


@pytest.fixture
def queue_service() -> QueueService:
    settings = get_settings()
    return QueueService(settings.QUEUE_SERVICE)


@pytest.fixture
def get_queue_message_send(fake):
    fake_session_id = f'admin-{str(fake.uuid4())}'
    fake_job_id = str(fake.uuid4())
    fake_source_id = str(fake.uuid4())
    fake_id = str(fake.uuid4())
    message = {
        'event_type': 'folder_copy',
        'payload': {
            'session_id': fake_session_id,
            'job_id': fake_job_id,
            'source_geid': fake_source_id,
            'include_geids': list(fake_id),
            'project': 'dataops_test',
            'generic': True,
            'operator': 'admin',
        },
        'create_timestamp': time(),
    }
    yield message


@pytest.fixture
def get_queue_message_response(fake):
    fake_session_id = f'admin-{str(fake.uuid4())}'
    fake_job_id = str(fake.uuid4())
    fake_source_id = str(fake.uuid4())
    fake_id = str(fake.uuid4())
    response = {
        'num_of_pages': 1,
        'page': 0,
        'total': 1,
        'result': [
            {
                'session_id': fake_session_id,
                'job_id': fake_job_id,
                'source_geid': fake_source_id,
                'include_geids': [fake_id],
                'project': 'dataops_test',
                'generic': True,
                'operator': 'admin',
                'rt': None,
            }
        ],
    }
    yield response
