"""Flask Web Dashboard application for Sustainable Supply Chain Agent with Restricted Member Authentication."""
from __future__ import annotations
import os
import sys
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Ensure all parent paths are available
web_dir = Path(__file__).resolve().parent
pkg_dir = web_dir.parent
root_dir = pkg_dir.parent
for p in (str(root_dir), str(pkg_dir), str(web_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from sustainable_supply_chain.data.mock_data import get_default_network, get_sample_return_stream
    from sustainable_supply_chain.engines.climate_engine import ClimateAwareEngine
    from sustainable_supply_chain.engines.circular_engine import CircularSupplyChainEngine
    from sustainable_supply_chain.engines.simulator import WhatIfSimulator
    from sustainable_supply_chain.agent.supply_chain_agent import SustainableSupplyChainAgent
    from sustainable_supply_chain.agent.tools import SupplyChainToolRegistry
    from sustainable_supply_chain.models.scenarios import SimulationScenario, ScenarioType
except ImportError:
    from data.mock_data import get_default_network, get_sample_return_stream
    from engines.climate_engine import ClimateAwareEngine
    from engines.circular_engine import CircularSupplyChainEngine
    from engines.simulator import WhatIfSimulator
    from agent.supply_chain_agent import SustainableSupplyChainAgent
    from agent.tools import SupplyChainToolRegistry
    from models.scenarios import SimulationScenario, ScenarioType

app = Flask(
    __name__,
    template_folder=str(web_dir / "templates"),
    static_folder=str(web_dir / "static"),
)

# Secure Session Management
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "sustainable-supply-chain-secure-session-key-2026")

# Pre-configured Authorized Members Database
AUTHORIZED_MEMBERS = {
    "swetha@apex.com": {
        "name": "Swetha",
        "role": "Chief Sustainability Officer (CSO)",
        "password": "green2026",
        "avatar": "👩‍💼",
    },
    "admin@apex.com": {
        "name": "System Administrator",
        "role": "Supply Chain Director",
        "password": "admin123",
        "avatar": "🛡️",
    },
    "auditor@esg.org": {
        "name": "ESG Compliance Officer",
        "role": "Third-Party Auditor",
        "password": "audit2026",
        "avatar": "📋",
    },
}

# Global singleton network and agent
network = get_default_network()
tool_registry = SupplyChainToolRegistry(network)
agent = SustainableSupplyChainAgent(network)


def login_required(f):
    """Decorator requiring an active authenticated member session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "Authentication required. Please log in as an authorized member.",
                    "login_required": True,
                }), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    """Restricted member login portal."""
    if "user" in session:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()

        if not email or not password:
            if request.is_json:
                data = request.get_json() or {}
                email = (data.get("email") or "").strip().lower()
                password = (data.get("password") or "").strip()

        member = AUTHORIZED_MEMBERS.get(email)
        if member and member["password"] == password:
            session["user"] = {
                "email": email,
                "name": member["name"],
                "role": member["role"],
                "avatar": member.get("avatar", "👤"),
            }
            if request.is_json:
                return jsonify({"status": "success", "redirect": "/"})
            return redirect(url_for("index"))
        else:
            error = "Access Denied: You are not an authorized member or password is incorrect."
            if request.is_json:
                return jsonify({"status": "error", "error": error}), 403

    return render_template("login.html", error=error, demo_members=AUTHORIZED_MEMBERS)


@app.route("/logout")
def logout():
    """Logs out the active member session."""
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/api/auth/me", methods=["GET"])
def get_current_user():
    """Returns the authenticated member's session profile."""
    if "user" in session:
        return jsonify({"authenticated": True, "user": session["user"]})
    return jsonify({"authenticated": False}), 401


@app.route("/")
@login_required
def index():
    """Serves the executive web dashboard for authenticated members."""
    return render_template("index.html", current_user=session.get("user"))


@app.route("/api/overview", methods=["GET"])
@login_required
def get_overview():
    """Returns aggregated executive sustainability telemetry."""
    climate_engine = ClimateAwareEngine(network, carbon_tax_usd=50.0)
    circular_engine = CircularSupplyChainEngine(network)
    simulator = WhatIfSimulator(network)

    carbon_report = climate_engine.generate_carbon_footprint_report()
    circ_metrics = circular_engine.compute_circularity_metrics()
    baseline = simulator.calculate_baseline()
    risks = climate_engine.assess_climate_risks()

    return jsonify({
        "network_name": network.name,
        "annual_production_volume": network.annual_production_volume,
        "carbon_report": carbon_report.model_dump(),
        "circularity_metrics": circ_metrics.model_dump(),
        "baseline_summary": baseline.model_dump(),
        "top_climate_risks": risks[:4],
        "suppliers_count": len(network.suppliers),
        "facilities_count": len(network.facilities),
        "routes_count": len(network.routes),
    })


@app.route("/api/climate/routes", methods=["GET"])
@login_required
def get_routes_analysis():
    """Returns multimodal route comparator and freight emissions."""
    origin = request.args.get("origin", "Hai Phong")
    destination = request.args.get("destination", "Frankfurt")
    weight = float(request.args.get("weight", 50.0))

    engine = ClimateAwareEngine(network)
    alternatives = engine.compare_modal_alternatives(origin, destination, weight)
    return jsonify({
        "origin": origin,
        "destination": destination,
        "cargo_weight_tons": weight,
        "modal_options": alternatives,
        "all_active_routes": [r.model_dump() for r in network.routes],
    })


@app.route("/api/climate/risks", methods=["GET"])
@login_required
def get_climate_risks():
    """Returns climate vulnerability and disruption scores."""
    engine = ClimateAwareEngine(network)
    risks = engine.assess_climate_risks()
    return jsonify({"climate_risks": risks})


@app.route("/api/climate/green-suppliers", methods=["GET"])
@login_required
def get_green_suppliers():
    """Returns green supplier optimization matrix."""
    engine = ClimateAwareEngine(network)
    recs = engine.get_green_supplier_recommendations()
    all_sups = [s.model_dump() for s in network.suppliers]
    return jsonify({
        "recommendations": recs,
        "suppliers": all_sups,
    })


@app.route("/api/circular/flows", methods=["GET"])
@login_required
def get_circular_flows():
    """Returns mass-balance material flows and reverse logistics triage."""
    circ_engine = CircularSupplyChainEngine(network)
    recycled = request.args.get("recycled", type=float)
    takeback = request.args.get("takeback", type=float)
    bio_pkg = request.args.get("bio_pkg", "false").lower() == "true"

    flows = circ_engine.calculate_material_flow(
        override_recycled_pct=recycled,
        override_takeback_pct=takeback,
        override_bio_packaging=bio_pkg,
    )
    metrics = circ_engine.compute_circularity_metrics(
        override_recycled_pct=recycled,
        override_takeback_pct=takeback,
        override_bio_packaging=bio_pkg,
    )
    batch = circ_engine.triage_return_batch(get_sample_return_stream())

    return jsonify({
        "metrics": metrics.model_dump(),
        "flows": flows.model_dump(),
        "triage_batch": batch.model_dump(),
    })


@app.route("/api/simulator/run", methods=["POST"])
@login_required
def run_simulation():
    """Executes What-If scenario simulation."""
    data = request.get_json() or {}
    preset = data.get("scenario_preset")

    carbon_tax = float(data.get("carbon_tax", 50.0))
    delay_days = float(data.get("delay_days", 0.0))
    recycled_pct = float(data.get("recycled_pct", 25.0))
    takeback_pct = float(data.get("takeback_pct", 18.0))
    green_shift_pct = float(data.get("green_shift_pct", 0.0))
    rail_shift_pct = float(data.get("rail_shift_pct", 0.0))
    ev_shift_pct = float(data.get("ev_shift_pct", 0.0))
    bio_pkg = bool(data.get("bio_pkg", False))

    simulator = WhatIfSimulator(network)
    presets = simulator.get_preset_scenarios()

    if preset and preset in presets:
        scenario = presets[preset]
    else:
        scenario = SimulationScenario(
            name=data.get("name", "Custom Scenario Simulation"),
            scenario_type=ScenarioType.CUSTOM_COMBINED,
            carbon_tax_usd_per_ton=carbon_tax,
            route_delay_days=delay_days,
            target_recycled_input_pct=recycled_pct,
            target_takeback_collection_pct=takeback_pct,
            shift_to_green_suppliers_pct=green_shift_pct,
            modal_shift_to_rail_pct=rail_shift_pct,
            modal_shift_to_electric_truck_pct=ev_shift_pct,
            sustainable_packaging_switch=bio_pkg,
        )

    comparison = simulator.run_simulation(scenario)
    return jsonify(comparison.model_dump())


@app.route("/api/agent/chat", methods=["POST"])
@login_required
def agent_chat():
    """Processes natural language user questions and returns structured agent output."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    api_key = data.get("api_key")
    if not message:
        return jsonify({"error": "Empty message"}), 400

    if api_key and isinstance(api_key, str) and api_key.strip():
        agent.llm.api_key = api_key.strip()

    result = agent.process_query(message)
    return jsonify(result)


def get_local_ip() -> str:
    """Returns machine LAN IP address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_server(host: str = "0.0.0.0", port: int = 5000, share: bool = False):
    """Launches the Flask server accessible to all local and network devices."""
    lan_ip = get_local_ip()
    print("\n" + "=" * 68)
    print("🌍 SUSTAINABLE SUPPLY CHAIN AI — RESTRICTED ACCESS PORTAL ACTIVE:")
    print("=" * 68)
    print(f"  • On this PC:                http://localhost:{port}")
    print(f"  • On Local Wi-Fi:            http://{lan_ip}:{port}")
    print(f"  • Authorized Sign In:        http://localhost:{port}/login")
    if share:
        try:
            from sustainable_supply_chain.web.tunnel import start_mobile_tunnel
            start_mobile_tunnel(port)
        except ImportError:
            try:
                from web.tunnel import start_mobile_tunnel
                start_mobile_tunnel(port)
            except Exception:
                pass
    else:
        print(f"\n  📱 TO OPEN ON YOUR MOBILE PHONE (No setup needed):")
        print(f"     Run: python run.py web --share")
    print("=" * 68 + "\n")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    share_flag = "--share" in sys.argv
    run_server(port=port, share=share_flag)
