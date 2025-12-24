# Build Progress Tracker

- [x] Phase 1: Repo scaffold + Docker
  - DONE: Created monorepo structure (web, api, worker, infra)
  - DONE: Docker Compose with all services
  - DONE: Health checks and basic configuration
  - DONE: README with local run instructions

- [x] Phase 2: Database schema + migrations
  - DONE: PostgreSQL schema with all required tables
  - DONE: Alembic migrations setup
  - DONE: Seed script with realistic fake data
  - DONE: Indexes and timestamps

- [x] Phase 3: Backend API
  - DONE: FastAPI endpoints (briefing/today, topics/{slug}, stories/{id}, search)
  - DONE: Pydantic schemas for request/response validation
  - DONE: ORM integration with pagination support
  - DONE: Returns summary, citations, score breakdown, rationale

- [x] Phase 4: Frontend UI
  - DONE: Home page (daily briefing)
  - DONE: Topic page with story listings
  - DONE: Story detail page
  - DONE: Search page
  - DONE: Components (StoryCard, citations, score breakdown display)
  - DONE: API client integration

- [x] Phase 5: Worker + agents
  - DONE: Worker CLI (`python run.py once`)
  - DONE: Scout agent (RSS + arXiv ingestion)
  - DONE: Cleaner agent (URL normalization, text extraction, spam filtering)
  - DONE: Clustering agent (text similarity-based deduplication)
  - DONE: Tagger agent (keyword-based topic assignment)
  - DONE: Editor agent (scoring with weighted formula)
  - DONE: Writer agent (summaries and citations)
  - DONE: People-to-Follow agent (placeholder)
  - DONE: Daily briefing generator

- [x] Phase 6: Hardening + tests
  - DONE: ARCHITECTURE.md documenting service boundaries and agent contracts
  - DONE: Unit tests for clustering, scoring, and tagging
  - DONE: Logging throughout pipeline
  - DONE: Error isolation (individual failures don't crash pipeline)
  - DONE: README with VPS deployment steps
  - DONE: Cron-compatible worker execution
