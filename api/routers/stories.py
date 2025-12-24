"""
Stories API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Cluster
from schemas import StoryItemResponse
from routers.briefing import cluster_to_story_response

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/{cluster_id}", response_model=StoryItemResponse)
async def get_story(cluster_id: int, db: Session = Depends(get_db)):
    """
    Get a specific story/cluster by ID
    
    Returns full details including summary, citations, score breakdown, and rationale.
    """
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
    
    if not cluster:
        raise HTTPException(status_code=404, detail=f"Story {cluster_id} not found")
    
    return cluster_to_story_response(cluster)
