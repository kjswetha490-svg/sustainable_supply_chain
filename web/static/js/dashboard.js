// Dashboard JavaScript for Sustainable Supply Chain Agent

let scopeChart = null;
let freightChart = null;
let routeChart = null;
let simChart = null;

// Tab Management
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('text-emerald-400', 'border-emerald-500', 'bg-gray-800/60');
        btn.classList.add('text-gray-400', 'border-transparent');
    });

    const activeContent = document.getElementById(`content-${tabId}`);
    const activeBtn = document.getElementById(`tab-btn-${tabId}`);
    if (activeContent) activeContent.classList.remove('hidden');
    if (activeBtn) {
        activeBtn.classList.add('text-emerald-400', 'border-emerald-500', 'bg-gray-800/60');
        activeBtn.classList.remove('text-gray-400', 'border-transparent');
    }

    // Trigger chart resizes if needed
    if (tabId === 'overview' && scopeChart) scopeChart.resize();
    if (tabId === 'climate' && routeChart) routeChart.resize();
    if (tabId === 'simulator' && simChart) simChart.resize();
}

// Format currency
function formatCurrency(val) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
}

// Format numbers
function formatNumber(val, decimals = 1) {
    return new Intl.NumberFormat('en-US', { maximumFractionDigits: decimals }).format(val);
}

// Fetch and load Overview Data
async function loadOverview() {
    try {
        const res = await fetch('/api/overview');
        const data = await res.json();

        // Populate Hero KPIs
        const carbon = data.carbon_report;
        const circ = data.circularity_metrics;
        const baseline = data.baseline_summary;

        document.getElementById('kpi-total-carbon').textContent = `${formatNumber(carbon.total_co2e_tons)} t`;
        document.getElementById('kpi-intensity').textContent = `${carbon.emissions_per_unit_kg} kg / unit`;
        document.getElementById('kpi-mci').textContent = `${circ.mci_score}%`;
        document.getElementById('kpi-maturity-tier').textContent = circ.circular_maturity_tier;
        document.getElementById('kpi-resilience').textContent = `${baseline.resilience_score}/100`;
        document.getElementById('kpi-tax-liability').textContent = formatCurrency(carbon.total_carbon_tax_liability_usd);

        // Circular KPIs in circular tab
        document.getElementById('circ-mci-hero').textContent = `${circ.mci_score}%`;
        document.getElementById('circ-feedstock-pct').textContent = `${circ.circular_feedstock_pct}%`;
        document.getElementById('circ-takeback-pct').textContent = `${circ.takeback_collection_rate_pct}%`;
        document.getElementById('circ-diversion-pct').textContent = `${circ.landfill_diversion_rate_pct}%`;
        document.getElementById('circ-val-recovered').textContent = formatCurrency(circ.economic_value_recovered_usd);
        document.getElementById('circ-avoided-co2').textContent = `${formatNumber(circ.embodied_carbon_avoided_tons)} t CO2e`;

        // Render Scope Doughnut Chart
        renderScopeChart(carbon);

        // Render Freight Mode Chart
        renderFreightChart(carbon.mode_breakdown_tons);

        // Populate Climate Risk Alerts Table
        renderRiskAlerts(data.top_climate_risks);

    } catch (err) {
        console.error("Error loading overview:", err);
    }
}

function renderScopeChart(carbon) {
    const ctx = document.getElementById('scopeEmissionsChart');
    if (!ctx) return;

    if (scopeChart) scopeChart.destroy();

    scopeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                `Scope 1 Direct (${carbon.scope_1_pct}%)`,
                `Scope 2 Grid (${carbon.scope_2_pct}%)`,
                `Scope 3 Value Chain (${carbon.scope_3_pct}%)`
            ],
            datasets: [{
                data: [carbon.scope_1_tons, carbon.scope_2_tons, carbon.scope_3_tons],
                backgroundColor: ['#10b981', '#06b6d4', '#f59e0b'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#9ca3af', font: { size: 11 } }
                }
            },
            cutout: '70%',
        }
    });
}

