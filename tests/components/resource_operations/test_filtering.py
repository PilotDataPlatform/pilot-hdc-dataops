# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from dataops.components.resource_operations.filtering import Item
from dataops.components.resource_operations.filtering import ItemFilter
from dataops.components.resource_operations.schemas import ResourceType


class TestItem:
    def test_id_returns_item_id(self, create_item):
        item = create_item()
        expected_id = item['id']

        assert item.id == expected_id

    def test_name_returns_item_name(self, create_item):
        item = create_item()
        expected_name = item['name']

        assert item.name == expected_name


class TestItemFiltering:
    def test_new_instance_converts_list_values_into_source_instances(self):
        items = ItemFilter([{'key': 'value'}])

        assert isinstance(items[0], Item)

    def test_ids_returns_set_with_all_item_ids(self, create_item):
        item_1 = create_item()
        item_2 = create_item()
        items = ItemFilter([item_1, item_2])
        expected_ids = {item_1.id, item_2.id}

        assert expected_ids == items.ids

    def test_names_returns_list_with_all_item_names(self, create_item):
        item_1 = create_item()
        item_2 = create_item()
        items = ItemFilter([item_1, item_2])
        expected_names = [item_1.name, item_2.name]

        assert expected_names == items.names

    def test_filter_folders_returns_sources_with_folder_resource_type(self, create_item):
        expected_item = create_item(resource_type=ResourceType.FOLDER)

        sources = ItemFilter([create_item(resource_type=ResourceType.FILE), expected_item])

        assert sources.filter_folders() == [expected_item]

    def test_filter_files_returns_sources_with_file_resource_type(self, create_item):
        expected_item = create_item(resource_type=ResourceType.FILE)
        sources = ItemFilter([create_item(resource_type=ResourceType.FOLDER), expected_item])

        assert sources.filter_files() == [expected_item]
