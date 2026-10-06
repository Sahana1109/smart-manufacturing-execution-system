"""add_quality_inspection_and_defects

Revision ID: 005_quality_inspection_and_defects
Revises: 004_execution_and_downtime
Create Date: 2026-08-19 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_quality_inspection_and_defects'
down_revision: Union[str, None] = '004_execution_and_downtime'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create quality_inspections table
    op.create_table(
        'quality_inspections',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('work_order_id', sa.CHAR(36), sa.ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('inspector_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('inspected_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('accepted_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rejected_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_quality_inspections_work_order_id'), 'quality_inspections', ['work_order_id'], unique=False)
    op.create_index(op.f('ix_quality_inspections_inspector_id'), 'quality_inspections', ['inspector_id'], unique=False)

    # 2. Create quality_defects table
    op.create_table(
        'quality_defects',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('inspection_id', sa.CHAR(36), sa.ForeignKey('quality_inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('defect_type', sa.String(length=50), nullable=False, server_default='OTHER'),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_quality_defects_inspection_id'), 'quality_defects', ['inspection_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_quality_defects_inspection_id'), table_name='quality_defects')
    op.drop_table('quality_defects')

    op.drop_index(op.f('ix_quality_inspections_inspector_id'), table_name='quality_inspections')
    op.drop_index(op.f('ix_quality_inspections_work_order_id'), table_name='quality_inspections')
    op.drop_table('quality_inspections')
