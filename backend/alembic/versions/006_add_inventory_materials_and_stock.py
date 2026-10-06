"""add_inventory_materials_and_stock

Revision ID: 006_inventory_materials_stock
Revises: 005_quality_inspection_and_defects
Create Date: 2026-08-20 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006_inventory_materials_stock'
down_revision: Union[str, None] = '005_quality_inspection_and_defects'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create materials table
    op.create_table(
        'materials',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('material_code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=False, server_default='PCS'),
        sa.Column('reorder_level', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_materials_material_code'), 'materials', ['material_code'], unique=True)

    # 2. Create inventory_stocks table
    op.create_table(
        'inventory_stocks',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('material_id', sa.CHAR(36), sa.ForeignKey('materials.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reserved_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('location', sa.String(length=100), nullable=False, server_default='MAIN-WAREHOUSE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_inventory_stocks_material_id'), 'inventory_stocks', ['material_id'], unique=True)

    # 3. Create stock_movements table
    op.create_table(
        'stock_movements',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('material_id', sa.CHAR(36), sa.ForeignKey('materials.id', ondelete='CASCADE'), nullable=False),
        sa.Column('work_order_id', sa.CHAR(36), sa.ForeignKey('work_orders.id', ondelete='SET NULL'), nullable=True),
        sa.Column('movement_type', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('reference', sa.Text(), nullable=True),
        sa.Column('performed_by_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_stock_movements_material_id'), 'stock_movements', ['material_id'], unique=False)
    op.create_index(op.f('ix_stock_movements_work_order_id'), 'stock_movements', ['work_order_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_stock_movements_work_order_id'), table_name='stock_movements')
    op.drop_index(op.f('ix_stock_movements_material_id'), table_name='stock_movements')
    op.drop_table('stock_movements')

    op.drop_index(op.f('ix_inventory_stocks_material_id'), table_name='inventory_stocks')
    op.drop_table('inventory_stocks')

    op.drop_index(op.f('ix_materials_material_code'), table_name='materials')
    op.drop_table('materials')
