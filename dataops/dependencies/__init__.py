# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from dataops.dependencies.db import get_db_session
from dataops.dependencies.redis import get_redis

__all__ = ['get_redis', 'get_db_session']
