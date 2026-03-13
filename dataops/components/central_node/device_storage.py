# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import secrets
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from dataops.config import Settings
from dataops.config import get_settings
from dataops.dependencies import get_redis


class UploadData(BaseModel):
    file_id: UUID
    project_code: str
    job_id: UUID
    session_id: str
    operator: str
    device_code: str


class DeviceStorage:
    def __init__(self, redis: Redis, key_prefix: str) -> None:
        self.redis = redis
        self.key_prefix = key_prefix

    async def save_upload_data(self, data: UploadData, ttl_seconds: int) -> str:
        key = secrets.token_hex(32)
        await self.redis.set(f'{self.key_prefix}:{key}', data.json(), ex=ttl_seconds)
        return key

    async def get_upload_data(self, key: str) -> UploadData | None:
        raw = await self.redis.get(f'{self.key_prefix}:{key}')
        if raw is None:
            return None
        return UploadData.parse_raw(raw)

    async def delete_upload_data(self, key: str) -> None:
        await self.redis.delete(f'{self.key_prefix}:{key}')


def get_device_storage(redis: Redis = Depends(get_redis), settings: Settings = Depends(get_settings)) -> DeviceStorage:
    return DeviceStorage(redis, settings.CENTRAL_NODE_DEVICE_AUTH_STORAGE_KEY_PREFIX)
