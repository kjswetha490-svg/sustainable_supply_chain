"""Domain data models for sustainable supply chain."""
from .network import (
    Supplier,
    Facility,
    TransportRoute,
    Product,
    SupplyChainNetwork,
    TransportMode,
    FacilityType,
)
from .carbon import (
    ScopeEmissions,
    CarbonFootprintReport,
    GLECEmissionFactors,
    RouteEmissions,
)
from .circularity import (
    DispositionType,
    MaterialFlow,
    CircularityMetrics,
    ReturnItem,
    ReverseLogisticsBatch,
)
from .scenarios import (
    SimulationScenario,
    ScenarioType,
    ScenarioResult,
    ScenarioComparison,
)

__all__ = [
    "Supplier",
    "Facility",
    "TransportRoute",
    "Product",
    "SupplyChainNetwork",
    "TransportMode",
    "FacilityType",
    "ScopeEmissions",
    "CarbonFootprintReport",
    "GLECEmissionFactors",
    "RouteEmissions",
    "DispositionType",
    "MaterialFlow",
    "CircularityMetrics",
    "ReturnItem",
    "ReverseLogisticsBatch",
    "SimulationScenario",
    "ScenarioType",
    "ScenarioResult",
    "ScenarioComparison",
]
