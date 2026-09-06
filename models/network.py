"""Supply chain network models."""
from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class TransportMode(str, Enum):
    AIR = "air"
    ROAD_DIESEL = "road_diesel"
    ROAD_ELECTRIC = "road_electric"
    RAIL = "rail"
    SEA = "sea"


class FacilityType(str, Enum):
    MANUFACTURING = "manufacturing"
    WAREHOUSE = "warehouse"
    DISTRIBUTION_CENTER = "distribution_center"
    REVERSE_HUB = "reverse_hub"
    RETAIL = "retail"


class ClimateRiskProfile(BaseModel):
    flood_risk: float = Field(default=0.0, ge=0.0, le=100.0, description="Flooding risk score (0-100)")
    heat_stress_risk: float = Field(default=0.0, ge=0.0, le=100.0, description="Heatwave/Grid outage risk (0-100)")
    severe_storm_risk: float = Field(default=0.0, ge=0.0, le=100.0, description="Typhoon/Hurricane risk (0-100)")
    sea_level_rise_risk: float = Field(default=0.0, ge=0.0, le=100.0, description="Coastal surge risk (0-100)")
    overall_vulnerability: float = Field(default=0.0, ge=0.0, le=100.0, description="Aggregated climate risk (0-100)")


class Supplier(BaseModel):
    id: str
    name: str
    category: str
    country: str
    city: str
    latitude: float
    longitude: float
    carbon_intensity_kg_per_unit: float = Field(description="Emissions generated per unit produced (kg CO2e)")
    renewable_energy_pct: float = Field(default=20.0, ge=0.0, le=100.0)
    esg_score: float = Field(default=65.0, ge=0.0, le=100.0)
    certified_green: bool = False
    climate_risk: ClimateRiskProfile = Field(default_factory=ClimateRiskProfile)
    annual_capacity_units: int = 100000
    cost_per_unit: float = 50.0
    sustainability_goals: List[str] = Field(default_factory=list, description="SDGs and sustainability goals followed")
    carbon_rating: str = Field(default="Medium", description="Carbon emission rating: Low, Medium, or High")
    water_conservation: bool = Field(default=False, description="Water conservation practices implemented")
    waste_recycling_program: bool = Field(default=False, description="Active zero-waste recycling program")
    sustainable_packaging: bool = Field(default=False, description="Sustainable biodegradable packaging practices")


class Facility(BaseModel):
    id: str
    name: str
    facility_type: FacilityType
    country: str
    city: str
    latitude: float
    longitude: float
    annual_electricity_kwh: float = 1200000.0
    grid_emission_factor_g_per_kwh: float = 400.0
    renewable_onsite_pct: float = 30.0
    waste_diversion_rate_pct: float = 65.0
    climate_risk: ClimateRiskProfile = Field(default_factory=ClimateRiskProfile)


class TransportRoute(BaseModel):
    id: str
    origin_name: str
    origin_country: str
    destination_name: str
    destination_country: str
    distance_km: float
    mode: TransportMode
    transit_time_days: float
    cost_per_ton_km: float
    climate_disruption_probability: float = Field(default=0.05, ge=0.0, le=1.0)
    is_chokepoint: bool = False
    chokepoint_name: Optional[str] = None


class Product(BaseModel):
    id: str
    name: str
    category: str
    weight_kg: float
    virgin_material_kg: float
    recycled_material_kg: float
    bio_material_kg: float = 0.0
    packaging_weight_kg: float = 0.5
    packaging_recycled_pct: float = 20.0
    packaging_is_biodegradable: bool = False
    embodied_carbon_kg: float
    expected_lifespan_years: float = 4.0
    return_rate_pct: float = 18.0
    disassembly_ease_score: float = Field(default=70.0, ge=0.0, le=100.0)


class SupplyChainNetwork(BaseModel):
    name: str
    suppliers: List[Supplier] = Field(default_factory=list)
    facilities: List[Facility] = Field(default_factory=list)
    routes: List[TransportRoute] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    annual_production_volume: int = 500000
