"""Add medicine and lab fields

Revision ID: add_medicine_lab_fields
Revises: initial_schema
Create Date: 2024-12-24 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_medicine_lab_fields'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add frontier_lab to raw_items
    op.add_column('raw_items', sa.Column('frontier_lab', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_raw_items_frontier_lab'), 'raw_items', ['frontier_lab'], unique=False)
    
    # Add clinical_maturity_level to clusters
    op.execute("CREATE TYPE clinicalmaturitylevel AS ENUM ('exploratory', 'clinically_validated', 'regulatory_relevant', 'approved_deployed')")
    op.add_column('clusters', sa.Column('clinical_maturity_level', postgresql.ENUM('exploratory', 'clinically_validated', 'regulatory_relevant', 'approved_deployed', name='clinicalmaturitylevel'), nullable=True))
    op.create_index(op.f('ix_clusters_clinical_maturity_level'), 'clusters', ['clinical_maturity_level'], unique=False)
    
    # Add PRIMARY_LAB to SourceType enum
    op.execute("ALTER TYPE sourcetype ADD VALUE IF NOT EXISTS 'primary_lab'")


def downgrade() -> None:
    op.drop_index(op.f('ix_clusters_clinical_maturity_level'), table_name='clusters')
    op.drop_column('clusters', 'clinical_maturity_level')
    op.execute('DROP TYPE clinicalmaturitylevel')
    
    op.drop_index(op.f('ix_raw_items_frontier_lab'), table_name='raw_items')
    op.drop_column('raw_items', 'frontier_lab')
    
    # Note: PostgreSQL doesn't support removing enum values, so PRIMARY_LAB will remain

