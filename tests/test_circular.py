"""Unit tests for CircularSupplyChainEngine."""
import unittest
from sustainable_supply_chain.data.mock_data import get_default_network, get_sample_return_stream
from sustainable_supply_chain.engines.circular_engine import CircularSupplyChainEngine


class TestCircularSupplyChainEngine(unittest.TestCase):
    def setUp(self):
        self.network = get_default_network()
        self.engine = CircularSupplyChainEngine(self.network)

    def test_material_flows(self):
        """Verify mass-balance material flow calculations."""
        flow = self.engine.calculate_material_flow()
        self.assertGreater(flow.total_input_materials_tons, 0)
        self.assertGreater(flow.virgin_raw_materials_tons, 0)
        self.assertGreater(flow.recycled_input_tons, 0)

        # Total input should equal virgin + recycled + bio
        computed_input = flow.virgin_raw_materials_tons + flow.recycled_input_tons + flow.bio_based_input_tons
        self.assertAlmostEqual(computed_input, flow.total_input_materials_tons, delta=0.5)

    def test_circularity_metrics_improvement(self):
        """Verify higher recycled input boosts MCI score."""
        base_metrics = self.engine.compute_circularity_metrics(override_recycled_pct=20.0)
        high_circ_metrics = self.engine.compute_circularity_metrics(override_recycled_pct=65.0)

        self.assertGreater(high_circ_metrics.mci_score, base_metrics.mci_score)
        self.assertGreater(high_circ_metrics.circular_feedstock_pct, base_metrics.circular_feedstock_pct)

    def test_return_batch_triage(self):
        """Verify reverse logistics triage classifies grades and calculates value recovery."""
        returns = get_sample_return_stream()
        batch = self.engine.triage_return_batch(returns)

        self.assertEqual(batch.total_units, len(returns))
        self.assertGreater(batch.total_recovery_value_usd, 0)
        self.assertGreater(batch.total_avoided_carbon_tons, 0)
        self.assertIn("refurbish", batch.disposition_counts)
        self.assertIn("remanufacture_harvest", batch.disposition_counts)


if __name__ == "__main__":
    unittest.main()
