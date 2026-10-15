"""
Unit Tests for SkillHub & Selective Retrieval (Phase 6)
Using Python standard library unittest.
"""
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.skills.skill_hub import SkillHub

class TestSkillHub(unittest.TestCase):
    def setUp(self):
        self.hub = SkillHub()

    def test_single_source_counts(self):
        counts = self.hub.get_skill_counts_by_source()
        self.assertEqual(counts["agent-skills"], 25, "agent-skills must have exactly 25 skills")
        self.assertEqual(counts["superpowers"], 15, "superpowers must have exactly 15 skills")
        self.assertEqual(counts["ecc"], 292, "ECC must have exactly 292 skills")
        self.assertEqual(counts["total_skills"], 332, "Total engineering skills must be 332")
        self.assertEqual(counts["agency-agents"], 303, "agency-agents must have 303 personas")
        self.assertEqual(counts["ai-hedge-fund"], 4, "ai-hedge-fund must have 4 strategies")
        self.assertEqual(counts["total_assets"], 639, "Total indexed assets must be 639")

    def test_namespacing_prevents_collision(self):
        # Both repos define test-driven-development
        s1 = self.hub.get_skill("agent-skills/test-driven-development")
        s2 = self.hub.get_skill("superpowers/test-driven-development")
        self.assertIsNotNone(s1)
        self.assertIsNotNone(s2)
        self.assertEqual(s1["source"], "agent-skills")
        self.assertEqual(s2["source"], "superpowers")
        self.assertNotEqual(s1["path"], s2["path"])

    def test_selective_retrieval(self):
        selected = self.hub.get_relevant_skills("Implement unit test with TDD and fix bug", max_skills=2)
        self.assertGreaterEqual(len(selected), 1)
        self.assertLessEqual(len(selected), 2)
        self.assertTrue("selection_reason" in selected[0])
        self.assertEqual(selected[0]["trust_status"], "untrusted_advisory_data")

    def test_untrusted_data_boundary_in_consult(self):
        content = self.hub.consult_skill("superpowers/systematic-debugging")
        self.assertIn("[UNTRUSTED ADVISORY GUIDELINES", content)
        self.assertIn("does NOT override security rules", content)

if __name__ == "__main__":
    unittest.main()
