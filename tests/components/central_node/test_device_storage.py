# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


from dataops.components.central_node.device_storage import DeviceStorage
from dataops.components.central_node.device_storage import UploadData
from tests.fixtures.fake import Faker


class TestDeviceStorage:

    async def test_save_upload_data_returns_unique_key(self, storage: DeviceStorage, fake: Faker) -> None:
        data = UploadData(
            file_id=fake.uuid4(),
            project_code=fake.project_code(),
            job_id=fake.uuid4(),
            session_id=fake.uuid4(),
            operator=fake.user_name(),
            device_code=fake.pystr(),
        )

        key1 = await storage.save_upload_data(data, ttl_seconds=60)
        key2 = await storage.save_upload_data(data, ttl_seconds=60)

        assert key1 != key2

    async def test_save_upload_data_respects_ttl(self, storage: DeviceStorage, fake: Faker):
        data = UploadData(
            file_id=fake.uuid4(),
            project_code=fake.project_code(),
            job_id=fake.uuid4(),
            session_id=fake.uuid4(),
            operator=fake.user_name(),
            device_code=fake.pystr(),
        )
        ttl = 120

        key = await storage.save_upload_data(data, ttl_seconds=ttl)

        remaining_ttl = await storage.redis.ttl(f'{storage.key_prefix}:{key}')
        assert 0 < remaining_ttl <= ttl

    async def test_get_upload_data_returns_upload_data_after_save(self, storage: DeviceStorage, fake: Faker):
        data = UploadData(
            file_id=fake.uuid4(),
            project_code=fake.project_code(),
            job_id=fake.uuid4(),
            session_id=fake.uuid4(),
            operator=fake.user_name(),
            device_code=fake.pystr(),
        )
        key = await storage.save_upload_data(data, ttl_seconds=60)

        result = await storage.get_upload_data(key)

        assert isinstance(result, UploadData)
        assert result == data

    async def test_get_upload_data_returns_none_for_missing_key(self, storage: DeviceStorage, fake: Faker):
        result = await storage.get_upload_data(fake.pystr())
        assert result is None

    async def test_get_upload_data_uses_prefix_in_lookup(self, storage: DeviceStorage, fake: Faker):
        key = fake.pystr()
        data = UploadData(
            file_id=fake.uuid4(),
            project_code=fake.project_code(),
            job_id=fake.uuid4(),
            session_id=fake.uuid4(),
            operator=fake.user_name(),
            device_code=fake.pystr(),
        )
        await storage.redis.set(f'other-prefix:{key}', data.json())

        result = await storage.get_upload_data(key)

        assert result is None

    async def test_delete_upload_data_removes_existing_key(self, storage: DeviceStorage, fake: Faker):
        data = UploadData(
            file_id=fake.uuid4(),
            project_code=fake.project_code(),
            job_id=fake.uuid4(),
            session_id=fake.uuid4(),
            operator=fake.user_name(),
            device_code=fake.pystr(),
        )
        key = await storage.save_upload_data(data, ttl_seconds=60)

        await storage.delete_upload_data(key)

        result = await storage.get_upload_data(key)
        assert result is None
