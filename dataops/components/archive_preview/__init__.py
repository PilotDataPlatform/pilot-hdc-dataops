# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from dataops.components.archive_preview.models import ArchivePreview
from dataops.components.archive_preview.views import router as archive_preview_router

__all__ = [
    'ArchivePreview',
    'archive_preview_router',
]
