"""Initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2024-12-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('source_type', postgresql.ENUM('rss', 'arxiv', name='sourcetype'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sources_id'), 'sources', ['id'], unique=False)
    op.create_index(op.f('ix_sources_name'), 'sources', ['name'], unique=False)

    # Create raw_items table
    op.create_table(
        'raw_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_items_id'), 'raw_items', ['id'], unique=False)
    op.create_index(op.f('ix_raw_items_source_id'), 'raw_items', ['source_id'], unique=False)
    op.create_index(op.f('ix_raw_items_url'), 'raw_items', ['url'], unique=False)

    # Create topics table
    op.create_table(
        'topics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_topics_id'), 'topics', ['id'], unique=False)
    op.create_index(op.f('ix_topics_name'), 'topics', ['name'], unique=True)
    op.create_index(op.f('ix_topics_slug'), 'topics', ['slug'], unique=True)

    # Create clusters table
    op.create_table(
        'clusters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('why_this_matters', sa.Text(), nullable=True),
        sa.Column('what_to_watch_next', sa.Text(), nullable=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('ranking_rationale', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clusters_id'), 'clusters', ['id'], unique=False)
    op.create_index(op.f('ix_clusters_score'), 'clusters', ['score'], unique=False)
    op.create_index(op.f('ix_clusters_title'), 'clusters', ['title'], unique=False)

    # Create cluster_items association table
    op.create_table(
        'cluster_items',
        sa.Column('cluster_id', sa.Integer(), nullable=False),
        sa.Column('raw_item_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['raw_item_id'], ['raw_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('cluster_id', 'raw_item_id')
    )

    # Create cluster_topics association table
    op.create_table(
        'cluster_topics',
        sa.Column('cluster_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('cluster_id', 'topic_id')
    )

    # Create score_breakdowns table
    op.create_table(
        'score_breakdowns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('impact_score', sa.Float(), nullable=False),
        sa.Column('credibility_score', sa.Float(), nullable=False),
        sa.Column('novelty_score', sa.Float(), nullable=False),
        sa.Column('corroboration_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cluster_id')
    )
    op.create_index(op.f('ix_score_breakdowns_id'), 'score_breakdowns', ['id'], unique=False)
    op.create_index(op.f('ix_score_breakdowns_cluster_id'), 'score_breakdowns', ['cluster_id'], unique=True)

    # Create citations table
    op.create_table(
        'citations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), nullable=False),
        sa.Column('raw_item_id', sa.Integer(), nullable=False),
        sa.Column('citation_text', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['raw_item_id'], ['raw_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_citations_id'), 'citations', ['id'], unique=False)
    op.create_index(op.f('ix_citations_cluster_id'), 'citations', ['cluster_id'], unique=False)
    op.create_index(op.f('ix_citations_raw_item_id'), 'citations', ['raw_item_id'], unique=False)

    # Create daily_briefings table
    op.create_table(
        'daily_briefings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('briefing_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('briefing_date')
    )
    op.create_index(op.f('ix_daily_briefings_id'), 'daily_briefings', ['id'], unique=False)
    op.create_index(op.f('ix_daily_briefings_briefing_date'), 'daily_briefings', ['briefing_date'], unique=True)

    # Create briefing_clusters association table
    op.create_table(
        'briefing_clusters',
        sa.Column('briefing_id', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['briefing_id'], ['daily_briefings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cluster_id'], ['clusters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('briefing_id', 'cluster_id')
    )

    # Create people_to_follow table
    op.create_table(
        'people_to_follow',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('organization', sa.String(length=255), nullable=True),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_people_to_follow_id'), 'people_to_follow', ['id'], unique=False)
    op.create_index(op.f('ix_people_to_follow_name'), 'people_to_follow', ['name'], unique=False)
    op.create_index(op.f('ix_people_to_follow_topic_id'), 'people_to_follow', ['topic_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_people_to_follow_topic_id'), table_name='people_to_follow')
    op.drop_index(op.f('ix_people_to_follow_name'), table_name='people_to_follow')
    op.drop_index(op.f('ix_people_to_follow_id'), table_name='people_to_follow')
    op.drop_table('people_to_follow')
    op.drop_table('briefing_clusters')
    op.drop_index(op.f('ix_daily_briefings_briefing_date'), table_name='daily_briefings')
    op.drop_index(op.f('ix_daily_briefings_id'), table_name='daily_briefings')
    op.drop_table('daily_briefings')
    op.drop_index(op.f('ix_citations_raw_item_id'), table_name='citations')
    op.drop_index(op.f('ix_citations_cluster_id'), table_name='citations')
    op.drop_index(op.f('ix_citations_id'), table_name='citations')
    op.drop_table('citations')
    op.drop_index(op.f('ix_score_breakdowns_cluster_id'), table_name='score_breakdowns')
    op.drop_index(op.f('ix_score_breakdowns_id'), table_name='score_breakdowns')
    op.drop_table('score_breakdowns')
    op.drop_table('cluster_topics')
    op.drop_table('cluster_items')
    op.drop_index(op.f('ix_clusters_title'), table_name='clusters')
    op.drop_index(op.f('ix_clusters_score'), table_name='clusters')
    op.drop_index(op.f('ix_clusters_id'), table_name='clusters')
    op.drop_table('clusters')
    op.drop_index(op.f('ix_topics_slug'), table_name='topics')
    op.drop_index(op.f('ix_topics_name'), table_name='topics')
    op.drop_index(op.f('ix_topics_id'), table_name='topics')
    op.drop_table('topics')
    op.drop_index(op.f('ix_raw_items_url'), table_name='raw_items')
    op.drop_index(op.f('ix_raw_items_source_id'), table_name='raw_items')
    op.drop_index(op.f('ix_raw_items_id'), table_name='raw_items')
    op.drop_table('raw_items')
    op.drop_index(op.f('ix_sources_name'), table_name='sources')
    op.drop_index(op.f('ix_sources_id'), table_name='sources')
    op.drop_table('sources')
    op.execute('DROP TYPE sourcetype')

