"""
Writer Agent: Generate summaries and citations
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session

from .models import Cluster, Citation, RawItem

logger = logging.getLogger(__name__)


def get_frontier_lab(cluster: Cluster) -> str:
    """Get frontier lab name from cluster items"""
    for item in cluster.raw_items:
        if item.frontier_lab:
            return item.frontier_lab
    return None


def generate_summary(cluster: Cluster) -> str:
    """Generate summary from cluster items - explicitly names labs and frames as primary"""
    if len(cluster.raw_items) == 0:
        return "No content available."
    
    first_item = cluster.raw_items[0]
    frontier_lab = get_frontier_lab(cluster)
    title = first_item.title
    content = first_item.content or ""
    
    # For frontier labs, frame as primary announcement
    if frontier_lab:
        # First sentence must explicitly name the lab
        summary = f"{frontier_lab} {'announced' if 'announce' in title.lower() or 'release' in title.lower() else 'released'}: {title}."
        
        # Add content if available
        if content:
            summary += " " + (content[:400] + "..." if len(content) > 400 else content)
        
        # Add downstream implications note
        summary += " This announcement has implications for research directions, deployment strategies, and policy considerations."
    else:
        # Standard summary for non-lab sources
        if content:
            summary = content[:500] + "..." if len(content) > 500 else content
        else:
            summary = f"Recent development: {title}"
        
        if len(cluster.raw_items) > 1:
            summary += f" (Based on {len(cluster.raw_items)} sources)"
    
    return summary


def generate_why_this_matters(cluster: Cluster) -> str:
    """Generate 'why this matters' section"""
    frontier_lab = get_frontier_lab(cluster)
    topics = [t.name for t in cluster.topics]
    has_medicine = any(t.slug == "medicine-healthcare-ai" for t in cluster.topics)
    
    # Medicine-specific framing
    if has_medicine:
        if cluster.clinical_maturity_level and cluster.clinical_maturity_level.value == "regulatory_relevant":
            return "FDA and NIH regulatory updates directly impact the deployment timeline and clinical adoption of AI technologies in healthcare. These decisions shape the entire medical AI ecosystem."
        elif cluster.clinical_maturity_level and cluster.clinical_maturity_level.value == "clinically_validated":
            return "Clinically validated AI systems represent a critical step from research to real-world patient care, with direct implications for healthcare delivery and outcomes."
        else:
            return f"This development in {', '.join(topics[:2]) if topics else 'medical AI'} has potential to improve diagnosis, treatment, and patient outcomes. Medical AI developments require careful evaluation of clinical evidence and regulatory pathways."
    
    # Frontier lab framing
    if frontier_lab:
        return f"{frontier_lab}'s announcements shape the direction of AI research and industry practices. This development influences model capabilities, safety standards, and policy considerations across the AI ecosystem."
    
    # Standard framing
    if topics:
        return f"This development in {', '.join(topics[:2])} represents an important advancement with potential implications for the field."
    else:
        return "This represents a significant development worth monitoring."


def generate_what_to_watch_next(cluster: Cluster) -> str:
    """Generate 'what to watch next' section"""
    has_medicine = any(t.slug == "medicine-healthcare-ai" for t in cluster.topics)
    frontier_lab = get_frontier_lab(cluster)
    
    if has_medicine:
        return "Watch for clinical trial results, regulatory approvals, real-world deployment data, and adoption in healthcare systems. Monitor FDA/NIH guidance updates and clinical guideline changes."
    elif frontier_lab:
        return "Monitor for research community responses, downstream model releases, safety evaluations, and policy discussions. Watch for adoption by developers and integration into production systems."
    else:
        return "Monitor for follow-up research, industry responses, and regulatory developments in the coming weeks."


def create_citations(cluster: Cluster) -> None:
    """Create citations for cluster"""
    # Remove existing citations
    for citation in cluster.citations:
        cluster.citations.remove(citation)
    
    # Create citations from raw items (up to 5)
    for item in cluster.raw_items[:5]:
        citation = Citation(
            cluster_id=cluster.id,
            raw_item_id=item.id,
            citation_text=item.title,
            url=item.url
        )
        cluster.citations.append(citation)


def run(db: Session) -> Dict:
    """Run writer agent"""
    logger.info("Starting Writer Agent")
    
    # Get clusters without summaries
    clusters = db.query(Cluster).filter(
        (Cluster.summary.is_(None)) | (Cluster.summary == '')
    ).limit(100).all()
    
    written = 0
    
    for cluster in clusters:
        cluster.summary = generate_summary(cluster)
        cluster.why_this_matters = generate_why_this_matters(cluster)
        cluster.what_to_watch_next = generate_what_to_watch_next(cluster)
        
        create_citations(cluster)
        
        written += 1
    
    db.commit()
    
    logger.info(f"Writer Agent completed: {written} clusters written")
    
    return {
        "written": written
    }

