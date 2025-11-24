# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

import base64
import logging
from functools import lru_cache

from pydantic import BaseSettings
from pydantic import Extra


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'dataops_service'
    VERSION = '2.5.8'
    PORT: int = 5063
    HOST: str = '127.0.0.1'
    WORKERS: int = 1
    RELOAD: bool = False

    LOGGING_LEVEL: int = logging.INFO
    LOGGING_FORMAT: str = 'json'

    GREEN_ZONE_LABEL: str = 'Greenroom'
    CORE_ZONE_LABEL: str = 'Core'

    QUEUE_SERVICE: str
    METADATA_SERVICE: str
    AUTH_SERVICE: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

    RDS_HOST: str
    RDS_PORT: str
    RDS_USERNAME: str
    RDS_PASSWORD: str
    RDS_NAME: str
    RDS_SCHEMA: str
    RDS_TABLE_NAME: str = 'archive_preview'
    RDS_ECHO_SQL_QUERIES: bool = False
    RDS_PRE_PING: bool = True

    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    RSA_PUBLIC_KEY: str

    SSE_PING_INTERVAL: int = 5

    def __init__(self):
        super().__init__()
        self.QUEUE_SERVICE = self.QUEUE_SERVICE + '/v1/'
        self.METADATA_SERVICE = self.METADATA_SERVICE + '/v1/'
        self.RSA_PUBLIC_KEY = bytes.decode(base64.b64decode(self.RSA_PUBLIC_KEY), 'utf-8').replace(r'\n', '\n')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = get_settings()
