"""create_products_production_plans_and_audit_logs

Revision ID: 002_products_plans_audit
Revises: 001_create_users_and_roles_tables
Create Date: 2026-08-14 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_products_plans_audit'
down_revision: Union[str, None] = '001_create_users_and_roles_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('product_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=False, server_default='PCS'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_products_product_code'), 'products', ['product_code'], unique=True)

    # 2. Create production_plans table
    plan_priority_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='production_plan_priority')
    plan_status_enum = sa.Enum('DRAFT', 'PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='production_plan_status')

    op.create_table(
        'production_plans',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('plan_number', sa.String(length=50), nullable=False),
        sa.Column('product_id', sa.CHAR(36), sa.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('planned_quantity', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('priority', plan_priority_enum, nullable=False, server_default='MEDIUM'),
        sa.Column('status', plan_status_enum, nullable=False, server_default='DRAFT'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_production_plans_plan_number'), 'production_plans', ['plan_number'], unique=True)
    op.create_index(op.f('ix_production_plans_product_id'), 'production_plans', ['product_id'], unique=False)

    # 3. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index(op.f('ix_production_plans_product_id'), table_name='production_plans')
    op.drop_index(op.f('ix_production_plans_plan_number'), table_name='production_plans')
    op.drop_table('production_plans')

    sa.Enum(name='production_plan_status').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='production_plan_priority').drop(op.get_bind(), checkfirst=False)

    op.drop_index(op.f('ix_products_product_code'), table_name='products')
    op.drop_table('products')
