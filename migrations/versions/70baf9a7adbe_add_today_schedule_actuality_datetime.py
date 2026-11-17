"""add today schedule actuality datetime

Revision ID: 70baf9a7adbe
Revises: f75e6b091bf0
Create Date: 2026-11-17 13:25:30.432028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70baf9a7adbe'
down_revision: Union[str, Sequence[str], None] = 'f75e6b091bf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('outage_groups',
                  sa.Column('schedule_actuality', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
