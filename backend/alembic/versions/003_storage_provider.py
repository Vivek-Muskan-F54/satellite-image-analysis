"""storage provider

Revision ID: 003_storage_provider
Revises: 002_create_satellite_images_table
Create Date: 2026-09-19 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_storage_provider'
down_revision: Union[str, None] = '002_create_satellite_images_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table('satellite_images') as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column('storage_provider', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('storage_key', sa.String(), nullable=True))

    # Data migration: 
    #   storage_provider = 'local'
    #   storage_key = stored_filename
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE satellite_images SET storage_provider = 'local', storage_key = stored_filename"))

    # Make them non-nullable and drop old columns
    with op.batch_alter_table('satellite_images') as batch_op:
        batch_op.alter_column('storage_provider', nullable=False)
        batch_op.alter_column('storage_key', nullable=False)
        
        batch_op.drop_constraint('uq_satellite_images_stored_filename', type_='unique') # SQLite might not have this name
        # Actually it's unnamed in SQLite, Alembic's batch alter table can handle recreations.
        # Let's just drop the columns and recreate the unique constraint.
        batch_op.drop_column('stored_filename')
        batch_op.drop_column('storage_path')
        batch_op.create_unique_constraint('uq_satellite_images_storage_key', ['storage_key'])


def downgrade() -> None:
    with op.batch_alter_table('satellite_images') as batch_op:
        batch_op.add_column(sa.Column('stored_filename', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('storage_path', sa.String(), nullable=True))
        
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE satellite_images SET stored_filename = storage_key, storage_path = storage_key"))

    with op.batch_alter_table('satellite_images') as batch_op:
        batch_op.alter_column('stored_filename', nullable=False)
        batch_op.alter_column('storage_path', nullable=False)
        batch_op.drop_constraint('uq_satellite_images_storage_key', type_='unique')
        batch_op.drop_column('storage_provider')
        batch_op.drop_column('storage_key')
        batch_op.create_unique_constraint('uq_satellite_images_stored_filename', ['stored_filename'])
