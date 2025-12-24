"""
Scout Agent: Ingest RSS feeds and arXiv
"""
import feedparser
import arxiv
import requests
from datetime import datetime
from typing import List, Dict
import json
import os
import logging
from sqlalchemy.orm import Session

from .models import Source, RawItem, SourceType
from urllib.parse import urlparse

# Frontier lab domains and identifiers
FRONTIER_LABS = {
    "anthropic.com": "Anthropic",
    "openai.com": "OpenAI",
    "deepmind.com": "DeepMind",
    "google.com": "Google AI",  # ai.googleblog.com, research.google
    "googleblog.com": "Google AI",
    "meta.com": "Meta AI",
    "facebook.com": "Meta AI",
    "microsoft.com": "Microsoft Research",
    "microsoftresearch.com": "Microsoft Research"
}

# arXiv author patterns for frontier labs
ARXIV_LAB_PATTERNS = {
    "Anthropic": ["anthropic", "anthropic ai"],
    "OpenAI": ["openai", "open ai"],
    "DeepMind": ["deepmind", "deep mind"],
    "Google AI": ["google research", "google ai", "google brain"],
    "Meta AI": ["meta ai", "facebook ai research", "fair"],
    "Microsoft Research": ["microsoft research", "msr"]
}

logger = logging.getLogger(__name__)


def load_rss_config() -> List[Dict]:
    """Load RSS feed configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rss_feeds.json')
    try:
        with open(config_path, 'r') as f:
            feeds = json.load(f)
        return [f for f in feeds if f.get('enabled', True)]
    except Exception as e:
        logger.error(f"Failed to load RSS config: {e}")
        return []


def load_arxiv_config() -> Dict:
    """Load arXiv configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'arxiv_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load arXiv config: {e}")
        return {"categories": [], "keywords": [], "max_results_per_category": 50}


def detect_frontier_lab_from_url(url: str) -> str:
    """Detect frontier lab from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    for lab_domain, lab_name in FRONTIER_LABS.items():
        if lab_domain in domain:
            return lab_name
    
    return None


def ingest_rss_feeds(db) -> int:
    """Ingest items from RSS feeds"""
    feeds = load_rss_config()
    count = 0
    
    for feed_config in feeds:
        try:
            logger.info(f"Ingesting RSS feed: {feed_config['name']}")
            
            # Check if this is a frontier lab feed
            frontier_lab = feed_config.get('frontier_lab')
            source_type = SourceType.PRIMARY_LAB if frontier_lab else SourceType.RSS
            
            # Get or create source
            source = db.query(Source).filter(
                Source.url == feed_config['url']
            ).first()
            
            if not source:
                source = Source(
                    name=feed_config['name'],
                    url=feed_config['url'],
                    source_type=source_type,
                    is_active=True
                )
                db.add(source)
                db.flush()
            else:
                # Update source type if it's a frontier lab
                if frontier_lab and source.source_type != SourceType.PRIMARY_LAB:
                    source.source_type = SourceType.PRIMARY_LAB
                    db.flush()
            
            # Parse feed
            parsed = feedparser.parse(feed_config['url'])
            
            for entry in parsed.entries[:20]:  # Limit to 20 items per feed
                # Check if already exists
                existing = db.query(RawItem).filter(
                    RawItem.url == entry.get('link', '')
                ).first()
                
                if existing:
                    continue
                
                # Detect frontier lab from URL if not in config
                item_frontier_lab = frontier_lab
                if not item_frontier_lab:
                    item_frontier_lab = detect_frontier_lab_from_url(entry.get('link', ''))
                
                # Parse published date
                published_at = None
                if 'published_parsed' in entry:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                
                item = RawItem(
                    source_id=source.id,
                    title=entry.get('title', 'Untitled'),
                    url=entry.get('link', ''),
                    content=entry.get('summary', ''),
                    published_at=published_at,
                    frontier_lab=item_frontier_lab
                )
                db.add(item)
                count += 1
            
            db.commit()
            logger.info(f"Ingested {count} items from {feed_config['name']}")
            
        except Exception as e:
            logger.error(f"Error ingesting RSS feed {feed_config.get('name', 'unknown')}: {e}")
            db.rollback()
            continue
    
    return count


def ingest_arxiv(db) -> int:
    """Ingest items from arXiv"""
    config = load_arxiv_config()
    count = 0
    
    # Get or create arXiv source
    source = db.query(Source).filter(
        Source.name == "ArXiv",
        Source.source_type == SourceType.ARXIV
    ).first()
    
    if not source:
        source = Source(
            name="ArXiv",
            url="https://arxiv.org/list/cs.AI/recent",
            source_type=SourceType.ARXIV,
            is_active=True
        )
        db.add(source)
        db.flush()
    
    categories = config.get('categories', [])
    
    for category in categories:
        try:
            logger.info(f"Ingesting arXiv category: {category}")
            
            # Search arXiv
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=config.get('max_results_per_category', 50),
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            for result in search.results():
                # Check if already exists
                existing = db.query(RawItem).filter(
                    RawItem.url == result.entry_id
                ).first()
                
                if existing:
                    continue
                
                # Detect frontier lab from author affiliations
                frontier_lab = None
                authors_str = ' '.join([str(a) for a in result.authors]).lower()
                for lab_name, patterns in ARXIV_LAB_PATTERNS.items():
                    for pattern in patterns:
                        if pattern in authors_str:
                            frontier_lab = lab_name
                            break
                    if frontier_lab:
                        break
                
                item = RawItem(
                    source_id=source.id,
                    title=result.title,
                    url=result.entry_id,
                    content=result.summary,
                    published_at=result.published,
                    frontier_lab=frontier_lab
                )
                db.add(item)
                count += 1
            
            db.commit()
            logger.info(f"Ingested {count} items from arXiv {category}")
            
        except Exception as e:
            logger.error(f"Error ingesting arXiv category {category}: {e}")
            db.rollback()
            continue
    
    return count


def run(db) -> Dict:
    """Run scout agent"""
    logger.info("Starting Scout Agent")
    
    rss_count = ingest_rss_feeds(db)
    arxiv_count = ingest_arxiv(db)
    
    total = rss_count + arxiv_count
    
    logger.info(f"Scout Agent completed: {total} items ingested ({rss_count} RSS, {arxiv_count} arXiv)")
    
    return {
        "rss_count": rss_count,
        "arxiv_count": arxiv_count,
        "total": total
    }

