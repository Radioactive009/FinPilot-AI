"""Initial Sprint 1 migration

Revision ID: 001_initial_sprint1
Revises: 
Create Date: 2026-07-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_sprint1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create User Role Enum in postgres
    # In order to support Enums, we define it here.
    user_role_enum = postgresql.ENUM('ADMIN', 'FINANCE_MANAGER', 'AUDITOR', 'EMPLOYEE', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create Document Type Enum in postgres
    doc_type_enum = postgresql.ENUM('INVOICE', 'EXPENSE_REPORT', 'AUDIT_REPORT', 'POLICY', 'VENDOR_STATEMENT', name='documenttype')
    doc_type_enum.create(op.get_bind(), checkfirst=True)

    # 3. Create 'users' table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'FINANCE_MANAGER', 'AUDITOR', 'EMPLOYEE', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 4. Create 'chat_sessions' table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('thread_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_sessions_thread_id'), 'chat_sessions', ['thread_id'], unique=True)

    # 5. Create 'ai_audit_logs' table
    op.create_table(
        'ai_audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('details', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Create 'documents' table
    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('original_file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('document_type', sa.Enum('INVOICE', 'EXPENSE_REPORT', 'AUDIT_REPORT', 'POLICY', 'VENDOR_STATEMENT', name='documenttype'), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('upload_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Create 'vendors' table
    op.create_table(
        'vendors',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_name', sa.String(length=255), nullable=False),
        sa.Column('vendor_code', sa.String(length=100), nullable=False),
        sa.Column('gst_number', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vendors_vendor_code'), 'vendors', ['vendor_code'], unique=True)

    # 8. Create 'invoices' table
    op.create_table(
        'invoices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('tax', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('payment_status', sa.String(length=50), nullable=False, server_default='unpaid'),
        sa.Column('validation_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0.0000'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Create 'invoice_items' table
    op.create_table(
        'invoice_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('invoice_id', sa.UUID(), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False, server_default='1.00'),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. Create 'payments' table
    op.create_table(
        'payments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('invoice_id', sa.UUID(), nullable=False),
        sa.Column('payment_reference', sa.String(length=100), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('payment_status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('payments')
    op.drop_table('invoice_items')
    op.drop_table('invoices')
    op.drop_index(op.f('ix_vendors_vendor_code'), table_name='vendors')
    op.drop_table('vendors')
    op.drop_table('documents')
    op.drop_table('ai_audit_logs')
    op.drop_index(op.f('ix_chat_sessions_thread_id'), table_name='chat_sessions')
    op.drop_table('chat_sessions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    # Drop custom Enums
    user_role_enum = postgresql.ENUM('ADMIN', 'FINANCE_MANAGER', 'AUDITOR', 'EMPLOYEE', name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
    doc_type_enum = postgresql.ENUM('INVOICE', 'EXPENSE_REPORT', 'AUDIT_REPORT', 'POLICY', 'VENDOR_STATEMENT', name='documenttype')
    doc_type_enum.drop(op.get_bind(), checkfirst=True)
