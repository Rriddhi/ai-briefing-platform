"""
Cleaner Agent: Normalize URLs, extract text, spam filtering
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import Optional, Dict
from sqlalchemy.orm import Session

from .models import RawItem

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """Normalize URL"""
    parsed = urlparse(url)
    # Remove fragment, normalize scheme
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized


def extract_main_text(url: str, existing_content: Optional[str] = None) -> Optional[str]:
    """Extract main readable text from URL"""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            # Limit length
            return text[:10000] if len(text) > 10000 else text
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to extract text from {url}: {e}")
        return existing_content


def is_spam(item: RawItem) -> bool:
    """Simple spam filter"""
    title = item.title.lower()
    content = (item.content or '').lower()
    
    spam_keywords = ['click here', 'free money', 'viagra', 'casino', 'lottery']
    
    for keyword in spam_keywords:
        if keyword in title or keyword in content:
            return True
    
    # Check for very short content
    if content and len(content) < 50:
        return True
    
    return False


def run(db: Session) -> Dict:
    """Run cleaner agent"""
    logger.info("Starting Cleaner Agent")
    
    # Get unprocessed raw items (simplified: process recent items)
    items = db.query(RawItem).filter(
        RawItem.content.is_(None) | (RawItem.content == '')
    ).limit(100).all()
    
    processed = 0
    normalized = 0
    spam_filtered = 0
    
    for item in items:
        try:
            # Normalize URL
            old_url = item.url
            item.url = normalize_url(item.url)
            if old_url != item.url:
                normalized += 1
            
            # Extract content if missing
            if not item.content or len(item.content) < 100:
                extracted = extract_main_text(item.url, item.content)
                if extracted:
                    item.content = extracted
            
            # Spam filter
            if is_spam(item):
                db.delete(item)
                spam_filtered += 1
                continue
            
            processed += 1
            
        except Exception as e:
            logger.error(f"Error cleaning item {item.id}: {e}")
            continue
    
    db.commit()
    
    logger.info(f"Cleaner Agent completed: {processed} processed, {normalized} normalized, {spam_filtered} spam filtered")
    
    return {
        "processed": processed,
        "normalized": normalized,
        "spam_filtered": spam_filtered
    }

