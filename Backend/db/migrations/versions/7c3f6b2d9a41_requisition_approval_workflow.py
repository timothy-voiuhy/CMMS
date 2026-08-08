"""add requisition approver assignment and notifications

Revision ID: 7c3f6b2d9a41
Revises: eb1eee384a95
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c3f6b2d9a41"
down_revision: Union[str, None] = "eb1eee384a95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "inventory_requisitions",
        sa.Column("approver_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_inventory_requisitions_approver_id",
        "inventory_requisitions",
        ["approver_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_inventory_requisitions_approver_id_users",
        "inventory_requisitions",
        "users",
        ["approver_id"],
        ["id"],
    )

    op.create_table(
        "notifications",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("link", sa.String(length=500), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"], unique=False)
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)
    op.create_index("ix_notifications_type", "notifications", ["type"], unique=False)
    op.create_index("ix_notifications_read", "notifications", ["read"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notifications_read", table_name="notifications")
    op.drop_index("ix_notifications_type", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_constraint(
        "fk_inventory_requisitions_approver_id_users",
        "inventory_requisitions",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_inventory_requisitions_approver_id",
        table_name="inventory_requisitions",
    )
    op.drop_column("inventory_requisitions", "approver_id")
