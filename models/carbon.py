"""Carbon accounting and GLEC emission models."""
from __future__ import annotations
from typing import Dict, List
from pydantic import BaseModel, Field
from .network import TransportMode


class GLECEmissionFactors:
    """Global Logistics Emissions Council (GLEC) standard factors (g CO2e / tonne-km, WTW)."""
    FACTORS: Dict[TransportMode, float] = {
        TransportMode.AIR: 602.0,           # Long-haul air freight
        TransportMode.ROAD_DIESEL: 82.0,    # Heavy articulated diesel truck
        TransportMode.ROAD_ELECTRIC: 24.0,  # Battery electric truck (avg grid)
        TransportMode.RAIL: 21.0,           # Electric/diesel hybrid freight rail
        TransportMode.SEA: 11.5,            # Ultra-large container vessel (ULCV)
    }

    @classmethod
    def get_factor(cls, mode: TransportMode) -> float:
        return cls.FACTORS.get(mode, 80.0)


class ScopeEmissions(BaseModel):
    scope_1_tons: float = Field(description="Direct emissions from owned fleets and boilers")
    scope_2_tons: float = Field(description="Indirect emissions from purchased electricity/heating")
    scope_3_upstream_tons: float = Field(description="Purchased goods, raw materials, supplier logistics")
    scope_3_downstream_tons: float = Field(description="Outbound distribution, product in-use, end-of-life")

    @property
    def scope_3_total_tons(self) -> float:
        return self.scope_3_upstream_tons + self.scope_3_downstream_tons

    @property
    def total_tons(self) -> float:
        return self.scope_1_tons + self.scope_2_tons + self.scope_3_total_tons


class RouteEmissions(BaseModel):
    route_id: str
    origin: str
    destination: str
    mode: TransportMode
    distance_km: float
    cargo_tons: float
    co2e_kg: float
    co2e_tons: float
    cost_usd: float
    transit_days: float
    is_chokepoint: bool = False


class CarbonFootprintReport(BaseModel):
    total_co2e_tons: float
    scope_1_tons: float
    scope_2_tons: float
    scope_3_tons: float
    scope_1_pct: float
    scope_2_pct: float
    scope_3_pct: float
    emissions_per_unit_kg: float
    carbon_tax_rate_usd_per_ton: float = 50.0
    total_carbon_tax_liability_usd: float
    mode_breakdown_tons: Dict[str, float] = Field(default_factory=dict)
    supplier_emissions_tons: Dict[str, float] = Field(default_factory=dict)
    facility_emissions_tons: Dict[str, float] = Field(default_factory=dict)
    reduction_recommendations: List[str] = Field(default_factory=list)
