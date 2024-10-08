# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import pytest
from common import JWTHandler


@pytest.fixture
async def mock_get_token(monkeypatch):
    def fake_return(x, y):
        return ''

    monkeypatch.setattr(JWTHandler, 'get_token', fake_return)


@pytest.fixture
async def mock_decode_validate_token(monkeypatch):
    def fake_return(x, y):
        return {}

    monkeypatch.setattr(JWTHandler, 'decode_validate_token', fake_return)


@pytest.fixture
async def mock_get_current_identity(monkeypatch):
    async def fake_return(x, y, z):
        return {
            'user_id': 'test',
            'username': 'test',
            'role': 'member',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            'realm_roles': [],
        }

    monkeypatch.setattr(JWTHandler, 'get_current_identity', fake_return)
