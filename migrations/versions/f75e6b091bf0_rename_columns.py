"""rename columns

Revision ID: f75e6b091bf0
Revises: 
Create Date: 2026-11-14 14:17:38.975752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f75e6b091bf0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('outage_groups', 'schedule_hash', new_column_name='today_schedule_hash')
    op.alter_column('outage_groups', 'schedule_json', new_column_name='today_schedule_json')


def downgrade() -> None:
    """Downgrade schema."""
    pass
