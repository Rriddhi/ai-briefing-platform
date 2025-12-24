"""
Topics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from database import get_db
from models import Topic, Cluster, ScoreBreakdown, Citation
from schemas import TopicStoriesResponse, TopicResponse, StoryItemResponse, ScoreBreakdownResponse, CitationResponse
from routers.briefing import cluster_to_story_response

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/{topic_slug}", response_model=TopicStoriesResponse)
async def get_topic_stories(
    topic_slug: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    Get stories for a specific topic
    
    Returns clusters/stories tagged with the given topic,
    sorted by score (highest first).
    """
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_slug}' not found")
    
    # Get clusters for this topic, ordered by score
    clusters = db.query(Cluster).join(
        Cluster.topics
    ).filter(
        Topic.id == topic.id
    ).order_by(desc(Cluster.score)).offset(skip).limit(limit).all()
    
    total = db.query(Cluster).join(
        Cluster.topics
    ).filter(Topic.id == topic.id).count()
    
    stories = [cluster_to_story_response(c) for c in clusters]
    
    topic_response = TopicResponse(
        id=topic.id,
        name=topic.name,
        slug=topic.slug
    )
    
    return TopicStoriesResponse(
        topic=topic_response,
        stories=stories,
        total=total
    )
