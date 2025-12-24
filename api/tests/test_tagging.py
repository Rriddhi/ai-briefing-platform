"""
Tests for tagging agent
"""
import unittest
import sys
import os

# Add worker to path for agent imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'worker'))

from agents.tagger import assign_topics


class MockTopic:
    """Mock topic for testing"""
    def __init__(self, name, slug):
        self.name = name
        self.slug = slug


class MockCluster:
    """Mock cluster for testing"""
    def __init__(self, title, summary):
        self.title = title
        self.summary = summary


class TestTagging(unittest.TestCase):
    
    def test_assign_topics_robotics_keywords(self):
        """Test topic assignment for robotics keywords"""
        cluster = MockCluster(
            title="New Robot Arm Technology",
            summary="Autonomous robot manipulation and grasping"
        )
        topics = [
            MockTopic("Robotics", "robotics"),
            MockTopic("General AI", "general-ai")
        ]
        assigned = assign_topics(cluster, topics)
        self.assertGreater(len(assigned), 0)
        self.assertTrue(any(t.slug == "robotics" for t in assigned))
    
    def test_assign_topics_medical_keywords(self):
        """Test topic assignment for medical keywords"""
        cluster = MockCluster(
            title="AI Diagnosis System",
            summary="Clinical diagnosis and patient treatment using machine learning"
        )
        topics = [
            MockTopic("Medicine & Healthcare AI", "medicine-healthcare-ai"),
            MockTopic("General AI", "general-ai")
        ]
        assigned = assign_topics(cluster, topics)
        self.assertTrue(any(t.slug == "medicine-healthcare-ai" for t in assigned))
    
    def test_assign_topics_fallback_to_general(self):
        """Test fallback to general-ai when no topics match"""
        cluster = MockCluster(
            title="Random Article",
            summary="Some unrelated content"
        )
        topics = [
            MockTopic("General AI", "general-ai")
        ]
        assigned = assign_topics(cluster, topics)
        self.assertEqual(len(assigned), 1)
        self.assertEqual(assigned[0].slug, "general-ai")


if __name__ == '__main__':
    unittest.main()

