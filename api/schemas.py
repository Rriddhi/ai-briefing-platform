"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ScoreBreakdownResponse(BaseModel):
    relevance_score: float
    impact_score: float
    credibility_score: float
    novelty_score: float
    corroboration_score: float
    
    class Config:
        from_attributes = True


class CitationResponse(BaseModel):
    id: int
    citation_text: Optional[str]
    url: str
    
    class Config:
        from_attributes = True


class TopicResponse(BaseModel):
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True


class StoryItemResponse(BaseModel):
    """Story/cluster response"""
    id: int
    title: str
    summary: Optional[str]
    why_this_matters: Optional[str]
    what_to_watch_next: Optional[str]
    score: float
    ranking_rationale: Optional[str]
    score_breakdown: Optional[ScoreBreakdownResponse]
    citations: List[CitationResponse]
    topics: List[TopicResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BriefingResponse(BaseModel):
    """Daily briefing response"""
    id: int
    briefing_date: datetime
    content: Optional[str]
    stories: List[StoryItemResponse]
    
    class Config:
        from_attributes = True


class TopicStoriesResponse(BaseModel):
    """Topic page response"""
    topic: TopicResponse
    stories: List[StoryItemResponse]
    total: int
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    stories: List[StoryItemResponse]
    total: int
    
    class Config:
        from_attributes = True

