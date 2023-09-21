# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from enum import Enum
from enum import unique
from typing import List
from typing import Optional
from typing import Tuple

from pydantic import BaseModel


@unique
class ResourceLockOperationSchema(str, Enum):
    """Operations schema for locking a resource."""

    READ = 'read'
    WRITE = 'write'

    class Config:
        use_enum_values = True


class ResourceLockCreateSchema(BaseModel):
    """Schema for creating resource lock by key and operation."""

    resource_key: str
    operation: ResourceLockOperationSchema


class ResourceLockBulkCreateSchema(BaseModel):
    """Schema for bulk creating resource lock by keys and operations."""

    resource_keys: List[str]
    operation: ResourceLockOperationSchema


class ResourceLockResponseSchema(BaseModel):
    """Schema for key and status of locked resource in response."""

    key: str
    status: Optional[str] = False


class ResourceLockBulkResponseSchema(BaseModel):
    """Schema for status of operation locking for multiple keys."""

    keys_status: List[Tuple[str, bool]]

    def is_successful(self) -> bool:
        """Return true if all statuses are true."""

        return all(status for _, status in self.keys_status)
