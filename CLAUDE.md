# STRIDE Project Reference

## Project Context

**STRIDE**: Sequential Temporal Resource Investment for Depot Electrification
**Institution**: Technical University of Munich (TUM)
**Type**: Master's Thesis
**Timeline**: October 2025 - April 13, 2026
**Problem**: Electric truck depot infrastructure planning over 25-30 year horizons (2025-2055)

**Core Objective**: Multi-stage optimization of PV solar, battery storage (ESS), EV chargers, and grid connections for depot electrification under technology cost decline, demand growth, and CO2 constraints.

---

## REVOLETION Architecture (Forked Base Package)

### Purpose
REVOL-E-TION (Resilient Electric Vehicle Optimization model for Local Energy TransitION) optimizes EV fleet integration into local energy systems (microgrids, company sites, apartment blocks). Built as wrapper on oemof-solph energy system framework.

### Building Blocks (`revoletion/revoletion/blocks.py`)

17 component classes representing energy system assets:

**Core Infrastructure**:
- `SystemCore`: AC/DC buses with bidirectional converter
- `GridConnection`: Grid interface with `GridMarket` subblocks for different tariff structures (peak/offpeak/feed-in)

**Generation**:
- `RenewableInvestBlock`: Base class for renewables
  - `PVSource`: PV arrays (pvlib integration)
  - `WindSource`: Wind turbines (windpowerlib integration)
- `ControllableSource`: Dispatchable generation (diesel, gas)

**Storage**:
- `StationaryEnergyStorage`: Stationary batteries
- `CommoditySystem`: Mobile storage systems
  - `VehicleCommoditySystem`: Electric vehicles
  - `BatteryCommoditySystem`: Swappable battery systems
  - `MobileCommodity`: Individual vehicle/battery (SubBlock)

**Demand**:
- `FixedDemand`: Inelastic electrical load
- `ICEVSystem`: Baseline ICE vehicles for comparison

**Key Concepts**:
- `Block`: Base class for all components, stores flows/energies/expenditures
- `InvestBlock(Block)`: Components with investment optimization (size_existing + size_invest)
- `SubBlock`: Nested components (e.g., GridMarkets within GridConnection)

### Optimization Flow

**Entry Points**:
- CLI: `python -m revoletion.main --settings settings.csv --scenario scenarios.csv`
- Python: `from revoletion import SimulationRun; SimulationRun(settings, scenarios).execute_simulation()`

**Execution Sequence**:
1. **SimulationRun** loads settings CSV + scenarios CSV
2. **For each Scenario**:
   - Parse CSV parameters → instantiate Block objects
   - (Optional) Run Discrete Event Simulation (DES) to generate mobility patterns
   - **For each PredictionHorizon** (rolling or global):
     - Slice timeseries data (weather, demand, prices)
     - Build oemof `EnergySystem` (buses, sources, sinks, storages, transformers)
     - Convert to pyomo MILP model
     - Apply custom constraints (`constraints.py`): CO2 limits, renewables-only feeding, investment limits
     - Solve with Gurobi/CBC solver
     - Extract results: power flows, investments, storage SOC
     - Calculate battery aging (rainflow counting for cyclic degradation)
   - Aggregate results across horizons: energy, costs, cashflows
   - Calculate meta-results: LCOE, NPV, IRR, renewable share, CO2 emissions
   - Generate Plotly dispatch plots
   - Save outputs: summary CSV/pickle, timeseries CSV, plots, system graph PDF

**Optimization Strategies**:
- `'go'` (Global Optimization): Single horizon covering entire simulation period
- `'rh'` (Rolling Horizon): Overlapping prediction/commitment horizons for large problems

### Scenario File Format (CSV)

Sparse matrix format defining block instances and parameters:

