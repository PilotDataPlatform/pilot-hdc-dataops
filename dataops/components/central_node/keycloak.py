# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import asyncio
import time as tm

import httpx
from fastapi import Depends
from pydantic import BaseModel

from dataops.config import Settings
from dataops.config import get_settings
from dataops.logger import logger


class TokenResponse(BaseModel):
    access_token: str


class DeviceAuth(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class KeycloakDeviceAuthError(Exception):
    pass


class KeycloakClient:
    def __init__(
        self,
        *,
        keycloak_url: str,
        keycloak_realm: str,
        keycloak_client_id: str,
        timeout: int = 30,
        poll_interval: int = 5,
        poll_timeout: int = 300,
    ) -> None:
        self.keycloak_url = keycloak_url
        self.keycloak_realm = keycloak_realm
        self.keycloak_client_id = keycloak_client_id
        self.device_auth_url = f'{self.keycloak_url}/realms/{self.keycloak_realm}/protocol/openid-connect/auth/device'
        self.token_url = f'{self.keycloak_url}/realms/{self.keycloak_realm}/protocol/openid-connect/token'
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.timeout)

    async def init_device_auth(self) -> DeviceAuth:
        try:
            async with self.client as client:
                response = await client.post(self.device_auth_url, data={'client_id': self.keycloak_client_id})
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.exception(f'Failed to initiate device authorization: {exc.response.text}')
            raise KeycloakDeviceAuthError from exc

        return DeviceAuth.parse_obj(response.json())

    async def wait_for_device_auth(self, device_code: str) -> TokenResponse:
        interval = self.poll_interval
        deadline = tm.monotonic() + self.poll_timeout

        while tm.monotonic() < deadline:
            await asyncio.sleep(interval)

            try:
                async with self.client as client:
                    response = await client.post(
                        self.token_url,
                        data={
                            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                            'device_code': device_code,
                            'client_id': self.keycloak_client_id,
                        },
                    )
            except (httpx.ConnectError, httpx.ReadTimeout):
                continue

            if response.status_code >= 500:
                continue

            if response.status_code == 200:
                return TokenResponse.parse_obj(response.json())

            body = response.json()
            error = body.get('error', '')

            if error == 'authorization_pending':
                continue

            if error == 'slow_down':
                interval += self.poll_interval
                continue

            if error == 'expired_token':
                raise KeycloakDeviceAuthError('Device code has expired')

            if error == 'access_denied':
                raise KeycloakDeviceAuthError('Authorization was denied by the user')

            raise KeycloakDeviceAuthError(body.get('error_description', 'Unexpected error from KeycloakClient'))

        raise TimeoutError('Device authorization timed out')


def get_keycloak_client(settings: Settings = Depends(get_settings)) -> KeycloakClient:
    return KeycloakClient(
        keycloak_url=settings.CENTRAL_NODE_KEYCLOAK_URL,
        keycloak_realm=settings.CENTRAL_NODE_KEYCLOAK_REALM,
        keycloak_client_id=settings.CENTRAL_NODE_KEYCLOAK_CLIENT_ID,
        timeout=settings.CENTRAL_NODE_KEYCLOAK_CLIENT_TIMEOUT_SECONDS,
        poll_interval=settings.CENTRAL_NODE_DEVICE_AUTH_POLL_INTERVAL_SECONDS,
        poll_timeout=settings.CENTRAL_NODE_DEVICE_AUTH_POLL_TIMEOUT_SECONDS,
    )
