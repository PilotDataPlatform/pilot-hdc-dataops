# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from typing import Any
from typing import Dict
from typing import List
from typing import Set

from dataops.components.resource_operations.schemas import ResourceType


class Item(dict):
    """Encapsulate single metadata item."""

    @property
    def id(self) -> str:
        """Return item id."""
        return self['id']

    @property
    def name(self) -> str:
        """Return item name."""
        return self['name']


class ItemFilter(list):
    """Filter metadata items."""

    def __init__(self, items: List[Dict[str, Any]]) -> None:
        super().__init__([Item(item) for item in items])

    @property
    def ids(self) -> Set[str]:
        """Return item ids."""
        return {item.id for item in self}

    @property
    def names(self) -> List[str]:
        """Return item names."""
        return [item.name for item in self]

    @property
    def target_type(self) -> str:
        """Returns type of item target or batch if multiple items are targets."""
        item_type = self[0]['type'] if len(self) == 1 else 'batch'
        return item_type

    def _get_by_resource_type(self, resource_type: ResourceType) -> List[Item]:
        """Validates source type against defined resource types."""
        return [source for source in self if source['type'] == resource_type]

    def filter_folders(self) -> List[Item]:
        """Returns items with folder resource type."""
        return self._get_by_resource_type(ResourceType.FOLDER)

    def filter_files(self) -> List[Item]:
        """Returns items with file resource type."""
        return self._get_by_resource_type(ResourceType.FILE)