```csv
block,key,scenario_base,scenario_co2_100
pv1,block_type,pv_source,pv_source
pv1,size_existing,0,0
pv1,size_invest,500000,500000
pv1,capex,0.5,0.5
pv1,opex,0.01,0.01
grid,co2_spec_g2s,0.4,0.4
scenario,co2_max,None,100000
```

**Key Parameters**:
- `block`: Block instance name (e.g., `pv1`, `grid`, `ess1`)
- `key`: Parameter name
- Columns: Scenario names (can have multiple scenarios in one CSV)
- Common keys: `size_existing`, `size_invest`, `capex`, `opex`, `mntex`, `lifetime`, `discount_rate`, `co2_spec_g2s`, `co2_max`

**Units**: Power in W, energy in Wh, costs in €, emissions in kg CO2, time in hours

### Key Modules (`revoletion/revoletion/`)

- `simulation.py` (1800 lines): `SimulationRun`, `Scenario`, `PredictionHorizon` classes - core orchestration
- `blocks.py` (3900 lines): 17 component classes with oemof integration
- `constraints.py` (340 lines): Custom pyomo constraints (CO2, renewables-only, investment limits)
- `dispatch.py` (900 lines): Discrete Event Simulation for EV mobility pattern generation
- `scheduler.py` (800 lines): Rule-based charging strategies (uncoordinated, FCFS, equal, SOC-based)
- `battery.py` (700 lines): Battery physics (aging via rainflow, OCV, internal resistance, NMC/LFP chemistries)
- `economics.py` (270 lines): NPV, LCOE, IRR, annuity, discount functions
- `mobility.py` (400 lines): Mobility demand modeling (log-normal distributions, usecase assignment)
- `utils.py` (440 lines): Data type inference, timeseries scaling, expenditure dataframe creation
- `checker.py` (110 lines): Input validation for settings/scenarios
- `logger.py` (30 lines): Logging configuration

**Output Structure** (`revoletion/results/TIMESTAMP_scenarioname/`):
- `summary.csv`: LCOE, NPV, IRR, renewable share, CO2 emissions
- `timeseries.csv`: Power flows, SOC per timestep
- `status.csv`: Scenario success/failure/infeasible
- `*.html`: Plotly dispatch visualizations
- `*.pdf`: System graph visualizations
- `*.pickle`: Complete result objects

---

## STRIDE Extensions (Master's Thesis Wrapper)

### What STRIDE Adds Over REVOLETION

1. **Multi-stage sequential optimization** (REVOLETION is single-stage):
   - 6 stages: 2025, 2030, 2035, 2040, 2045, 2050
   - Each stage optimizes 5-year investment period
   - Myopic optimization (realistic vs perfect foresight)

2. **Technology cost evolution**:
   - PV: $0.50/W (2025) → $0.14/W (2050), -5%/year
   - ESS: $0.250/Wh (2025) → $0.031/Wh (2050), -8%/year

3. **Fleet demand growth**:
   - 30k vehicles (2025) → 325k vehicles (2050), +10%/year

4. **CO2 decarbonization pathways**:
   - Linear tightening: 500 kg (2025) → 100 kg (2050) per 50-day simulation

5. **Stage-linking constraints**:
   - Investments carry forward: stage N results → `size_existing` in stage N+1
   - Non-reversible (capacities only increase)

6. **NPV analysis**:
   - 9% WACC discount rate
   - 25-year total horizon NPV calculation

### Multi-Stage Workflow

```
For each stage (2025, 2030, 2035, 2040, 2045, 2050):
  1. ScenarioBuilder generates stage-specific CSV:
     - Inherit size_existing from previous stage investments
     - Apply cost curves for current year
     - Scale demand for fleet growth
     - Set CO2 limit from decarbonization pathway
     - Set project_duration to 5 years

  2. Call REVOLETION via subprocess:
     python -m revoletion.main --settings settings.csv --scenario stage_2025.csv

  3. ResultsParser extracts:
     - Investment decisions (PV kW, ESS kWh, grid kW, chargers)
     - Economics (NPV, CAPEX, OPEX, LCOE)
     - Emissions (simulation & project-level CO2)
     - Operational metrics (grid import/export, PV generation, renewable share)

  4. Feed results forward:
     stage_2030.csv gets size_existing from stage_2025 results

  5. Handle infeasibility:
     - Diagnostic output if solver fails
     - Track infeasible scenarios
```

