# AI Briefing Platform

A production-grade AI news and research briefing platform using a multi-agent pipeline to collect, deduplicate, rank, and summarize the most important AI developments across multiple domains.

## Features

- **Multi-Source Ingestion**: RSS feeds and arXiv papers
- **Intelligent Clustering**: Automatic deduplication of related stories
- **Scoring System**: Explainable ranking with weighted criteria
- **Topic Organization**: 6 major AI topic categories
- **Daily Briefings**: Curated daily summaries
- **Search**: Full-text search across all stories
- **Citations**: Proper attribution and source tracking

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Worker**: Python multi-agent pipeline
- **Database**: PostgreSQL 15
- **Infrastructure**: Docker Compose

## Local Development

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-briefing-platform
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferences (defaults work for local dev)
   ```

3. **Start services**
   ```bash
   docker compose up
   ```

4. **Run database migrations**
   ```bash
   docker compose exec api alembic upgrade head
   ```

5. **Seed initial data**
   ```bash
   docker compose exec api python seed.py
   ```

6. **Access the application**
   - Web UI: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - API Health: http://localhost:8000/health

### Running the Worker

The worker runs the multi-agent pipeline to ingest and process content:

```bash
# Run once
docker compose exec worker python run.py once

# Or run in background
docker compose exec -d worker python run.py once
```

## VPS Deployment (Hostinger)

### Prerequisites

- VPS with Docker and Docker Compose installed
- Domain name (optional) pointing to VPS IP
- SSH access to VPS

### Deployment Steps

1. **Connect to VPS**
   ```bash
   ssh user@your-vps-ip
   ```

2. **Clone repository**
   ```bash
   git clone <repository-url>
   cd ai-briefing-platform
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with production values
   ```
   
   Important variables:
   - `POSTGRES_PASSWORD`: Strong password for database
   - `DATABASE_URL`: Full PostgreSQL connection string
   - `NEXT_PUBLIC_API_URL`: Your API URL (e.g., `http://your-domain.com:8000`)

4. **Build and start services**
   ```bash
   docker compose build
   docker compose up -d
   ```

5. **Run migrations**
   ```bash
   docker compose exec api alembic upgrade head
   ```

6. **Seed initial data (optional)**
   ```bash
   docker compose exec api python seed.py
   ```

7. **Set up cron for daily worker runs**
   ```bash
   crontab -e
   ```
   
   Add line (runs at 6 AM daily):
   ```cron
   0 6 * * * cd /path/to/ai-briefing-platform && docker compose exec -T worker python run.py once >> /var/log/briefing-worker.log 2>&1
   ```

8. **Configure firewall (if needed)**
   ```bash
   # Allow ports 3000 (web) and 8000 (api)
   sudo ufw allow 3000/tcp
   sudo ufw allow 8000/tcp
   ```

9. **Set up reverse proxy (optional, for HTTPS)**
   
   Using Nginx:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

10. **Monitor logs**
    ```bash
    # All services
    docker compose logs -f
    
    # Specific service
    docker compose logs -f api
    docker compose logs -f worker
    ```

### Maintenance

- **View logs**: `docker compose logs -f`
- **Restart services**: `docker compose restart`
- **Update code**: `git pull && docker compose build && docker compose up -d`
- **Backup database**: 
  ```bash
  docker compose exec postgres pg_dump -U briefing_user briefing_db > backup.sql
  ```
- **Restore database**:
  ```bash
  docker compose exec -T postgres psql -U briefing_user briefing_db < backup.sql
  ```

## Testing

Run tests:
```bash
docker compose exec api pytest tests/
```

Run specific test file:
```bash
docker compose exec api pytest tests/test_scoring.py
```

## Project Structure

```
.
├── api/              # FastAPI backend
│   ├── routers/      # API endpoints
│   ├── models.py     # Database models
│   ├── schemas.py    # Pydantic schemas
│   └── tests/        # Unit tests
├── web/              # Next.js frontend
│   ├── app/          # App router pages
│   ├── components/   # React components
│   └── lib/          # Utilities
├── worker/           # Worker service
│   ├── agents/       # Multi-agent pipeline
│   ├── config/       # Configuration files
│   └── run.py        # CLI entry point
├── docker-compose.yml
└── README.md
```

## API Endpoints

- `GET /briefing/today` - Get today's daily briefing
- `GET /topics/{slug}` - Get stories by topic
- `GET /stories/{id}` - Get story details
- `GET /search?q={query}` - Search stories
- `GET /health` - Health check

See `/docs` endpoint for full API documentation.

## Configuration

### RSS Feeds

Edit `worker/config/rss_feeds.json` to add/modify RSS feeds.

### arXiv Categories

Edit `worker/config/arxiv_config.json` to configure arXiv categories and keywords.

## License

[Your License Here]

## Contributing

[Contributing Guidelines]