function renderFreightChart(modeData) {
    const ctx = document.getElementById('freightModesChart');
    if (!ctx) return;

    if (freightChart) freightChart.destroy();

    const labels = Object.keys(modeData).map(k => k.replace('_', ' ').toUpperCase());
    const values = Object.values(modeData);

    freightChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Annual Freight Emissions (t CO2e)',
                data: values,
                backgroundColor: ['#ef4444', '#f97316', '#10b981', '#3b82f6', '#06b6d4'],
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } },
                y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

function renderRiskAlerts(risks) {
    const container = document.getElementById('risk-alerts-container');
    if (!container) return;

    container.innerHTML = risks.map(r => {
        const badgeColor = r.overall_score > 70 ? 'bg-red-500/20 text-red-400 border-red-500/30' :
            (r.overall_score > 50 ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30');
        return `
            <div class="p-3 bg-gray-900/60 rounded-lg border border-gray-800 flex items-center justify-between">
                <div>
                    <div class="font-medium text-sm text-gray-200">${r.name}</div>
                    <div class="text-xs text-gray-400">${r.location} • <span class="text-gray-300 font-semibold">${r.primary_threat}</span></div>
                </div>
                <div class="text-right">
                    <span class="px-2 py-0.5 text-xs font-semibold rounded-full border ${badgeColor}">
                        Score: ${Math.round(r.overall_score)}/100
                    </span>
                    <div class="text-[10px] text-gray-400 mt-1">${r.risk_level}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Load Climate Tab Data
async function loadClimateData() {
    try {
        // Load Green Suppliers Matrix
        const supRes = await fetch('/api/climate/green-suppliers');
        const supData = await supRes.json();
        const supContainer = document.getElementById('green-suppliers-matrix');
        if (supContainer && supData.recommendations) {
            supContainer.innerHTML = supData.recommendations.map(r => `
                <div class="glass-card p-4 rounded-xl border border-gray-800">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">${r.category}</span>
                        <span class="text-xs font-bold text-emerald-400">-${r.carbon_savings_pct}% Carbon</span>
                    </div>
                    <div class="text-sm font-semibold text-gray-200 mb-1">Replace: <span class="text-red-400">${r.current_supplier}</span></div>
                    <div class="text-sm font-semibold text-gray-200 mb-3">With: <span class="text-emerald-400">${r.recommended_green_supplier}</span></div>
                    <div class="grid grid-cols-2 gap-2 text-xs text-gray-400 bg-gray-900/80 p-2.5 rounded-lg">
                        <div>Emissions: <span class="text-gray-200 font-medium">${r.current_carbon_kg} ➔ ${r.green_carbon_kg} kg/u</span></div>
                        <div>Renewable: <span class="text-emerald-400 font-medium">${r.green_renewable_pct}%</span></div>
                        <div>Cost Delta: <span class="text-gray-200 font-medium">${r.cost_delta_per_unit_usd >= 0 ? '+' : ''}$${r.cost_delta_per_unit_usd}/u</span></div>
                        <div>ESG Uplift: <span class="text-emerald-400 font-medium">+${r.esg_score_improvement} pts</span></div>
                    </div>
                </div>
            `).join('');
        }

        // Run Route Comparison
        runRouteComparison();

    } catch (err) {
        console.error("Error loading climate data:", err);
    }
}

async function runRouteComparison() {
    const origin = document.getElementById('route-origin')?.value || "Hai Phong";
    const destination = document.getElementById('route-dest')?.value || "Frankfurt";
    const weight = document.getElementById('route-weight')?.value || 50;

    try {
        const res = await fetch(`/api/climate/routes?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&weight=${weight}`);
        const data = await res.json();

        // Render Table
        const tbody = document.getElementById('route-table-body');
        if (tbody && data.modal_options) {
            tbody.innerHTML = data.modal_options.map((m, idx) => {
                const isGreenest = idx === 0;
                return `
                    <tr class="border-b border-gray-800 ${isGreenest ? 'bg-emerald-950/20' : ''}">
                        <td class="py-2.5 px-3 font-semibold ${isGreenest ? 'text-emerald-400' : 'text-gray-200'}">
                            ${m.mode.toUpperCase()}
                            ${isGreenest ? '<span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">GREENEST</span>' : ''}
                        </td>
                        <td class="py-2.5 px-3 text-gray-300">${formatNumber(m.distance_km, 0)} km</td>
                        <td class="py-2.5 px-3 text-gray-300">${m.transit_days} days</td>
                        <td class="py-2.5 px-3 font-bold ${isGreenest ? 'text-emerald-400' : 'text-gray-200'}">${m.co2e_tons} t</td>
                        <td class="py-2.5 px-3 text-gray-300">${formatCurrency(m.cost_usd)}</td>
                        <td class="py-2.5 px-3">
                            <span class="px-2 py-0.5 text-xs rounded-full ${m.climate_risk > 25 ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}">
                                ${Math.round(m.climate_risk)}%
                            </span>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // Render Route Chart
        renderRouteChart(data.modal_options);

    } catch (err) {
        console.error("Error comparing routes:", err);
    }
}

function renderRouteChart(options) {
    const ctx = document.getElementById('routeComparisonChart');
    if (!ctx) return;

    if (routeChart) routeChart.destroy();

    const labels = options.map(o => o.mode.toUpperCase());
    const carbonData = options.map(o => o.co2e_tons);

    routeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Carbon Footprint (t CO2e)',
                data: carbonData,
                backgroundColor: ['#10b981', '#06b6d4', '#3b82f6', '#f59e0b', '#ef4444'],
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } },
                y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: 't CO2e', color: '#6b7280' } }
            }
        }
    });
}

