# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from uuid import UUID

from sqlalchemy import select

from dataops.components.archive_preview.models import ArchivePreview
from dataops.components.crud import CRUD


class ArchivePreviewCRUD(CRUD):
    """CRUD for managing dataops database models."""

    model = ArchivePreview

    async def retrieve_by_file_id(self, file_id: UUID) -> ArchivePreview:
        """Get an existing archive_preview by unique code."""

        statement = select(self.model).where(self.model.file_id == file_id)

        archive_preview = await self._retrieve_one(statement)

        return archive_preview
