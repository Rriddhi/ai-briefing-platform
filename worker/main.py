"""
Worker service for AI Briefing Platform
Multi-agent pipeline will be implemented here
"""
import os
import sys

# Add worker directory to path
sys.path.insert(0, os.path.dirname(__file__))

from run import main

if __name__ == "__main__":
    main()
