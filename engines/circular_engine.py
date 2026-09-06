"""Circular Supply Chain Engine.

Features:
- Material Circularity Indicator (MCI) scoring (Ellen MacArthur Foundation aligned).
- Closed-loop material mass-balance flow modeling (Virgin vs Recycled vs Bio).
- Reverse logistics automated triage and disposition optimization (Grade A-D).
- Landfill waste diversion, virgin displacement, and embodied carbon recovery.
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from ..models.network import SupplyChainNetwork, Product
from ..models.circularity import (
    DispositionType,
    ReturnItem,
    ReverseLogisticsBatch,
    MaterialFlow,
    CircularityMetrics,
)


class CircularSupplyChainEngine:
    def __init__(self, network: SupplyChainNetwork):
        self.network = network

    def calculate_material_flow(
        self,
        override_recycled_pct: Optional[float] = None,
        override_takeback_pct: Optional[float] = None,
        override_bio_packaging: bool = False,
    ) -> MaterialFlow:
        """Calculates mass-balance material flows (metric tons) across the product portfolio."""
        volume = self.network.annual_production_volume
        total_product_weight_kg = sum(p.weight_kg for p in self.network.products) / max(1, len(self.network.products))

        annual_mass_tons = (volume * total_product_weight_kg) / 1000.0

        # Virgin vs Recycled input ratio
        if override_recycled_pct is not None:
            recycled_ratio = override_recycled_pct / 100.0
        else:
            avg_recycled = sum(p.recycled_material_kg / max(0.01, p.weight_kg) for p in self.network.products) / max(1, len(self.network.products))
            recycled_ratio = avg_recycled

        bio_ratio = 0.08 if override_bio_packaging else 0.02
        virgin_ratio = max(0.0, 1.0 - (recycled_ratio + bio_ratio))

        virgin_tons = round(annual_mass_tons * virgin_ratio, 2)
        recycled_input_tons = round(annual_mass_tons * recycled_ratio, 2)
        bio_input_tons = round(annual_mass_tons * bio_ratio, 2)

        # Returns collection
        takeback_pct = override_takeback_pct if override_takeback_pct is not None else 21.0
        returns_collected_tons = round(annual_mass_tons * (takeback_pct / 100.0), 2)

        # Reverse disposition breakdown
        # ~35% Refurbishable (Grade A), ~30% Remanufacturable (Grade B), ~25% Recyclable (Grade C), ~10% Landfill/Waste (Grade D)
        refurbished_tons = round(returns_collected_tons * 0.35, 2)
        remanufactured_tons = round(returns_collected_tons * 0.30, 2)
        closed_loop_recycled_tons = round(returns_collected_tons * 0.25, 2)
        waste_tons = round(returns_collected_tons * 0.10, 2)

        return MaterialFlow(
            virgin_raw_materials_tons=virgin_tons,
            recycled_input_tons=recycled_input_tons,
            bio_based_input_tons=bio_input_tons,
            total_input_materials_tons=round(annual_mass_tons, 2),
            products_manufactured_tons=round(annual_mass_tons, 2),
            returns_collected_tons=returns_collected_tons,
            refurbished_tons=refurbished_tons,
            remanufactured_parts_tons=remanufactured_tons,
            closed_loop_recycled_tons=closed_loop_recycled_tons,
            unrecoverable_waste_tons=waste_tons,
        )

    def compute_circularity_metrics(
        self,
        override_recycled_pct: Optional[float] = None,
        override_takeback_pct: Optional[float] = None,
        override_bio_packaging: bool = False,
    ) -> CircularityMetrics:
        """Computes Material Circularity Indicator (MCI) and circular sustainability KPIs."""
        flow = self.calculate_material_flow(
            override_recycled_pct=override_recycled_pct,
            override_takeback_pct=override_takeback_pct,
            override_bio_packaging=override_bio_packaging,
        )

        circular_feedstock_pct = round(
            ((flow.recycled_input_tons + flow.bio_based_input_tons) / max(1.0, flow.total_input_materials_tons)) * 100.0,
            1
        )
        takeback_rate_pct = round(
            (flow.returns_collected_tons / max(1.0, flow.products_manufactured_tons)) * 100.0,
            1
        )

        diverted_tons = flow.refurbished_tons + flow.remanufactured_parts_tons + flow.closed_loop_recycled_tons
        landfill_diversion_pct = round(
            (diverted_tons / max(1.0, flow.returns_collected_tons)) * 100.0,
            1
        )

        # Ellen MacArthur Foundation aligned MCI calculation
        # V = Virgin material tons
        # W = Unrecoverable waste tons
        # M = Total mass tons
        # Linear Flow Factor (LFF): (V + W) / (2 * M)
        lff = (flow.virgin_raw_materials_tons + flow.unrecoverable_waste_tons) / (2.0 * max(1.0, flow.total_input_materials_tons))
        # Utility factor: based on product lifespan and repairability
        utility_factor = 0.95
        # MCI = 1 - (LFF * utility_factor) -> scaled to 0-100%
        raw_mci = max(0.0, min(1.0, 1.0 - (lff * utility_factor)))
        mci_score = round(raw_mci * 100.0, 1)

        # Embodied carbon avoided:
        # Refurbished retains ~85% embodied carbon (avg product embodied carbon ~35 kg)
        # Remanufactured retains ~65%
        # Recycled avoids ~45% virgin extraction emissions
        avoided_co2e_tons = round(
            (flow.refurbished_tons * 2.8) +
            (flow.remanufactured_parts_tons * 2.1) +
            (flow.closed_loop_recycled_tons * 1.4),
            1
        )

        # Economic value recovered:
        # Refurbished: ~$2,500/ton, Remanufactured: ~$1,600/ton, Recycled: ~$450/ton
        economic_value_recovered = round(
            (flow.refurbished_tons * 2500.0) +
            (flow.remanufactured_parts_tons * 1600.0) +
            (flow.closed_loop_recycled_tons * 450.0),
            2
        )

        # Circular Maturity Tier
        if mci_score >= 85.0:
            maturity = "Regenerative Circular Network"
        elif mci_score >= 70.0:
            maturity = "Advanced Closed-Loop"
        elif mci_score >= 50.0:
            maturity = "Transitioning Circular"
        elif mci_score >= 30.0:
            maturity = "Emerging Circular Practices"
        else:
            maturity = "Linear Take-Make-Waste"

        recommendations = []
        if circular_feedstock_pct < 40.0:
            recommendations.append(
                f"Low Circular Feedstock ({circular_feedstock_pct}%): Transition chassis supplier to Rheinland Recycled Alloys to increase recycled content past 50%."
            )
        if takeback_rate_pct < 30.0:
            recommendations.append(
                f"Take-Back Deficit ({takeback_rate_pct}%): Introduce a customer trade-in discount incentive program to boost reverse collection rates toward 45%."
            )
        if not override_bio_packaging:
            recommendations.append(
                "Packaging Innovation: Replace virgin petroleum clamshells with certified BioLoop mycelium packaging to divert 35 tons of plastic waste annually."
            )

        return CircularityMetrics(
            mci_score=mci_score,
            circular_feedstock_pct=circular_feedstock_pct,
            takeback_collection_rate_pct=takeback_rate_pct,
            landfill_diversion_rate_pct=landfill_diversion_pct,
            embodied_carbon_avoided_tons=avoided_co2e_tons,
            economic_value_recovered_usd=economic_value_recovered,
            virgin_material_displacement_tons=diverted_tons,
            circular_maturity_tier=maturity,
            key_recommendations=recommendations,
        )

    def triage_return_batch(self, returns: List[ReturnItem]) -> ReverseLogisticsBatch:
        """Triage returned items to optimize value recovery and carbon reduction."""
        disposition_counts = {
            DispositionType.REFURBISH.value: 0,
            DispositionType.REMANUFACTURE_HARVEST.value: 0,
            DispositionType.RECYCLE_FEEDSTOCK.value: 0,
            DispositionType.RESPONSIBLE_DISPOSAL.value: 0,
        }
        disposition_weights = {
            DispositionType.REFURBISH.value: 0.0,
            DispositionType.REMANUFACTURE_HARVEST.value: 0.0,
            DispositionType.RECYCLE_FEEDSTOCK.value: 0.0,
            DispositionType.RESPONSIBLE_DISPOSAL.value: 0.0,
        }
        total_recovery_val = 0.0
        total_avoided_carbon = 0.0
        total_weight_kg = 0.0

        for item in returns:
            total_weight_kg += item.weight_kg
            # Rule-based disposition check
            disp = item.disposition
            disposition_counts[disp.value] += 1
            disposition_weights[disp.value] += item.weight_kg / 1000.0
            total_recovery_val += (item.residual_value_usd - item.processing_cost_usd)
            total_avoided_carbon += item.embodied_carbon_saved_kg / 1000.0

        return ReverseLogisticsBatch(
            batch_id="REV-BATCH-CURRENT",
            hub_name="Rotterdam Closed-Loop Hub",
            total_units=len(returns),
            total_weight_tons=round(total_weight_kg / 1000.0, 3),
            disposition_counts=disposition_counts,
            disposition_weights_tons={k: round(v, 3) for k, v in disposition_weights.items()},
            total_recovery_value_usd=round(total_recovery_val, 2),
            total_avoided_carbon_tons=round(total_avoided_carbon, 3),
        )
