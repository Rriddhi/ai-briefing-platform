"""
Seed script for populating database with realistic fake data
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import (
    Source, RawItem, Topic, Cluster, ScoreBreakdown, Citation,
    DailyBriefing, PersonToFollow, SourceType
)
from datetime import datetime, timedelta
import random

# Initialize database
from models import Base
Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()


def seed_topics():
    """Seed topics"""
    topics_data = [
        {"name": "Robotics", "slug": "robotics", "description": "Robotics and autonomous systems"},
        {"name": "Medicine & Healthcare AI", "slug": "medicine-healthcare-ai", "description": "AI applications in medicine and healthcare"},
        {"name": "Automotive & Autonomous Systems", "slug": "automotive-autonomous", "description": "Self-driving cars and automotive AI"},
        {"name": "Human-Centered AI", "slug": "human-centered-ai", "description": "AI designed with human needs in mind"},
        {"name": "AI Policy & Governance", "slug": "ai-policy-governance", "description": "Regulations and governance of AI systems"},
        {"name": "General AI", "slug": "general-ai", "description": "General AI models, infrastructure, and tools"},
    ]
    
    topics = []
    for topic_data in topics_data:
        topic = db.query(Topic).filter(Topic.slug == topic_data["slug"]).first()
        if not topic:
            topic = Topic(**topic_data)
            db.add(topic)
            db.flush()
        topics.append(topic)
    
    db.commit()
    return topics


def seed_sources():
    """Seed sources"""
    sources_data = [
        {"name": "ArXiv CS.AI", "url": "https://arxiv.org/list/cs.AI/recent", "source_type": SourceType.ARXIV},
        {"name": "ArXiv CS.RO", "url": "https://arxiv.org/list/cs.RO/recent", "source_type": SourceType.ARXIV},
        {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "source_type": SourceType.RSS},
        {"name": "AI News RSS", "url": "https://example.com/ai-news.xml", "source_type": SourceType.RSS},
    ]
    
    sources = []
    for source_data in sources_data:
        source = db.query(Source).filter(Source.url == source_data["url"]).first()
        if not source:
            source = Source(**source_data)
            db.add(source)
            db.flush()
        sources.append(source)
    
    db.commit()
    return sources


def seed_raw_items(sources):
    """Seed raw items"""
    items = []
    now = datetime.utcnow()
    
    for i in range(20):
        item = RawItem(
            source_id=random.choice(sources).id,
            title=f"AI Development {i+1}: Breakthrough in Machine Learning",
            url=f"https://example.com/article-{i+1}",
            content=f"This is the content of article {i+1} discussing important AI developments.",
            published_at=now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23)),
            ingested_at=now - timedelta(hours=random.randint(0, 24))
        )
        db.add(item)
        db.flush()
        items.append(item)
    
    db.commit()
    return items


def seed_clusters_and_scores(topics, raw_items):
    """Seed clusters with score breakdowns"""
    clusters = []
    
    cluster_titles = [
        "GPT-5 Announcement Signals Next Generation of Language Models",
        "Autonomous Vehicle Regulations Gain Traction in EU",
        "AI-Powered Drug Discovery Shows Promise in Clinical Trials",
        "New Robotics Framework Enables Better Human-Robot Collaboration",
        "White House Releases Executive Order on AI Safety",
        "Open Source LLM Ecosystem Expands Rapidly",
        "AI Ethics Guidelines Updated by Leading Research Labs",
        "Breakthrough in Computer Vision for Medical Imaging",
    ]
    
    for i, title in enumerate(cluster_titles[:6]):  # Create 6 clusters
        # Calculate weighted score
        relevance = random.uniform(0.7, 1.0)
        impact = random.uniform(0.6, 0.95)
        credibility = random.uniform(0.75, 1.0)
        novelty = random.uniform(0.5, 0.9)
        corroboration = random.uniform(0.6, 0.95)
        
        score = (
            0.30 * relevance +
            0.25 * impact +
            0.20 * credibility +
            0.15 * novelty +
            0.10 * corroboration
        )
        
        cluster = Cluster(
            title=title,
            summary=f"This is a summary of {title}. The development represents a significant advancement in the field.",
            why_this_matters=f"This matters because it demonstrates the growing impact of AI in real-world applications.",
            what_to_watch_next=f"Watch for follow-up research and industry adoption in the coming months.",
            score=score,
            ranking_rationale=f"Ranked high due to strong relevance ({relevance:.2f}), impact ({impact:.2f}), and credibility ({credibility:.2f}) scores."
        )
        db.add(cluster)
        db.flush()
        
        # Add score breakdown
        score_breakdown = ScoreBreakdown(
            cluster_id=cluster.id,
            relevance_score=relevance,
            impact_score=impact,
            credibility_score=credibility,
            novelty_score=novelty,
            corroboration_score=corroboration
        )
        db.add(score_breakdown)
        
        # Associate with topics (1-3 topics per cluster)
        cluster_topics = random.sample(topics, k=random.randint(1, 3))
        cluster.topics = cluster_topics
        
        # Associate with raw items (2-5 items per cluster)
        cluster_items = random.sample(raw_items, k=min(random.randint(2, 5), len(raw_items)))
        cluster.raw_items = cluster_items
        
        # Create citations
        for raw_item in cluster_items[:3]:  # Up to 3 citations per cluster
            citation = Citation(
                cluster_id=cluster.id,
                raw_item_id=raw_item.id,
                citation_text=f"Source: {raw_item.title}",
                url=raw_item.url
            )
            db.add(citation)
        
        clusters.append(cluster)
    
    db.commit()
    return clusters


def seed_daily_briefing(clusters):
    """Seed daily briefing"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    briefing = db.query(DailyBriefing).filter(DailyBriefing.briefing_date == today).first()
    if not briefing:
        briefing = DailyBriefing(
            briefing_date=today,
            content=f"Today's briefing covers {len(clusters[:5])} key developments in AI. Here are the highlights..."
        )
        db.add(briefing)
        db.flush()
        
        # Associate top 5 clusters with briefing
        top_clusters = sorted(clusters, key=lambda c: c.score, reverse=True)[:5]
        briefing.clusters = top_clusters
        
        db.commit()
    
    return briefing


