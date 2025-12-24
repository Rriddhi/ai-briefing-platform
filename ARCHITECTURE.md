# Architecture Documentation

## Overview

The AI Briefing Platform is a multi-service application that collects, processes, and presents AI-related news and research. The system uses a multi-agent pipeline to ingest, deduplicate, rank, and summarize content.

## Service Boundaries

### 1. Web Frontend (`/web`)
- **Technology**: Next.js 14 (App Router), React, TypeScript, Tailwind CSS
- **Responsibility**: 
  - User interface for viewing briefings, topics, stories, and search
  - Client-side API communication
  - Responsive design and user experience
- **Dependencies**: Backend API service
- **Port**: 3000

### 2. Backend API (`/api`)
- **Technology**: FastAPI, SQLAlchemy, PostgreSQL
- **Responsibility**:
  - RESTful API endpoints
  - Database access via ORM
  - Request/response validation (Pydantic)
  - CORS handling
- **Dependencies**: PostgreSQL database
- **Port**: 8000
- **Endpoints**:
  - `GET /briefing/today` - Daily briefing
  - `GET /topics/{slug}` - Stories by topic
  - `GET /stories/{id}` - Story detail
  - `GET /search?q=` - Search stories

### 3. Worker Service (`/worker`)
- **Technology**: Python, SQLAlchemy
- **Responsibility**:
  - Multi-agent pipeline execution
  - Data ingestion and processing
  - Scheduled runs (cron-compatible)
- **Dependencies**: PostgreSQL database, external APIs (RSS, arXiv)
- **CLI**: `python run.py once`

### 4. Database (`postgres`)
- **Technology**: PostgreSQL 15
- **Responsibility**:
  - Persistent data storage
  - Relational data integrity
- **Port**: 5432

## Agent Contracts

The worker pipeline consists of 7 agents, each with strict input/output contracts:

### 1. Scout Agent
- **Input**: RSS feed configs, arXiv config
- **Output**: Raw items stored in `raw_items` table
- **Error Handling**: Individual feed failures don't crash pipeline
- **Dependencies**: `feedparser`, `arxiv` library

### 2. Cleaner Agent
- **Input**: Raw items from database
- **Output**: Normalized URLs, extracted text content, spam-filtered items
- **Processing**: URL normalization, HTML parsing, spam detection
- **Dependencies**: `beautifulsoup4`, `requests`

### 3. Clustering Agent
- **Input**: Cleaned raw items
- **Output**: Clusters in `clusters` table, associations in `cluster_items`
- **Algorithm**: Text similarity-based deduplication (SequenceMatcher)
- **Threshold**: 0.6 similarity for grouping

### 4. Tagger Agent
- **Input**: Clusters without topics
- **Output**: Topics assigned to clusters (multi-label via `cluster_topics`)
- **Method**: Keyword matching against predefined topic keywords
- **Topics**: Robotics, Medicine & Healthcare AI, Automotive & Autonomous, Human-Centered AI, AI Policy & Governance, General AI

### 5. Editor Agent (Scoring)
- **Input**: Clusters without scores
- **Output**: Score breakdowns and overall scores
- **Formula**: 
  ```
  score = 0.30 * relevance + 0.25 * impact + 0.20 * credibility + 
          0.15 * novelty + 0.10 * corroboration
  ```
- **Explainability**: Stores ranking rationale text
- **Output Tables**: `score_breakdowns`, updates `clusters.score` and `clusters.ranking_rationale`

### 6. Writer Agent
- **Input**: Clusters without summaries
- **Output**: 
  - `clusters.summary`
  - `clusters.why_this_matters`
  - `clusters.what_to_watch_next`
  - Citations in `citations` table
- **Requirement**: Citations mandatory (at least one per cluster)

### 7. People-to-Follow Agent
- **Input**: All raw items and clusters
- **Output**: Updates to `people_to_follow` table
- **Note**: Currently placeholder implementation

### Daily Briefing Generator
- **Input**: Top clusters by score
- **Output**: `daily_briefings` record with associated clusters
- **Selection**: Top 10 clusters by score
- **Timing**: One briefing per day (unique on `briefing_date`)

## Data Model

### Core Tables
- `sources` - RSS feeds and arXiv sources
- `raw_items` - Ingested items from sources
- `clusters` - Deduplicated story clusters
- `cluster_items` - Many-to-many: clusters ↔ raw_items
- `topics` - Topic categories
- `cluster_topics` - Many-to-many: clusters ↔ topics
- `score_breakdowns` - Detailed scoring (one per cluster)
- `citations` - Citations for clusters (links to raw_items)
- `daily_briefings` - Daily briefing documents
- `briefing_clusters` - Many-to-many: briefings ↔ clusters
- `people_to_follow` - Tracked individuals/organizations

### Key Relationships
- Source → RawItems (one-to-many)
- Cluster → RawItems (many-to-many)
- Cluster → Topics (many-to-many)
- Cluster → ScoreBreakdown (one-to-one)
- Cluster → Citations (one-to-many)
- DailyBriefing → Clusters (many-to-many)
- Topic → PeopleToFollow (one-to-many)

## Design Decisions

### 1. Monorepo Structure
- **Rationale**: Shared database models, easier deployment
- **Trade-off**: Coupling between services, but simplifies development

### 2. Simple Clustering Algorithm
- **Decision**: Text similarity (SequenceMatcher) instead of advanced ML
- **Rationale**: Sufficient for deduplication, faster, no training data needed
- **Future**: Can be upgraded to embeddings-based clustering

### 3. Keyword-Based Tagging
- **Decision**: Rule-based keyword matching
- **Rationale**: Transparent, deterministic, no training required
- **Future**: Can be upgraded to classifier model

### 4. Scoring Weights
- **Decision**: Fixed weights (30% relevance, 25% impact, 20% credibility, 15% novelty, 10% corroboration)
- **Rationale**: Specified in requirements, provides explainability
- **Flexibility**: Weights stored per-score for potential future customization

### 5. No Authentication
- **Decision**: Public API, no user accounts
- **Rationale**: Phase 1 requirement, simplifies deployment
- **Future**: Can add authentication layer

### 6. Docker Compose
- **Decision**: All services containerized
- **Rationale**: Consistent environments, easy local development, VPS-ready
- **Trade-off**: Slight overhead, but enables reproducible deployments

### 7. Error Isolation
- **Decision**: Individual agent failures don't crash entire pipeline
- **Rationale**: Resilience - one failed RSS feed shouldn't stop processing
- **Implementation**: Try-catch per feed/item with logging

## Deployment

### Local Development
```bash
docker compose up
```

### VPS Deployment
1. Clone repository
2. Copy `.env.example` to `.env` and configure
3. Run migrations: `docker compose exec api alembic upgrade head`
4. Seed data: `docker compose exec api python seed.py`
5. Start services: `docker compose up -d`
6. Schedule worker: Add cron job `0 6 * * * cd /path/to/project && docker compose exec -T worker python run.py once`

## Logging

- All agents log at INFO level
- Errors logged with stack traces
- Format: `TIMESTAMP - MODULE - LEVEL - MESSAGE`
- Worker logs show agent stages and results

## Future Improvements

1. **Clustering**: Upgrade to embeddings-based similarity
2. **Tagging**: Use classifier model for topic assignment
3. **Summarization**: Integrate LLM for better summaries
4. **People Extraction**: Use NER models for entity extraction
5. **Caching**: Add Redis for API response caching
6. **Monitoring**: Add Prometheus metrics
7. **Alerting**: Notify on pipeline failures

