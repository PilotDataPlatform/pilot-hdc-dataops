# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import asyncio

import pytest
from redis.asyncio import Redis

from dataops.components.central_node.device_storage import DeviceStorage
from dataops.components.central_node.keycloak import KeycloakClient
from tests.fixtures.fake import Faker


@pytest.fixture
def skip_sleep(monkeypatch: pytest.MonkeyPatch):
    async def noop(*args, **kwds):
        pass

    monkeypatch.setattr(asyncio, 'sleep', noop)


@pytest.fixture
def keycloak_client(fake: Faker) -> KeycloakClient:
    return KeycloakClient(
        keycloak_url='https://keycloak',
        keycloak_realm=fake.pystr(),
        keycloak_client_id=fake.pystr(),
        timeout=10,
        poll_interval=1,
        poll_timeout=10,
    )


@pytest.fixture
def storage(redis: Redis) -> DeviceStorage:
    return DeviceStorage(redis, 'test-prefix')