def seed_people_to_follow(topics):
    """Seed people to follow"""
    people_data = [
        {"name": "Dr. Jane Smith", "title": "AI Researcher", "organization": "MIT CSAIL", "topic": "General AI", "url": "https://example.com/jane-smith"},
        {"name": "Dr. John Doe", "title": "Robotics Professor", "organization": "Stanford", "topic": "Robotics", "url": "https://example.com/john-doe"},
        {"name": "Dr. Sarah Chen", "title": "Medical AI Director", "organization": "Johns Hopkins", "topic": "Medicine & Healthcare AI", "url": "https://example.com/sarah-chen"},
        {"name": "Alex Johnson", "title": "Autonomous Systems Engineer", "organization": "Waymo", "topic": "Automotive & Autonomous Systems", "url": "https://example.com/alex-johnson"},
        {"name": "Dr. Michael Brown", "title": "AI Policy Expert", "organization": "Georgetown", "topic": "AI Policy & Governance", "url": "https://example.com/michael-brown"},
        {"name": "Dr. Emily Davis", "title": "HCI Researcher", "organization": "CMU", "topic": "Human-Centered AI", "url": "https://example.com/emily-davis"},
    ]
    
    people = []
    for person_data in people_data:
        topic = next((t for t in topics if t.name == person_data["topic"]), None)
        if topic:
            person = PersonToFollow(
                name=person_data["name"],
                title=person_data["title"],
                organization=person_data["organization"],
                topic_id=topic.id,
                url=person_data["url"],
                notes=f"Key researcher in {person_data['topic']}"
            )
            db.add(person)
            db.flush()
            people.append(person)
    
    db.commit()
    return people


def main():
    """Main seed function"""
    print("Seeding database...")
    
    topics = seed_topics()
    print(f"✓ Seeded {len(topics)} topics")
    
    sources = seed_sources()
    print(f"✓ Seeded {len(sources)} sources")
    
    raw_items = seed_raw_items(sources)
    print(f"✓ Seeded {len(raw_items)} raw items")
    
    clusters = seed_clusters_and_scores(topics, raw_items)
    print(f"✓ Seeded {len(clusters)} clusters with score breakdowns")
    
    briefing = seed_daily_briefing(clusters)
    print(f"✓ Seeded daily briefing")
    
    people = seed_people_to_follow(topics)
    print(f"✓ Seeded {len(people)} people to follow")
    
    print("\nDatabase seeded successfully!")


if __name__ == "__main__":
    main()

