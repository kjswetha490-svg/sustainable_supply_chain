"""Unit tests for WhatIfSimulator."""
import unittest
from sustainable_supply_chain.data.mock_data import get_default_network
from sustainable_supply_chain.engines.simulator import WhatIfSimulator
from sustainable_supply_chain.models.scenarios import SimulationScenario, ScenarioType


class TestWhatIfSimulator(unittest.TestCase):
    def setUp(self):
        self.network = get_default_network()
        self.simulator = WhatIfSimulator(self.network)

    def test_baseline_calculation(self):
        """Verify baseline scenario result computes successfully."""
        base = self.simulator.calculate_baseline()
        self.assertGreater(base.total_cost_usd, 0)
        self.assertGreater(base.total_carbon_tons, 0)
        self.assertGreater(base.circularity_mci_score, 0)
        self.assertGreater(base.resilience_score, 0)

    def test_carbon_tax_shock_simulation(self):
        """Verify higher carbon tax increases total cost but calculates deltas."""
        scenario = SimulationScenario(
            name="High Carbon Tax",
            scenario_type=ScenarioType.CARBON_TAX,
            carbon_tax_usd_per_ton=150.0,
            modal_shift_to_rail_pct=30.0,
        )
        comp = self.simulator.run_simulation(scenario)

        self.assertGreater(comp.simulated.carbon_tax_cost_usd, comp.baseline.carbon_tax_cost_usd)
        self.assertLess(comp.simulated.total_carbon_tons, comp.baseline.total_carbon_tons)
        self.assertLess(comp.carbon_delta_tons, 0)
        self.assertTrue(len(comp.executive_takeaways) > 0)

    def test_climate_disruption_simulation(self):
        """Verify canal/port disruption increases lead time."""
        scenario = SimulationScenario(
            name="Suez Disruption",
            scenario_type=ScenarioType.CLIMATE_DISRUPTION,
            disrupted_route_ids=["R-HPH-FRA-SEA"],
            route_delay_days=15.0,
        )
        comp = self.simulator.run_simulation(scenario)

        self.assertGreater(comp.simulated.avg_lead_time_days, comp.baseline.avg_lead_time_days)
        self.assertGreater(comp.lead_time_delta_days, 0)

    def test_circular_mandate_simulation(self):
        """Verify circular mandate increases MCI score and cuts landfill waste."""
        scenario = SimulationScenario(
            name="Circular Mandate",
            scenario_type=ScenarioType.CIRCULAR_TRANSITION,
            target_recycled_input_pct=70.0,
            target_takeback_collection_pct=50.0,
            sustainable_packaging_switch=True,
        )
        comp = self.simulator.run_simulation(scenario)

        self.assertGreater(comp.simulated.circularity_mci_score, comp.baseline.circularity_mci_score)
        self.assertGreater(comp.mci_delta_points, 0)


if __name__ == "__main__":
    unittest.main()
