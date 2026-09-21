"""create analysis tables

Revision ID: 004
Revises: 003
Create Date: 2026-09-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table('analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('image_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='analysisstatus'), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['image_id'], ['satellite_images.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_created_at'), 'analyses', ['created_at'], unique=False)
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)
    op.create_index(op.f('ix_analyses_image_id'), 'analyses', ['image_id'], unique=False)
    op.create_index(op.f('ix_analyses_status'), 'analyses', ['status'], unique=False)
    op.create_index(op.f('ix_analyses_user_id'), 'analyses', ['user_id'], unique=False)

    op.create_table('predictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('analysis_id', sa.String(), nullable=False),
        sa.Column('predicted_class', sa.String(), nullable=False),
        sa.Column('class_index', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('probabilities', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_analysis_id'), 'predictions', ['analysis_id'], unique=False)
    op.create_index(op.f('ix_predictions_id'), 'predictions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_predictions_id'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_analysis_id'), table_name='predictions')
    op.drop_table('predictions')

    op.drop_index(op.f('ix_analyses_user_id'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_status'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_image_id'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_id'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_created_at'), table_name='analyses')
    op.drop_table('analyses')

    analysis_status = postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='analysisstatus')
    analysis_status.drop(op.get_bind(), checkfirst=True)