### Key Files (Outside `revoletion/` Submodule)

**Multi-Stage Framework** (`multi_stage/`):
- `sequential_optimizer.py`: Orchestrates workflow, manages subprocess calls
- `scenario_builder.py`: Generates stage CSVs with cost evolution, demand growth, CO2 pathways, stage linking
- `results_parser.py`: Extracts metrics, aggregates across stages, NPV discounting
- `stage_linker.py`: (Minimal - linking done in scenario_builder)
- `economics.py`: (Minimal - economics in results_parser)
- `uncertainty.py`: (Placeholder for future stochastic analysis)

**Validation Notebooks** (`notebooks/`):
- `01_test_co2_constraint/01_test_co2_constraint.ipynb`: Validates CO2 constraint across 7 emission limits, marginal abatement cost analysis, 4 publication plots + CSV/JSON exports
- `02_test_2_stage/02_test_2_stage.ipynb`: Tests 2-stage optimization (2025→2030), validates stage linking and technology cost decreases

**Analysis Modules** (`analysis/`) - **STUBS ONLY**:
- `visualizations.py`: Investment timelines, NPV waterfalls, sensitivity heatmaps
- `comparison.py`: Scenario comparisons
- `sensitivity.py`: Parameter sensitivity studies
- `recommendations.py`: Actionable insights generation

**Case Studies** (`case_studies/`):
- `baseline/scenarios_multistage.csv`: Template scenario configurations
- `baseline/settings_multistage.csv`: REVOLETION settings for multi-stage runs

**Documentation**:
- `README.md`: Installation, usage, project overview
- `STRIDE_Thesis_Master_Reference.md`: Complete thesis roadmap, methodology justification
- `THESIS_REFERENCE.md`: Additional thesis context
- `multi_stage/IMPLEMENTATION_SUMMARY.md`: Detailed technical implementation notes
- `docs/methodology.md`: Methodology documentation
- `docs/formulation.tex`: Mathematical formulation (LaTeX)

---

## Critical File Locations

### REVOLETION Submodule (DO NOT MODIFY - Keep Clean for Forked Updates)
```
revoletion/
├── revoletion/
│   ├── simulation.py         # Core: SimulationRun, Scenario, PredictionHorizon
│   ├── blocks.py             # 17 energy component classes
│   ├── constraints.py        # Custom pyomo constraints (CO2, renewables-only)
│   ├── dispatch.py           # DES for mobility patterns
│   ├── scheduler.py          # Rule-based charging strategies
│   ├── battery.py            # Aging models (rainflow, NMC/LFP)
│   ├── economics.py          # NPV, LCOE, IRR
│   ├── mobility.py           # Mobility demand modeling
│   └── utils.py              # Helper functions
├── example/
│   ├── scenarios_example.csv # Example scenario definitions
│   └── settings.csv          # Example settings
└── results/
    └── TIMESTAMP_*/          # Optimization outputs
```

### STRIDE Wrapper (Active Development)
```
multi_stage/
├── sequential_optimizer.py   # Multi-stage orchestrator
├── scenario_builder.py       # Stage CSV generation with cost/demand/CO2 evolution
└── results_parser.py         # Metrics extraction and aggregation

notebooks/
├── 01_test_co2_constraint/
│   ├── 01_test_co2_constraint.ipynb
│   └── output/               # Plots, CSVs, JSONs
└── 02_test_2_stage/
    └── 02_test_2_stage.ipynb

case_studies/
└── baseline/
    ├── scenarios_multistage.csv
    └── settings_multistage.csv

analysis/                     # STUBS - Not implemented yet
├── visualizations.py
├── comparison.py
├── sensitivity.py
└── recommendations.py
```