// Load Circularity Tab Data
async function loadCircularityData() {
    try {
        const res = await fetch('/api/circular/flows');
        const data = await res.json();

        // Triage batch table
        const triage = data.triage_batch;
        const triageContainer = document.getElementById('triage-breakdown-container');
        if (triageContainer) {
            triageContainer.innerHTML = `
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                    <div class="p-3 bg-emerald-950/30 rounded-lg border border-emerald-500/30">
                        <div class="text-xs text-emerald-400 font-semibold uppercase">Grade A: Refurbish</div>
                        <div class="text-xl font-bold text-gray-100 my-1">${triage.disposition_counts.refurbish} units</div>
                        <div class="text-[11px] text-gray-400">${triage.disposition_weights_tons.refurbish} t • 90% retention</div>
                    </div>
                    <div class="p-3 bg-cyan-950/30 rounded-lg border border-cyan-500/30">
                        <div class="text-xs text-cyan-400 font-semibold uppercase">Grade B: Remanufacture</div>
                        <div class="text-xl font-bold text-gray-100 my-1">${triage.disposition_counts.remanufacture_harvest} units</div>
                        <div class="text-[11px] text-gray-400">${triage.disposition_weights_tons.remanufacture_harvest} t • Parts harvest</div>
                    </div>
                    <div class="p-3 bg-amber-950/30 rounded-lg border border-amber-500/30">
                        <div class="text-xs text-amber-400 font-semibold uppercase">Grade C: Recycle</div>
                        <div class="text-xl font-bold text-gray-100 my-1">${triage.disposition_counts.recycle_feedstock} units</div>
                        <div class="text-[11px] text-gray-400">${triage.disposition_weights_tons.recycle_feedstock} t • Raw feedstock</div>
                    </div>
                    <div class="p-3 bg-red-950/30 rounded-lg border border-red-500/30">
                        <div class="text-xs text-red-400 font-semibold uppercase">Grade D: Disposal</div>
                        <div class="text-xl font-bold text-gray-100 my-1">${triage.disposition_counts.responsible_disposal} units</div>
                        <div class="text-[11px] text-gray-400">${triage.disposition_weights_tons.responsible_disposal} t • Safe WtE</div>
                    </div>
                </div>
            `;
        }

        // Material Flow Bars
        const flow = data.flows;
        const total = flow.total_input_materials_tons || 1;
        const virginPct = Math.round((flow.virgin_raw_materials_tons / total) * 100);
        const recPct = Math.round((flow.recycled_input_tons / total) * 100);
        const bioPct = Math.round((flow.bio_based_input_tons / total) * 100);

        document.getElementById('flow-virgin-bar').style.width = `${virginPct}%`;
        document.getElementById('flow-virgin-label').textContent = `${flow.virgin_raw_materials_tons} t (${virginPct}%)`;
        document.getElementById('flow-recycled-bar').style.width = `${recPct}%`;
        document.getElementById('flow-recycled-label').textContent = `${flow.recycled_input_tons} t (${recPct}%)`;
        document.getElementById('flow-bio-bar').style.width = `${bioPct}%`;
        document.getElementById('flow-bio-label').textContent = `${flow.bio_based_input_tons} t (${bioPct}%)`;

    } catch (err) {
        console.error("Error loading circular data:", err);
    }
}

