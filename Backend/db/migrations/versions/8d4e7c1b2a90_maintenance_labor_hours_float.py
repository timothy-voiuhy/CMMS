"""store maintenance labor hours as a fractional value

Revision ID: 8d4e7c1b2a90
Revises: 7c3f6b2d9a41
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d4e7c1b2a90"
down_revision: Union[str, None] = "7c3f6b2d9a41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "maintenance_reports",
        "labor_hours",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=True,
        postgresql_using="labor_hours::double precision",
    )


def downgrade() -> None:
    op.alter_column(
        "maintenance_reports",
        "labor_hours",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="round(labor_hours)::integer",
    )
