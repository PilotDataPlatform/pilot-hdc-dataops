# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


class TestCache:
    async def test_set_stores_value_by_key(self, fake, cache):
        key = fake.pystr()
        value = fake.binary(10)

        result = await cache.set(key, value)
        assert result is True

        result = await cache.get(key)
        assert result == value

    async def test_get_returns_value_by_key(self, fake, cache):
        key = fake.pystr()
        value = fake.binary(10)
        await cache.set(key, value)

        result = await cache.get(key)
        assert result == value

    async def test_get_returns_none_if_key_does_not_exist(self, fake, cache):
        key = fake.pystr()

        result = await cache.get(key)
        assert result is None

    async def test_delete_removes_value_by_key(self, fake, cache):
        key = fake.pystr()
        value = fake.pystr()
        await cache.set(key, value)

        result = await cache.delete(key)
        assert result is True

        result = await cache.get(key)
        assert result is None

    async def test_delete_returns_false_if_key_did_not_exist(self, fake, cache):
        key = fake.pystr()

        result = await cache.delete(key)
        assert result is False

    async def test_is_exist_returns_true_if_key_exists(self, fake, cache):
        key = fake.pystr()
        value = fake.pystr()
        await cache.set(key, value)

        result = await cache.is_exist(key)
        assert result is True

    async def test_is_exist_returns_false_if_key_does_not_exist(self, fake, cache):
        key = fake.pystr()

        result = await cache.is_exist(key)
        assert result is False
