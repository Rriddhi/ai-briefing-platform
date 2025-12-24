"""
Editor Agent: Score and rank clusters
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from .models import Cluster, ScoreBreakdown, RawItem

logger = logging.getLogger(__name__)


def calculate_relevance_score(cluster: Cluster) -> float:
    """Calculate relevance score (0-1)"""
    # Based on topic match and content quality
    if not cluster.summary or len(cluster.summary) < 100:
        return 0.3
    
    if len(cluster.topics) > 0:
        return 0.8 + (len(cluster.topics) * 0.05)
    
    return 0.5


def calculate_impact_score(cluster: Cluster) -> float:
    """Calculate impact score (0-1)"""
    # Based on number of sources and engagement signals
    item_count = len(cluster.raw_items)
    
    if item_count >= 5:
        return 0.9
    elif item_count >= 3:
        return 0.7
    elif item_count >= 2:
        return 0.5
    else:
        return 0.3


def calculate_credibility_score(cluster: Cluster) -> float:
    """Calculate credibility score (0-1)"""
    # Based on source quality (simplified)
    has_arxiv = any(item.source.source_type.value == 'arxiv' for item in cluster.raw_items)
    
    if has_arxiv:
        return 0.9
    elif len(cluster.raw_items) >= 2:
        return 0.7
    else:
        return 0.5


def calculate_novelty_score(cluster: Cluster) -> float:
    """Calculate novelty score (0-1)"""
    # Based on recency
    if not cluster.raw_items:
        return 0.3
    
    newest_item = max(cluster.raw_items, key=lambda x: x.published_at or datetime.min)
    
    if not newest_item.published_at:
        return 0.3
    
    age_days = (datetime.utcnow() - newest_item.published_at.replace(tzinfo=None)).days
    
    if age_days <= 1:
        return 0.9
    elif age_days <= 3:
        return 0.7
    elif age_days <= 7:
        return 0.5
    else:
        return 0.3


def calculate_corroboration_score(cluster: Cluster) -> float:
    """Calculate corroboration score (0-1)"""
    # Based on number of sources
    item_count = len(cluster.raw_items)
    
    if item_count >= 5:
        return 0.9
    elif item_count >= 3:
        return 0.7
    elif item_count >= 2:
        return 0.5
    else:
        return 0.3


def calculate_overall_score(breakdown: Dict) -> float:
    """Calculate overall score using weighted formula"""
    return (
        0.30 * breakdown['relevance_score'] +
        0.25 * breakdown['impact_score'] +
        0.20 * breakdown['credibility_score'] +
        0.15 * breakdown['novelty_score'] +
        0.10 * breakdown['corroboration_score']
    )


def generate_rationale(breakdown: Dict) -> str:
    """Generate ranking rationale"""
    parts = []
    
    if breakdown['relevance_score'] > 0.8:
        parts.append("highly relevant")
    if breakdown['impact_score'] > 0.8:
        parts.append("significant impact")
    if breakdown['credibility_score'] > 0.8:
        parts.append("high credibility sources")
    if breakdown['novelty_score'] > 0.8:
        parts.append("recent developments")
    if breakdown['corroboration_score'] > 0.8:
        parts.append("multiple corroborating sources")
    
    if parts:
        return f"Ranked high due to: {', '.join(parts)}."
    else:
        return "Ranked based on standard criteria."


def run(db: Session) -> Dict:
    """Run editor agent"""
    logger.info("Starting Editor Agent")
    
    # Get clusters without scores or with outdated scores
    clusters = db.query(Cluster).filter(
        (Cluster.score_breakdown == None) | (Cluster.score < 0.1)
    ).limit(100).all()
    
    scored = 0
    
    for cluster in clusters:
        breakdown = {
            'relevance_score': calculate_relevance_score(cluster),
            'impact_score': calculate_impact_score(cluster),
            'credibility_score': calculate_credibility_score(cluster),
            'novelty_score': calculate_novelty_score(cluster),
            'corroboration_score': calculate_corroboration_score(cluster)
        }
        
        overall_score = calculate_overall_score(breakdown)
        
        cluster.score = overall_score
        cluster.ranking_rationale = generate_rationale(breakdown)
        
        # Create or update score breakdown
        if cluster.score_breakdown:
            sb = cluster.score_breakdown
        else:
            sb = ScoreBreakdown(cluster_id=cluster.id)
            db.add(sb)
            db.flush()
        
        sb.relevance_score = breakdown['relevance_score']
        sb.impact_score = breakdown['impact_score']
        sb.credibility_score = breakdown['credibility_score']
        sb.novelty_score = breakdown['novelty_score']
        sb.corroboration_score = breakdown['corroboration_score']
        
        scored += 1
    
    db.commit()
    
    logger.info(f"Editor Agent completed: {scored} clusters scored")
    
    return {
        "scored": scored
    }

