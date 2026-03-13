# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import asyncio

import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI

from dataops.app import create_app
from dataops.components.central_node.device_storage import get_device_storage
from dataops.components.central_node.keycloak import get_keycloak_client
from dataops.dependencies import get_redis
from dataops.dependencies.db import get_db_session


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    asyncio.set_event_loop_policy(None)


@pytest.fixture
def app(event_loop, db_session, cache, redis, keycloak_client, storage) -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_redis] = lambda: redis
    app.dependency_overrides[get_keycloak_client] = lambda: keycloak_client
    app.dependency_overrides[get_device_storage] = lambda: storage
    yield app


@pytest.fixture
async def test_client(app):
    async with TestClient(app) as client:
        yield client