// What-If Simulator Execution
async function runSimulation(presetKey = null) {
    const payload = {};
    if (presetKey) {
        payload.scenario_preset = presetKey;
    } else {
        payload.carbon_tax = parseFloat(document.getElementById('sim-tax-input')?.value || 50);
        payload.delay_days = parseFloat(document.getElementById('sim-delay-input')?.value || 0);
        payload.recycled_pct = parseFloat(document.getElementById('sim-recycled-input')?.value || 25);
        payload.takeback_pct = parseFloat(document.getElementById('sim-takeback-input')?.value || 18);
        payload.green_shift_pct = parseFloat(document.getElementById('sim-greenshift-input')?.value || 0);
        payload.rail_shift_pct = parseFloat(document.getElementById('sim-rail-input')?.value || 0);
        payload.ev_shift_pct = parseFloat(document.getElementById('sim-ev-input')?.value || 0);
        payload.bio_pkg = document.getElementById('sim-bio-check')?.checked || false;
    }

    try {
        const res = await fetch('/api/simulator/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const comp = await res.json();
        renderSimulationResults(comp);

    } catch (err) {
        console.error("Error running simulation:", err);
    }
}

function renderSimulationResults(comp) {
    const sim = comp.simulated;
    const base = comp.baseline;

    document.getElementById('sim-scenario-title').textContent = comp.scenario_name;

    // Delta badges
    const formatDelta = (val, pct, isGoodWhenNegative = true, unit = "") => {
        const isGood = isGoodWhenNegative ? val <= 0 : val >= 0;
        const colorClass = isGood ? 'text-emerald-400 bg-emerald-950/40 border-emerald-500/30' : 'text-red-400 bg-red-950/40 border-red-500/30';
        const sign = val > 0 ? '+' : '';
        return `<span class="px-2 py-0.5 rounded text-xs border ${colorClass} font-semibold">${sign}${formatNumber(val)}${unit} (${sign}${formatNumber(pct)}%)</span>`;
    };

    document.getElementById('sim-carbon-base').textContent = `${formatNumber(base.total_carbon_tons)} t`;
    document.getElementById('sim-carbon-val').textContent = `${formatNumber(sim.total_carbon_tons)} t`;
    document.getElementById('sim-carbon-delta').innerHTML = formatDelta(comp.carbon_delta_tons, comp.carbon_delta_pct, true, " t");

    document.getElementById('sim-cost-base').textContent = formatCurrency(base.total_cost_usd);
    document.getElementById('sim-cost-val').textContent = formatCurrency(sim.total_cost_usd);
    document.getElementById('sim-cost-delta').innerHTML = formatDelta(comp.cost_delta_usd, comp.cost_delta_pct, true, "");

    document.getElementById('sim-lead-base').textContent = `${base.avg_lead_time_days} d`;
    document.getElementById('sim-lead-val').textContent = `${sim.avg_lead_time_days} d`;
    document.getElementById('sim-lead-delta').innerHTML = formatDelta(comp.lead_time_delta_days, comp.lead_time_delta_pct, true, " d");

    document.getElementById('sim-mci-base').textContent = `${base.circularity_mci_score}%`;
    document.getElementById('sim-mci-val').textContent = `${sim.circularity_mci_score}%`;
    document.getElementById('sim-mci-delta').innerHTML = formatDelta(comp.mci_delta_points, (comp.mci_delta_points / base.circularity_mci_score) * 100, false, " pts");

    document.getElementById('sim-res-base').textContent = `${base.resilience_score}/100`;
    document.getElementById('sim-res-val').textContent = `${sim.resilience_score}/100`;
    document.getElementById('sim-res-delta').innerHTML = formatDelta(comp.resilience_delta_points, (comp.resilience_delta_points / base.resilience_score) * 100, false, " pts");

    // Takeaways & Recommendations
    const takeContainer = document.getElementById('sim-takeaways-container');
    if (takeContainer) {
        takeContainer.innerHTML = comp.executive_takeaways.map(t => `<li class="text-sm text-gray-300">${t}</li>`).join('');
    }

    const recContainer = document.getElementById('sim-recs-container');
    if (recContainer) {
        recContainer.innerHTML = comp.actionable_recommendations.map(a => `<li class="text-sm text-emerald-300 font-medium">${a}</li>`).join('');
    }

    // Render Simulation Comparison Chart
    renderSimulationChart(base, sim);
}

function renderSimulationChart(base, sim) {
    const ctx = document.getElementById('simulationDeltaChart');
    if (!ctx) return;

    if (simChart) simChart.destroy();

    simChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Decarbonization Index', 'Cost Efficiency', 'Speed / Lead Time', 'Material Circularity', 'Supply Resilience'],
            datasets: [
                {
                    label: 'Baseline',
                    data: [
                        100 - Math.min(100, (base.total_carbon_tons / 500)),
                        100 - Math.min(100, (base.total_cost_usd / 200000)),
                        Math.max(10, 100 - (base.avg_lead_time_days * 3)),
                        base.circularity_mci_score,
                        base.resilience_score,
                    ],
                    borderColor: '#6b7280',
                    backgroundColor: 'rgba(107, 114, 128, 0.2)',
                    borderWidth: 2,
                },
                {
                    label: 'Simulated Scenario',
                    data: [
                        100 - Math.min(100, (sim.total_carbon_tons / 500)),
                        100 - Math.min(100, (sim.total_cost_usd / 200000)),
                        Math.max(10, 100 - (sim.avg_lead_time_days * 3)),
                        sim.circularity_mci_score,
                        sim.resilience_score,
                    ],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.25)',
                    borderWidth: 2,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    pointLabels: { color: '#9ca3af', font: { size: 11 } },
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { labels: { color: '#d1d5db', font: { size: 12 } } }
            }
        }
    });
}

