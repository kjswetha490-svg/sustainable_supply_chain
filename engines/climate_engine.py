"""Climate-Aware Supply Chain Engine.

Features:
- Scope 1, Scope 2, and Scope 3 carbon footprint accounting.
- GLEC Framework multimodal freight emissions calculation.
- Dynamic route comparison (Air vs Sea vs Rail vs EV vs Diesel Truck).
- Climate hazard vulnerability scoring (floods, heat stress, storms, sea surge).
- Green supplier ranking and decarbonization recommendations.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from ..models.network import (
    SupplyChainNetwork,
    Supplier,
    Facility,
    TransportRoute,
    TransportMode,
)
from ..models.carbon import (
    CarbonFootprintReport,
    RouteEmissions,
    GLECEmissionFactors,
)


class ClimateAwareEngine:
    def __init__(self, network: SupplyChainNetwork, carbon_tax_usd: float = 50.0):
        self.network = network
        self.carbon_tax_usd = carbon_tax_usd

    def calculate_freight_emissions(
        self,
        route: TransportRoute,
        cargo_weight_tons: float = 50.0,
    ) -> RouteEmissions:
        """Calculates freight carbon emissions using GLEC emission factors."""
        factor_g_per_tkm = GLECEmissionFactors.get_factor(route.mode)
        # Emissions in grams = factor * cargo_tons * distance_km
        emissions_grams = factor_g_per_tkm * cargo_weight_tons * route.distance_km
        co2e_kg = emissions_grams / 1000.0
        co2e_tons = co2e_kg / 1000.0
        cost_usd = route.cost_per_ton_km * cargo_weight_tons * route.distance_km

        return RouteEmissions(
            route_id=route.id,
            origin=route.origin_name,
            destination=route.destination_name,
            mode=route.mode,
            distance_km=route.distance_km,
            cargo_tons=cargo_weight_tons,
            co2e_kg=round(co2e_kg, 2),
            co2e_tons=round(co2e_tons, 3),
            cost_usd=round(cost_usd, 2),
            transit_days=route.transit_time_days,
            is_chokepoint=route.is_chokepoint,
        )

    def calculate_facility_scope2(self, facility: Facility) -> float:
        """Calculates Scope 2 indirect emissions from electricity consumption (tons CO2e)."""
        non_renewable_ratio = max(0.0, (100.0 - facility.renewable_onsite_pct) / 100.0)
        grid_kwh = facility.annual_electricity_kwh * non_renewable_ratio
        # grid factor in grams / kWh -> convert to metric tons
        emissions_tons = (grid_kwh * facility.grid_emission_factor_g_per_kwh) / 1_000_000.0
        return round(emissions_tons, 2)

    def calculate_supplier_scope3(self, supplier: Supplier, volume_share: float = 1.0) -> float:
        """Calculates Scope 3 upstream supplier embodied emissions (tons CO2e)."""
        allocated_units = self.network.annual_production_volume * volume_share
        emissions_kg = supplier.carbon_intensity_kg_per_unit * allocated_units
        return round(emissions_kg / 1000.0, 2)

    def generate_carbon_footprint_report(self) -> CarbonFootprintReport:
        """Generates an end-to-end Scope 1, Scope 2, Scope 3 ESG carbon footprint report."""
        # 1. Scope 1: Direct fleet emissions (internal logistics, factory boilers)
        scope_1_tons = round(self.network.annual_production_volume * 0.0035, 2)

        # 2. Scope 2: Facility emissions
        facility_breakdown: Dict[str, float] = {}
        scope_2_total = 0.0
        for fac in self.network.facilities:
            fac_tons = self.calculate_facility_scope2(fac)
            facility_breakdown[fac.name] = fac_tons
            scope_2_total += fac_tons
        scope_2_tons = round(scope_2_total, 2)

        # 3. Scope 3: Upstream suppliers + Freight Logistics
        supplier_breakdown: Dict[str, float] = {}
        scope_3_supplier_total = 0.0
        num_suppliers = max(1, len(self.network.suppliers))
        for sup in self.network.suppliers:
            sup_tons = self.calculate_supplier_scope3(sup, volume_share=1.0 / num_suppliers)
            supplier_breakdown[sup.name] = sup_tons
            scope_3_supplier_total += sup_tons

        # Scope 3 Freight across routes
        mode_breakdown: Dict[str, float] = {
            "air": 0.0,
            "road_diesel": 0.0,
            "road_electric": 0.0,
            "rail": 0.0,
            "sea": 0.0,
        }
        freight_total_tons = 0.0
        for route in self.network.routes:
            # Assume 100 annual shipments per route
            re = self.calculate_freight_emissions(route, cargo_weight_tons=75.0)
            annual_route_tons = re.co2e_tons * 50
            mode_breakdown[route.mode.value] = round(
                mode_breakdown[route.mode.value] + annual_route_tons, 2
            )
            freight_total_tons += annual_route_tons

        scope_3_tons = round(scope_3_supplier_total + freight_total_tons, 2)
        total_co2e_tons = round(scope_1_tons + scope_2_tons + scope_3_tons, 2)

        scope_1_pct = round((scope_1_tons / total_co2e_tons) * 100, 1) if total_co2e_tons else 0.0
        scope_2_pct = round((scope_2_tons / total_co2e_tons) * 100, 1) if total_co2e_tons else 0.0
        scope_3_pct = round((scope_3_tons / total_co2e_tons) * 100, 1) if total_co2e_tons else 0.0

        emissions_per_unit_kg = round(
            (total_co2e_tons * 1000.0) / max(1, self.network.annual_production_volume), 2
        )
        tax_liability = round(total_co2e_tons * self.carbon_tax_usd, 2)

        # Strategic Decarbonization Recommendations
        recommendations = []
        if mode_breakdown.get("air", 0.0) > 0.2 * freight_total_tons:
            recommendations.append(
                "High Air Freight Exposure: Shifting expedited air shipments to Eurasian Rail or Sea/Air multimodal corridors can reduce logistics emissions by up to 82%."
            )
        if any(sup.carbon_intensity_kg_per_unit > 20.0 for sup in self.network.suppliers):
            recommendations.append(
                "Supplier Carbon Hotspot: Sourcing metals & chassis from certified circular suppliers (e.g. Rheinland Recycled Alloys) will eliminate ~68% of Scope 3 upstream emissions."
            )
        if any(fac.renewable_onsite_pct < 50.0 for fac in self.network.facilities):
            recommendations.append(
                "Scope 2 Decarbonization: Expanding onsite Power Purchase Agreements (PPAs) in Hai Phong and Memphis can save ~1,200 metric tons of Scope 2 emissions annually."
            )

        return CarbonFootprintReport(
            total_co2e_tons=total_co2e_tons,
            scope_1_tons=scope_1_tons,
            scope_2_tons=scope_2_tons,
            scope_3_tons=scope_3_tons,
            scope_1_pct=scope_1_pct,
            scope_2_pct=scope_2_pct,
            scope_3_pct=scope_3_pct,
            emissions_per_unit_kg=emissions_per_unit_kg,
            carbon_tax_rate_usd_per_ton=self.carbon_tax_usd,
            total_carbon_tax_liability_usd=tax_liability,
            mode_breakdown_tons=mode_breakdown,
            supplier_emissions_tons=supplier_breakdown,
            facility_emissions_tons=facility_breakdown,
            reduction_recommendations=recommendations,
        )

    def compare_modal_alternatives(
        self,
        origin: str,
        destination: str,
        cargo_weight_tons: float = 50.0,
    ) -> List[Dict[str, Any]]:
        """Compares modal options (Air, Sea, Rail, Road, EV) between two nodes."""
        matching_routes = [
            r for r in self.network.routes
            if origin.lower() in r.origin_name.lower() and destination.lower() in r.destination_name.lower()
        ]

        # If direct routes don't exist, calculate hypothetical multimodal alternatives
        results = []
        if matching_routes:
            for route in matching_routes:
                em = self.calculate_freight_emissions(route, cargo_weight_tons)
                results.append({
                    "route_id": route.id,
                    "mode": route.mode.value,
                    "distance_km": route.distance_km,
                    "transit_days": route.transit_time_days,
                    "co2e_tons": em.co2e_tons,
                    "cost_usd": em.cost_usd,
                    "climate_risk": route.climate_disruption_probability * 100,
                    "is_chokepoint": route.is_chokepoint,
                    "chokepoint_name": route.chokepoint_name,
                })
        else:
            # Generate synthetic multimodal comparison for any queried route
            dist_km = 8000.0
            modes = [
                (TransportMode.AIR, 1.5, 1.35, 10.0),
                (TransportMode.SEA, 22.0, 0.05, 30.0),
                (TransportMode.RAIL, 12.0, 0.11, 15.0),
                (TransportMode.ROAD_DIESEL, 6.0, 0.22, 12.0),
                (TransportMode.ROAD_ELECTRIC, 7.0, 0.25, 8.0),
            ]
            for mode, transit_d, cost_tkm, risk_pct in modes:
                factor = GLECEmissionFactors.get_factor(mode)
                em_tons = round((factor * cargo_weight_tons * dist_km) / 1_000_000.0, 3)
                cost = round(cost_tkm * cargo_weight_tons * dist_km, 2)
                results.append({
                    "route_id": f"SIM-{mode.value.upper()}",
                    "mode": mode.value,
                    "distance_km": dist_km,
                    "transit_days": transit_d,
                    "co2e_tons": em_tons,
                    "cost_usd": cost,
                    "climate_risk": risk_pct,
                    "is_chokepoint": mode == TransportMode.SEA,
                    "chokepoint_name": "Maritime Canal" if mode == TransportMode.SEA else None,
                })

        # Sort by co2e_tons ascending (greenest first)
        results.sort(key=lambda x: x["co2e_tons"])
        return results

    def assess_climate_risks(self) -> List[Dict[str, Any]]:
        """Assesses climate vulnerability index for all supply chain nodes and routes."""
        risk_audit = []

        for sup in self.network.suppliers:
            risk = sup.climate_risk
            risk_level = "CRITICAL" if risk.overall_vulnerability > 70 else (
                "HIGH" if risk.overall_vulnerability > 50 else (
                    "MODERATE" if risk.overall_vulnerability > 30 else "LOW"
                )
            )
            risk_audit.append({
                "type": "Supplier",
                "name": sup.name,
                "location": f"{sup.city}, {sup.country}",
                "overall_score": risk.overall_vulnerability,
                "flood_risk": risk.flood_risk,
                "heat_stress": risk.heat_stress_risk,
                "storm_typhoon_risk": risk.severe_storm_risk,
                "sea_level_rise": risk.sea_level_rise_risk,
                "risk_level": risk_level,
                "primary_threat": (
                    "Typhoon/Coastal Flooding" if risk.severe_storm_risk > 70
                    else ("Extreme Heat & Power Grid Stress" if risk.heat_stress_risk > 70 else "Operational Disruption")
                ),
            })

        for fac in self.network.facilities:
            risk = fac.climate_risk
            risk_level = "CRITICAL" if risk.overall_vulnerability > 70 else (
                "HIGH" if risk.overall_vulnerability > 50 else (
                    "MODERATE" if risk.overall_vulnerability > 30 else "LOW"
                )
            )
            risk_audit.append({
                "type": "Facility",
                "name": fac.name,
                "location": f"{fac.city}, {fac.country}",
                "overall_score": risk.overall_vulnerability,
                "flood_risk": risk.flood_risk,
                "heat_stress": risk.heat_stress_risk,
                "storm_typhoon_risk": risk.severe_storm_risk,
                "sea_level_rise": risk.sea_level_rise_risk,
                "risk_level": risk_level,
                "primary_threat": (
                    "Monsoon Flooding & Sea Surge" if risk.flood_risk > 70
                    else ("Grid Instability from Heat" if risk.heat_stress_risk > 60 else "Weather Disruption")
                ),
            })

        risk_audit.sort(key=lambda x: x["overall_score"], reverse=True)
        return risk_audit

    def get_green_supplier_recommendations(self) -> List[Dict[str, Any]]:
        """Identifies certified green suppliers and proposes decarbonization transitions."""
        green_options = [s for s in self.network.suppliers if s.certified_green]
        fossil_options = [s for s in self.network.suppliers if not s.certified_green]

        recommendations = []
        for fossil in fossil_options:
            # Find green alternative in same category
            matching_green = next(
                (g for g in green_options if g.category == fossil.category),
                None
            )
            if matching_green:
                carbon_saved_per_unit = fossil.carbon_intensity_kg_per_unit - matching_green.carbon_intensity_kg_per_unit
                carbon_reduction_pct = round(
                    (carbon_saved_per_unit / fossil.carbon_intensity_kg_per_unit) * 100, 1
                )
                cost_diff_usd = matching_green.cost_per_unit - fossil.cost_per_unit

                goals_short = [g.split("–")[0].strip() if "–" in g else g for g in matching_green.sustainability_goals[:3]]
                goals_str = ", ".join(goals_short) if goals_short else "UN SDGs"
                pkg_str = "follows sustainable packaging practices" if matching_green.sustainable_packaging else "implements clean manufacturing"
                water_str = ", enforces water conservation" if matching_green.water_conservation else ""
                ai_reason = (
                    f"{matching_green.name} is recommended because it follows {goals_str}, uses "
                    f"{matching_green.renewable_energy_pct:.0f}% renewable energy, has a high ESG score "
                    f"({matching_green.esg_score:.0f}/100){water_str}, and {pkg_str}."
                )

                recommendations.append({
                    "category": fossil.category,
                    "current_supplier": fossil.name,
                    "current_carbon_kg": fossil.carbon_intensity_kg_per_unit,
                    "current_renewable_pct": fossil.renewable_energy_pct,
                    "current_climate_risk": fossil.climate_risk.overall_vulnerability,
                    "current_esg_score": fossil.esg_score,
                    "current_carbon_rating": fossil.carbon_rating,
                    "recommended_green_supplier": matching_green.name,
                    "green_supplier_id": matching_green.id,
                    "green_carbon_kg": matching_green.carbon_intensity_kg_per_unit,
                    "green_renewable_pct": matching_green.renewable_energy_pct,
                    "green_climate_risk": matching_green.climate_risk.overall_vulnerability,
                    "green_esg_score": matching_green.esg_score,
                    "green_carbon_rating": matching_green.carbon_rating,
                    "green_water_conservation": matching_green.water_conservation,
                    "green_waste_recycling": matching_green.waste_recycling_program,
                    "green_sustainable_packaging": matching_green.sustainable_packaging,
                    "green_sustainability_goals": matching_green.sustainability_goals,
                    "ai_recommendation_reason": ai_reason,
                    "carbon_savings_pct": carbon_reduction_pct,
                    "cost_delta_per_unit_usd": round(cost_diff_usd, 2),
                    "esg_score_improvement": round(matching_green.esg_score - fossil.esg_score, 1),
                })

        return recommendations
