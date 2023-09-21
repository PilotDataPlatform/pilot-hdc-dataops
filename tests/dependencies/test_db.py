# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from sqlalchemy.ext.asyncio import AsyncEngine


class TestCreateDBEngine:
    async def test_instance_has_uninitialized_instance_attribute_after_creation(self, create_db_engine):
        assert create_db_engine.instance is None

    async def test_call_returns_an_instance_of_async_engine(self, create_db_engine):
        db_engine = await create_db_engine()
        assert db_engine is create_db_engine.instance
        assert isinstance(db_engine, AsyncEngine)
