# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Request

from dataops.components.exceptions import Unauthorized


class Authorization:
    """Manage authorization for requests."""

    def __init__(self, request: Request):
        self.request = request

    async def jwt_required(self) -> str:
        token = self.request.headers.get('Authorization')
        if not token:
            raise Unauthorized()
        return token.split()[-1]
