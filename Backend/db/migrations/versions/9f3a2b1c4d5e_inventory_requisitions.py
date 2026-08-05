"""inventory requisitions

Revision ID: 9f3a2b1c4d5e
Revises: b379a6c90f50
Create Date: 2026-08-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f3a2b1c4d5e'
down_revision: Union[str, None] = 'b379a6c90f50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'inventory_requisitions',
        sa.Column('requisition_number', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'PARTIALLY_FULFILLED', 'FULFILLED', 'CANCELLED', name='requisitionstatus'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='requisitionpriority'), nullable=False),
        sa.Column('needed_by', sa.String(length=20), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('work_order_id', sa.Integer(), nullable=True),
        sa.Column('production_order_id', sa.Integer(), nullable=True),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('fulfilled_by', sa.Integer(), nullable=True),
        sa.Column('fulfilled_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['fulfilled_by'], ['users.id']),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id']),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id']),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_requisitions_id'), 'inventory_requisitions', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_requisitions_requisition_number'), 'inventory_requisitions', ['requisition_number'], unique=True)
    op.create_index(op.f('ix_inventory_requisitions_requested_by'), 'inventory_requisitions', ['requested_by'], unique=False)
    op.create_index(op.f('ix_inventory_requisitions_status'), 'inventory_requisitions', ['status'], unique=False)

    op.create_table(
        'inventory_requisition_items',
        sa.Column('requisition_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('requested_quantity', sa.Float(), nullable=False),
        sa.Column('approved_quantity', sa.Float(), nullable=True),
        sa.Column('fulfilled_quantity', sa.Float(), nullable=False),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'PARTIALLY_FULFILLED', 'FULFILLED', 'REJECTED', 'CANCELLED', name='requisitionlinestatus'), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['inventory_items.id']),
        sa.ForeignKeyConstraint(['requisition_id'], ['inventory_requisitions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_requisition_items_id'), 'inventory_requisition_items', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_requisition_items_item_id'), 'inventory_requisition_items', ['item_id'], unique=False)
    op.create_index(op.f('ix_inventory_requisition_items_requisition_id'), 'inventory_requisition_items', ['requisition_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_requisition_items_requisition_id'), table_name='inventory_requisition_items')
    op.drop_index(op.f('ix_inventory_requisition_items_item_id'), table_name='inventory_requisition_items')
    op.drop_index(op.f('ix_inventory_requisition_items_id'), table_name='inventory_requisition_items')
    op.drop_table('inventory_requisition_items')

    op.drop_index(op.f('ix_inventory_requisitions_status'), table_name='inventory_requisitions')
    op.drop_index(op.f('ix_inventory_requisitions_requested_by'), table_name='inventory_requisitions')
    op.drop_index(op.f('ix_inventory_requisitions_requisition_number'), table_name='inventory_requisitions')
    op.drop_index(op.f('ix_inventory_requisitions_id'), table_name='inventory_requisitions')
    op.drop_table('inventory_requisitions')
