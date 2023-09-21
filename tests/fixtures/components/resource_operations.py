# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import random
import time
import uuid
from typing import Any
from typing import Callable

import pytest

from dataops.components.resource_operations.crud.base import BaseResourceProcessing
from dataops.components.resource_operations.filtering import Item
from dataops.components.resource_operations.schemas import ResourceType


@pytest.fixture
def get_BaseResourceProcessing(metadata_service, queue_service, redis):
    yield BaseResourceProcessing(metadata_service, queue_service, redis)


@pytest.fixture
def create_item(fake) -> Callable[..., Item]:
    def _create_item(
        id_=None,
        name=None,
        resource_type=None,
        **kwds: Any,
    ) -> Item:
        if id_ is None:
            id_ = f'{uuid.uuid4()}-{round(time.time())}'

        if name is None:
            name = fake.word()

        if resource_type is None:
            resource_type = random.choice(list(ResourceType))

        return Item(
            {
                'id': id_,
                'name': name,
                'type': resource_type,
                **kwds,
            }
        )

    return _create_item
