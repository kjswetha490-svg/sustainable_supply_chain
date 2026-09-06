"""Unit tests for SustainableSupplyChainAgent."""
import unittest
from sustainable_supply_chain.data.mock_data import get_default_network
from sustainable_supply_chain.agent.supply_chain_agent import SustainableSupplyChainAgent


class TestSustainableSupplyChainAgent(unittest.TestCase):
    def setUp(self):
        self.network = get_default_network()
        self.agent = SustainableSupplyChainAgent(self.network)

    def test_intent_detection_carbon(self):
        """Verify carbon footprint queries are detected correctly."""
        res = self.agent.process_query("What is our current Scope 3 carbon footprint?")
        self.assertEqual(res["intent"], "AUDIT_CARBON")
        self.assertIn("Scope", res["response"])
        self.assertTrue(len(res["suggested_actions"]) > 0)

    def test_intent_detection_climate_risk(self):
        """Verify climate hazard queries are handled."""
        res = self.agent.process_query("How vulnerable are our facilities to typhoons and flooding?")
        self.assertEqual(res["intent"], "ASSESS_CLIMATE_RISK")
        self.assertIn("Climate Vulnerability", res["response"])

    def test_intent_detection_circularity(self):
        """Verify MCI and circularity queries."""
        res = self.agent.process_query("Calculate our Material Circularity Index (MCI) score.")
        self.assertEqual(res["intent"], "GET_CIRCULARITY_KPIS")
        self.assertIn("MCI", res["response"])

    def test_intent_detection_simulation(self):
        """Verify what-if simulation requests."""
        res = self.agent.process_query("Simulate what happens if carbon tax rises to $120 per ton.")
        self.assertIn("SIMULATE", res["intent"])
        self.assertIn("Baseline vs. Simulated", res["response"])

    def test_intent_detection_routes(self):
        """Verify route comparison requests."""
        res = self.agent.process_query("Compare shipping freight options from Hai Phong to Frankfurt")
        self.assertEqual(res["intent"], "COMPARE_ROUTES")
        self.assertIn("Multimodal Green Freight", res["response"])


if __name__ == "__main__":
    unittest.main()
