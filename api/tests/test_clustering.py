"""
Tests for clustering agent
"""
import unittest
import sys
import os

# Add worker to path for agent imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'worker'))

from agents.cluster import similarity_score


class TestClustering(unittest.TestCase):
    
    def test_similarity_score_identical(self):
        """Test similarity score for identical texts"""
        text1 = "AI breakthrough in machine learning"
        text2 = "AI breakthrough in machine learning"
        score = similarity_score(text1, text2)
        self.assertEqual(score, 1.0)
    
    def test_similarity_score_similar(self):
        """Test similarity score for similar texts"""
        text1 = "AI breakthrough in machine learning"
        text2 = "AI breakthrough in deep learning"
        score = similarity_score(text1, text2)
        self.assertGreater(score, 0.7)
        self.assertLess(score, 1.0)
    
    def test_similarity_score_different(self):
        """Test similarity score for different texts"""
        text1 = "AI breakthrough in machine learning"
        text2 = "Weather forecast for tomorrow"
        score = similarity_score(text1, text2)
        self.assertLess(score, 0.3)
    
    def test_similarity_score_empty(self):
        """Test similarity score with empty strings"""
        score1 = similarity_score("", "test")
        score2 = similarity_score("test", "")
        score3 = similarity_score("", "")
        self.assertEqual(score1, 0.0)
        self.assertEqual(score2, 0.0)
        self.assertEqual(score3, 0.0)


if __name__ == '__main__':
    unittest.main()
