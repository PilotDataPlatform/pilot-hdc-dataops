# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from typing import List

from common import LoggerFactory

from dataops.components.cache import Cache
from dataops.components.resource_lock.schemas import ResourceLockBulkResponseSchema
from dataops.components.resource_lock.schemas import ResourceLockResponseSchema
from dataops.config import ConfigClass

logger = LoggerFactory(
    'resource_lock',
    level_default=ConfigClass.LOG_LEVEL_DEFAULT,
    level_file=ConfigClass.LOG_LEVEL_FILE,
    level_stdout=ConfigClass.LOG_LEVEL_STDOUT,
    level_stderr=ConfigClass.LOG_LEVEL_STDERR,
).get_logger()


class ResourceLockerCache(Cache):
    """Manages resource operation locking and unlocking and their respective lock statuses."""

    def str_to_int_list(self, input_: bytes) -> List[int]:
        """Return decoded strings as a list of integers."""
        return [int(x) for x in input_.decode('utf-8').split(',')]

    def int_list_to_str(self, input_: List[int]) -> str:
        """Return joined list as a string with delimiter."""
        return ','.join([str(x) for x in input_])

    async def perform_bulk_lock(self, keys: List[str], operation: str) -> ResourceLockBulkResponseSchema:
        """Perform bulk lock for multiple keys.

        If one of the lock attempts fails, the locking attempts of the following keys are stopped.
        """

        keys = sorted(keys)
        status = []
        have_failed_lock = False

        for key in keys:
            if have_failed_lock:
                status.append((key, False))
                continue

            is_successful = await self.perform_rw_lock(key, operation)
            status.append((key, is_successful.status))

            if not is_successful:
                have_failed_lock = True

        return ResourceLockBulkResponseSchema(keys_status=status)

    async def perform_bulk_unlock(self, keys: List[str], operation: str) -> ResourceLockBulkResponseSchema:
        """Perform bulk unlock for multiple keys."""

        keys = sorted(keys)
        status = []

        for key in keys:
            is_successful = await self.perform_rw_unlock(key, operation)
            status.append((key, is_successful.status))

        return ResourceLockBulkResponseSchema(keys_status=status)

    async def perform_rw_lock(self, key: str, operation: str) -> ResourceLockResponseSchema:
        """
        Description:
            An async function will do the read/write lock on the key.
            Inside Redis, the entry will be key:"<read_count>, <write_count>"(no bracket)
            read_count will be >=0, while write_count CAN ONLY be 0 or 1.
            ----
            The read count will increase one, if there is a new read operation
            (eg. download). Once the operation finish, the count will decrease one.
            During the read operation, other read operation will proceed as well.
            But write operation is not allowed.
            ---
            The write will increase one, if there a write operation(eg.delete). And
            any other operation will be blocked.
            ---
            Therefore, the value pairs will be (N, 0), (0, 1). Also to avoid the racing
            condition, the await keyword will be used for the function.
        Parameters:
            - key: the object path in minio (eg. <bucket>/file.py)
            - operation: either read or write
        Return:
            - True: the lock operation is success
            - False: the other operation blocks the current one
        """
        if await self.is_exist(key):
            rw_str = await self.get(key)
            # index 0 is read_count, index 1 is write_count
            read_count, write_count = tuple(self.str_to_int_list(rw_str))
            logger.info(f'Found key:{key}, with r/w {read_count}/{write_count}')

            # read_count > 0 -> block write
            if read_count > 0 and operation == 'write':
                return ResourceLockResponseSchema(key=key)
            # write_count > 0 -> block all
            elif write_count > 0:
                return ResourceLockResponseSchema(key=key)

        # TODO might refactor here later
        if operation == 'read':
            # check if the key exist, if not exist then create pair with (1,0)
            # else increase the read count(index 0) by one
            if await self.is_exist(key):
                rw_str = await self.get(key)
                read_count, write_count = tuple(self.str_to_int_list(rw_str))
                await self.set(key, self.int_list_to_str([read_count + 1, write_count]))
            else:
                await self.set(key, '1,0')

        else:
            await self.set(key, '0,1')

        logger.info(f'Add {operation} lock to {key}')

        return ResourceLockResponseSchema(key=key, status=True)

    async def perform_rw_unlock(self, key: str, operation: str) -> ResourceLockResponseSchema:
        """
        Description:
            An async function to reduce the read_write count based on key.
            ---
            Read count can be "N,0", so each operation will do N-1. if count is
            "1,0" then function will remove the entry for cleanup
            ---
            Write count can only be "0,1", so function will just remove it. BUT
            to check the validation, the pair must be "0,1". Otherwise, we might
            remove the read count by accident.
            ---
            Also to avoid the racing issue, we use the awwait
        Parameters:
            - key: the object path in minio (eg. <bucket>/file.py)
            - operation: either read or write
        Return:
            - True: the lock operation is success
            - False: the other operation blocks the current one
        """
        # we cannot unlock the IDLE file
        if not await self.is_exist(key):
            return ResourceLockResponseSchema(key=key)

        # TODO: might need some check here
        # delete cannot just remove the entry
        rw_str = await self.get(key)
        read_count, write_count = tuple(self.str_to_int_list(rw_str))
        logger.info(f'Found key:{key}, with r/w {read_count}/{write_count}')
        if operation == 'read':
            # if the current read operation is the last one
            # then we just remove the entry for cleanup
            if read_count > 1:
                await self.set(key, self.int_list_to_str([read_count - 1, write_count]))
            else:
                await self.delete(key)

        else:
            # corner case if there are some read operation ongoing(readcount>0)
            # we should block the delete on the key
            if read_count > 0:
                return ResourceLockResponseSchema(key=key)
            else:
                await self.delete(key)

        logger.info(f'Remove {operation} lock to {key}')

        return ResourceLockResponseSchema(key=key, status=True)

    async def check_lock_status(self, key: str) -> ResourceLockResponseSchema:
        """Returns respective key lock status."""
        value = await self.get(key)
        status_decode = value.decode() if value else None
        return ResourceLockResponseSchema(key=key, status=status_decode)
