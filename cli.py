"""Command-line interface for Sustainable Supply Chain Agent."""
from __future__ import annotations
import argparse
import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows consoles to prevent charmap errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure both current directory and parent directory are on sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
for p in (str(parent_dir), str(current_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from sustainable_supply_chain.data.mock_data import get_default_network
    from sustainable_supply_chain.engines.climate_engine import ClimateAwareEngine
    from sustainable_supply_chain.engines.circular_engine import CircularSupplyChainEngine
    from sustainable_supply_chain.engines.simulator import WhatIfSimulator
    from sustainable_supply_chain.agent.supply_chain_agent import SustainableSupplyChainAgent
except ImportError:
    from data.mock_data import get_default_network
    from engines.climate_engine import ClimateAwareEngine
    from engines.circular_engine import CircularSupplyChainEngine
    from engines.simulator import WhatIfSimulator
    from agent.supply_chain_agent import SustainableSupplyChainAgent


def main():
    parser = argparse.ArgumentParser(
        description="Sustainable Supply Chain Agent CLI - Climate, Circularity, What-If Simulation & AI Assistant"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command 1: audit
    audit_parser = subparsers.add_parser("audit", help="Audit Scope 1, 2, and 3 carbon emissions")
    audit_parser.add_argument("--tax", type=float, default=50.0, help="Carbon tax rate ($/tonne)")

    # Command 2: climate-risk
    risk_parser = subparsers.add_parser("climate-risk", help="Assess physical climate risks across suppliers and facilities")
    risk_parser.add_argument("--min-risk", type=float, default=0.0, help="Minimum risk threshold to display")

    # Command 3: circularity
    circ_parser = subparsers.add_parser("circularity", help="Evaluate circular economy metrics and MCI")
    circ_parser.add_argument("--recycled", type=float, default=None, help="Override recycled material input %")
    circ_parser.add_argument("--takeback", type=float, default=None, help="Override take-back return %")
    circ_parser.add_argument("--bio-pkg", action="store_true", help="Enable bio-based packaging")

    # Command 4: routes
    routes_parser = subparsers.add_parser("routes", help="Compare multimodal freight emissions")
    routes_parser.add_argument("--origin", type=str, default="Hai Phong", help="Origin port/hub")
    routes_parser.add_argument("--dest", type=str, default="Frankfurt", help="Destination port/hub")
    routes_parser.add_argument("--weight", type=float, default=50.0, help="Cargo weight in metric tons")

    # Command 5: simulate
    sim_parser = subparsers.add_parser("simulate", help="Run What-If scenario simulation")
    sim_parser.add_argument("--preset", type=str, choices=["carbon_tax_shock", "suez_canal_climate_disruption", "circular_packaging_transition", "green_nearshoring_shift"], help="Preset scenario")
    sim_parser.add_argument("--tax", type=float, default=50.0, help="Carbon tax rate ($/tonne)")
    sim_parser.add_argument("--delay", type=float, default=0.0, help="Transit delay days from disruption")
    sim_parser.add_argument("--recycled", type=float, default=25.0, help="Recycled input %")
    sim_parser.add_argument("--takeback", type=float, default=18.0, help="Return take-back %")
    sim_parser.add_argument("--green-shift", type=float, default=0.0, help="Shift to green suppliers %")

    # Command 6: chat
    chat_parser = subparsers.add_parser("chat", help="Interactive natural language supply chain assistant session")

    # Command 7: web
    web_parser = subparsers.add_parser("web", help="Start the interactive Web Dashboard server")
    web_parser.add_argument("--port", type=int, default=5000, help="Port to bind server")
    web_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host IP to bind (0.0.0.0 for all devices)")
    web_parser.add_argument("--share", action="store_true", help="Create instant public HTTPS link for mobile phones")

    args = parser.parse_args()
    network = get_default_network()

    if args.command == "audit":
        engine = ClimateAwareEngine(network, carbon_tax_usd=args.tax)
        report = engine.generate_carbon_footprint_report()
        print("\n" + "=" * 65)
        print("🌱 SUSTAINABLE SUPPLY CHAIN: CARBON FOOTPRINT AUDIT (GLEC)")
        print("=" * 65)
        print(f"Total Greenhouse Gas Emissions: {report.total_co2e_tons:,.1f} metric tons CO2e")
        print(f"  • Scope 1 (Direct Operations):   {report.scope_1_tons:,.1f} t ({report.scope_1_pct}%)")
        print(f"  • Scope 2 (Grid Electricity):    {report.scope_2_tons:,.1f} t ({report.scope_2_pct}%)")
        print(f"  • Scope 3 (Upstream & Freight):  {report.scope_3_tons:,.1f} t ({report.scope_3_pct}%)")
        print(f"Emissions Intensity:             {report.emissions_per_unit_kg:.2f} kg CO2e / unit produced")
        print(f"Carbon Tax Liability (@${args.tax}/t):   ${report.total_carbon_tax_liability_usd:,.2f}")
        print("\nStrategic Decarbonization Priorities:")
        for r in report.reduction_recommendations:
            print(f"  [+] {r}")
        print("=" * 65 + "\n")

    elif args.command == "climate-risk":
        engine = ClimateAwareEngine(network)
        risks = engine.assess_climate_risks()
        print("\n" + "=" * 80)
        print("🌪️ PHYSICAL CLIMATE VULNERABILITY & EXTREME WEATHER AUDIT")
        print("=" * 80)
        print(f"{'Node / Asset':<30} {'Type':<10} {'Score':<8} {'Threat Level':<12} {'Primary Threat':<20}")
        print("-" * 80)
        for r in risks:
            if r["overall_score"] >= args.min_risk:
                print(f"{r['name'][:28]:<30} {r['type']:<10} {r['overall_score']:<8.0f} {r['risk_level']:<12} {r['primary_threat']}")
        print("=" * 80 + "\n")

    elif args.command == "circularity":
        circ = CircularSupplyChainEngine(network)
        metrics = circ.compute_circularity_metrics(
            override_recycled_pct=args.recycled,
            override_takeback_pct=args.takeback,
            override_bio_packaging=args.bio_pkg,
        )
        flow = circ.calculate_material_flow(
            override_recycled_pct=args.recycled,
            override_takeback_pct=args.takeback,
            override_bio_packaging=args.bio_pkg,
        )
        print("\n" + "=" * 65)
        print("🔄 CIRCULAR SUPPLY CHAIN & MATERIAL CIRCULARITY INDICATOR")
        print("=" * 65)
        print(f"Circularity Maturity Tier:        {metrics.circular_maturity_tier}")
        print(f"Material Circularity Index (MCI): {metrics.mci_score:.1f}%")
        print(f"Circular Feedstock Ratio:         {metrics.circular_feedstock_pct:.1f}%")
        print(f"Reverse Take-Back Rate:           {metrics.takeback_collection_rate_pct:.1f}%")
        print(f"Landfill Diversion Rate:          {metrics.landfill_diversion_rate_pct:.1f}%")
        print(f"Avoided Embodied Carbon:          {metrics.embodied_carbon_avoided_tons:,.1f} t CO2e")
        print(f"Economic Value Recovered:         ${metrics.economic_value_recovered_usd:,.2f}")
        print(f"Landfill Waste Diverted:          {metrics.virgin_material_displacement_tons:,.1f} tons")
        print("\nMaterial Flows (tons):")
        print(f"  • Virgin Raw Input:  {flow.virgin_raw_materials_tons:,.1f} t")
        print(f"  • Recycled Input:    {flow.recycled_input_tons:,.1f} t")
        print(f"  • Returns Reclaimed: {flow.returns_collected_tons:,.1f} t")
        print(f"  • Unrecovered Waste: {flow.unrecoverable_waste_tons:,.1f} t")
        print("=" * 65 + "\n")

    elif args.command == "routes":
        engine = ClimateAwareEngine(network)
        routes = engine.compare_modal_alternatives(args.origin, args.dest, cargo_weight_tons=args.weight)
        print("\n" + "=" * 75)
        print(f"🚢 MULTIMODAL FREIGHT COMPARISON: {args.origin} ➔ {args.dest}")
        print("=" * 75)
        print(f"{'Mode':<15} {'Transit':<10} {'Carbon (t CO2e)':<18} {'Cost ($)':<12} {'Risk %':<8}")
        print("-" * 75)
        for r in routes:
            print(f"{r['mode'].upper():<15} {r['transit_days']:<5.1f} d   {r['co2e_tons']:<18.2f} ${r['cost_usd']:<11,.2f} {r['climate_risk']:<6.0f}%")
        print("=" * 75 + "\n")

    elif args.command == "simulate":
        try:
            from sustainable_supply_chain.agent.tools import SupplyChainToolRegistry
        except ImportError:
            from agent.tools import SupplyChainToolRegistry
        registry = SupplyChainToolRegistry(network)
        comp = registry.run_what_if_simulation(
            scenario_preset=args.preset,
            carbon_tax=args.tax,
            delay_days=args.delay,
            recycled_pct=args.recycled,
            takeback_pct=args.takeback,
            green_shift_pct=args.green_shift,
        )
        base = comp["baseline"]
        sim = comp["simulated"]
        print("\n" + "=" * 70)
        print(f"🔮 WHAT-IF AI SIMULATOR: {comp['scenario_name']}")
        print("=" * 70)
        print(f"{'Metric':<28} {'Baseline':<16} {'Simulated':<16} {'Delta':<12}")
        print("-" * 70)
        print(f"{'Total Carbon (t CO2e)':<28} {base['total_carbon_tons']:<16,.1f} {sim['total_carbon_tons']:<16,.1f} {comp['carbon_delta_tons']:+,.1f} ({comp['carbon_delta_pct']:+}%)")
        print(f"{'Total Cost ($)':<28} ${base['total_cost_usd']:<15,.2f} ${sim['total_cost_usd']:<15,.2f} ${comp['cost_delta_usd']:+,.2f} ({comp['cost_delta_pct']:+}%)")
        print(f"{'Avg Lead Time (days)':<28} {base['avg_lead_time_days']:<16.1f} {sim['avg_lead_time_days']:<16.1f} {comp['lead_time_delta_days']:+.1f} d")
        print(f"{'Circularity (MCI %)':<28} {base['circularity_mci_score']:<16.1f} {sim['circularity_mci_score']:<16.1f} {comp['mci_delta_points']:+.1f} pts")
        print(f"{'Resilience Score (0-100)':<28} {base['resilience_score']:<16.1f} {sim['resilience_score']:<16.1f} {comp['resilience_delta_points']:+.1f} pts")
        print("\nExecutive Takeaways:")
        for t in comp["executive_takeaways"]:
            print(f"  [>] {t}")
        print("\nRecommended Interventions:")
        for a in comp["actionable_recommendations"]:
            print(f"  [+] {a}")
        print("=" * 70 + "\n")

    elif args.command == "chat":
        agent = SustainableSupplyChainAgent(network)
        print("\n" + "=" * 70)
        print("🤖 SUSTAINABLE SUPPLY CHAIN NATURAL LANGUAGE ASSISTANT")
        print("Type 'exit' or 'quit' to end. Type your query in plain English:")
        print("=" * 70)
        while True:
            try:
                user_in = input("\n👤 Supply Chain Exec > ").strip()
                if not user_in:
                    continue
                if user_in.lower() in ["exit", "quit"]:
                    print("Exiting assistant session. Goodbye!")
                    break
                result = agent.process_query(user_in)
                print("\n" + result["response"] + "\n")
                if result.get("suggested_actions"):
                    print("💡 Suggested follow-ups:")
                    for s in result["suggested_actions"][:3]:
                        print(f"   • {s}")
            except (KeyboardInterrupt, EOFError):
                print("\nSession ended.")
                break

    elif args.command == "web":
        try:
            from sustainable_supply_chain.web.app import run_server
        except ImportError:
            from web.app import run_server
        print(f"Starting Sustainable Supply Chain Web Dashboard on http://{args.host}:{args.port} ...")
        run_server(host=args.host, port=args.port, share=args.share)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
