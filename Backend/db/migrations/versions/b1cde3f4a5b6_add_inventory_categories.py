"""add inventory categories

Revision ID: b1cde3f4a5b6
Revises: 93841c847f82
Create Date: 2026-08-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1cde3f4a5b6'
down_revision = '93841c847f82'
branch_labels = None
depends_on = None


def upgrade():
    # Check if inventory_categories table exists (it may have been auto-created)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    
    if 'inventory_categories' not in tables:
        # Create inventory_categories table only if it doesn't exist
        op.create_table(
            'inventory_categories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('parent_id', sa.Integer(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['parent_id'], ['inventory_categories.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Check if category_id column already exists
    columns = [col['name'] for col in inspector.get_columns('inventory_items')]
    
    if 'category_id' in columns:
        # Migration already applied, skip
        return
    
    # Check if there are existing inventory items
    result = bind.execute(sa.text("SELECT COUNT(*) as count FROM inventory_items")).fetchone()
    has_items = result[0] > 0
    
    if has_items:
        # Only create default migration categories if there are existing items to migrate
        # These are temporary categories for data migration only
        op.execute("""
            INSERT INTO inventory_categories (name, description, is_active, created_at, updated_at) VALUES
            ('Raw Materials', 'Raw materials for production', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Work in Progress', 'Products currently in production', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Finished Goods', 'Completed products ready for sale', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Spare Parts', 'Equipment spare parts and components', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Tools', 'Tools and equipment', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Consumables', 'Consumable items', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Packaging', 'Packaging materials', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """)
    
    # Use batch mode for SQLite to add column and foreign key
    with op.batch_alter_table('inventory_items', schema=None) as batch_op:
        # Add category_id column (nullable first)
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        
    if has_items:
        # Migrate data (outside batch mode)
        op.execute("""
            UPDATE inventory_items
            SET category_id = (
                SELECT id FROM inventory_categories 
                WHERE name = CASE 
                    WHEN category = 'raw_material' THEN 'Raw Materials'
                    WHEN category = 'wip' THEN 'Work in Progress'
                    WHEN category = 'finished_good' THEN 'Finished Goods'
                    WHEN category = 'spare_part' THEN 'Spare Parts'
                    WHEN category = 'tool' THEN 'Tools'
                    WHEN category = 'consumable' THEN 'Consumables'
                    WHEN category = 'packaging' THEN 'Packaging'
                END
                LIMIT 1
            )
        """)
    
    # Make category_id NOT NULL and add foreign key, drop old column
    with op.batch_alter_table('inventory_items', schema=None) as batch_op:
        if has_items:
            batch_op.alter_column('category_id', nullable=False)
        batch_op.create_foreign_key('fk_inventory_items_category_id', 'inventory_categories', ['category_id'], ['id'])
        batch_op.drop_column('category')


def downgrade():
    # Add back category enum column
    op.add_column('inventory_items', sa.Column('category', sa.String(length=50), nullable=True))
    
    # Migrate data back from category_id to enum
    op.execute("""
        UPDATE inventory_items
        SET category = CASE 
            WHEN (SELECT name FROM inventory_categories WHERE id = category_id) = 'Raw Materials' THEN 'raw_material'
            WHEN (SELECT name FROM inventory_categories WHERE id = category_id) = 'Work in Progress' THEN 'wip'
            WHEN (SELECT name FROM inventory_categories WHERE id = category_id) = 'Finished Goods' THEN 'finished_good'
            WHEN (SELECT name FROM inventory_categories WHERE id = category_id) = 'Spare Parts' THEN 'spare_part'
            WHEN (SELECT name FROM inventory_categories WHERE id = category_id) = 'Tools' THEN 'tool'
            WHEN (SELECT name FROM inventory_categories WHERE id = category_id) = 'Consumables' THEN 'consumable'
            WHEN (SELECT name FROM inventory_categories WHERE id = category_id) = 'Packaging' THEN 'packaging'
            ELSE 'raw_material'
        END
    """)
    
    # Make category NOT NULL
    op.alter_column('inventory_items', 'category', nullable=False)
    
    # Drop foreign key and category_id column
    op.drop_constraint('fk_inventory_items_category_id', 'inventory_items', type_='foreignkey')
    op.drop_column('inventory_items', 'category_id')
    
    # Drop inventory_categories table
    op.drop_table('inventory_categories')
