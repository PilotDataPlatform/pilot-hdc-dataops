# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import os
from contextlib import contextmanager
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.command import downgrade
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from dataops.components.archive_preview.models import ArchivePreview
from dataops.dependencies.db import CreateEngine


@contextmanager
def chdir(directory: Path) -> None:
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture(scope='session')
def project_root() -> Path:
    path = Path(__file__)

    while path.name != 'dataops':
        path = path.parent

    yield path


@pytest.fixture(scope='session')
def db_uri(project_root) -> str:
    with PostgresContainer('postgres:9.5') as postgres:
        database_uri = postgres.get_connection_url().replace('+psycopg2', '+asyncpg')
        config = Config('migrations/alembic.ini')
        with chdir(project_root):
            config.set_main_option('database_uri', database_uri)
            upgrade(config, 'head')
            yield database_uri
            downgrade(config, 'base')


@pytest_asyncio.fixture(scope='session')
async def db_engine(db_uri):
    engine = create_async_engine(db_uri)
    yield engine
    await engine.dispose()


@pytest.fixture
def create_db_engine() -> CreateEngine:
    yield CreateEngine()


@pytest.fixture
async def db_session(db_engine) -> AsyncSession:
    session = AsyncSession(bind=db_engine, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def setup_archive_table(db_session):
    archive_row = ArchivePreview(
        file_id='689665f9-eb57-4029-9fb4-526ce743d1c9',
        archive_preview='{"script.py": {"filename": "script.py", "size": 2550, '
        '"is_dir": false}, "dir2": {"is_dir": true, "script2.py": '
        '{"filename": "script2.py", "size": 1219, "is_dir": false}}}',
    )
    db_session.add(archive_row)
    await db_session.commit()
    yield
    await db_session.delete(archive_row)
    await db_session.commit()
