# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from datetime import timedelta
from typing import Any
from typing import Optional
from typing import Type
from typing import Union
from uuid import UUID

from pydantic import BaseModel
from redis.asyncio.client import Redis
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.engine import Result
from sqlalchemy.engine import ScalarResult
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Executable
from sqlalchemy.sql import Select

from dataops.components.db_model import DBModel
from dataops.components.exceptions import AlreadyExists
from dataops.components.exceptions import NotFound
from dataops.components.exceptions import ServiceException
from dataops.components.exceptions import UnhandledException


class CRUD:
    """Base CRUD class for managing database models."""

    session: AsyncSession
    model: Type[DBModel]
    db_error_codes: dict[str, ServiceException] = {
        '23503': NotFound(),  # missing foreign key
        '23505': AlreadyExists(),  # duplicated entry
    }

    def __init__(self, db_session: AsyncSession) -> None:
        self.session = db_session
        self.transaction = None

    async def __aenter__(self) -> 'CRUD':
        """Start a new transaction."""

        self.transaction = self.session.begin_nested()
        await self.transaction.__aenter__()

        return self

    async def __aexit__(self, *args: Any) -> None:
        """Commit an existing transaction."""

        await self.transaction.__aexit__(*args)

        return None

    @property
    def select_query(self) -> Select:
        """Create base select."""
        return select(self.model)

    async def execute(self, statement: Executable, **kwds: Any) -> Union[CursorResult, Result]:
        """Execute a statement and return buffered result."""

        return await self.session.execute(statement, **kwds)

    async def scalars(self, statement: Executable, **kwds: Any) -> ScalarResult:
        """Execute a statement and return scalar result."""

        return await self.session.scalars(statement, **kwds)

    async def _create_one(self, statement: Executable) -> Union[UUID, str]:
        """Execute a statement to create one entry."""

        try:
            result = await self.execute(statement)
            return result.inserted_primary_key.id
        except Exception as e:
            if isinstance(e, DBAPIError):
                pg_code = e.orig.pgcode
                if pg_code in self.db_error_codes:
                    raise self.db_error_codes.get(pg_code)
            raise UnhandledException()

    async def _retrieve_one(self, statement: Executable) -> DBModel:
        """Execute a statement to retrieve one entry."""

        result = await self.scalars(statement)
        instance = result.first()

        if instance is None:
            raise NotFound()

        return instance

    async def _delete_one(self, statement: Executable) -> None:
        """Execute a statement to delete one entry."""

        result = await self.execute(statement)

        if result.rowcount == 0:
            raise NotFound()

    async def create(self, entry_create: BaseModel, **kwds: Any) -> DBModel:
        """Create a new entry."""
        values = entry_create.dict()
        statement = insert(self.model).values(**(values | kwds))
        entry_id = await self._create_one(statement)

        entry = await self.retrieve_by_id(entry_id)

        return entry

    async def retrieve_by_id(self, id_: UUID) -> DBModel:
        """Get an existing entry by id (primary key)."""

        statement = self.select_query.where(self.model.id == id_)
        entry = await self._retrieve_one(statement)

        return entry

    async def delete(self, id_: UUID) -> None:
        """Remove an existing entry."""

        statement = delete(self.model).where(self.model.id == id_)

        await self._delete_one(statement)


class RedisCRUD:
    """Base CRUD class for managing Redis."""

    def __init__(self, redis: Redis) -> None:
        self.__instance = redis

    async def ping(self) -> bool:
        """Checks if connection is alive."""
        return await self.__instance.ping()

    async def get_by_key(self, key: str) -> bytes:
        """Retrieve record by key."""
        return await self.__instance.get(key)

    async def set_by_key(self, key: str, content: str, expire: int = Optional[None]) -> bool:
        """Create record by key and respective value."""
        expire_time = timedelta(hours=expire) if expire else None
        res = await self.__instance.set(key, content, ex=expire_time)
        return res

    async def mget_by_prefix(self, prefix: str) -> bytes:
        """Query to find key with pattern and retrieve respective record."""
        query = '{}:*'.format(prefix)
        keys = await self.__instance.keys(query)
        return await self.__instance.mget(keys)

    async def delete_by_key(self, key: str) -> int:
        """Delete record by key."""
        return await self.__instance.delete(key)

    async def unlink_by_key(self, key: str) -> int:
        """Unlinks the key from the keyspace."""
        return await self.__instance.unlink(key)

    async def mdele_by_prefix(self, prefix: str) -> list:
        """Query to find key with pattern and delete respective record."""
        query = '{}:*'.format(prefix)
        keys = await self.__instance.keys(query)
        results = []
        for key in keys:
            res = await self.delete_by_key(key)
            results.append(res)
        return results

    async def publish(self, channel: str, data: str) -> int:
        """Publish data to a channel."""
        res = await self.__instance.publish(channel, data)
        return res

    async def streams_xadd(self, key: str, values: dict, id_arg: str = '*') -> bytes:
        """Add data to stream."""
        return await self.__instance.xadd(name=key, fields=values, id=id_arg)

    async def streams_xread(self, key: str, offset: str, block=None, count: int = None) -> list:
        """Read data from stream."""
        return await self.__instance.xread(streams={key: offset}, block=block, count=count)

    async def streams_scan(self, cursor: int = 0, pattern: str = None, count: int = None):
        """Search Redis for streams.

        cursor: an iteration starts when cursor is 0 and terminates when cursor returned by the server is 0
        count: the amount of work that should be done at every call in order to retrieve elements from the collection
        pattern: a filter applied after elements are retrieved from the collection
        """
        unique_streams = set()
        while True:  # iterate until all matches are found
            cursor, streams = await self.__instance.scan(cursor, pattern, count, 'STREAM')
            for stream in streams:
                unique_streams.add(stream)
            if cursor == 0:
                return unique_streams
