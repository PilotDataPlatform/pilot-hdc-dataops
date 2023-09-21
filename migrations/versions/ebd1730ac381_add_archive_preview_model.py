# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

"""add_archive_preview_model.

Revision ID: ebd1730ac381
Revises:
Create Date: 2022-07-05 13:38:12.607701
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ebd1730ac381'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'archive_preview',
        sa.Column('id', sa.BigInteger),
        sa.Column('file_id', postgresql.UUID(as_uuid=True)),
        sa.Column('archive_preview', sa.VARCHAR),
        sa.PrimaryKeyConstraint('id'),
        schema='public',
    )


def downgrade() -> None:
    op.drop_table('archive_preview', schema='public')
