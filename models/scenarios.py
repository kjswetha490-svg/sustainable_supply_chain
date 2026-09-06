"""What-If scenario and simulation models."""
from __future__ import annotations
from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    CARBON_TAX = "carbon_tax"
    CLIMATE_DISRUPTION = "climate_disruption"
    CIRCULAR_TRANSITION = "circular_transition"
    GREEN_SOURCING = "green_sourcing"
    CUSTOM_COMBINED = "custom_combined"


class SimulationScenario(BaseModel):
    name: str = "Baseline Simulation"
    scenario_type: ScenarioType = ScenarioType.CUSTOM_COMBINED
    description: str = ""
    # Climate / Carbon parameters
    carbon_tax_usd_per_ton: float = Field(default=50.0, ge=0.0, le=500.0)
    modal_shift_to_rail_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    modal_shift_to_electric_truck_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    # Climate disruption parameters
    disrupted_route_ids: List[str] = Field(default_factory=list)
    route_delay_days: float = Field(default=0.0, ge=0.0)
    reroute_avoid_chokepoints: bool = False
    # Circularity parameters
    target_recycled_input_pct: float = Field(default=25.0, ge=0.0, le=100.0)
    target_takeback_collection_pct: float = Field(default=18.0, ge=0.0, le=100.0)
    sustainable_packaging_switch: bool = False
    # Supplier sourcing
    shift_to_green_suppliers_pct: float = Field(default=0.0, ge=0.0, le=100.0)


class ScenarioResult(BaseModel):
    scenario_name: str
    total_cost_usd: float
    transport_cost_usd: float
    carbon_tax_cost_usd: float
    material_cost_usd: float
    total_carbon_tons: float
    scope_1_tons: float
    scope_2_tons: float
    scope_3_tons: float
    avg_lead_time_days: float
    circularity_mci_score: float
    climate_risk_exposure: float
    resilience_score: float
    waste_to_landfill_tons: float


class ScenarioComparison(BaseModel):
    scenario_name: str
    scenario_type: str
    baseline: ScenarioResult
    simulated: ScenarioResult
    cost_delta_usd: float
    cost_delta_pct: float
    carbon_delta_tons: float
    carbon_delta_pct: float
    lead_time_delta_days: float
    lead_time_delta_pct: float
    mci_delta_points: float
    resilience_delta_points: float
    executive_takeaways: List[str] = Field(default_factory=list)
    actionable_recommendations: List[str] = Field(default_factory=list)