// Natural Language Assistant Chat
async function sendChatMessage(presetQuery = null) {
    const inputEl = document.getElementById('chat-input');
    const message = presetQuery || inputEl?.value.trim();
    if (!message) return;

    if (!presetQuery && inputEl) inputEl.value = '';

    const feed = document.getElementById('chat-messages-container');
    if (!feed) return;

    // Append User Message
    const userBubble = `
        <div class="flex justify-end mb-4">
            <div class="max-w-2xl bg-emerald-600/20 border border-emerald-500/40 rounded-2xl rounded-tr-sm px-4 py-3 text-gray-100 text-sm">
                <div class="text-[11px] text-emerald-400 font-semibold mb-1 uppercase">Executive Query</div>
                <div>${escapeHtml(message)}</div>
            </div>
        </div>
    `;
    feed.insertAdjacentHTML('beforeend', userBubble);
    feed.scrollTop = feed.scrollHeight;

    // Show Typing Indicator
    const typingId = `typing-${Date.now()}`;
    const typingBubble = `
        <div id="${typingId}" class="flex justify-start mb-4">
            <div class="max-w-2xl glass-card rounded-2xl rounded-tl-sm px-4 py-3 border border-gray-800 text-gray-400 text-sm flex items-center space-x-2">
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" style="animation-delay: 0.2s"></span>
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" style="animation-delay: 0.4s"></span>
                <span class="ml-2 text-xs text-gray-400">Analyzing supply chain telemetry...</span>
            </div>
        </div>
    `;
    feed.insertAdjacentHTML('beforeend', typingBubble);
    feed.scrollTop = feed.scrollHeight;

    try {
        const res = await fetch('/api/agent/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message }),
        });
        const data = await res.json();

        // Remove typing indicator
        document.getElementById(typingId)?.remove();

        // Convert simple markdown to HTML
        const formattedHtml = renderMarkdown(data.response || "No response received.");

        // Suggested action chips
        let chipsHtml = '';
        if (data.suggested_actions && data.suggested_actions.length > 0) {
            chipsHtml = `
                <div class="mt-3 pt-3 border-t border-gray-800/80">
                    <div class="text-[11px] font-semibold text-gray-400 mb-1.5 uppercase">Suggested Follow-ups:</div>
                    <div class="flex flex-wrap gap-1.5">
                        ${data.suggested_actions.map(s => `
                            <button onclick="sendChatMessage('${escapeHtml(s)}')" class="text-xs px-2.5 py-1 rounded-full bg-gray-800 hover:bg-emerald-950/60 hover:text-emerald-300 text-gray-300 border border-gray-700 transition">
                                💡 ${escapeHtml(s)}
                            </button>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        const agentBubble = `
            <div class="flex justify-start mb-4">
                <div class="max-w-3xl glass-card rounded-2xl rounded-tl-sm px-5 py-4 border border-gray-800 text-gray-100 text-sm shadow-xl">
                    <div class="flex items-center space-x-2 text-[11px] text-emerald-400 font-semibold mb-2 uppercase">
                        <span class="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
                        <span>AI Sustainability Officer</span>
                        <span class="text-gray-500">•</span>
                        <span class="text-gray-400 font-normal">Telemetry-Verified</span>
                    </div>
                    <div class="chat-prose text-gray-200">
                        ${formattedHtml}
                    </div>
                    ${chipsHtml}
                </div>
            </div>
        `;
        feed.insertAdjacentHTML('beforeend', agentBubble);
        feed.scrollTop = feed.scrollHeight;

    } catch (err) {
        document.getElementById(typingId)?.remove();
        console.error("Chat error:", err);
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function renderMarkdown(md) {
    if (!md) return '';
    let html = md;

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

    // Code blocks
    html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');

    // Inline code
    html = html.replace(/`([^`]+)`/gim, '<code class="px-1.5 py-0.5 rounded bg-gray-800 text-emerald-300 font-mono text-xs">$1</code>');

    // Bullet lists
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Tables: basic markdown table parsing
    const lines = html.split('\n');
    let inTable = false;
    let tableHtml = '';
    let newLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('|') && line.endsWith('|')) {
            if (line.includes('---')) continue; // Skip table header separator
            const cols = line.split('|').slice(1, -1);
            if (!inTable) {
                inTable = true;
                tableHtml = '<table class="w-full text-xs my-2 border border-gray-800"><thead><tr>';
                cols.forEach(c => tableHtml += `<th>${c.trim()}</th>`);
                tableHtml += '</tr></thead><tbody>';
            } else {
                tableHtml += '<tr>';
                cols.forEach(c => tableHtml += `<td>${c.trim()}</td>`);
                tableHtml += '</tr>';
            }
        } else {
            if (inTable) {
                inTable = false;
                tableHtml += '</tbody></table>';
                newLines.push(tableHtml);
            }
            newLines.push(line);
        }
    }
    if (inTable) {
        tableHtml += '</tbody></table>';
        newLines.push(tableHtml);
    }

    html = newLines.join('\n');
    // Paragraphs
    html = html.replace(/\n\n+/g, '<p></p>');

    return html;
}

// Initial page setup
document.addEventListener('DOMContentLoaded', () => {
    loadOverview();
    loadClimateData();
    loadCircularityData();
    runSimulation('carbon_tax_shock'); // default scenario in simulator

    // Hook up chat Enter key
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    // Live slider values
    const hookSlider = (sliderId, labelId, prefix = '', suffix = '') => {
        const slider = document.getElementById(sliderId);
        const label = document.getElementById(labelId);
        if (slider && label) {
            slider.addEventListener('input', () => {
                label.textContent = `${prefix}${slider.value}${suffix}`;
            });
        }
    };

    hookSlider('sim-tax-input', 'sim-tax-label', '$', '/t');
    hookSlider('sim-delay-input', 'sim-delay-label', '', ' days');
    hookSlider('sim-recycled-input', 'sim-recycled-label', '', '%');
    hookSlider('sim-takeback-input', 'sim-takeback-label', '', '%');
    hookSlider('sim-greenshift-input', 'sim-greenshift-label', '', '%');
    hookSlider('sim-rail-input', 'sim-rail-label', '', '%');
    hookSlider('sim-ev-input', 'sim-ev-label', '', '%');
});
