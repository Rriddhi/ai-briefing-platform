"""
Editor Agent: Score and rank clusters
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from .models import Cluster, ScoreBreakdown, RawItem, SourceType, ClinicalMaturityLevel

logger = logging.getLogger(__name__)


def has_medicine_topic(cluster: Cluster) -> bool:
    """Check if cluster has medicine topic"""
    return any(t.slug == "medicine-healthcare-ai" for t in cluster.topics)


def has_frontier_lab(cluster: Cluster) -> bool:
    """Check if cluster has frontier lab items"""
    return any(item.frontier_lab for item in cluster.raw_items)


def calculate_relevance_score(cluster: Cluster) -> float:
    """Calculate relevance score (0-1)"""
    # Based on topic match and content quality
    if not cluster.summary or len(cluster.summary) < 100:
        return 0.3
    
    # Medicine topics get priority
    if has_medicine_topic(cluster):
        base_score = 0.85
    elif len(cluster.topics) > 0:
        base_score = 0.8
    else:
        base_score = 0.5
    
    # Add bonus for multiple topics
    return min(1.0, base_score + (len(cluster.topics) * 0.03))


def calculate_impact_score(cluster: Cluster) -> float:
    """Calculate impact score (0-1)"""
    # Frontier labs get high impact by default
    if has_frontier_lab(cluster):
        return 0.95  # Single lab announcement is high impact
    
    # Medicine regulatory updates get high impact
    if has_medicine_topic(cluster) and cluster.clinical_maturity_level == ClinicalMaturityLevel.REGULATORY_RELEVANT:
        return 0.95
    
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


def calculate_credibility_score(cluster: Cluster) -> float:
    """Calculate credibility score (0-1) - boosted for medicine and frontier labs"""
    # Frontier labs get maximum credibility
    if has_frontier_lab(cluster):
        return 0.95
    
    # Medicine sources get boosted credibility (evidence quality prioritized)
    if has_medicine_topic(cluster):
        # FDA/NIH regulatory sources get highest credibility
        has_regulatory = any(
            "fda" in item.url.lower() or "nih" in item.url.lower() or 
            "fda" in (item.title or "").lower() or "nih" in (item.title or "").lower()
            for item in cluster.raw_items
        )
        if has_regulatory:
            return 0.95
        
        # Clinical validation increases credibility
        if cluster.clinical_maturity_level == ClinicalMaturityLevel.CLINICALLY_VALIDATED:
            return 0.9
        elif cluster.clinical_maturity_level == ClinicalMaturityLevel.REGULATORY_RELEVANT:
            return 0.92
        
        # Medicine sources generally higher credibility
        return 0.85
    
    # Standard credibility scoring
    has_arxiv = any(item.source.source_type.value == 'arxiv' for item in cluster.raw_items)
    
    if has_arxiv:
        return 0.9
    elif len(cluster.raw_items) >= 2:
        return 0.7
    else:
        return 0.5


def calculate_novelty_score(cluster: Cluster) -> float:
    """Calculate novelty score (0-1) - regulatory relevance can outweigh novelty for medicine"""
    if not cluster.raw_items:
        return 0.3
    
    newest_item = max(cluster.raw_items, key=lambda x: x.published_at or datetime.min)
    
    if not newest_item.published_at:
        return 0.3
    
    age_days = (datetime.utcnow() - newest_item.published_at.replace(tzinfo=None)).days
    
    # For medicine regulatory updates, maintain higher novelty even if older
    if has_medicine_topic(cluster) and cluster.clinical_maturity_level == ClinicalMaturityLevel.REGULATORY_RELEVANT:
        if age_days <= 7:
            return 0.9  # Regulatory updates stay relevant longer
        elif age_days <= 30:
            return 0.75
    
    # Standard novelty scoring
    if age_days <= 1:
        return 0.9
    elif age_days <= 3:
        return 0.7
    elif age_days <= 7:
        return 0.5
    else:
        return 0.3


def calculate_corroboration_score(cluster: Cluster) -> float:
    """Calculate corroboration score (0-1) - reduced requirement for frontier labs"""
    # Frontier labs don't need corroboration - single source is sufficient
    if has_frontier_lab(cluster):
        return 0.9  # High score even with single source
    
    # Medicine regulatory sources also don't need multiple corroborations
    if has_medicine_topic(cluster) and cluster.clinical_maturity_level == ClinicalMaturityLevel.REGULATORY_RELEVANT:
        return 0.9
    
    # Standard corroboration scoring
    item_count = len(cluster.raw_items)
    
    if item_count >= 5:
        return 0.9
    elif item_count >= 3:
        return 0.7
    elif item_count >= 2:
        return 0.5
    else:
        return 0.3


def calculate_overall_score(breakdown: Dict, cluster: Cluster) -> float:
    """Calculate overall score using weighted formula - adjusted for medicine"""
    # Medicine-specific weights: higher credibility weight
    if has_medicine_topic(cluster):
        return (
            0.30 * breakdown['relevance_score'] +
            0.25 * breakdown['impact_score'] +
            0.30 * breakdown['credibility_score'] +  # Increased from 0.20
            0.10 * breakdown['novelty_score'] +      # Decreased from 0.15
            0.05 * breakdown['corroboration_score']  # Decreased from 0.10
        )
    
    # Standard weights
    return (
        0.30 * breakdown['relevance_score'] +
        0.25 * breakdown['impact_score'] +
        0.20 * breakdown['credibility_score'] +
        0.15 * breakdown['novelty_score'] +
        0.10 * breakdown['corroboration_score']
    )


def generate_rationale(breakdown: Dict, cluster: Cluster) -> str:
    """Generate ranking rationale with medicine and lab context"""
    parts = []
    
    # Frontier lab mentions
    if has_frontier_lab(cluster):
        labs = list(set(item.frontier_lab for item in cluster.raw_items if item.frontier_lab))
        parts.append(f"primary announcement from {', '.join(labs)}")
    
    # Medicine-specific rationale
    if has_medicine_topic(cluster):
        if cluster.clinical_maturity_level == ClinicalMaturityLevel.REGULATORY_RELEVANT:
            parts.append("regulatory significance (FDA/NIH)")
        elif cluster.clinical_maturity_level == ClinicalMaturityLevel.CLINICALLY_VALIDATED:
            parts.append("clinically validated evidence")
        parts.append("medical AI priority topic")
    
    # Standard rationale
    if breakdown['relevance_score'] > 0.8 and not has_medicine_topic(cluster):
        parts.append("highly relevant")
    if breakdown['impact_score'] > 0.8:
        parts.append("significant impact")
    if breakdown['credibility_score'] > 0.8:
        parts.append("high credibility sources")
    if breakdown['novelty_score'] > 0.8:
        parts.append("recent developments")
    if breakdown['corroboration_score'] > 0.8 and not has_frontier_lab(cluster):
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
        
        overall_score = calculate_overall_score(breakdown, cluster)
        
        cluster.score = overall_score
        cluster.ranking_rationale = generate_rationale(breakdown, cluster)
        
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

