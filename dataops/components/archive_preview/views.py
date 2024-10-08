# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from dataops.components.archive_preview.crud import ArchivePreviewCRUD
from dataops.components.archive_preview.dependencies import get_archive_preview_crud
from dataops.components.archive_preview.schemas import ArchivePreviewDeleteSchema
from dataops.components.archive_preview.schemas import ArchivePreviewResponseSchema
from dataops.components.archive_preview.schemas import ArchivePreviewSchema
from dataops.logger import logger

router = APIRouter(prefix='/archive', tags=['Archive Preview'])


@router.get('', summary='Get a archive preview given file id', response_model=ArchivePreviewResponseSchema)
async def get_archive_preview(
    file_id: Union[UUID, str], archive_preview_crud: ArchivePreviewCRUD = Depends(get_archive_preview_crud)
) -> ArchivePreviewResponseSchema:
    """Get an archive preview by id or code."""

    logger.info(f'Get archive preview for: {file_id}')
    async with archive_preview_crud:
        archive_preview = await archive_preview_crud.retrieve_by_file_id(file_id)

    return archive_preview


@router.post('', summary='Create a new archive preview.', response_model=ArchivePreviewResponseSchema)
async def create_archive_preview(
    body: ArchivePreviewSchema, archive_preview_crud: ArchivePreviewCRUD = Depends(get_archive_preview_crud)
) -> ArchivePreviewResponseSchema:
    """Create a new archive preview."""

    async with archive_preview_crud:
        archive_preview = await archive_preview_crud.create(body)

    return archive_preview


@router.delete('', summary='Delete a new archive preview by file_id.')
async def delete_archive_preview(
    body: ArchivePreviewDeleteSchema, archive_preview_crud: ArchivePreviewCRUD = Depends(get_archive_preview_crud)
) -> Response:
    """Delete a new archive preview by file_id."""

    async with archive_preview_crud:
        archive_preview = await archive_preview_crud.retrieve_by_file_id(body.file_id)
        await archive_preview_crud.delete(archive_preview.id)

    return Response(status_code=204)
