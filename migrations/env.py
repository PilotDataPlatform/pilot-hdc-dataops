# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import logging
from logging.config import fileConfig
from typing import Optional
from urllib.parse import urlparse

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from dataops.components import DBModel
from dataops.config import get_settings

logger = logging.getLogger('alembic')

config = context.config
fileConfig(config.config_file_name)
settings = get_settings()

target_metadata = DBModel.metadata
database_schema = config.get_main_option('database_schema', settings.RDS_SCHEMA)
database_uri = config.get_main_option(
    'database_uri',
    f'postgresql://{settings.RDS_USERNAME}:'
    f'{settings.RDS_PASSWORD}@{settings.RDS_HOST}:'
    f'{settings.RDS_PORT}/{settings.RDS_NAME}',
)


def include_name(name: Optional[str], type_: str, parent_names: dict[str, Optional[str]]) -> bool:
    """Consider only tables from desired schema."""

    if type_ == 'schema':
        return name == database_schema

    return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    url = database_uri.replace(f'{urlparse(database_uri).scheme}://', 'postgresql://', 1)
    connectable = create_engine(url, poolclass=NullPool, echo=settings.RDS_ECHO_SQL_QUERIES)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=database_schema,
            include_schemas=True,
            include_name=include_name,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.execute(f'CREATE SCHEMA IF NOT EXISTS {database_schema}')
            context.run_migrations()


if context.is_offline_mode():
    logger.error('Offline migrations environment is not supported.')
    exit(1)

run_migrations_online()
