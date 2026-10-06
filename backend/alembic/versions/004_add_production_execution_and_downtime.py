"""add_production_execution_and_downtime

Revision ID: 004_execution_and_downtime
Revises: 003_work_orders_machines_employees
Create Date: 2026-08-18 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004_execution_and_downtime'
down_revision: Union[str, None] = '003_work_orders_machines_employees'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add execution tracking columns to work_orders
    op.add_column('work_orders', sa.Column('actual_start_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('work_orders', sa.Column('actual_completion_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('work_orders', sa.Column('produced_quantity', sa.Integer(), nullable=False, server_default='0'))

    # 2. Create downtime_records table
    op.create_table(
        'downtime_records',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('work_order_id', sa.CHAR(36), sa.ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('machine_id', sa.CHAR(36), sa.ForeignKey('machines.id', ondelete='SET NULL'), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=100), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('recorded_by_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_downtime_records_work_order_id'), 'downtime_records', ['work_order_id'], unique=False)
    op.create_index(op.f('ix_downtime_records_machine_id'), 'downtime_records', ['machine_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_downtime_records_machine_id'), table_name='downtime_records')
    op.drop_index(op.f('ix_downtime_records_work_order_id'), table_name='downtime_records')
    op.drop_table('downtime_records')

    op.drop_column('work_orders', 'produced_quantity')
    op.drop_column('work_orders', 'actual_completion_time')
    op.drop_column('work_orders', 'actual_start_time')
