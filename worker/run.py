"""
Worker CLI entry point
"""
import argparse
import logging
import sys
import os

# Add api to path for models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agents
from agents.scout import run as scout_run
from agents.cleaner import run as cleaner_run
from agents.cluster import run as cluster_run
from agents.tagger import run as tagger_run
from agents.editor import run as editor_run
from agents.writer import run as writer_run
from agents.people import run as people_run
from agents.briefing import run as briefing_run


def run_once():
    """Run the full pipeline once"""
    logger.info("=" * 60)
    logger.info("Starting AI Briefing Platform Worker Pipeline")
    logger.info("=" * 60)
    
    db = next(get_db())
    
    try:
        # Agent 1: Scout
        logger.info("\n[1/7] Scout Agent")
        scout_result = scout_run(db)
        logger.info(f"Scout result: {scout_result}")
        
        # Agent 2: Cleaner
        logger.info("\n[2/7] Cleaner Agent")
        cleaner_result = cleaner_run(db)
        logger.info(f"Cleaner result: {cleaner_result}")
        
        # Agent 3: Clustering
        logger.info("\n[3/7] Clustering Agent")
        cluster_result = cluster_run(db)
        logger.info(f"Clustering result: {cluster_result}")
        
        # Agent 4: Tagger
        logger.info("\n[4/7] Tagger Agent")
        tagger_result = tagger_run(db)
        logger.info(f"Tagger result: {tagger_result}")
        
        # Agent 5: Editor (Scoring)
        logger.info("\n[5/7] Editor Agent")
        editor_result = editor_run(db)
        logger.info(f"Editor result: {editor_result}")
        
        # Agent 6: Writer
        logger.info("\n[6/7] Writer Agent")
        writer_result = writer_run(db)
        logger.info(f"Writer result: {writer_result}")
        
        # Agent 7: People-to-Follow
        logger.info("\n[7/7] People-to-Follow Agent")
        people_result = people_run(db)
        logger.info(f"People result: {people_result}")
        
        # Generate daily briefing
        logger.info("\nGenerating Daily Briefing")
        briefing_result = briefing_run(db)
        logger.info(f"Briefing result: {briefing_result}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='AI Briefing Platform Worker')
    parser.add_argument('command', choices=['once'], help='Command to run')
    
    args = parser.parse_args()
    
    if args.command == 'once':
        sys.exit(run_once())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

