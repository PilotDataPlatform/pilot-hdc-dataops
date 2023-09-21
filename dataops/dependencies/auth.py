# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from common import JWTHandler
from fastapi import Request

from dataops.components.exceptions import Unauthorized


class AuthManager:
    def __init__(self, settings) -> None:
        self.AUTH_SERVICE = settings.AUTH_SERVICE
        self.jwt_handler = JWTHandler(settings.RSA_PUBLIC_KEY)

    async def get_current_identity(self, request: Request) -> dict:
        try:
            encoded_token = self.jwt_handler.get_token(request)
            decoded_token = self.jwt_handler.decode_validate_token(encoded_token)
            current_identity = await self.jwt_handler.get_current_identity(self.AUTH_SERVICE, decoded_token)
        except Exception:
            raise Unauthorized()
        return current_identity
