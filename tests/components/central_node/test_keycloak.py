# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import time as tm

import pytest
from pytest import MonkeyPatch
from pytest_httpx import HTTPXMock

from dataops.components.central_node.keycloak import DeviceAuth
from dataops.components.central_node.keycloak import KeycloakClient
from dataops.components.central_node.keycloak import KeycloakDeviceAuthError
from dataops.components.central_node.keycloak import TokenResponse
from tests.fixtures.fake import Faker


class TestKeycloakClient:
    async def test_init_device_auth_returns_device_auth_on_success(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock, fake: Faker
    ):
        device_code = fake.pystr()
        expires_in = fake.pyint()
        httpx_mock.add_response(
            url=keycloak_client.device_auth_url,
            json={
                'device_code': device_code,
                'user_code': 'USER-CODE',
                'verification_uri': f'{keycloak_client.keycloak_url}/activate',
                'verification_uri_complete': f'{keycloak_client.keycloak_url}/activate?user_code=USER-CODE',
                'expires_in': expires_in,
                'interval': 5,
            },
        )

        result = await keycloak_client.init_device_auth()

        assert isinstance(result, DeviceAuth)
        assert result.device_code == device_code
        assert result.expires_in == expires_in

    async def test_init_device_auth_raises_exception_on_http_error(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(url=keycloak_client.device_auth_url, status_code=401)

        with pytest.raises(KeycloakDeviceAuthError):
            await keycloak_client.init_device_auth()

    async def test_wait_for_device_auth_returns_token_response_on_success(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock, fake: Faker, skip_sleep: None
    ):
        access_token = fake.pystr()
        httpx_mock.add_response(url=keycloak_client.token_url, json={'access_token': access_token})

        result = await keycloak_client.wait_for_device_auth('code')

        assert isinstance(result, TokenResponse)
        assert result.access_token == access_token

    async def test_wait_for_device_auth_retries_on_authorization_pending(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock, fake: Faker, skip_sleep: None
    ):
        access_token = fake.pystr()
        httpx_mock.add_response(url=keycloak_client.token_url, status_code=400, json={'error': 'authorization_pending'})
        httpx_mock.add_response(url=keycloak_client.token_url, json={'access_token': access_token})

        result = await keycloak_client.wait_for_device_auth('code')

        assert result.access_token == access_token

    async def test_wait_for_device_auth_raises_on_expired_token(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock, skip_sleep: None
    ):
        httpx_mock.add_response(url=keycloak_client.token_url, status_code=400, json={'error': 'expired_token'})

        with pytest.raises(KeycloakDeviceAuthError, match='expired'):
            await keycloak_client.wait_for_device_auth('code')

    async def test_wait_for_device_auth_raises_on_access_denied(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock, skip_sleep: None
    ):
        httpx_mock.add_response(url=keycloak_client.token_url, status_code=400, json={'error': 'access_denied'})

        with pytest.raises(KeycloakDeviceAuthError, match='denied'):
            await keycloak_client.wait_for_device_auth('code')

    async def test_wait_for_device_auth_raises_on_unexpected_error(
        self, keycloak_client: KeycloakClient, httpx_mock: HTTPXMock, fake: Faker, skip_sleep: None
    ):
        error_text = fake.sentence()
        httpx_mock.add_response(
            url=keycloak_client.token_url,
            status_code=400,
            json={'error': 'unknown_error', 'error_description': error_text},
        )

        with pytest.raises(KeycloakDeviceAuthError, match=error_text):
            await keycloak_client.wait_for_device_auth('code')

    async def test_wait_for_device_auth_raises_timeout_when_deadline_exceeded(
        self, keycloak_client: KeycloakClient, monkeypatch: MonkeyPatch
    ):
        with monkeypatch.context() as m:
            steps = iter([0, 1000])
            m.setattr(tm, 'monotonic', lambda: next(steps))

            with pytest.raises(TimeoutError, match='timed out'):
                await keycloak_client.wait_for_device_auth('code')
