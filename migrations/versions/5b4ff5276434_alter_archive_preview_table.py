# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

"""add index to file_id, alter archive_preview to jsonb.

Revision ID: 5b4ff5276434
Revises: ebd1730ac381
Create Date: 2022-11-12 12:02:23.778705
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5b4ff5276434'
down_revision = 'ebd1730ac381'
branch_labels = None
depends_on = 'ebd1730ac381'


def upgrade() -> None:
    op.alter_column('archive_preview', 'archive_preview', postgresql.JSONB(astext_type=sa.Text()))
    op.create_index(op.f('ix_archive_preview_file_id'), 'archive_preview', ['file_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_archive_preview_file_id'), table_name='archive_preview')
    op.alter_column('archive_preview', 'archive_preview', sa.VARCHAR)
