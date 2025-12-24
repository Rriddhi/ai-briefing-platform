"""
Briefing API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List

from database import get_db
from models import DailyBriefing, Cluster, ScoreBreakdown, Citation, Topic
from schemas import BriefingResponse, StoryItemResponse, ScoreBreakdownResponse, CitationResponse, TopicResponse

router = APIRouter(prefix="/briefing", tags=["briefing"])


def cluster_to_story_response(cluster: Cluster) -> StoryItemResponse:
    """Convert cluster model to story response"""
    score_breakdown = None
    if cluster.score_breakdown:
        score_breakdown = ScoreBreakdownResponse(
            relevance_score=cluster.score_breakdown.relevance_score,
            impact_score=cluster.score_breakdown.impact_score,
            credibility_score=cluster.score_breakdown.credibility_score,
            novelty_score=cluster.score_breakdown.novelty_score,
            corroboration_score=cluster.score_breakdown.corroboration_score,
        )
    
    citations = [
        CitationResponse(
            id=c.id,
            citation_text=c.citation_text,
            url=c.url
        )
        for c in cluster.citations
    ]
    
    topics = [
        TopicResponse(
            id=t.id,
            name=t.name,
            slug=t.slug
        )
        for t in cluster.topics
    ]
    
    return StoryItemResponse(
        id=cluster.id,
        title=cluster.title,
        summary=cluster.summary,
        why_this_matters=cluster.why_this_matters,
        what_to_watch_next=cluster.what_to_watch_next,
        score=cluster.score,
        ranking_rationale=cluster.ranking_rationale,
        score_breakdown=score_breakdown,
        citations=citations,
        topics=topics,
        clinical_maturity_level=cluster.clinical_maturity_level.value if cluster.clinical_maturity_level else None,
        created_at=cluster.created_at
    )


@router.get("/today", response_model=BriefingResponse)
async def get_today_briefing(db: Session = Depends(get_db)):
    """
    Get today's daily briefing with ranked stories
    
    Returns the briefing for today's date with associated clusters/stories,
    sorted by score (highest first).
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    briefing = db.query(DailyBriefing).filter(
        DailyBriefing.briefing_date == today
    ).first()
    
    if not briefing:
        # If no briefing exists for today, return empty briefing with top clusters
        clusters = db.query(Cluster).order_by(desc(Cluster.score)).limit(10).all()
        stories = [cluster_to_story_response(c) for c in clusters]
        
        return BriefingResponse(
            id=0,
            briefing_date=today,
            content="No briefing available for today",
            stories=stories
        )
    
    # Get clusters associated with briefing, sorted by score
    clusters = sorted(briefing.clusters, key=lambda c: c.score, reverse=True)
    stories = [cluster_to_story_response(c) for c in clusters]
    
    return BriefingResponse(
        id=briefing.id,
        briefing_date=briefing.briefing_date,
        content=briefing.content,
        stories=stories
    )
