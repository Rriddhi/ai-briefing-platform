"""
SQLAlchemy models for AI Briefing Platform
"""
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Table,
    Enum as SQLEnum, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class SourceType(str, enum.Enum):
    RSS = "rss"
    ARXIV = "arxiv"
    PRIMARY_LAB = "primary_lab"


class ClinicalMaturityLevel(str, enum.Enum):
    EXPLORATORY = "exploratory"
    CLINICALLY_VALIDATED = "clinically_validated"
    REGULATORY_RELEVANT = "regulatory_relevant"
    APPROVED_DEPLOYED = "approved_deployed"


# Association tables
cluster_items = Table(
    'cluster_items',
    Base.metadata,
    Column('cluster_id', Integer, ForeignKey('clusters.id', ondelete='CASCADE'), primary_key=True),
    Column('raw_item_id', Integer, ForeignKey('raw_items.id', ondelete='CASCADE'), primary_key=True),
)

cluster_topics = Table(
    'cluster_topics',
    Base.metadata,
    Column('cluster_id', Integer, ForeignKey('clusters.id', ondelete='CASCADE'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id', ondelete='CASCADE'), primary_key=True),
)

briefing_clusters = Table(
    'briefing_clusters',
    Base.metadata,
    Column('briefing_id', Integer, ForeignKey('daily_briefings.id', ondelete='CASCADE'), primary_key=True),
    Column('cluster_id', Integer, ForeignKey('clusters.id', ondelete='CASCADE'), primary_key=True),
)


class Source(Base):
    """RSS feeds and arXiv sources"""
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    source_type = Column(SQLEnum(SourceType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    raw_items = relationship("RawItem", back_populates="source", cascade="all, delete-orphan")


class RawItem(Base):
    """Raw ingested items from sources"""
    __tablename__ = 'raw_items'

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('sources.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, index=True)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    frontier_lab = Column(String(100), nullable=True, index=True)  # e.g., "Anthropic", "OpenAI", "DeepMind"

    source = relationship("Source", back_populates="raw_items")
    clusters = relationship("Cluster", secondary=cluster_items, back_populates="raw_items")
    citations = relationship("Citation", back_populates="raw_item", cascade="all, delete-orphan")


class Topic(Base):
    """Topics/categories for clustering"""
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    clusters = relationship("Cluster", secondary=cluster_topics, back_populates="topics")
    people = relationship("PersonToFollow", back_populates="topic", cascade="all, delete-orphan")


class Cluster(Base):
    """Deduplicated story clusters"""
    __tablename__ = 'clusters'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    why_this_matters = Column(Text, nullable=True)
    what_to_watch_next = Column(Text, nullable=True)
    score = Column(Float, nullable=False, index=True)  # Overall score for ranking
    ranking_rationale = Column(Text, nullable=True)  # Explainable ranking reason
    clinical_maturity_level = Column(SQLEnum(ClinicalMaturityLevel), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    raw_items = relationship("RawItem", secondary=cluster_items, back_populates="clusters")
    topics = relationship("Topic", secondary=cluster_topics, back_populates="clusters")
    score_breakdown = relationship("ScoreBreakdown", back_populates="cluster", uselist=False, cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="cluster", cascade="all, delete-orphan")
    briefings = relationship("DailyBriefing", secondary=briefing_clusters, back_populates="clusters")


class ScoreBreakdown(Base):
    """Detailed scoring breakdown for explainability"""
    __tablename__ = 'score_breakdowns'

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey('clusters.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    relevance_score = Column(Float, nullable=False)  # 0.30 weight
    impact_score = Column(Float, nullable=False)  # 0.25 weight
    credibility_score = Column(Float, nullable=False)  # 0.20 weight
    novelty_score = Column(Float, nullable=False)  # 0.15 weight
    corroboration_score = Column(Float, nullable=False)  # 0.10 weight
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cluster = relationship("Cluster", back_populates="score_breakdown")


class Citation(Base):
    """Citations for cluster summaries"""
    __tablename__ = 'citations'

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey('clusters.id', ondelete='CASCADE'), nullable=False, index=True)
    raw_item_id = Column(Integer, ForeignKey('raw_items.id', ondelete='CASCADE'), nullable=False, index=True)
    citation_text = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cluster = relationship("Cluster", back_populates="citations")
    raw_item = relationship("RawItem", back_populates="citations")


class DailyBriefing(Base):
    """Daily briefing documents"""
    __tablename__ = 'daily_briefings'

    id = Column(Integer, primary_key=True, index=True)
    briefing_date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    clusters = relationship("Cluster", secondary=briefing_clusters, back_populates="briefings")


class PersonToFollow(Base):
    """Key people to follow per topic"""
    __tablename__ = 'people_to_follow'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False, index=True)
    url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    topic = relationship("Topic", back_populates="people")

