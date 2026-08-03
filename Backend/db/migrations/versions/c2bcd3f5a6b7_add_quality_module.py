"""add quality module

Revision ID: c2bcd3f5a6b7
Revises: b1cde3f4a5b6
Create Date: 2026-08-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2bcd3f5a6b7'
down_revision = 'b1cde3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create quality_inspections table
    op.create_table('quality_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inspection_number', sa.String(length=50), nullable=False),
        sa.Column('production_order_id', sa.Integer(), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('inspection_type', sa.String(length=100), nullable=False),
        sa.Column('inspection_date', sa.DateTime(), nullable=False),
        sa.Column('inspector_id', sa.Integer(), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('defects_found', sa.Integer(), nullable=True),
        sa.Column('specifications', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', name='inspectionstatus'), nullable=False),
        sa.Column('result', sa.Enum('pass', 'fail', 'conditional', 'pending', name='inspectionresult'), nullable=False),
        sa.Column('pass_rate', sa.Float(), nullable=True),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quality_inspections_id'), 'quality_inspections', ['id'], unique=False)
    op.create_index(op.f('ix_quality_inspections_inspection_number'), 'quality_inspections', ['inspection_number'], unique=True)

    # Create quality_inspection_items table
    op.create_table('quality_inspection_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inspection_id', sa.Integer(), nullable=False),
        sa.Column('checkpoint_name', sa.String(length=200), nullable=False),
        sa.Column('specification', sa.String(length=500), nullable=True),
        sa.Column('measured_value', sa.String(length=200), nullable=True),
        sa.Column('result', sa.Enum('pass', 'fail', 'conditional', 'pending', name='inspectionresult'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['inspection_id'], ['quality_inspections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quality_inspection_items_id'), 'quality_inspection_items', ['id'], unique=False)

    # Create non_conformance_reports table
    op.create_table('non_conformance_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ncr_number', sa.String(length=50), nullable=False),
        sa.Column('inspection_id', sa.Integer(), nullable=True),
        sa.Column('production_order_id', sa.Integer(), nullable=True),
        sa.Column('equipment_id', sa.Integer(), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.Enum('critical', 'major', 'minor', name='ncrseverity'), nullable=False),
        sa.Column('status', sa.Enum('open', 'investigating', 'corrective_action', 'closed', 'rejected', name='ncrstatus'), nullable=False),
        sa.Column('reported_by_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('corrective_action', sa.Text(), nullable=True),
        sa.Column('preventive_action', sa.Text(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ),
        sa.ForeignKeyConstraint(['inspection_id'], ['quality_inspections.id'], ),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ),
        sa.ForeignKeyConstraint(['reported_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_non_conformance_reports_id'), 'non_conformance_reports', ['id'], unique=False)
    op.create_index(op.f('ix_non_conformance_reports_ncr_number'), 'non_conformance_reports', ['ncr_number'], unique=True)

    # Create quality_metrics table
    op.create_table('quality_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_inspections', sa.Integer(), nullable=True),
        sa.Column('passed_inspections', sa.Integer(), nullable=True),
        sa.Column('failed_inspections', sa.Integer(), nullable=True),
        sa.Column('pass_rate', sa.Float(), nullable=True),
        sa.Column('total_ncrs', sa.Integer(), nullable=True),
        sa.Column('open_ncrs', sa.Integer(), nullable=True),
        sa.Column('closed_ncrs', sa.Integer(), nullable=True),
        sa.Column('defect_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quality_metrics_id'), 'quality_metrics', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_quality_metrics_id'), table_name='quality_metrics')
    op.drop_table('quality_metrics')
    op.drop_index(op.f('ix_non_conformance_reports_ncr_number'), table_name='non_conformance_reports')
    op.drop_index(op.f('ix_non_conformance_reports_id'), table_name='non_conformance_reports')
    op.drop_table('non_conformance_reports')
    op.drop_index(op.f('ix_quality_inspection_items_id'), table_name='quality_inspection_items')
    op.drop_table('quality_inspection_items')
    op.drop_index(op.f('ix_quality_inspections_inspection_number'), table_name='quality_inspections')
    op.drop_index(op.f('ix_quality_inspections_id'), table_name='quality_inspections')
    op.drop_table('quality_inspections')
