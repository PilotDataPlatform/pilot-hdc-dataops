# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import pytest

from dataops.config import get_settings
from dataops.services.metadata import MetadataService


@pytest.fixture
def metadata_service() -> MetadataService:
    settings = get_settings()
    return MetadataService(settings.METADATA_SERVICE)


@pytest.fixture()
def get_items_response(fake):
    fake_id = str(fake.uuid4())
    response = {
        'num_of_pages': 1,
        'page': 0,
        'total': 1,
        'result': {
            'id': fake_id,
            'parent': None,
            'parent_path': None,
            'restore_path': None,
            'status': 'ACTIVE',
            'type': 'file',
            'zone': 0,
            'name': 'testfile.txt',
            'size': 0,
            'owner': 'admin',
            'container_code': 'dataops_test',
            'container_type': 'project',
            'created_time': '2022-08-31 15:38:22.999269',
            'last_updated_time': '2022-08-31 15:38:22.999278',
            'storage': {'id': fake_id, 'location_uri': None, 'version': None},
            'extended': {
                'id': fake_id,
                'extra': {'tags': [], 'system_tags': [], 'attributes': {}},
            },
        },
    }
    yield response


@pytest.fixture()
def get_items_response_folder(fake):
    fake_id = str(fake.uuid4())
    response = {
        'num_of_pages': 1,
        'page': 0,
        'total': 1,
        'result': {
            'id': fake_id,
            'parent': None,
            'parent_path': None,
            'restore_path': None,
            'status': 'ACTIVE',
            'type': 'folder',
            'zone': 0,
            'name': 'testfolder',
            'size': 0,
            'owner': 'admin',
            'container_code': 'dataops_test',
            'container_type': 'project',
            'created_time': '2022-08-31 15:38:22.999269',
            'last_updated_time': '2022-08-31 15:38:22.999278',
            'storage': {'id': fake_id, 'location_uri': None, 'version': None},
            'extended': {
                'id': fake_id,
                'extra': {'tags': [], 'system_tags': [], 'attributes': {}},
            },
        },
    }
    yield response


@pytest.fixture()
def get_items_response_not_found():
    response = {
        'num_of_pages': 1,
        'page': 0,
        'total': 1,
        'result': [],
    }
    yield response
