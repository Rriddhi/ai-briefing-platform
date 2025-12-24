"""
Tagger Agent: Assign topics to clusters
"""
import logging
from typing import Dict, List
from sqlalchemy.orm import Session

from .models import Cluster, Topic, ClinicalMaturityLevel

logger = logging.getLogger(__name__)

# Topic keywords mapping (medicine expanded)
TOPIC_KEYWORDS = {
    "robotics": ["robot", "robotics", "autonomous robot", "drone", "manipulation", "grasping"],
    "medicine-healthcare-ai": [
        "medical", "healthcare", "clinical", "diagnosis", "drug", "treatment", "patient",
        "fda", "nih", "regulatory", "approval", "clinical trial", "medical device",
        "health tech", "telemedicine", "electronic health record", "ehr", "medical imaging",
        "radiology", "pathology", "oncology", "cardiovascular", "neuroscience", "biomedical"
    ],
    "automotive-autonomous": ["autonomous vehicle", "self-driving", "car", "automotive", "autopilot", "tesla"],
    "human-centered-ai": ["human", "interaction", "ui", "ux", "accessibility", "fairness", "bias", "ethics"],
    "ai-policy-governance": ["policy", "regulation", "governance", "law", "government", "compliance", "ethics"],
    "general-ai": ["language model", "llm", "neural network", "deep learning", "machine learning", "ai", "transformer"]
}

# Frontier lab default topics
FRONTIER_LAB_DEFAULT_TOPICS = {
    "Anthropic": ["general-ai", "ai-policy-governance", "human-centered-ai"],
    "OpenAI": ["general-ai", "ai-policy-governance"],
    "DeepMind": ["general-ai", "robotics"],
    "Google AI": ["general-ai"],
    "Meta AI": ["general-ai"],
    "Microsoft Research": ["general-ai", "human-centered-ai"]
}


def detect_clinical_maturity(cluster: Cluster) -> ClinicalMaturityLevel:
    """Detect clinical maturity level from cluster content"""
    cluster_text = f"{cluster.title} {cluster.summary or ''}".lower()
    
    # Check for regulatory relevance
    regulatory_keywords = ["fda", "nih", "approval", "clearance", "regulatory", "ce mark", "ema"]
    if any(kw in cluster_text for kw in regulatory_keywords):
        if any(kw in cluster_text for kw in ["approved", "cleared", "authorized"]):
            return ClinicalMaturityLevel.APPROVED_DEPLOYED
        return ClinicalMaturityLevel.REGULATORY_RELEVANT
    
    # Check for clinical validation
    validation_keywords = ["clinical trial", "randomized", "validated", "peer-reviewed", "phase"]
    if any(kw in cluster_text for kw in validation_keywords):
        return ClinicalMaturityLevel.CLINICALLY_VALIDATED
    
    # Default to exploratory
    return ClinicalMaturityLevel.EXPLORATORY


def assign_topics(cluster: Cluster, topics: List[Topic]) -> List[Topic]:
    """Assign topics to a cluster based on content and frontier lab status"""
    cluster_text = f"{cluster.title} {cluster.summary or ''}".lower()
    topic_dict = {t.slug: t for t in topics}
    assigned = []
    
    # Check for frontier lab items
    frontier_labs = set()
    for item in cluster.raw_items:
        if item.frontier_lab:
            frontier_labs.add(item.frontier_lab)
    
    # Add frontier lab default topics
    for lab in frontier_labs:
        default_topics = FRONTIER_LAB_DEFAULT_TOPICS.get(lab, [])
        for topic_slug in default_topics:
            if topic_slug in topic_dict and topic_dict[topic_slug] not in assigned:
                assigned.append(topic_dict[topic_slug])
    
    # Special handling for Anthropic policy/safety content
    if "Anthropic" in frontier_labs:
        policy_keywords = ["safety", "alignment", "policy", "governance", "regulation"]
        if any(kw in cluster_text for kw in policy_keywords):
            if "ai-policy-governance" in topic_dict and topic_dict["ai-policy-governance"] not in assigned:
                assigned.append(topic_dict["ai-policy-governance"])
            if "human-centered-ai" in topic_dict and topic_dict["human-centered-ai"] not in assigned:
                assigned.append(topic_dict["human-centered-ai"])
    
    # Medicine tagging (high priority, lower threshold)
    medicine_topic = topic_dict.get("medicine-healthcare-ai")
    if medicine_topic:
        medicine_keywords = TOPIC_KEYWORDS.get("medicine-healthcare-ai", [])
        medicine_match_count = sum(1 for keyword in medicine_keywords if keyword in cluster_text)
        if medicine_match_count >= 1:  # Lower threshold for medicine
            if medicine_topic not in assigned:
                assigned.append(medicine_topic)
    
    # Other topics (standard threshold)
    for topic in topics:
        if topic in assigned:  # Skip already assigned
            continue
        
        topic_slug = topic.slug
        if topic_slug == "medicine-healthcare-ai":  # Already handled
            continue
            
        keywords = TOPIC_KEYWORDS.get(topic_slug, [])
        match_count = sum(1 for keyword in keywords if keyword in cluster_text)
        
        if match_count >= 2:  # At least 2 keyword matches
            assigned.append(topic)
    
    # If no topics assigned, assign to general-ai
    if not assigned:
        general_ai = topic_dict.get("general-ai")
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
        
        # Detect and set clinical maturity level if medicine-related
        has_medicine = any(t.slug == "medicine-healthcare-ai" for t in assigned_topics)
        if has_medicine and not cluster.clinical_maturity_level:
            cluster.clinical_maturity_level = detect_clinical_maturity(cluster)
        
        tagged += 1
    
    db.commit()
    
    logger.info(f"Tagger Agent completed: {tagged} clusters tagged")
    
    return {
        "tagged": tagged
    }

