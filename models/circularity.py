"""Circularity and closed-loop supply chain models."""
from __future__ import annotations
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, Field


class DispositionType(str, Enum):
    REFURBISH = "refurbish"
    REMANUFACTURE_HARVEST = "remanufacture_harvest"
    RECYCLE_FEEDSTOCK = "recycle_feedstock"
    RESPONSIBLE_DISPOSAL = "responsible_disposal"


class ReturnItem(BaseModel):
    item_id: str
    product_id: str
    product_name: str
    condition_grade: str = Field(description="Grade: A (Like New), B (Minor Wear), C (Damaged/Obsolete), D (End of Life)")
    weight_kg: float
    disposition: DispositionType
    residual_value_usd: float
    embodied_carbon_saved_kg: float
    processing_cost_usd: float


class ReverseLogisticsBatch(BaseModel):
    batch_id: str
    hub_name: str
    total_units: int
    total_weight_tons: float
    disposition_counts: Dict[str, int]
    disposition_weights_tons: Dict[str, float]
    total_recovery_value_usd: float
    total_avoided_carbon_tons: float


class MaterialFlow(BaseModel):
    virgin_raw_materials_tons: float
    recycled_input_tons: float
    bio_based_input_tons: float
    total_input_materials_tons: float
    products_manufactured_tons: float
    returns_collected_tons: float
    refurbished_tons: float
    remanufactured_parts_tons: float
    closed_loop_recycled_tons: float
    unrecoverable_waste_tons: float


class CircularityMetrics(BaseModel):
    mci_score: float = Field(ge=0.0, le=100.0, description="Material Circularity Indicator score (0-100%)")
    circular_feedstock_pct: float = Field(ge=0.0, le=100.0, description="% of input from recycled or bio-based sources")
    takeback_collection_rate_pct: float = Field(ge=0.0, le=100.0, description="% of sold goods recovered at EOL")
    landfill_diversion_rate_pct: float = Field(ge=0.0, le=100.0, description="% of waste stream diverted from landfills")
    embodied_carbon_avoided_tons: float = Field(description="GHG emissions avoided via closed-loop reuse")
    economic_value_recovered_usd: float = Field(description="Net residual market value unlocked via circular streams")
    virgin_material_displacement_tons: float
    circular_maturity_tier: str = Field(description="Linear, Emerging, Transitioning, Advanced, or Regenerative")
    key_recommendations: List[str] = Field(default_factory=list)
