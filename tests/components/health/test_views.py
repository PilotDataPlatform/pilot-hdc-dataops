# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import pytest


class TestHealthViews:
    async def test_health_endpoint_returns_204_when_resources_are_online(self, test_client):
        response = await test_client.get('/v1/health/')

        assert response.status_code == 204

    @pytest.mark.parametrize('db', (True, False))
    @pytest.mark.parametrize('redis', (True, False))
    async def test_health_endpoint_returns_503_when_db_or_redis_is_not_online_or_204_if_online(
        self, test_client, mocker, db, redis
    ):

        mocker.patch('dataops.components.health.resource_checkers.DBChecker.is_online', return_value=db)
        mocker.patch('dataops.components.health.resource_checkers.RedisChecker.is_online', return_value=redis)

        response = await test_client.get('/v1/health/')
        if db and redis:
            assert response.status_code == 204
        else:
            assert response.status_code == 503
