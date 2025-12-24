"""
Writer Agent: Generate summaries and citations
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session

from .models import Cluster, Citation, RawItem

logger = logging.getLogger(__name__)


def generate_summary(cluster: Cluster) -> str:
    """Generate summary from cluster items"""
    if len(cluster.raw_items) == 0:
        return "No content available."
    
    # Use first item's title and content as base
    first_item = cluster.raw_items[0]
    
    title = first_item.title
    content = first_item.content or ""
    
    # Create summary (simplified - in production would use LLM)
    if content:
        summary = content[:500] + "..." if len(content) > 500 else content
    else:
        summary = f"Recent development: {title}"
    
    if len(cluster.raw_items) > 1:
        summary += f" (Based on {len(cluster.raw_items)} sources)"
    
    return summary


def generate_why_this_matters(cluster: Cluster) -> str:
    """Generate 'why this matters' section"""
    topics = [t.name for t in cluster.topics]
    
    if topics:
        return f"This development in {', '.join(topics[:2])} represents an important advancement with potential implications for the field."
    else:
        return "This represents a significant development worth monitoring."


def generate_what_to_watch_next(cluster: Cluster) -> str:
    """Generate 'what to watch next' section"""
    return "Monitor for follow-up research, industry responses, and regulatory developments in the coming weeks."


def create_citations(cluster: Cluster) -> None:
    """Create citations for cluster"""
    # Remove existing citations
    for citation in cluster.citations:
        cluster.citations.remove(citation)
    
    # Create citations from raw items (up to 5)
    for item in cluster.raw_items[:5]:
        citation = Citation(
            cluster_id=cluster.id,
            raw_item_id=item.id,
            citation_text=item.title,
            url=item.url
        )
        cluster.citations.append(citation)


def run(db: Session) -> Dict:
    """Run writer agent"""
    logger.info("Starting Writer Agent")
    
    # Get clusters without summaries
    clusters = db.query(Cluster).filter(
        (Cluster.summary.is_(None)) | (Cluster.summary == '')
    ).limit(100).all()
    
    written = 0
    
    for cluster in clusters:
        cluster.summary = generate_summary(cluster)
        cluster.why_this_matters = generate_why_this_matters(cluster)
        cluster.what_to_watch_next = generate_what_to_watch_next(cluster)
        
        create_citations(cluster)
        
        written += 1
    
    db.commit()
    
    logger.info(f"Writer Agent completed: {written} clusters written")
    
    return {
        "written": written
    }

