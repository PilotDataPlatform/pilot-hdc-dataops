# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dataops.components.archive_preview.crud import ArchivePreviewCRUD
from dataops.dependencies import get_db_session


def get_archive_preview_crud(db_session: AsyncSession = Depends(get_db_session)) -> ArchivePreviewCRUD:
    """Return an instance of ArchivePreviewCRUD as a dependency."""

    return ArchivePreviewCRUD(db_session)
