# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from dataops.config import ConfigClass


class CreateEngine:
    def __init__(self) -> None:
        self.instance = None

    async def __call__(self) -> AsyncEngine:
        """Return an instance of AsyncEngine class."""
        if not self.instance:
            self.instance = create_async_engine(
                f'postgresql+asyncpg://{ConfigClass.RDS_USERNAME}:{ConfigClass.RDS_PASSWORD}@{ConfigClass.RDS_HOST}:'
                f'{ConfigClass.RDS_PORT}/{ConfigClass.RDS_NAME}',
                echo=ConfigClass.RDS_ECHO_SQL_QUERIES,
                pool_pre_ping=ConfigClass.RDS_PRE_PING,
            )

        return self.instance


get_db_engine = CreateEngine()


async def get_db_session(engine: AsyncEngine = Depends(get_db_engine)) -> AsyncSession:
    """Create a FastAPI callable dependency for SQLAlchemy AsyncSession instance."""
    session = AsyncSession(bind=engine, expire_on_commit=False)
    try:
        yield session
        await session.commit()
    finally:
        await session.close()
