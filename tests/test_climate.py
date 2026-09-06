"""Unit tests for ClimateAwareEngine."""
import unittest
from sustainable_supply_chain.data.mock_data import get_default_network
from sustainable_supply_chain.engines.climate_engine import ClimateAwareEngine
from sustainable_supply_chain.models.network import TransportMode, TransportRoute


class TestClimateAwareEngine(unittest.TestCase):
    def setUp(self):
        self.network = get_default_network()
        self.engine = ClimateAwareEngine(self.network, carbon_tax_usd=60.0)

    def test_glec_freight_emissions_order(self):
        """Verify that Air freight emits significantly more than Rail or Sea freight per ton-km."""
        route_air = TransportRoute(
            id="R-TEST-AIR",
            origin_name="A",
            origin_country="A",
            destination_name="B",
            destination_country="B",
            distance_km=1000.0,
            mode=TransportMode.AIR,
            transit_time_days=1.0,
            cost_per_ton_km=1.0,
        )
        route_rail = TransportRoute(
            id="R-TEST-RAIL",
            origin_name="A",
            origin_country="A",
            destination_name="B",
            destination_country="B",
            distance_km=1000.0,
            mode=TransportMode.RAIL,
            transit_time_days=3.0,
            cost_per_ton_km=0.1,
        )
        route_sea = TransportRoute(
            id="R-TEST-SEA",
            origin_name="A",
            origin_country="A",
            destination_name="B",
            destination_country="B",
            distance_km=1000.0,
            mode=TransportMode.SEA,
            transit_time_days=10.0,
            cost_per_ton_km=0.05,
        )

        em_air = self.engine.calculate_freight_emissions(route_air, cargo_weight_tons=10.0)
        em_rail = self.engine.calculate_freight_emissions(route_rail, cargo_weight_tons=10.0)
        em_sea = self.engine.calculate_freight_emissions(route_sea, cargo_weight_tons=10.0)

        self.assertGreater(em_air.co2e_tons, em_rail.co2e_tons)
        self.assertGreater(em_rail.co2e_tons, em_sea.co2e_tons)

    def test_carbon_footprint_report(self):
        """Verify end-to-end carbon accounting report."""
        report = self.engine.generate_carbon_footprint_report()

        self.assertGreater(report.total_co2e_tons, 0)
        self.assertGreater(report.scope_1_tons, 0)
        self.assertGreater(report.scope_2_tons, 0)
        self.assertGreater(report.scope_3_tons, 0)

        # Percentages should sum to approx 100%
        pct_sum = report.scope_1_pct + report.scope_2_pct + report.scope_3_pct
        self.assertAlmostEqual(pct_sum, 100.0, delta=0.5)

        # Tax liability calculation check
        self.assertEqual(
            report.total_carbon_tax_liability_usd,
            round(report.total_co2e_tons * 60.0, 2),
        )

    def test_climate_risk_audit(self):
        """Verify climate vulnerability scoring identifies threats."""
        risks = self.engine.assess_climate_risks()
        self.assertGreater(len(risks), 0)

        # Confirm critical risk items are captured
        critical_items = [r for r in risks if r["risk_level"] == "CRITICAL"]
        self.assertTrue(len(critical_items) >= 1)

    def test_green_supplier_recommendations(self):
        """Verify green supplier matching finds alternatives."""
        recs = self.engine.get_green_supplier_recommendations()
        self.assertGreater(len(recs), 0)

        for rec in recs:
            self.assertGreater(rec["carbon_savings_pct"], 0)
            self.assertGreater(rec["green_renewable_pct"], rec["current_renewable_pct"])


if __name__ == "__main__":
    unittest.main()
