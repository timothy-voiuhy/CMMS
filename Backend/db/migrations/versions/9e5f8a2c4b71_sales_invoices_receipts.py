"""add sales invoices and payment receipts

Revision ID: 9e5f8a2c4b71
Revises: 8d4e7c1b2a90
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9e5f8a2c4b71"
down_revision: Union[str, None] = "8d4e7c1b2a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sales_invoices",
        sa.Column("invoice_number", sa.String(length=100), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("ISSUED", "PARTIALLY_PAID", "PAID", "VOIDED", name="salesinvoicestatus"), nullable=False),
        sa.Column("invoice_date", sa.DateTime(), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("tax_amount", sa.Float(), nullable=False),
        sa.Column("discount_amount", sa.Float(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("amount_paid", sa.Float(), nullable=False),
        sa.Column("balance_due", sa.Float(), nullable=False),
        sa.Column("issued_by", sa.Integer(), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("voided_by", sa.Integer(), nullable=True),
        sa.Column("voided_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["issued_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"]),
        sa.ForeignKeyConstraint(["voided_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sales_order_id"),
    )
    op.create_index("ix_sales_invoices_id", "sales_invoices", ["id"], unique=False)
    op.create_index("ix_sales_invoices_invoice_number", "sales_invoices", ["invoice_number"], unique=True)
    op.create_index("ix_sales_invoices_sales_order_id", "sales_invoices", ["sales_order_id"], unique=False)
    op.create_index("ix_sales_invoices_customer_id", "sales_invoices", ["customer_id"], unique=False)
    op.create_index("ix_sales_invoices_status", "sales_invoices", ["status"], unique=False)

    op.create_table(
        "sales_invoice_items",
        sa.Column("invoice_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_item_id", sa.Integer(), nullable=True),
        sa.Column("item_code", sa.String(length=100), nullable=False),
        sa.Column("item_name", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_of_measure", sa.String(length=20), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("tax_rate", sa.Float(), nullable=False),
        sa.Column("discount_amount", sa.Float(), nullable=False),
        sa.Column("line_total", sa.Float(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["sales_invoices.id"]),
        sa.ForeignKeyConstraint(["sales_order_item_id"], ["sales_order_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sales_invoice_items_id", "sales_invoice_items", ["id"], unique=False)
    op.create_index("ix_sales_invoice_items_invoice_id", "sales_invoice_items", ["invoice_id"], unique=False)

    op.create_table(
        "sales_receipts",
        sa.Column("receipt_number", sa.String(length=100), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=False),
        sa.Column("receipt_date", sa.DateTime(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.Enum("CASH", "BANK_TRANSFER", "CARD", "MOBILE_MONEY", "CHEQUE", "OTHER", name="paymentmethod"), nullable=False),
        sa.Column("reference", sa.String(length=200), nullable=True),
        sa.Column("received_by", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["sales_invoices.id"]),
        sa.ForeignKeyConstraint(["received_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sales_receipts_id", "sales_receipts", ["id"], unique=False)
    op.create_index("ix_sales_receipts_receipt_number", "sales_receipts", ["receipt_number"], unique=True)
    op.create_index("ix_sales_receipts_invoice_id", "sales_receipts", ["invoice_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sales_receipts_invoice_id", table_name="sales_receipts")
    op.drop_index("ix_sales_receipts_receipt_number", table_name="sales_receipts")
    op.drop_index("ix_sales_receipts_id", table_name="sales_receipts")
    op.drop_table("sales_receipts")
    op.drop_index("ix_sales_invoice_items_invoice_id", table_name="sales_invoice_items")
    op.drop_index("ix_sales_invoice_items_id", table_name="sales_invoice_items")
    op.drop_table("sales_invoice_items")
    op.drop_index("ix_sales_invoices_status", table_name="sales_invoices")
    op.drop_index("ix_sales_invoices_customer_id", table_name="sales_invoices")
    op.drop_index("ix_sales_invoices_sales_order_id", table_name="sales_invoices")
    op.drop_index("ix_sales_invoices_invoice_number", table_name="sales_invoices")
    op.drop_index("ix_sales_invoices_id", table_name="sales_invoices")
    op.drop_table("sales_invoices")
    sa.Enum(name="paymentmethod").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="salesinvoicestatus").drop(op.get_bind(), checkfirst=True)
