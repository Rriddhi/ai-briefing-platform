"""
Tests for scoring/editor agent
"""
import unittest
import sys
import os

# Add worker to path for agent imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'worker'))

from agents.editor import (
    calculate_relevance_score,
    calculate_impact_score,
    calculate_credibility_score,
    calculate_novelty_score,
    calculate_corroboration_score,
    calculate_overall_score,
    generate_rationale
)
from models import Cluster, RawItem, Source, SourceType


class MockCluster:
    """Mock cluster for testing"""
    def __init__(self, summary=None, topics=None, raw_items=None):
        self.summary = summary or ""
        self.topics = topics or []
        self.raw_items = raw_items or []


class TestScoring(unittest.TestCase):
    
    def test_calculate_relevance_score_with_summary(self):
        """Test relevance score calculation with summary"""
        cluster = MockCluster(summary="This is a long summary" * 10)  # > 100 chars
        score = calculate_relevance_score(cluster)
        self.assertGreater(score, 0.3)
    
    def test_calculate_relevance_score_with_topics(self):
        """Test relevance score increases with topics"""
        cluster = MockCluster(summary="Test" * 50, topics=[1, 2, 3])  # 3 topics
        score = calculate_relevance_score(cluster)
        self.assertGreater(score, 0.8)
    
    def test_calculate_impact_score_multiple_items(self):
        """Test impact score increases with item count"""
        items = [None] * 5  # 5 items
        cluster = MockCluster(raw_items=items)
        score = calculate_impact_score(cluster)
        self.assertGreater(score, 0.8)
    
    def test_calculate_credibility_score_arxiv(self):
        """Test credibility score for arXiv sources"""
        source = Source(source_type=SourceType.ARXIV)
        item = RawItem(source=source)
        cluster = MockCluster(raw_items=[item])
        score = calculate_credibility_score(cluster)
        self.assertGreater(score, 0.8)
    
    def test_calculate_overall_score_formula(self):
        """Test overall score calculation follows formula"""
        breakdown = {
            'relevance_score': 0.8,
            'impact_score': 0.7,
            'credibility_score': 0.9,
            'novelty_score': 0.6,
            'corroboration_score': 0.5
        }
        score = calculate_overall_score(breakdown)
        
        expected = (
            0.30 * 0.8 +
            0.25 * 0.7 +
            0.20 * 0.9 +
            0.15 * 0.6 +
            0.10 * 0.5
        )
        self.assertAlmostEqual(score, expected, places=5)
    
    def test_generate_rationale_high_scores(self):
        """Test rationale generation for high scores"""
        breakdown = {
            'relevance_score': 0.9,
            'impact_score': 0.85,
            'credibility_score': 0.9,
            'novelty_score': 0.85,
            'corroboration_score': 0.8
        }
        rationale = generate_rationale(breakdown)
        self.assertIsInstance(rationale, str)
        self.assertGreater(len(rationale), 0)


if __name__ == '__main__':
    unittest.main()

