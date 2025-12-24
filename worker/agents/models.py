"""
Import models from api directory
"""
import sys
import os

# Add api directory to path
api_path = os.path.join(os.path.dirname(__file__), '..', '..', 'api')
sys.path.insert(0, api_path)

from models import *  # noqa

