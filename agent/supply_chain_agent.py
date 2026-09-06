"""Conversational Sustainable Supply Chain Agent."""
from __future__ import annotations
import re
from typing import Dict, List, Any, Optional
from ..models.network import SupplyChainNetwork
from .tools import SupplyChainToolRegistry
from .llm_client import LLMClient


class SustainableSupplyChainAgent:
    """Natural Language Assistant for Sustainable Supply Chain operations."""

    SYSTEM_PROMPT = """You are the Chief Sustainability & Resilience AI Officer for Apex Global Supply Chain.
Your mission is to guide enterprise executives, procurement directors, and logistics planners in:
1. Decarbonizing Scope 1, 2, and 3 operations using GLEC standards.
2. Building circular closed-loop value chains, optimizing reverse logistics, and tracking MCI.
3. Quantifying physical climate risks (flooding, typhoons, extreme heat) across global nodes and transit corridors.
4. Simulating What-If policy and climate disruption scenarios with clear ROI and trade-off metrics.

Deliver precise, data-grounded insights, cite specific numbers from the provided tool telemetry, and recommend concrete interventions.
Format your responses cleanly with markdown headings, bullet points, and tables where helpful.
"""

    def __init__(
        self,
        network: SupplyChainNetwork,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
    ):
        self.network = network
        self.tools = SupplyChainToolRegistry(network)
        self.llm = LLMClient(api_key=api_key, model=model)
        self.chat_history: List[Dict[str, str]] = []

    def process_query(self, user_message: str) -> Dict[str, Any]:
        """Processes user input, orchestrates tool calls, and returns an intelligent response."""
        user_message_clean = user_message.strip()
        self.chat_history.append({"role": "user", "content": user_message_clean})

        # 1. Detect Intent and Extract Parameters
        intent, params = self._detect_intent_and_params(user_message_clean)

        # 2. Execute Relevant Domain Tool
        tool_data = self._execute_tool_by_intent(intent, params, user_message_clean)

        # 3. Formulate Response (Gemini if available, else Semantic Synthesizer)
        reply_text = None
        if self.llm.api_key:
            prompt = f"""User Request: "{user_message_clean}"
Detected Intent: {intent}
Operational Telemetry Data from Tools:
{tool_data}

Please generate an executive-level, insightful, data-driven answer grounded in this telemetry."""
            reply_text = self.llm.query_gemini(prompt, self.SYSTEM_PROMPT)

        if not reply_text:
            reply_text = self._synthesize_local_response(intent, tool_data, user_message_clean, params)

        self.chat_history.append({"role": "assistant", "content": reply_text})

        return {
            "intent": intent,
            "response": reply_text,
            "telemetry": tool_data,
            "suggested_actions": self._generate_suggested_actions(intent),
        }

    def _detect_intent_and_params(self, query: str) -> tuple[str, Dict[str, Any]]:
        q = query.lower()
        params: Dict[str, Any] = {}

        # Parameter extraction helpers
        tax_match = re.search(r"\$?(\d+(?:\.\d+)?)\s*(?:dollar|usd|/ton|per ton|tax)", q)
        if tax_match:
            try:
                params["carbon_tax"] = float(tax_match.group(1))
            except ValueError:
                pass

        pct_match = re.search(r"(\d+)%", q)
        if pct_match:
            params["percent"] = float(pct_match.group(1))

        # What-if simulation
        if any(w in q for w in ["what if", "simulate", "scenario", "what-if", "what happens if", "model"]):
            if "tax" in q:
                return "SIMULATE_CARBON_TAX", params
            elif any(w in q for w in ["suez", "red sea", "disrupt", "delay", "blockage", "storm", "hurricane"]):
                return "SIMULATE_DISRUPTION", params
            elif any(w in q for w in ["circular", "recycle", "packaging", "takeback", "take-back", "closed-loop"]):
                return "SIMULATE_CIRCULARITY", params
            elif any(w in q for w in ["green", "supplier", "nearshore", "sourcing"]):
                return "SIMULATE_GREEN_SOURCING", params
            return "SIMULATE_GENERIC", params

        # Climate & carbon footprint
        if any(w in q for w in ["carbon", "footprint", "emission", "scope 1", "scope 2", "scope 3", "ghg", "glec", "audit"]):
            return "AUDIT_CARBON", params

        # Climate risk & hazards
        if any(w in q for w in ["climate risk", "vulnerability", "flood", "typhoon", "weather", "hazard", "threat", "heatwave"]):
            return "ASSESS_CLIMATE_RISK", params

        # Circular supply chain & returns
        if any(w in q for w in ["circular", "mci", "material", "reverse", "return", "refurbish", "recycle", "landfill", "waste"]):
            if any(w in q for w in ["return", "triage", "batch"]):
                return "TRIAGE_RETURNS", params
            return "GET_CIRCULARITY_KPIS", params

        # Route comparison & green corridor
        if any(w in q for w in ["route", "shipping", "freight", "transport", "air vs", "sea vs", "rail", "electric truck", "corridor"]):
            return "COMPARE_ROUTES", params

        # Green suppliers
        if any(w in q for w in ["supplier", "procurement", "vendor", "partner", "cleaner supplier", "green supplier"]):
            return "RECOMMEND_SUPPLIERS", params

        return "GENERAL_OVERVIEW", params

    def _execute_tool_by_intent(self, intent: str, params: Dict[str, Any], query: str) -> Dict[str, Any]:
        if intent == "AUDIT_CARBON":
            tax = params.get("carbon_tax", 50.0)
            return self.tools.audit_carbon_footprint(carbon_tax_usd=tax)

        elif intent == "ASSESS_CLIMATE_RISK":
            return {"climate_risks": self.tools.assess_climate_risks()}

        elif intent == "GET_CIRCULARITY_KPIS":
            recycled = params.get("percent") if "recycled" in query.lower() else None
            return self.tools.get_circularity_kpis(recycled_input_pct=recycled)

        elif intent == "TRIAGE_RETURNS":
            return self.tools.triage_returns()

        elif intent == "COMPARE_ROUTES":
            return {"modal_comparison": self.tools.compare_routes("Hai Phong", "Frankfurt", weight_tons=50.0)}

        elif intent == "RECOMMEND_SUPPLIERS":
            return {"recommendations": self.tools.recommend_green_suppliers()}

        elif intent == "SIMULATE_CARBON_TAX":
            tax = params.get("carbon_tax", 100.0)
            return self.tools.run_what_if_simulation(carbon_tax=tax, green_shift_pct=25.0)

        elif intent == "SIMULATE_DISRUPTION":
            return self.tools.run_what_if_simulation(scenario_preset="suez_canal_climate_disruption")

        elif intent == "SIMULATE_CIRCULARITY":
            recycled = params.get("percent", 65.0)
            return self.tools.run_what_if_simulation(recycled_pct=recycled, takeback_pct=40.0)

        elif intent == "SIMULATE_GREEN_SOURCING":
            shift = params.get("percent", 70.0)
            return self.tools.run_what_if_simulation(green_shift_pct=shift)

        elif intent == "SIMULATE_GENERIC":
            return self.tools.run_what_if_simulation(scenario_preset="carbon_tax_shock")

        else:
            # Default to executive summary
            report = self.tools.audit_carbon_footprint(50.0)
            circ = self.tools.get_circularity_kpis()
            return {
                "carbon_summary": {
                    "total_co2e_tons": report["total_co2e_tons"],
                    "scope_3_pct": report["scope_3_pct"],
                },
                "circularity_summary": {
                    "mci_score": circ["metrics"]["mci_score"],
                    "tier": circ["metrics"]["circular_maturity_tier"],
                }
            }

    def _synthesize_local_response(
        self,
        intent: str,
        data: Dict[str, Any],
        query: str,
        params: Dict[str, Any],
    ) -> str:
        """Built-in domain reasoning synthesizer delivering executive markdown insights."""
        if intent == "AUDIT_CARBON":
            total = data.get("total_co2e_tons", 0)
            s1 = data.get("scope_1_tons", 0)
            s2 = data.get("scope_2_tons", 0)
            s3 = data.get("scope_3_tons", 0)
            tax_bill = data.get("total_carbon_tax_liability_usd", 0)
            tax_rate = data.get("carbon_tax_rate_usd_per_ton", 50)
            recs = data.get("reduction_recommendations", [])

            rec_bullets = "\n".join([f"- **Intervention**: {r}" for r in recs])
            return f"""### 📊 Scope 1, 2, & 3 Carbon Footprint Audit

Our annual supply chain greenhouse gas emissions total **{total:,.1f} metric tons CO2e**.

| Emission Tier | Emissions (t CO2e) | % of Total Footprint | Key Source Driver |
| :--- | :--- | :--- | :--- |
| **Scope 1 (Direct)** | {s1:,.1f} t | {data.get('scope_1_pct', 0)}% | Internal transport fleet & boilers |
| **Scope 2 (Electricity)** | {s2:,.1f} t | {data.get('scope_2_pct', 0)}% | Grid power across 4 facilities |
| **Scope 3 (Upstream & Freight)** | **{s3:,.1f} t** | **{data.get('scope_3_pct', 0)}%** | **Supply base & multimodal shipping** |

- **Carbon Tax Liability**: At **\${tax_rate:.0f}/ton**, your estimated annual carbon tax bill is **\${tax_bill:,.2f}**.
- **Scope 3 Dominance**: **{data.get('scope_3_pct', 0)}%** of emissions reside outside our direct walls, primarily in raw metal extraction (Shenyang) and long-haul maritime/air shipping.

#### 💡 Strategic Decarbonization Roadmap:
{rec_bullets}"""

        elif intent == "ASSESS_CLIMATE_RISK":
            risks = data.get("climate_risks", [])
            rows = []
            for r in risks[:6]:
                status_icon = "🔴" if r["overall_score"] > 70 else ("🟡" if r["overall_score"] > 50 else "🟢")
                rows.append(f"| {status_icon} **{r['name']}** | {r['location']} | {r['overall_score']:.0f}/100 | {r['primary_threat']} |")
            rows_str = "\n".join(rows)

            return f"""### 🌪️ Climate Vulnerability & Extreme Weather Exposure

We continuously monitor acute and chronic physical climate risks across all production sites, tier-1 suppliers, and transit corridors:

| Asset / Node | Location | Vulnerability Index | Primary Climate Threat |
| :--- | :--- | :--- | :--- |
{rows_str}

#### ⚡ Critical Vulnerability Alerts:
- **Hai Phong Assembly (Score: 76/100)**: Situated in high-exposure typhoon & coastal surge zone. A major Category 4 storm risks shutting assembly for 12–18 days.
- **Pacific Microelectronics (Score: 78/100)**: Exposed to extreme monsoon rainfall and semiconductor fab water rationing during regional droughts.
- **Action Required**: Qualify backup capacity with **Nordic Eco Silicon** (Sweden, Vulnerability: 14/100) to de-risk single-origin dependency."""

        elif intent == "GET_CIRCULARITY_KPIS":
            metrics = data.get("metrics", {})
            flows = data.get("material_flows_tons", {})
            mci = metrics.get("mci_score", 0)
            tier = metrics.get("circular_maturity_tier", "")
            feedstock = metrics.get("circular_feedstock_pct", 0)
            takeback = metrics.get("takeback_collection_rate_pct", 0)
            landfill_div = metrics.get("landfill_diversion_rate_pct", 0)
            val_recovered = metrics.get("economic_value_recovered_usd", 0)
            carbon_avoided = metrics.get("embodied_carbon_avoided_tons", 0)

            recs = metrics.get("key_recommendations", [])
            rec_bullets = "\n".join([f"- {r}" for r in recs])

            return f"""### 🔄 Circular Supply Chain & Material Circularity Index (MCI)

Current Circular Performance Tier: **{tier}** (MCI Score: **{mci:.1f}%**)

- **Circular Feedstock Ratio**: **{feedstock:.1f}%** of manufacturing input consists of recycled or bio-based material.
- **Reverse Take-Back Rate**: **{takeback:.1f}%** of sold units are reclaimed via closed-loop collection.
- **Landfill Diversion Rate**: **{landfill_div:.1f}%** of returned material is diverted into refurbishment or recycling.
- **Economic Value Unlocked**: **\${val_recovered:,.2f}** in net residual hardware value recovered this cycle.
- **Avoided Embodied Carbon**: **{carbon_avoided:,.1f} metric tons CO2e** prevented vs virgin smelting.

```
[Raw Materials: {flows.get('virgin_raw_materials_tons', 0):,.0f}t Virgin | {flows.get('recycled_input_tons', 0):,.0f}t Recycled]
           │
           ▼
[Manufacturing & Distribution: {flows.get('products_manufactured_tons', 0):,.0f}t]
           │
           ▼
[Reverse Logistics Reclaimed: {flows.get('returns_collected_tons', 0):,.0f}t]
   ├── Refurbished & Resold: {flows.get('refurbished_tons', 0):,.0f}t
   ├── Parts Remanufactured: {flows.get('remanufactured_parts_tons', 0):,.0f}t
   └── Closed-Loop Recycled: {flows.get('closed_loop_recycled_tons', 0):,.0f}t
```

#### 📌 Circular Action Priorities:
{rec_bullets}"""

        elif intent == "TRIAGE_RETURNS":
            batch = data
            return f"""### 📦 Reverse Logistics Return Stream Triage

Hub: **{batch.get('hub_name')}** | Processed Units: **{batch.get('total_units')}** ({batch.get('total_weight_tons')} tons)

- **Grade A (Refurbish & Direct Resale)**: **{batch.get('disposition_counts', {}).get('refurbish', 0)} units** ({batch.get('disposition_weights_tons', {}).get('refurbish', 0):.2f} tons) — 90% carbon retention.
- **Grade B (Remanufacture & Parts Harvest)**: **{batch.get('disposition_counts', {}).get('remanufacture_harvest', 0)} units** — High-yield sub-assemblies.
- **Grade C (Recycle into Feedstock)**: **{batch.get('disposition_counts', {}).get('recycle_feedstock', 0)} units** — Smelted into certified secondary alloy.
- **Grade D (Responsible Disposal)**: **{batch.get('disposition_counts', {}).get('responsible_disposal', 0)} units** — Diverted to certified safe waste-to-energy.

**Financial & Environmental Yield**:
- Net Residual Value Recovered: **\${batch.get('total_recovery_value_usd', 0):,.2f}**
- Embodied Carbon Avoided: **{batch.get('total_avoided_carbon_tons', 0):.2f} metric tons CO2e**"""

        elif intent == "COMPARE_ROUTES":
            comp = data.get("modal_comparison", [])
            rows = []
            for c in comp:
                rows.append(
                    f"| **{c['mode'].upper()}** | {c['distance_km']:,.0f} km | {c['transit_days']:.1f} days | **{c['co2e_tons']:.2f} t** | \${c['cost_usd']:,.2f} | {c['climate_risk']:.0f}% |"
                )
            rows_str = "\n".join(rows)

            return f"""### 🚢 Multimodal Green Freight Analysis (Hai Phong ➔ Frankfurt)

Freight Cargo Payload: **50 Metric Tons**

| Mode | Distance | Transit Time | Carbon (t CO2e) | Freight Cost | Risk Exposure |
| :--- | :--- | :--- | :--- | :--- | :--- |
{rows_str}

#### 🎯 Strategic Green Routing Insight:
- **Eurasian Rail Freight** produces **~95% less carbon** than Air Freight, while arriving **14 days faster** than Maritime shipping through the Suez Canal.
- **Road vs Electric Truck**: Transitioning European regional legs to Electric Trucks cuts transport emissions by **71%** at near-parity cost per ton-km."""

        elif intent == "RECOMMEND_SUPPLIERS":
            recs = data.get("recommendations", [])
            cards = []
            for r in recs:
                ai_reason = r.get("ai_recommendation_reason") or (
                    f"{r['recommended_green_supplier']} is recommended because it follows "
                    f"{', '.join([g.split('–')[0].strip() for g in r.get('green_sustainability_goals', [])[:3]])}, "
                    f"uses {r.get('green_renewable_pct', 90):.0f}% renewable energy, has a high ESG score "
                    f"({r.get('green_esg_score', 90):.0f}/100), and follows sustainable packaging practices."
                )
                goals_list = [f"`{g}`" for g in r.get("green_sustainability_goals", [])]
                goals_str = " &bull; ".join(goals_list) if goals_list else "SDG 7, SDG 12, SDG 13"

                cards.append(
                    f"#### 🌿 {r['category']}: Transition to {r['recommended_green_supplier']}\n"
                    f"- **AI Recommendation**: *\"{ai_reason}\"*\n"
                    f"- **Current Partner**: {r['current_supplier']} ({r['current_carbon_kg']} kg CO2e/unit | {r['current_renewable_pct']}% Renewable | ESG: {r.get('current_esg_score', 60):.0f})\n"
                    f"- **Green Alternative**: **{r['recommended_green_supplier']}** ({r['green_carbon_kg']} kg CO2e/unit | {r['green_renewable_pct']}% Renewable | ESG: {r.get('green_esg_score', 90):.0f})\n"
                    f"- **Sustainability Goals Followed**: {goals_str}\n"
                    f"- **Emissions Reduction**: **-{r['carbon_savings_pct']}%** per unit produced.\n"
                    f"- **ESG Score Uplift**: **+{r['esg_score_improvement']} points** | Climate Risk: **{r['green_climate_risk']:.0f}/100** (vs {r['current_climate_risk']:.0f}/100)."
                )
            cards_str = "\n\n".join(cards)
            return f"""### 🤝 Green Supplier Decarbonization Matrix

We evaluated your supplier base to identify high-impact green procurement swaps:

{cards_str}

*Estimated total Scope 3 upstream decarbonization potential across product line: **~58.4% reduction**.*"""

        elif "SIMULATE" in intent:
            sim = data.get("simulated", {})
            base = data.get("baseline", {})
            cost_d = data.get("cost_delta_usd", 0)
            cost_pct = data.get("cost_delta_pct", 0)
            co2_d = data.get("carbon_delta_tons", 0)
            co2_pct = data.get("carbon_delta_pct", 0)
            lead_d = data.get("lead_time_delta_days", 0)
            mci_d = data.get("mci_delta_points", 0)
            res_d = data.get("resilience_delta_points", 0)

            takeaways = "\n".join([f"- {t}" for t in data.get("executive_takeaways", [])])
            actions = "\n".join([f"- {a}" for a in data.get("actionable_recommendations", [])])

            return f"""### 🔮 What-If AI Simulation: {data.get('scenario_name', 'Scenario Results')}

#### 📊 Baseline vs. Simulated Impact:
| Strategic Dimension | Baseline | Simulated Scenario | Net Delta |
| :--- | :--- | :--- | :--- |
| **Total Carbon Footprint** | {base.get('total_carbon_tons', 0):,.1f} t | **{sim.get('total_carbon_tons', 0):,.1f} t** | **{co2_d:+,.1f} t ({co2_pct:+}%)** |
| **Total Operating Cost** | \${base.get('total_cost_usd', 0):,.2f} | **\${sim.get('total_cost_usd', 0):,.2f}** | **\${cost_d:+,.2f} ({cost_pct:+}%)** |
| **Average Delivery Lead Time** | {base.get('avg_lead_time_days', 0):.1f} days | **{sim.get('avg_lead_time_days', 0):.1f} days** | **{lead_d:+.1f} days** |
| **Material Circularity (MCI)** | {base.get('circularity_mci_score', 0):.1f}% | **{sim.get('circularity_mci_score', 0):.1f}%** | **{mci_d:+.1f} pts** |
| **Resilience / ESG Index** | {base.get('resilience_score', 0):.1f}/100 | **{sim.get('resilience_score', 0):.1f}/100** | **{res_d:+.1f} pts** |

#### 💡 Executive Takeaways:
{takeaways}

#### 🚀 Recommended Action Plan:
{actions}"""

        else:
            return """### 👋 Sustainable Supply Chain Intelligence Agent

I am ready to assist you across the complete sustainability lifecycle of your supply chain:

1. **🌍 Climate-Aware Logistics & Carbon Footprint**:
   - Scope 1, 2, and 3 emissions auditing using the GLEC standard.
   - Multimodal route greening (Air vs Ocean vs Rail vs Electric Truck).
   - Physical climate risk and extreme weather vulnerability scoring.
2. **🔄 Circular Supply Chain & Reverse Logistics**:
   - Closed-loop material tracking and Ellen MacArthur Foundation MCI scoring.
   - Return stream triage (Refurbish, Harvest, Recycle, Dispose).
   - Landfill waste diversion and secondary value recovery.
3. **🔮 What-If AI Scenario Simulator**:
   - Carbon tax shocks (\$50 to \$200/ton).
   - Canal and port climate disruptions (Suez / Panama).
   - Circular packaging and recycled content transitions.
   - Green supplier nearshoring allocations.

*Try asking: "What is our current carbon footprint breakdown?", "Simulate a \$120 carbon tax", or "How vulnerable are our Asian suppliers to typhoons?"*"""

    def _generate_suggested_actions(self, intent: str) -> List[str]:
        suggestions = {
            "AUDIT_CARBON": [
                "Simulate a $100/ton carbon tax increase",
                "Compare freight emissions between Hai Phong and Frankfurt",
                "Recommend green suppliers to lower Scope 3",
            ],
            "ASSESS_CLIMATE_RISK": [
                "Simulate a 14-day disruption on the Suez Canal",
                "Show alternative low-risk suppliers",
                "What is our overall supply chain resilience score?",
            ],
            "GET_CIRCULARITY_KPIS": [
                "Triage incoming reverse logistics return stream",
                "Simulate 60% recycled material target",
                "How much embodied carbon can we avoid by refurbishing?",
            ],
            "TRIAGE_RETURNS": [
                "Calculate Material Circularity Indicator (MCI)",
                "Simulate bio-packaging mandate",
                "Export reverse logistics recovery audit",
            ],
            "COMPARE_ROUTES": [
                "Audit Scope 3 logistics emissions",
                "Simulate a modal shift to 40% rail",
                "Check climate risk on maritime corridors",
            ],
            "RECOMMEND_SUPPLIERS": [
                "Simulate switching 70% volume to green suppliers",
                "Audit Scope 3 supplier carbon footprint",
                "Assess climate vulnerability of Swedish vs Taiwan suppliers",
            ],
            "SIMULATE_CARBON_TAX": [
                "Simulate a canal climate disruption scenario",
                "Test 65% recycled content target",
                "How does carbon tax affect our modal choice?",
            ],
        }
        return suggestions.get(intent, [
            "Audit our Scope 1, 2, and 3 carbon footprint",
            "Assess climate risks across global suppliers",
            "What is our Material Circularity Index (MCI)?",
            "Simulate a $120 carbon tax shock",
        ])
