# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID

from dataops.components import DBModel
from dataops.config import ConfigClass


class ArchivePreview(DBModel):
    __tablename__ = ConfigClass.RDS_TABLE_NAME
    __table_args__ = {'schema': ConfigClass.RDS_SCHEMA}
    id = Column(BigInteger, primary_key=True)
    file_id = Column(UUID(as_uuid=True), unique=True, index=True, nullable=False)
    archive_preview = Column(JSONB())

    def __init__(self, file_id, archive_preview):
        self.file_id = file_id
        self.archive_preview = archive_preview
