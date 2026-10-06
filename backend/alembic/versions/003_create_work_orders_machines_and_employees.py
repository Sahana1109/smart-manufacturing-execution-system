"""create_work_orders_machines_and_employees

Revision ID: 003_work_orders_machines_employees
Revises: 002_products_plans_audit
Create Date: 2026-08-17 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_work_orders_machines_employees'
down_revision: Union[str, None] = '002_products_plans_audit'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create machines table
    op.create_table(
        'machines',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('machine_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='OPERATIONAL'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_machines_machine_code'), 'machines', ['machine_code'], unique=True)

    # 2. Create employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('employee_code', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('role_title', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_employees_employee_code'), 'employees', ['employee_code'], unique=True)

    # 3. Create work_orders table
    wo_priority_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='work_order_priority')
    wo_status_enum = sa.Enum('DRAFT', 'RELEASED', 'IN_PROGRESS', 'PAUSED', 'COMPLETED', 'CLOSED', 'CANCELLED', name='work_order_status')

    op.create_table(
        'work_orders',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('work_order_number', sa.String(length=50), nullable=False),
        sa.Column('production_plan_id', sa.CHAR(36), sa.ForeignKey('production_plans.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('product_id', sa.CHAR(36), sa.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('planned_quantity', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('priority', wo_priority_enum, nullable=False, server_default='MEDIUM'),
        sa.Column('status', wo_status_enum, nullable=False, server_default='DRAFT'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('assigned_machine_id', sa.CHAR(36), sa.ForeignKey('machines.id', ondelete='SET NULL'), nullable=True),
        sa.Column('assigned_employee_id', sa.CHAR(36), sa.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_work_orders_work_order_number'), 'work_orders', ['work_order_number'], unique=True)
    op.create_index(op.f('ix_work_orders_production_plan_id'), 'work_orders', ['production_plan_id'], unique=False)
    op.create_index(op.f('ix_work_orders_product_id'), 'work_orders', ['product_id'], unique=False)
    op.create_index(op.f('ix_work_orders_assigned_machine_id'), 'work_orders', ['assigned_machine_id'], unique=False)
    op.create_index(op.f('ix_work_orders_assigned_employee_id'), 'work_orders', ['assigned_employee_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_work_orders_assigned_employee_id'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_assigned_machine_id'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_product_id'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_production_plan_id'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_work_order_number'), table_name='work_orders')
    op.drop_table('work_orders')

    sa.Enum(name='work_order_status').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='work_order_priority').drop(op.get_bind(), checkfirst=False)

    op.drop_index(op.f('ix_employees_employee_code'), table_name='employees')
    op.drop_table('employees')

    op.drop_index(op.f('ix_machines_machine_code'), table_name='machines')
    op.drop_table('machines')