---

## Development Status (Nov 2025)

### Completed ✅
- CO2 constraint implementation in REVOLETION (`constraints.py:296-343`)
- CO2 constraint validation (7 scenarios, marginal abatement cost analysis)
- 2-stage optimizer working (2025→2030 validated)
- Technology cost evolution functions (PV -5%/yr, ESS -8%/yr tested)
- Fleet demand growth modeling (+10%/yr)
- Project duration per stage (5 years)
- Project-level CO2 tracking (simulation period → 25-year extrapolation)
- Infeasibility detection + diagnostics
- Stage-linking constraints (size_existing inheritance)

### In Development 🚧
- Full 6-stage (2025-2050) optimization runs
- Debugging stage N>2 issues (git log mentions "2030 debugging")
- Multi-stage constraint linking verification

### Planned 📅
- Analysis/visualization modules (currently stubs)
- Sensitivity studies (demand growth, cost decline rates, CO2 pathways, WACC)
- Multiple case study scenarios (baseline, high_growth, conservative mentioned but not present)
- Stochastic demand modeling (`uncertainty.py` placeholder)
- Policy scenario analysis (carbon pricing, subsidies)
- Thesis writing (60-90 pages target per `STRIDE_Thesis_Master_Reference.md`)

---

## Important Conventions

### Virtual Environment
- **CRITICAL**: All code must run in `venv/`
- Installation: `cd revoletion && pip install -e . && cd ..`
- Jupyter kernel: Verify with `import sys; print(sys.executable)` → should show venv path
- PyCharm: Settings → Project → Python Interpreter → Select `venv/bin/python3`

### Git Submodule
- `revoletion/` is git submodule - **do not modify** to allow clean updates from upstream fork
- STRIDE code stays outside `revoletion/` directory
- Current status: `revoletion` shows as modified in git status (likely local changes during debugging)

### Results Naming
- Timestamp-based: `revoletion/results/YYYYMMDD_HHMMSS_scenarioname/`
- Prevents overwrites, enables version tracking

### CSV Format
- Sparse matrix: rows = block parameters, columns = scenarios
- Format: `block,key,scenario_name_1,scenario_name_2,...`
- Example: `pv1,size_invest,100000,200000` → 100kW option in scenario 1, 200kW in scenario 2

### Units
- **Power**: W (watts)
- **Energy**: Wh (watt-hours)
- **Costs**: € (euros)
- **Emissions**: kg CO2
- **Time**: hours
- Note: REVOLETION uses W/Wh internally, display often converts to kW/kWh/MWh

### Optimization Solver
- **Preferred**: Gurobi (commercial, faster, handles large MILPs)
- **Fallback**: CBC (open-source, slower for large problems)
- Set in settings CSV: `solver,gurobi` or `solver,cbc`

### Code Style
- REVOLETION uses verbose variable names (e.g., `prediction_horizon`, `commitment_horizon`)
- STRIDE follows same convention for consistency
- Type hints not consistently used in REVOLETION - STRIDE code should add them where helpful

### Scenario Naming Convention
- Base scenarios: `scenarios_base.csv`, `scenarios_example.csv`
- Multi-stage: `scenarios_multistage.csv`, `stage_2025.csv`, `stage_2030.csv`, etc.
- CO2 variants: `scenario_co2_100`, `scenario_co2_500` (numbers = kg CO2 limit)

---

## Common Tasks Reference

### Run Single-Stage REVOLETION Optimization
```bash
cd revoletion
python -m revoletion.main \
    --settings example/settings.csv \
    --scenario example/scenarios_example.csv
```

