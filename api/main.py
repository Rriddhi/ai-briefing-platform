"""
FastAPI backend for AI Briefing Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Import routers
from routers import briefing, topics, stories, search

app = FastAPI(
    title="AI Briefing Platform API",
    description="API for AI news and research briefing platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://web:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(briefing.router)
app.include_router(topics.router)
app.include_router(stories.router)
app.include_router(search.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Briefing Platform API",
        "version": "1.0.0",
        "status": "running"
    }

