"""
Search API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from database import get_db
from models import Cluster
from schemas import SearchResponse, StoryItemResponse
from routers.briefing import cluster_to_story_response

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search_stories(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    Search stories by query string
    
    Searches in cluster titles and summaries.
    Returns results sorted by score (highest first).
    """
    if not q or not q.strip():
        return SearchResponse(query=q, stories=[], total=0)
    
    search_term = f"%{q.strip()}%"
    
    # Search in title and summary
    clusters = db.query(Cluster).filter(
        or_(
            Cluster.title.ilike(search_term),
            Cluster.summary.ilike(search_term)
        )
    ).order_by(desc(Cluster.score)).offset(skip).limit(limit).all()
    
    total = db.query(Cluster).filter(
        or_(
            Cluster.title.ilike(search_term),
            Cluster.summary.ilike(search_term)
        )
    ).count()
    
    stories = [cluster_to_story_response(c) for c in clusters]
    
    return SearchResponse(
        query=q,
        stories=stories,
        total=total
    )
