"""
Tagger Agent: Assign topics to clusters
"""
import logging
from typing import Dict, List
from sqlalchemy.orm import Session

from .models import Cluster, Topic

logger = logging.getLogger(__name__)

# Topic keywords mapping
TOPIC_KEYWORDS = {
    "robotics": ["robot", "robotics", "autonomous robot", "drone", "manipulation", "grasping"],
    "medicine-healthcare-ai": ["medical", "healthcare", "clinical", "diagnosis", "drug", "treatment", "patient"],
    "automotive-autonomous": ["autonomous vehicle", "self-driving", "car", "automotive", "autopilot", "tesla"],
    "human-centered-ai": ["human", "interaction", "ui", "ux", "accessibility", "fairness", "bias", "ethics"],
    "ai-policy-governance": ["policy", "regulation", "governance", "law", "government", "compliance", "ethics"],
    "general-ai": ["language model", "llm", "neural network", "deep learning", "machine learning", "ai", "transformer"]
}


def assign_topics(cluster: Cluster, topics: List[Topic]) -> List[Topic]:
    """Assign topics to a cluster based on content"""
    cluster_text = f"{cluster.title} {cluster.summary or ''}".lower()
    
    assigned = []
    
    for topic in topics:
        keywords = TOPIC_KEYWORDS.get(topic.slug, [])
        match_count = sum(1 for keyword in keywords if keyword in cluster_text)
        
        if match_count >= 2:  # At least 2 keyword matches
            assigned.append(topic)
    
    # If no topics assigned, assign to general-ai
    if not assigned:
        general_ai = next((t for t in topics if t.slug == "general-ai"), None)
        if general_ai:
            assigned.append(general_ai)
    
    return assigned


def run(db: Session) -> Dict:
    """Run tagger agent"""
    logger.info("Starting Tagger Agent")
    
    # Get all topics
    topics = db.query(Topic).all()
    topic_dict = {t.slug: t for t in topics}
    
    # Get untagged clusters
    clusters = db.query(Cluster).filter(
        ~Cluster.topics.any()
    ).limit(100).all()
    
    tagged = 0
    
    for cluster in clusters:
        assigned_topics = assign_topics(cluster, topics)
        cluster.topics = assigned_topics
        tagged += 1
    
    db.commit()
    
    logger.info(f"Tagger Agent completed: {tagged} clusters tagged")
    
    return {
        "tagged": tagged
    }

