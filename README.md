# 🌿 Sustainable Supply Chain Agent Platform

An autonomous, enterprise-grade AI intelligence system for sustainable global supply chains built in Python.

---

## 🌟 Key Features

### 1. 🌍 Climate-Aware Supply Chain Engine
- **Scope 1, 2, & 3 Carbon Footprint Auditing**: Aligned with the **GHG Protocol** and **GLEC Framework** (Global Logistics Emissions Council).
- **Multimodal Freight Emissions Calculator**: Real-time emission calculations across Air, Sea, Rail, Diesel Road, and Electric Truck corridors based on cargo payload (t-km) and well-to-wheel emission factors.
- **Physical Climate Hazard Exposure**: Pinpoints acute weather vulnerabilities (Typhoons, Monsoonal Flooding, Extreme Heat / Grid Stress, Sea Surge) across manufacturing plants and supplier hubs.
- **Green Supplier Decarbonization Matrix**: Identifies certified low-carbon suppliers (e.g. Nordic Eco Silicon, Rheinland Recycled Alloys) to systematically de-fossilize tier-1 procurement.

### 2. 🔄 Circular Supply Chain & Reverse Logistics Engine
- **Material Circularity Indicator (MCI)**: Formulated in alignment with the **Ellen MacArthur Foundation** circularity methodology.
- **Closed-Loop Mass-Balance Flow Modeling**: Tracks raw virgin materials, post-consumer recycled alloys, and bio-based packaging throughout the production lifecycle.
- **Reverse Logistics Return Stream Triage**: Automated grade diagnostics (Grade A–D) routing returned units to Refurbishment (90% carbon retention), Remanufacturing / Harvesting, Secondary Feedstock Recycling, or Responsible Disposal.
- **Landfill Diversion & Avoided Embodied Carbon**: Quantifies net dollar residual value extracted and tons of virgin resource extraction prevented.

### 3. 🔮 What-If AI Scenario Simulator
- **Multi-Factor Perturbation Modeling**:
  - **Carbon Tax Shocks**: Tests regulatory levies from \$0 to \$300/tonne, showing net operating expenditure impact, green freight break-even thresholds, and decarbonization ROI.
  - **Canal & Port Bottlenecks**: Simulates Suez/Panama blockages and typhoon shutdowns, assessing transit delays, stockout risks, and autonomous rerouting strategies.
  - **Circular Packaging & Take-Back Mandates**: Models aggressive transitions to 65%+ recycled content and 100% bio-based mycelium packaging.
  - **Green Sourcing & Nearshoring Shifts**: Simulates volume reallocations to low-emission domestic and nearshore suppliers.
- **Multi-Objective Trade-Off Analytics**: Side-by-side comparative radar and delta metrics across Cost, Carbon Footprint, Lead Time, MCI Score, and Supply Chain Resilience.

### 4. 🤖 Natural Language Supply Chain Assistant
- **Autonomous Tool-Calling Agent**: Understands plain English queries, extracts operational parameters, executes targeted analytical tools, and delivers executive-level structured insights.
- **Dual-Mode Intelligence**:
  - **Google Gemini API**: Seamlessly integrates when `GEMINI_API_KEY` is provided.
  - **Built-in Semantic Reasoning Engine**: Provides robust, instantaneous offline intent detection and data-grounded synthesis out of the box with zero external dependencies.
- **Suggested Follow-Up Action Chips**: Proactively prompts users with high-impact inquiries and interventions.

---

## 🚀 Quickstart Guide

### 1. Launch Interactive Web Dashboard
Run the web application server:
```bash
python -m sustainable_supply_chain.cli web --port 5000
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
Explore the 5 interactive tabs:
- **📊 Executive Overview**: Real-time Scope 1/2/3 charts, freight breakdown, MCI gauge, and climate alerts.
- **🌍 Climate-Aware Logistics**: Multimodal route comparison calculator and green supplier matrix.
- **🔄 Circular Supply Chain**: Mass-balance flow bars, reverse triage diagnostics, and circular yield.
- **🔮 What-If AI Simulator**: Live sliders for carbon tax, delays, recycled input %, and radar trade-offs.
- **🤖 Natural Language Assistant**: Interactive conversational interface with quick prompt chips.

---

### 2. Command Line Interface (CLI)

#### Audit Carbon Footprint (Scope 1, 2, 3)
```bash
python -m sustainable_supply_chain.cli audit --tax 75
```

#### Assess Physical Climate Hazards
```bash
python -m sustainable_supply_chain.cli climate-risk
```

#### Evaluate Circular Economy & Material Circularity Index (MCI)
```bash
python -m sustainable_supply_chain.cli circularity --recycled 60 --takeback 40 --bio-pkg
```

#### Compare Freight Routes (Hai Phong ➔ Frankfurt)
```bash
python -m sustainable_supply_chain.cli routes --origin "Hai Phong" --dest "Frankfurt" --weight 50
```

#### Run What-If AI Simulation
```bash
# Using a preset:
python -m sustainable_supply_chain.cli simulate --preset carbon_tax_shock

# Custom parameters:
python -m sustainable_supply_chain.cli simulate --tax 120 --delay 10 --recycled 50 --green-shift 60
```

#### Interactive Natural Language Assistant Terminal Session
```bash
python -m sustainable_supply_chain.cli chat
```

---

## 🧪 Running Automated Tests

Run the full unit test suite (100% pass rate):
```bash
python -m unittest discover -s sustainable_supply_chain/tests -p "test_*.py" -v
```

---

## 🏛️ Architecture Overview

```
sustainable_supply_chain/
├── models/                  # Domain schemas (Pydantic)
│   ├── network.py           # Suppliers, Facilities, Routes, Products
│   ├── carbon.py            # Scope 1/2/3, GLEC emission factors
│   ├── circularity.py       # Material flows, return grades, MCI metrics
│   └── scenarios.py         # What-If parameters, simulation results
├── engines/                 # Core analytical engines
│   ├── climate_engine.py    # GLEC emissions, green routes, climate risk index
│   ├── circular_engine.py   # Mass-balance flows, reverse triage, MCI score
│   └── simulator.py         # Multi-factor perturbation & trade-off modeling
├── agent/                   # Conversational AI Assistant
│   ├── tools.py             # Tool execution registry
│   ├── llm_client.py        # Gemini API client + local reasoning engine
│   └── supply_chain_agent.py# Conversational agent & intent orchestrator
├── web/                     # Flask interactive web application
│   ├── app.py               # REST API & endpoints
│   ├── templates/index.html # Modern responsive single-page dashboard
│   └── static/              # Tailwind styling & Chart.js dynamic dashboard
├── cli.py                   # CLI runner
└── tests/                   # Comprehensive unit test suite
```
