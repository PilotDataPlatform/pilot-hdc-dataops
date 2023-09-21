# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from uuid import UUID

from pydantic import BaseModel
from pydantic import Json


class ArchivePreviewSchema(BaseModel):
    """General archive peview schema."""

    file_id: UUID
    archive_preview: dict


class ArchivePreviewResponseSchema(ArchivePreviewSchema):
    """Default schema for single workbench in response."""

    archive_preview: Json

    class Config:
        orm_mode = True


class ArchivePreviewDeleteSchema(BaseModel):
    file_id: UUID
