# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import httpx
from fastapi import Depends

from dataops.components.exceptions import NotFound
from dataops.components.exceptions import ServiceNotAvailable
from dataops.components.exceptions import UnhandledException
from dataops.config import Settings
from dataops.config import get_settings
from dataops.logger import logger


class MetadataService:
    """Client to connect with metadata service."""

    def __init__(self, metadata_service_url: str) -> None:
        self.service_url = metadata_service_url

    async def get_resource_by_id(self, item_id: str) -> dict:
        """Retrieve item from metadata service by item id."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f'{self.service_url}item/{item_id}/')
                response.raise_for_status()

            resource = response.json()['result']
            if not resource:
                raise NotFound()
            return resource

        except httpx.HTTPStatusError:
            logger.exception(f'Metadata service failed to retrieve item": {item_id}; error {response.text}')
            raise UnhandledException()

        except httpx.RequestError:
            logger.exception(f'Unable to connect to the metadata service to retrieve item id: {item_id}')
            raise ServiceNotAvailable()

        except NotFound:
            logger.exception(f'Target resource: {item_id} not found')
            raise

        except Exception:
            logger.exception(f'Unable to retrieve item info: {item_id}')
            raise UnhandledException()


def get_metadata_service(settings: Settings = Depends(get_settings)) -> MetadataService:
    """Creates a callable dependency for MetadataService instance."""
    return MetadataService(settings.METADATA_SERVICE)