### Run Multi-Stage STRIDE Optimization
```bash
python multi_stage/sequential_optimizer.py --config config.yaml
```
(Config specifies: base scenario CSV, stages, cost evolution params, CO2 pathway)

### Validate CO2 Constraint
```bash
jupyter notebook notebooks/01_test_co2_constraint/01_test_co2_constraint.ipynb
```

### Test 2-Stage Workflow
```bash
jupyter notebook notebooks/02_test_2_stage/02_test_2_stage.ipynb
```

### Check Results
- Summary: `revoletion/results/TIMESTAMP_*/summary.csv`
- Timeseries: `revoletion/results/TIMESTAMP_*/timeseries.csv`
- Plots: `revoletion/results/TIMESTAMP_*/*.html` (open in browser)
- Status: `revoletion/results/TIMESTAMP_*/status.csv` (check for infeasibility)

---

## Key Technical Insights

### CO2 Constraint Implementation
- Location: `revoletion/revoletion/constraints.py:296-343`
- Mechanism: Adds pyomo constraint limiting total CO2 emissions from grid imports
- Formula: `sum(grid_import * co2_spec_g2s * dt) <= co2_max`
- Set via scenario CSV: `scenario,co2_max,100000` (kg CO2)
- Project-level tracking: Simulation emissions extrapolated to full project duration

### Stage Linking Mechanism
- ScenarioBuilder reads previous stage results (pickled)
- Extracts final capacities: `pv_size_total`, `ess_size_total`, `grid_size_total`
- Writes to next stage CSV: `pv1,size_existing,<prev_total>`
- Investment-only optimization: `size_invest` variable optimizes additional capacity
- Non-reversible: No capacity reduction allowed (realistic constraint)

### Technology Cost Evolution
- Exponential decline formula: `cost(year) = cost_2025 * (1 - decline_rate)^(year - 2025)`
- PV: 5% annual decline (conservative vs historical 10-20%)
- ESS: 8% annual decline (aligned with NREL projections)
- Applied per stage in `scenario_builder.py`

### Myopic vs Perfect Foresight
- **Myopic** (STRIDE approach): Each stage optimizes independently, no future knowledge
- **Perfect foresight**: Single optimization knows all 25 years (unrealistic)
- Tradeoff: Myopic may over/under-invest due to uncertainty, but reflects real decision-making

### NPV Calculation
- 9% WACC (Weighted Average Cost of Capital) - typical for utility-scale solar+storage
- Discounting formula: `NPV = sum(cashflow_t / (1 + WACC)^t)` for t = 0 to 25 years
- Stage cashflows discounted back to 2025 base year
- Handled in `results_parser.py`

---

## Thesis Milestones (Reference)

Based on `STRIDE_Thesis_Master_Reference.md`:

- **Oct 2025**: Start, REVOLETION integration (✅ Done)
- **Nov 2025**: CO2 constraint, 2-stage optimizer (✅ Done)
- **Dec 2025 - Jan 2026**: Full 6-stage runs, case studies (🚧 Current)
- **Feb 2026**: Sensitivity analysis, visualizations
- **Mar 2026**: Thesis writing (60-90 pages)
- **Apr 13, 2026**: Submission deadline

---

## Questions/Clarifications for AI Assistant

When working on this codebase, consider:

1. **Modifying REVOLETION**: Should changes go in fork or STRIDE wrapper? Default: wrapper unless core bug fix
2. **Stage duration**: Currently fixed 5 years - variable durations possible future extension
3. **Analysis modules**: Stubs exist (`analysis/*.py`) - implementations needed for visualizations
4. **Infeasibility handling**: Current approach logs diagnostics - more sophisticated recovery strategies possible
5. **Uncertainty modeling**: `uncertainty.py` placeholder - stochastic formulations future work
6. **Battery degradation**: REVOLETION has detailed aging models - STRIDE doesn't yet use in multi-stage context

---

*Last updated: November 2025*
*For questions on this codebase, refer to this file first before exploring code*
