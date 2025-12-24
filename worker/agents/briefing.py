"""
Daily Briefing Generator: Create daily briefing from top clusters
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from .models import DailyBriefing, Cluster

logger = logging.getLogger(__name__)


def generate_briefing_content(clusters: list) -> str:
    """Generate briefing content"""
    if not clusters:
        return "No stories available for today."
    
    content = f"Today's briefing covers {len(clusters)} key developments in AI:\n\n"
    
    for i, cluster in enumerate(clusters[:10], 1):  # Top 10
        content += f"{i}. {cluster.title}\n"
        if cluster.summary:
            content += f"   {cluster.summary[:200]}...\n\n"
    
    return content


def run(db: Session) -> Dict:
    """Run daily briefing generator"""
    logger.info("Starting Daily Briefing Generator")
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if briefing already exists
    existing = db.query(DailyBriefing).filter(
        DailyBriefing.briefing_date == today
    ).first()
    
    if existing:
        logger.info("Daily briefing already exists for today")
        return {
            "briefing_id": existing.id,
            "clusters_count": len(existing.clusters),
            "created": False
        }
    
    # Get top clusters by score
    top_clusters = db.query(Cluster).order_by(
        desc(Cluster.score)
    ).limit(10).all()
    
    if not top_clusters:
        logger.warning("No clusters available for briefing")
        return {
            "briefing_id": None,
            "clusters_count": 0,
            "created": False
        }
    
    # Create briefing
    briefing = DailyBriefing(
        briefing_date=today,
        content=generate_briefing_content(top_clusters)
    )
    db.add(briefing)
    db.flush()
    
    # Associate clusters
    briefing.clusters = top_clusters
    
    db.commit()
    
    logger.info(f"Daily Briefing Generator completed: briefing {briefing.id} created with {len(top_clusters)} clusters")
    
    return {
        "briefing_id": briefing.id,
        "clusters_count": len(top_clusters),
        "created": True
    }

