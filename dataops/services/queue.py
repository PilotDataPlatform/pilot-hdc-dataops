# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import httpx
from fastapi import Depends

from dataops.components.exceptions import ServiceNotAvailable
from dataops.components.exceptions import UnhandledException
from dataops.config import Settings
from dataops.config import get_settings
from dataops.logger import logger


class QueueService:
    """Client to connect with queue service."""

    def __init__(self, queue_service_url: str) -> None:
        self.service_url = queue_service_url

    async def send_message(self, message: dict) -> dict:
        """Send message to queue service for processing."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url=f'{self.service_url}send_message', json=message)
                response.raise_for_status()

            message_response = response.json()['result']
            return message_response
        except httpx.HTTPStatusError:
            logger.exception(f'Queue service failed to process message: {message}; error {response.text}')
            raise UnhandledException()

        except httpx.RequestError:
            logger.exception(f'Unable to connect to the queue service to send message: {message}')
            raise ServiceNotAvailable()

        except Exception:
            logger.exception(f'Unable to send message: {message}')
            raise UnhandledException()


def get_queue_service(settings: Settings = Depends(get_settings)) -> QueueService:
    """Creates a callable dependency for QueueService instance."""
    return QueueService(settings.QUEUE_SERVICE)
