"""
Unit Tests for Model Registry, Fallback & Targeted Teams (Phase 5)
Using Python standard library unittest.
"""
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.models.model_registry import ModelRegistry, ModelProfile
from core.agents.team import AgentTeam

class TestModelRegistryAndTeam(unittest.TestCase):
    def setUp(self):
        self.registry = ModelRegistry()
        self.team = AgentTeam()

    def test_model_profiles_and_capabilities(self):
        profile = self.registry.get_profile("nvidia/nemotron-3-super-120b-a12b:free")
        self.assertIsNotNone(profile)
        self.assertTrue(profile.supports_tools)
        self.assertTrue(profile.supports_structured_output)
        self.assertTrue(profile.is_free)

    def test_circuit_breaker(self):
        model_id = "grok-4.7"
        telem = self.registry.telemetry[model_id]

        self.assertTrue(self.registry.is_endpoint_healthy(model_id))

        # Record 3 failures
        telem.record_failure()
        telem.record_failure()
        telem.record_failure()

        # Circuit breaker must trip
        self.assertFalse(self.registry.is_endpoint_healthy(model_id))

        # Fallback should avoid the tripped model
        fallback = self.registry.select_compatible_fallback(failed_model="dummy", requires_tools=True)
        self.assertNotEqual(fallback, model_id)

    def test_targeted_sub_team_activation(self):
        # Bug task -> Engineer + Reviewer
        team_bug = self.team.create_targeted_team("bug fix")
        names_bug = [a.name for a in team_bug._participants]
        self.assertEqual(names_bug, ["Engineer", "Reviewer"])

        # UI task -> FullStackDev + Reviewer
        team_ui = self.team.create_targeted_team("build responsive ui dashboard")
        names_ui = [a.name for a in team_ui._participants]
        self.assertEqual(names_ui, ["FullStackDev", "Reviewer"])

        # Quant task -> QuantTrader + Reviewer
        team_quant = self.team.create_targeted_team("run quant backtest on btc")
        names_quant = [a.name for a in team_quant._participants]
        self.assertEqual(names_quant, ["QuantTrader", "Reviewer"])

        # Algorithm task -> Engineer + NemotronSuper + Reviewer
        team_algo = self.team.create_targeted_team("solve complex math algorithm")
        names_algo = [a.name for a in team_algo._participants]
        self.assertEqual(names_algo, ["Engineer", "NemotronSuper", "Reviewer"])

        # SystemExecutor is NOT a participant in any team
        self.assertNotIn("SystemExecutor", names_bug)
        self.assertNotIn("SystemExecutor", names_ui)
        self.assertNotIn("SystemExecutor", names_quant)
        self.assertNotIn("SystemExecutor", names_algo)

if __name__ == "__main__":
    unittest.main()
