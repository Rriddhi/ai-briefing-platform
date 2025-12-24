"""
Clustering Agent: Deduplicate items into story clusters
"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from difflib import SequenceMatcher

from .models import RawItem, Cluster

logger = logging.getLogger(__name__)


def similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity between two texts"""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def find_similar_items(item: RawItem, items: List[RawItem], threshold: float = 0.7) -> List[RawItem]:
    """Find items similar to the given item"""
    similar = []
    item_text = f"{item.title} {item.content or ''}"[:500]
    
    for other in items:
        if other.id == item.id:
            continue
        
        other_text = f"{other.title} {other.content or ''}"[:500]
        sim = similarity_score(item_text, other_text)
        
        if sim >= threshold:
            similar.append(other)
    
    return similar


def run(db: Session) -> Dict:
    """Run clustering agent"""
    logger.info("Starting Clustering Agent")
    
    # Get unclustered items
    items = db.query(RawItem).filter(
        ~RawItem.clusters.any()
    ).limit(200).all()
    
    clusters_created = 0
    items_clustered = 0
    
    processed_item_ids = set()
    
    for item in items:
        if item.id in processed_item_ids:
            continue
        
        # Find similar items
        similar = find_similar_items(item, items, threshold=0.6)
        
        if similar:
            # Create cluster
            cluster = Cluster(
                title=item.title[:500],  # Use first item's title as cluster title
                summary=item.content[:1000] if item.content else None,
                score=0.5  # Default score, will be updated by editor
            )
            db.add(cluster)
            db.flush()
            
            # Add items to cluster
            cluster.raw_items.append(item)
            processed_item_ids.add(item.id)
            
            for sim_item in similar:
                if sim_item.id not in processed_item_ids:
                    cluster.raw_items.append(sim_item)
                    processed_item_ids.add(sim_item.id)
            
            clusters_created += 1
            items_clustered += len(similar) + 1
        else:
            # Single item cluster
            cluster = Cluster(
                title=item.title[:500],
                summary=item.content[:1000] if item.content else None,
                score=0.5
            )
            db.add(cluster)
            db.flush()
            cluster.raw_items.append(item)
            processed_item_ids.add(item.id)
            clusters_created += 1
            items_clustered += 1
    
    db.commit()
    
    logger.info(f"Clustering Agent completed: {clusters_created} clusters created, {items_clustered} items clustered")
    
    return {
        "clusters_created": clusters_created,
        "items_clustered": items_clustered
    }

