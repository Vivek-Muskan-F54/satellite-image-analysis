"""create satellite images table

Revision ID: 002_create_satellite_images_table
Revises: 001_create_user_table
Create Date: 2026-09-19 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_create_satellite_images_table'
down_revision: Union[str, None] = '001_create_user_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('satellite_images',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('stored_filename', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_extension', sa.String(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stored_filename')
    )
    op.create_index(op.f('ix_satellite_images_id'), 'satellite_images', ['id'], unique=False)
    op.create_index(op.f('ix_satellite_images_user_id'), 'satellite_images', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_satellite_images_user_id'), table_name='satellite_images')
    op.drop_index(op.f('ix_satellite_images_id'), table_name='satellite_images')
    op.drop_table('satellite_images')
