"""
People-to-Follow Agent: Track key people, labs, companies, policymakers
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session
import re

from .models import PersonToFollow, Topic, RawItem

logger = logging.getLogger(__name__)


def extract_entities(text: str) -> list:
    """Extract potential person/organization names (simplified)"""
    # Simple pattern matching for names and organizations
    # In production, would use NER or LLM
    patterns = [
        r'Dr\.\s+[A-Z][a-z]+\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+',  # Simple name pattern
    ]
    
    entities = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        entities.extend(matches)
    
    return list(set(entities))[:5]  # Limit to 5 unique entities


def run(db: Session) -> Dict:
    """Run people-to-follow agent"""
    logger.info("Starting People-to-Follow Agent")
    
    # This is a placeholder - in production would extract and track entities
    # For now, just ensure existing people are maintained
    
    people_count = db.query(PersonToFollow).count()
    
    logger.info(f"People-to-Follow Agent completed: {people_count} people tracked")
    
    return {
        "people_tracked": people_count
    }

