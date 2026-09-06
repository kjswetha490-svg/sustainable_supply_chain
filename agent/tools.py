"""Agent tools registry for executing supply chain queries and simulations."""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from ..models.network import SupplyChainNetwork
from ..models.scenarios import SimulationScenario, ScenarioType
from ..engines.climate_engine import ClimateAwareEngine
from ..engines.circular_engine import CircularSupplyChainEngine
from ..engines.simulator import WhatIfSimulator
from ..data.mock_data import get_sample_return_stream


class SupplyChainToolRegistry:
    """Provides callable analytical tools for the Natural Language Supply Chain Assistant."""

    def __init__(self, network: SupplyChainNetwork):
        self.network = network
        self.climate_engine = ClimateAwareEngine(network)
        self.circular_engine = CircularSupplyChainEngine(network)
        self.simulator = WhatIfSimulator(network)

    def audit_carbon_footprint(self, carbon_tax_usd: float = 50.0) -> Dict[str, Any]:
        """Audits Scope 1, 2, and 3 carbon emissions across facilities, transport, and suppliers."""
        engine = ClimateAwareEngine(self.network, carbon_tax_usd=carbon_tax_usd)
        report = engine.generate_carbon_footprint_report()
        return report.model_dump()

    def assess_climate_risks(self, minimum_risk: float = 0.0) -> List[Dict[str, Any]]:
        """Assesses climate vulnerability (flooding, typhoons, extreme heat) for facilities and suppliers."""
        risks = self.climate_engine.assess_climate_risks()
        if minimum_risk > 0:
            risks = [r for r in risks if r["overall_score"] >= minimum_risk]
        return risks

    def get_circularity_kpis(
        self,
        recycled_input_pct: Optional[float] = None,
        takeback_rate_pct: Optional[float] = None,
        bio_packaging: bool = False,
    ) -> Dict[str, Any]:
        """Calculates Material Circularity Indicator (MCI) and reverse logistics KPIs."""
        metrics = self.circular_engine.compute_circularity_metrics(
            override_recycled_pct=recycled_input_pct,
            override_takeback_pct=takeback_rate_pct,
            override_bio_packaging=bio_packaging,
        )
        flows = self.circular_engine.calculate_material_flow(
            override_recycled_pct=recycled_input_pct,
            override_takeback_pct=takeback_rate_pct,
            override_bio_packaging=bio_packaging,
        )
        return {
            "metrics": metrics.model_dump(),
            "material_flows_tons": flows.model_dump(),
        }

    def triage_returns(self) -> Dict[str, Any]:
        """Runs automated triage on the current reverse logistics return stream."""
        returns = get_sample_return_stream()
        batch = self.circular_engine.triage_return_batch(returns)
        return batch.model_dump()

    def compare_routes(
        self,
        origin: str = "Hai Phong",
        destination: str = "Frankfurt",
        weight_tons: float = 50.0,
    ) -> List[Dict[str, Any]]:
        """Compares multimodal freight routes (Air vs Sea vs Rail vs Road vs EV)."""
        return self.climate_engine.compare_modal_alternatives(origin, destination, weight_tons)

    def recommend_green_suppliers(self) -> List[Dict[str, Any]]:
        """Recommends certified low-carbon suppliers to replace high-emission partners."""
        return self.climate_engine.get_green_supplier_recommendations()

    def run_what_if_simulation(
        self,
        scenario_preset: Optional[str] = None,
        carbon_tax: Optional[float] = None,
        delay_days: Optional[float] = None,
        recycled_pct: Optional[float] = None,
        takeback_pct: Optional[float] = None,
        green_shift_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Simulates supply chain shocks and comparative trade-offs."""
        presets = self.simulator.get_preset_scenarios()

        if scenario_preset and scenario_preset in presets:
            scenario = presets[scenario_preset]
        else:
            scenario = SimulationScenario(
                name="Custom Scenario",
                scenario_type=ScenarioType.CUSTOM_COMBINED,
                carbon_tax_usd_per_ton=carbon_tax if carbon_tax is not None else 50.0,
                route_delay_days=delay_days if delay_days is not None else 0.0,
                target_recycled_input_pct=recycled_pct if recycled_pct is not None else 25.0,
                target_takeback_collection_pct=takeback_pct if takeback_pct is not None else 18.0,
                shift_to_green_suppliers_pct=green_shift_pct if green_shift_pct is not None else 0.0,
            )

        comparison = self.simulator.run_simulation(scenario)
        return comparison.model_dump()
