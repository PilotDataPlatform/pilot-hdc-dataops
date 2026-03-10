# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from uuid import UUID

from dataops.components.schemas import BaseSchema


class FileUploadSchema(BaseSchema):
    file_id: UUID
    project_code: str
    job_id: UUID
    session_id: str
    operator: str


class FileUploadResponseSchema(BaseSchema):
    upload_key: str
    login_url: str
